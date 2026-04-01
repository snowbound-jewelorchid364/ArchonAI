"""Tests for CostReader — AWS, GCP, Azure CSV parsing."""
import pytest
from datetime import date
from archon.infrastructure.tools.cost_reader import CostReader, CostLineItem, CostSummary


@pytest.fixture
def reader():
    return CostReader()


AWS_CSV = """Service,UsageType,Region,Cost,StartDate,EndDate
Amazon EC2,BoxUsage:m5.xlarge,us-east-1,450.00,2024-01-01,2024-01-31
Amazon S3,Requests-Tier1,us-east-1,25.50,2024-01-01,2024-01-31
Amazon RDS,InstanceUsage:db.r5.large,us-west-2,320.00,2024-01-01,2024-01-31
Amazon Lambda,Request,us-east-1,0,2024-01-01,2024-01-31"""

GCP_CSV = """Service description,SKU description,Location,Cost,Usage start date,Usage end date
Compute Engine,N1 Predefined Instance Core,us-central1,380.00,2024-01-01,2024-01-31
Cloud Storage,Standard Storage US Multi-region,us,12.75,2024-01-01,2024-01-31"""

AZURE_CSV = """MeterCategory,MeterSubCategory,ResourceLocation,CostInBillingCurrency,Date,SubscriptionId
Virtual Machines,Dv3 Series,eastus,290.00,2024-01-15,sub-123
Storage,Blob Storage,westeurope,45.50,2024-01-15,sub-123"""


def test_parse_aws_csv(reader):
    summary = reader.parse_aws_csv(AWS_CSV)
    assert summary.provider == "aws"
    assert summary.total_cost == 795.50
    assert len(summary.line_items) == 3  # Lambda $0 excluded
    assert "Amazon EC2" in summary.by_service
    assert summary.by_service["Amazon EC2"] == 450.00
    assert summary.period_start == date(2024, 1, 1)


def test_parse_gcp_csv(reader):
    summary = reader.parse_gcp_csv(GCP_CSV)
    assert summary.provider == "gcp"
    assert summary.total_cost == 392.75
    assert len(summary.line_items) == 2
    assert "Compute Engine" in summary.by_service


def test_parse_azure_csv(reader):
    summary = reader.parse_azure_csv(AZURE_CSV)
    assert summary.provider == "azure"
    assert summary.total_cost == 335.50
    assert len(summary.line_items) == 2
    assert "Virtual Machines" in summary.by_service
    assert summary.by_region["eastus"] == 290.00


def test_zero_cost_items_excluded(reader):
    summary = reader.parse_aws_csv(AWS_CSV)
    services = [item.service for item in summary.line_items]
    assert "Amazon Lambda" not in services


def test_top_items_sorted_by_cost(reader):
    summary = reader.parse_aws_csv(AWS_CSV)
    costs = [item.cost for item in summary.top_items]
    assert costs == sorted(costs, reverse=True)


def test_empty_csv(reader):
    summary = reader.parse_aws_csv("Service,Cost\n")
    assert summary.total_cost == 0.0
    assert summary.line_items == []
    assert summary.period_start is None


def test_unsupported_provider(reader):
    with pytest.raises(ValueError, match="Unsupported provider"):
        reader.parse_file("dummy.csv", "oracle")


def test_parse_float_edge_cases():
    assert CostReader._parse_float("$1,234.56") == 1234.56
    assert CostReader._parse_float("invalid") == 0.0
    assert CostReader._parse_float("") == 0.0


def test_parse_date_formats():
    assert CostReader._parse_date("2024-01-15") == date(2024, 1, 15)
    assert CostReader._parse_date("01/15/2024") == date(2024, 1, 15)
    assert CostReader._parse_date("2024/01/15") == date(2024, 1, 15)
    assert CostReader._parse_date(None) is None
    assert CostReader._parse_date("not-a-date") is None
