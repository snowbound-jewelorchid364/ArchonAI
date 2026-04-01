from __future__ import annotations

import json
from typing import Any

from .base import InputParser, ParsedInput


class APMParser(InputParser):
    async def parse(self, source: str | bytes) -> ParsedInput:
        text = source.decode("utf-8", errors="ignore") if isinstance(source, bytes) else source
        if not text.strip():
            return ParsedInput(
                source_type="apm",
                content="No APM payload provided.",
                metadata={"peak_rps": 0, "p99_latency_ms": 0.0, "error_rate_pct": 0.0},
            )

        data = json.loads(text)
        endpoints = _extract_endpoints(data)

        if not endpoints:
            return ParsedInput(
                source_type="apm",
                content="No endpoint metrics found.",
                metadata={"peak_rps": 0, "p99_latency_ms": 0.0, "error_rate_pct": 0.0},
            )

        slowest = sorted(endpoints, key=lambda e: e.get("p99", 0.0), reverse=True)[:5]
        peak_rps = max(float(e.get("rps", 0.0)) for e in endpoints)
        p99 = max(float(e.get("p99", 0.0)) for e in endpoints)
        err = max(float(e.get("error_rate_pct", 0.0)) for e in endpoints)

        lines = ["Endpoint latency and error summary:"]
        for e in slowest:
            lines.append(
                f"- {e['endpoint']}: p50={e['p50']}ms p95={e['p95']}ms p99={e['p99']}ms "
                f"error={e['error_rate_pct']}% rps={e['rps']}"
            )

        return ParsedInput(
            source_type="apm",
            content="\n".join(lines),
            metadata={"peak_rps": peak_rps, "p99_latency_ms": p99, "error_rate_pct": err},
        )


def _extract_endpoints(data: dict[str, Any]) -> list[dict[str, float | str]]:
    candidates = data.get("endpoints") or data.get("routes") or data.get("metrics") or []
    out: list[dict[str, float | str]] = []
    if isinstance(candidates, dict):
        candidates = list(candidates.values())
    if not isinstance(candidates, list):
        return out

    for item in candidates:
        if not isinstance(item, dict):
            continue
        endpoint = str(item.get("endpoint") or item.get("path") or item.get("name") or "unknown")
        out.append(
            {
                "endpoint": endpoint,
                "p50": float(item.get("p50") or item.get("latency_p50") or 0),
                "p95": float(item.get("p95") or item.get("latency_p95") or 0),
                "p99": float(item.get("p99") or item.get("latency_p99") or 0),
                "error_rate_pct": float(item.get("error_rate_pct") or item.get("error_rate") or 0),
                "rps": float(item.get("rps") or item.get("requests_per_second") or 0),
            }
        )
    return out
