from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from .base import ConnectorContext, MCPConnector, now_iso


class AWSConnector(MCPConnector):
    name = "aws"

    async def fetch(self, **kwargs) -> ConnectorContext:
        aws_region = kwargs.get("aws_region", "us-east-1")
        raw_data: dict = {
            "stacks": [],
            "costs": [],
            "alarms": [],
            "security_findings": {"CRITICAL": 0, "HIGH": 0},
        }

        access_key = os.getenv("AWS_ACCESS_KEY_ID", "")
        secret = os.getenv("AWS_SECRET_ACCESS_KEY", "")
        if not access_key or not secret:
            return ConnectorContext(
                source=self.name,
                summary="AWS credentials not configured. Returning empty AWS context.",
                raw_data=raw_data,
                fetched_at=now_iso(),
            )

        try:
            import boto3
        except Exception:
            return ConnectorContext(
                source=self.name,
                summary="boto3 unavailable. Returning empty AWS context.",
                raw_data=raw_data,
                fetched_at=now_iso(),
            )

        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret,
            region_name=aws_region,
        )

        try:
            cfn = session.client("cloudformation", region_name=aws_region)
            stacks = cfn.list_stacks().get("StackSummaries", [])
            raw_data["stacks"] = [
                {
                    "name": s.get("StackName"),
                    "status": s.get("StackStatus"),
                    "last_updated": (s.get("LastUpdatedTime") or s.get("CreationTime")).isoformat()
                    if (s.get("LastUpdatedTime") or s.get("CreationTime"))
                    else None,
                }
                for s in stacks[:50]
            ]
        except Exception:
            raw_data["stacks"] = []

        try:
            ce = session.client("ce", region_name="us-east-1")
            end = datetime.now(timezone.utc).date()
            start = end - timedelta(days=30)
            out = ce.get_cost_and_usage(
                TimePeriod={"Start": str(start), "End": str(end)},
                Granularity="MONTHLY",
                Metrics=["UnblendedCost"],
                GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
            )
            groups = (out.get("ResultsByTime", [{}])[0]).get("Groups", [])
            costs = []
            for g in groups:
                service = (g.get("Keys") or ["Unknown"])[0]
                amount = float(((g.get("Metrics") or {}).get("UnblendedCost") or {}).get("Amount", "0"))
                costs.append({"service": service, "amount": amount})
            raw_data["costs"] = sorted(costs, key=lambda x: x["amount"], reverse=True)[:10]
        except Exception:
            raw_data["costs"] = []

        try:
            cw = session.client("cloudwatch", region_name=aws_region)
            alarms = cw.describe_alarms(StateValue="ALARM").get("MetricAlarms", [])
            raw_data["alarms"] = [
                {
                    "name": a.get("AlarmName"),
                    "state": a.get("StateValue"),
                    "updated": a.get("StateUpdatedTimestamp").isoformat()
                    if a.get("StateUpdatedTimestamp")
                    else None,
                }
                for a in alarms
            ]
        except Exception:
            raw_data["alarms"] = []

        try:
            sh = session.client("securityhub", region_name=aws_region)
            findings = sh.get_findings(
                Filters={
                    "SeverityLabel": [
                        {"Value": "CRITICAL", "Comparison": "EQUALS"},
                        {"Value": "HIGH", "Comparison": "EQUALS"},
                    ]
                },
                MaxResults=100,
            ).get("Findings", [])
            critical = sum(1 for f in findings if (f.get("Severity") or {}).get("Label") == "CRITICAL")
            high = sum(1 for f in findings if (f.get("Severity") or {}).get("Label") == "HIGH")
            raw_data["security_findings"] = {"CRITICAL": critical, "HIGH": high}
        except Exception:
            raw_data["security_findings"] = {"CRITICAL": 0, "HIGH": 0}

        summary = (
            f"Fetched AWS context in {aws_region}. "
            f"Stacks: {len(raw_data['stacks'])}, cost services: {len(raw_data['costs'])}, "
            f"alarms in ALARM: {len(raw_data['alarms'])}, "
            f"Security Hub findings (CRITICAL/HIGH): "
            f"{raw_data['security_findings']['CRITICAL']}/{raw_data['security_findings']['HIGH']}."
        )
        return ConnectorContext(
            source=self.name,
            summary=summary,
            raw_data=raw_data,
            fetched_at=now_iso(),
        )
