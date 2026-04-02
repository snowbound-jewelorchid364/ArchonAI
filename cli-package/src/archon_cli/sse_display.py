from __future__ import annotations

import json
from io import StringIO
from typing import Any

import httpx
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

STATUS_STYLES = {
    "RUNNING": "yellow",
    "COMPLETED": "green",
    "FAILED": "red",
    "PARTIAL": "dark_orange",
}
console = Console()


def _render_table(rows: dict[str, dict[str, Any]]) -> Table:
    table = Table(title="ARCHON Review Progress")
    table.add_column("Agent")
    table.add_column("Status")
    table.add_column("Findings")
    for agent, payload in rows.items():
        status = str(payload.get("status", "RUNNING")).upper()
        findings = payload.get("findings_count", "-")
        style = STATUS_STYLES.get(status, "white")
        table.add_row(agent, f"[{style}]{status}[/{style}]", str(findings))
    return table


def stream_review_progress(url: str, token: str) -> None:
    rows: dict[str, dict[str, Any]] = {}
    event_type = "message"
    summary = "Review stream complete."

    with httpx.Client(headers={"Authorization": f"Bearer {token}"}, timeout=httpx.Timeout(None)) as client:
        with client.stream("GET", url) as response:
            response.raise_for_status()
            with Live(_render_table(rows), console=console, refresh_per_second=4) as live:
                for raw_line in response.iter_lines():
                    if raw_line is None:
                        continue
                    line = raw_line if isinstance(raw_line, str) else raw_line.decode("utf-8")
                    if not line:
                        continue
                    if line.startswith("event: "):
                        event_type = line[7:].strip()
                        continue
                    if not line.startswith("data: "):
                        continue
                    data = line[6:].strip()
                    if event_type == "done":
                        summary = data or summary
                        break
                    if event_type != "agent_update":
                        continue
                    try:
                        payload = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    agent = payload.get("agent", "unknown")
                    rows[agent] = payload
                    live.update(_render_table(rows))

    console.print(Panel(summary, title="ARCHON Review Summary", border_style="green"))
