import pytest
from archon.infrastructure.tools.cost_reader import CostReader, CostSummary


class TestCostReaderAWS:
    def test_parse_aws_csv(self):
        csv_content = "Service,UsageType,Region,Cost,StartDate,EndDate\n"
        csv_content += "EC2,BoxUsage,us-east-1,150.00,2024-01-01,2024-01-31\n"
        csv_content += "S3,TimedStorage,us-east-1,25.50,2024-01-01,2024-01-31\n"
        reader = CostReader()
        summary = reader.parse_aws_csv(csv_content)
        assert isinstance(summary, CostSummary)
        assert summary.total_cost == pytest.approx(175.50)
        assert summary.provider == "aws"
        assert "EC2" in summary.by_service
        assert "S3" in summary.by_service

    def test_parse_aws_zero_cost_skipped(self):
        csv_content = "Service,UsageType,Region,Cost\nEC2,BoxUsage,us-east-1,0.00\n"
        reader = CostReader()
        summary = reader.parse_aws_csv(csv_content)
        assert summary.total_cost == 0.0
        assert len(summary.line_items) == 0

    def test_parse_aws_empty_csv(self):
        csv_content = "Service,UsageType,Region,Cost\n"
        reader = CostReader()
        summary = reader.parse_aws_csv(csv_content)
        assert summary.total_cost == 0.0


class TestCostReaderGCP:
    def test_parse_gcp_csv(self):
        csv_content = "Service description,SKU description,Location,Cost\n"
        csv_content += "Compute Engine,N1 Standard,us-central1,200.00\n"
        reader = CostReader()
        summary = reader.parse_gcp_csv(csv_content)
        assert isinstance(summary, CostSummary)
        assert summary.provider == "gcp"
        assert summary.total_cost == pytest.approx(200.00)
