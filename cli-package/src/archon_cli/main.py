"""ARCHON CLI - main entry point."""
from __future__ import annotations

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from archon_cli.client import (
    ArchonAPIClient,
    ArchonAPIError,
    ArchonAuthError,
    ArchonConnectionError,
)
from archon_cli.config import clear_config, get_config, save_config
from archon_cli.sse_display import stream_review_progress

console = Console()

MODES = [
    "review",
    "design",
    "migration_planner",
    "compliance_auditor",
    "due_diligence",
    "incident_responder",
    "cost_optimiser",
    "pr_reviewer",
    "scaling_advisor",
    "drift_monitor",
    "feature_feasibility",
    "vendor_evaluator",
    "onboarding_accelerator",
    "sunset_planner",
]


@click.group()
@click.version_option(version="0.1.0", prog_name="archon")
def cli() -> None:
    """ARCHON - Your Frontier AI Architect.

    Run autonomous architecture reviews powered by 6 specialist AI agents.
    """


@cli.command()
@click.option("--api-url", prompt="ARCHON API URL", default="https://api.archon.dev")
@click.option("--api-key", prompt="ARCHON API Key / Clerk session token", hide_input=True)
def login(api_url: str, api_key: str) -> None:
    client = ArchonAPIClient(api_url, api_key)
    try:
        user = client.validate_token()
    except (ArchonConnectionError, ArchonAuthError, ArchonAPIError) as exc:
        console.print(f"[red]Login failed:[/red] {exc}")
        raise SystemExit(1) from exc

    save_config(api_url, api_key)
    console.print(f"[green]Logged in.[/green] {user.get('email', 'unknown')} ({user.get('plan', 'starter')})")


@cli.command()
def logout() -> None:
    clear_config()
    console.print("[green]Logged out.[/green]")


@cli.command()
def status() -> None:
    config = get_config()
    if not config.api_key:
        console.print("[yellow]Not logged in.[/yellow] Run [bold]archon login[/bold].")
        return

    client = ArchonAPIClient(config.api_url, config.api_key)
    try:
        user = client.validate_token()
    except (ArchonConnectionError, ArchonAuthError, ArchonAPIError) as exc:
        console.print(f"[red]Status check failed:[/red] {exc}")
        raise SystemExit(1) from exc

    table = Table(title="ARCHON CLI Status")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("API URL", config.api_url)
    table.add_row("Email", user.get("email", "unknown"))
    table.add_row("Plan", user.get("plan", "starter"))
    table.add_row("User ID", user.get("user_id", "unknown"))
    console.print(table)


