from __future__ import annotations

import csv
import io
from typing import Any

from .base import InputParser, ParsedInput


class CostParser(InputParser):
    async def parse(self, source: str | bytes) -> ParsedInput:
        text = source.decode("utf-8", errors="ignore") if isinstance(source, bytes) else source
        text = text.strip()
        if not text:
            return ParsedInput(
                source_type="cost_csv",
                content="No cost records were provided.",
                metadata={"total_monthly": 0.0, "top_services": [], "currency": "USD"},
            )

        reader = csv.DictReader(io.StringIO(text))
        rows: list[dict[str, Any]] = list(reader)
        if not rows:
            return ParsedInput(
                source_type="cost_csv",
                content="No cost records were provided.",
                metadata={"total_monthly": 0.0, "top_services": [], "currency": "USD"},
            )

        services: dict[str, float] = {}
        trends: dict[str, str] = {}
        currency = "USD"

        for row in rows:
            service = str(
                row.get("Service")
                or row.get("service")
                or row.get("ServiceName")
                or row.get("PRODUCT_NAME")
                or "unknown"
            ).strip()
            amount = _to_float(
                row.get("MonthlyCost")
                or row.get("Cost")
                or row.get("UnblendedCost")
                or row.get("Amount")
                or row.get("cost")
                or 0
            )
            prev = _to_float(row.get("PreviousMonthCost") or row.get("PrevCost") or 0)
            currency = str(row.get("Currency") or row.get("currency") or currency or "USD")

            services[service] = services.get(service, 0.0) + amount
            trends[service] = "up" if amount > prev else "down" if amount < prev else "flat"

        top_services = sorted(services.items(), key=lambda x: x[1], reverse=True)[:10]
        total_monthly = round(sum(services.values()), 2)

        lines = ["Top service spend summary:"]
        for name, cost in top_services:
            lines.append(f"- {name}: {cost:.2f} {currency} ({trends.get(name, 'flat')})")

        return ParsedInput(
            source_type="cost_csv",
            content="\n".join(lines),
            metadata={
                "total_monthly": total_monthly,
                "top_services": [
                    {"service": name, "monthly_cost": round(cost, 2), "trend": trends.get(name, "flat")}
                    for name, cost in top_services
                ],
                "currency": currency,
            },
        )


def _to_float(value: Any) -> float:
    try:
        return float(str(value).replace(",", "").strip() or 0)
    except (TypeError, ValueError):
        return 0.0
