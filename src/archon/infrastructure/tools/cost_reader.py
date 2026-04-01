"""Cloud cost data reader for Cost Optimiser mode.

Parses AWS Cost Explorer and GCP Billing CSV exports into structured
cost data that agents can analyse.
"""
from __future__ import annotations

import csv
import io
import logging
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CostLineItem:
    """Single cost line item from a cloud provider."""

    provider: str  # "aws" | "gcp" | "azure"
    service: str
    usage_type: str
    region: str
    cost: float
    currency: str = "USD"
    period_start: date | None = None
    period_end: date | None = None
    account_id: str = ""
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class CostSummary:
    """Aggregated cost summary for agent consumption."""

    total_cost: float
    currency: str
    provider: str
    period_start: date | None
    period_end: date | None
    by_service: dict[str, float] = field(default_factory=dict)
    by_region: dict[str, float] = field(default_factory=dict)
    top_items: list[CostLineItem] = field(default_factory=list)
    line_items: list[CostLineItem] = field(default_factory=list)


class CostReader:
    """Reads and parses cloud cost CSV exports."""

    def parse_aws_csv(self, content: str) -> CostSummary:
        """Parse AWS Cost Explorer CSV export.

        Expected columns: Service, UsageType, Region, Cost, StartDate, EndDate
        """
        reader = csv.DictReader(io.StringIO(content))
        items: list[CostLineItem] = []
        for row in reader:
            cost_val = self._parse_float(row.get("Cost") or row.get("TotalCost") or "0")
            if cost_val == 0.0:
                continue
            items.append(CostLineItem(
                provider="aws",
                service=row.get("Service", row.get("ProductName", "Unknown")),
                usage_type=row.get("UsageType", ""),
                region=row.get("Region", row.get("AvailabilityZone", "")),
                cost=cost_val,
                period_start=self._parse_date(row.get("StartDate") or row.get("BillingPeriodStart")),
                period_end=self._parse_date(row.get("EndDate") or row.get("BillingPeriodEnd")),
                account_id=row.get("LinkedAccountId", row.get("AccountId", "")),
            ))
        return self._build_summary(items, "aws")

    def parse_gcp_csv(self, content: str) -> CostSummary:
        """Parse GCP Billing CSV export.

        Expected columns: Service description, SKU description, Location, Cost, Usage start date
        """
        reader = csv.DictReader(io.StringIO(content))
        items: list[CostLineItem] = []
        for row in reader:
            cost_val = self._parse_float(row.get("Cost") or row.get("cost") or "0")
            if cost_val == 0.0:
                continue
            items.append(CostLineItem(
                provider="gcp",
                service=row.get("Service description", row.get("service.description", "Unknown")),
                usage_type=row.get("SKU description", row.get("sku.description", "")),
                region=row.get("Location", row.get("location.region", "")),
                cost=cost_val,
                period_start=self._parse_date(row.get("Usage start date") or row.get("usage_start_time")),
                period_end=self._parse_date(row.get("Usage end date") or row.get("usage_end_time")),
                account_id=row.get("Project ID", row.get("project.id", "")),
            ))
        return self._build_summary(items, "gcp")

    def parse_azure_csv(self, content: str) -> CostSummary:
        """Parse Azure Cost Management CSV export."""
        reader = csv.DictReader(io.StringIO(content))
        items: list[CostLineItem] = []
        for row in reader:
            cost_val = self._parse_float(
                row.get("CostInBillingCurrency") or row.get("PreTaxCost") or row.get("Cost") or "0"
            )
            if cost_val == 0.0:
                continue
            items.append(CostLineItem(
                provider="azure",
                service=row.get("MeterCategory", row.get("ServiceName", "Unknown")),
                usage_type=row.get("MeterSubCategory", row.get("MeterName", "")),
                region=row.get("ResourceLocation", ""),
                cost=cost_val,
                period_start=self._parse_date(row.get("Date") or row.get("UsageDateTime")),
                account_id=row.get("SubscriptionId", ""),
            ))
        return self._build_summary(items, "azure")

    def parse_file(self, path: str | Path, provider: str) -> CostSummary:
        """Read a CSV file and parse based on provider."""
        parsers = {"aws": self.parse_aws_csv, "gcp": self.parse_gcp_csv, "azure": self.parse_azure_csv}
        parser = parsers.get(provider.lower())
        if not parser:
            raise ValueError(f"Unsupported provider: {provider}. Use: aws, gcp, azure")
        content = Path(path).read_text(encoding="utf-8")
        return parser(content)

    def _build_summary(self, items: list[CostLineItem], provider: str) -> CostSummary:
        by_service: dict[str, float] = {}
        by_region: dict[str, float] = {}
        for item in items:
            by_service[item.service] = by_service.get(item.service, 0) + item.cost
            if item.region:
                by_region[item.region] = by_region.get(item.region, 0) + item.cost

        total = sum(item.cost for item in items)
        dates = [i.period_start for i in items if i.period_start]
        top_items = sorted(items, key=lambda x: x.cost, reverse=True)[:10]

        return CostSummary(
            total_cost=round(total, 2),
            currency="USD",
            provider=provider,
            period_start=min(dates) if dates else None,
            period_end=max(dates) if dates else None,
            by_service=dict(sorted(by_service.items(), key=lambda x: x[1], reverse=True)),
            by_region=dict(sorted(by_region.items(), key=lambda x: x[1], reverse=True)),
            top_items=top_items,
            line_items=items,
        )

    @staticmethod
    def _parse_float(val: str) -> float:
        try:
            return float(val.replace(",", "").replace("$", "").strip())
        except (ValueError, AttributeError):
            return 0.0

    @staticmethod
    def _parse_date(val: str | None) -> date | None:
        if not val:
            return None
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S", "%Y/%m/%d"):
            try:
                from datetime import datetime
                return datetime.strptime(val.strip(), fmt).date()
            except ValueError:
                continue
        return None