@cli.command(name='run')
@click.argument("repo_url")
@click.option("--mode", "-m", type=click.Choice(MODES), default="review", help="Review mode")
@click.option("--hitl", type=click.Choice(["autopilot", "balanced", "supervised"]), default="balanced", help="Human-in-the-loop mode")
@click.option("--output", "-o", type=click.Path(), default=None, help="Output directory for the review package")
@click.option("--format", "fmt", type=click.Choice(["markdown", "zip", "both"]), default="both", help="Output format")
@click.option("--no-stream", is_flag=True, help="Skip SSE live display and poll for completion instead")
def run(repo_url: str, mode: str, hitl: str, output: str | None, fmt: str, no_stream: bool) -> None:
    config = get_config()
    if not config.api_key:
        console.print("[red]No API key configured.[/red] Run [bold]archon login[/bold] or [bold]archon configure[/bold].")
        raise SystemExit(1)

    client = ArchonAPIClient(config.api_url, config.api_key)
    console.print(
        Panel(
            f"[bold blue]ARCHON[/bold blue] - {mode.replace('_', ' ').title()}\nRepo: {repo_url}\nHITL: {hitl}",
            title="Starting Review",
            border_style="blue",
        )
    )

    try:
        review_ref = client.start_review(repo_url, mode, hitl)
        review_id = review_ref["review_id"]
        job_id = review_ref["job_id"]
        console.print(f"[green]Review started:[/green] review_id={review_id} job_id={job_id}")

        if no_stream:
            review = client.poll_review(review_id)
        else:
            stream_review_progress(f"{config.api_url.rstrip('/')}/api/v1/jobs/{job_id}/stream", config.api_key)
            review = client.get_review(review_id)

        findings = review.get("findings", [])
        console.print()
        _print_summary(findings)

        output_dir = output or "."
        if fmt in ("zip", "both"):
            zip_path = client.download_package(review_id, output_dir)
            console.print(f"\n[green]Package saved:[/green] {zip_path}")
        if fmt in ("markdown", "both"):
            md_path = client.download_markdown(review_id, output_dir)
            console.print(f"[green]Markdown saved:[/green] {md_path}")
    except KeyboardInterrupt:
        console.print("\n[yellow]Review cancelled.[/yellow]")
        raise SystemExit(1)
    except (ArchonConnectionError, ArchonAuthError, ArchonAPIError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise SystemExit(1) from exc


@cli.command()
def modes() -> None:
    table = Table(title="ARCHON Review Modes")
    table.add_column("#", style="dim")
    table.add_column("Mode", style="bold")
    table.add_column("Description")
    descriptions = {
        "review": "Audit existing codebase",
        "design": "New product from scratch",
        "migration_planner": "Modernisation project",
        "compliance_auditor": "SOC2/HIPAA/GDPR audit",
        "due_diligence": "Fundraise / M&A",
        "incident_responder": "P0/P1 outage",
        "cost_optimiser": "Cloud bill spike",
        "pr_reviewer": "Pull request opened",
        "scaling_advisor": "Traffic growing",
        "drift_monitor": "Weekly architecture check",
        "feature_feasibility": "Can we build X?",
        "vendor_evaluator": "Database / cloud choice",
        "onboarding_accelerator": "New CTO / senior hire",
        "sunset_planner": "Decommission a service",
    }
    for index, mode_name in enumerate(MODES, 1):
        table.add_row(str(index), mode_name, descriptions.get(mode_name, ""))
    console.print(table)


@cli.command()
@click.option("--api-url", prompt="ARCHON API URL", default="https://api.archon.dev")
@click.option("--api-key", prompt="ARCHON API Key", hide_input=True)
def configure(api_url: str, api_key: str) -> None:
    save_config(api_url, api_key)
    console.print("[green]Configuration saved.[/green]")


@cli.command()
def history() -> None:
    config = get_config()
    if not config.api_key:
        console.print("[red]No API key configured.[/red] Run [bold]archon login[/bold] or [bold]archon configure[/bold].")
        raise SystemExit(1)

    client = ArchonAPIClient(config.api_url, config.api_key)
    try:
        reviews = client.get_history()
    except (ArchonConnectionError, ArchonAuthError, ArchonAPIError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise SystemExit(1) from exc

    table = Table(title="Review History")
    table.add_column("ID", style="dim")
    table.add_column("Mode")
    table.add_column("Status")
    table.add_column("Findings")
    table.add_column("Date")
    for review in reviews:
        table.add_row(
            review["id"][:8],
            review.get("mode", "?"),
            review.get("status", "?"),
            str(len(review.get("findings", []))),
            review.get("completedAt", "-"),
        )
    console.print(table)


def _print_summary(findings: list[dict[str, object]]) -> None:
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    for finding in findings:
        severity = str(finding.get("severity", "INFO"))
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    table = Table(title=f"Review Complete - {len(findings)} Findings")
    table.add_column("Severity", style="bold")
    table.add_column("Count")
    colors = {"CRITICAL": "red", "HIGH": "yellow", "MEDIUM": "cyan", "LOW": "green", "INFO": "dim"}
    for severity, count in severity_counts.items():
        if count > 0:
            table.add_row(f"[{colors[severity]}]{severity}[/{colors[severity]}]", str(count))
    console.print(table)


if __name__ == "__main__":
    cli()
