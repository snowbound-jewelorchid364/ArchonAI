"""ARCHON CLI - main entry point."""
import sys
import time
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.markdown import Markdown

from archon_cli.client import ArchonAPIClient
from archon_cli.config import get_config

console = Console()

MODES = [
    "review", "design", "migration_planner", "compliance_auditor",
    "due_diligence", "incident_responder", "cost_optimiser", "pr_reviewer",
    "scaling_advisor", "drift_monitor", "feature_feasibility",
    "vendor_evaluator", "onboarding_accelerator", "sunset_planner",
]


@click.group()
@click.version_option(version="0.1.0", prog_name="archon")
def cli():
    """ARCHON - Your Frontier AI Architect.

    Run autonomous architecture reviews powered by 6 specialist AI agents.
    """
    pass


@cli.command()
@click.argument("repo_url")
@click.option("--mode", "-m", type=click.Choice(MODES), default="review", help="Review mode")
@click.option("--hitl", type=click.Choice(["autopilot", "balanced", "supervised"]), default="balanced", help="Human-in-the-loop mode")
@click.option("--output", "-o", type=click.Path(), default=None, help="Output directory for the review package")
@click.option("--format", "fmt", type=click.Choice(["markdown", "zip", "both"]), default="both", help="Output format")
def run(repo_url: str, mode: str, hitl: str, output: str, fmt: str):
    """Run an architecture review on a GitHub repository.

    Example: archon run https://github.com/org/repo --mode review
    """
    config = get_config()
    client = ArchonAPIClient(config.api_url, config.api_key)

    console.print(Panel(
        f"[bold blue]ARCHON[/bold blue] - {mode.replace('_', ' ').title()}\n"
        f"Repo: {repo_url}\n"
        f"HITL: {hitl}",
        title="Starting Review",
        border_style="blue",
    ))

    try:
        # Start review
        job_id = client.start_review(repo_url, mode, hitl)
        console.print(f"[green]Review started:[/green] job_id={job_id}")

        # Stream progress
        agents_status = {}
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Waiting for agents...", total=6)

            for event in client.stream_progress(job_id):
                agent = event.get("agent", "unknown")
                status = event.get("status", "unknown")
                agents_status[agent] = status

                completed = sum(1 for s in agents_status.values() if s == "complete")
                progress.update(task, completed=completed, description=f"{agent}: {status}")

                if status == "complete":
                    findings = event.get("findingCount", 0)
                    console.print(f"  [green]✓[/green] {agent}: {findings} findings")
                elif status == "failed":
                    console.print(f"  [red]✗[/red] {agent}: failed")

        # Get results
        review = client.get_review(job_id)
        findings = review.get("findings", [])

        # Display summary
        console.print()
        _print_summary(findings)

        # Download package
        if fmt in ("zip", "both"):
            output_dir = output or "."
            zip_path = client.download_package(job_id, output_dir)
            console.print(f"\n[green]Package saved:[/green] {zip_path}")

        if fmt in ("markdown", "both"):
            md_path = client.download_markdown(job_id, output or ".")
            console.print(f"[green]Markdown saved:[/green] {md_path}")

    except KeyboardInterrupt:
        console.print("\n[yellow]Review cancelled.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@cli.command()
def modes():
    """List all available review modes."""
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

    for i, mode in enumerate(MODES, 1):
        table.add_row(str(i), mode, descriptions.get(mode, ""))

    console.print(table)


@cli.command()
@click.option("--api-url", prompt="ARCHON API URL", default="https://api.archon.dev")
@click.option("--api-key", prompt="ARCHON API Key", hide_input=True)
def configure(api_url: str, api_key: str):
    """Configure ARCHON CLI credentials."""
    from archon_cli.config import save_config
    save_config(api_url, api_key)
    console.print("[green]Configuration saved.[/green]")


@cli.command()
def history():
    """Show review history."""
    config = get_config()
    client = ArchonAPIClient(config.api_url, config.api_key)

    reviews = client.get_history()
    table = Table(title="Review History")
    table.add_column("ID", style="dim")
    table.add_column("Mode")
    table.add_column("Status")
    table.add_column("Findings")
    table.add_column("Date")

    for r in reviews:
        table.add_row(
            r["id"][:8],
            r.get("mode", "?"),
            r.get("status", "?"),
            str(len(r.get("findings", []))),
            r.get("completedAt", "-"),
        )

    console.print(table)


def _print_summary(findings: list) -> None:
    """Print findings summary table."""
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    for f in findings:
        sev = f.get("severity", "INFO")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    table = Table(title=f"Review Complete - {len(findings)} Findings")
    table.add_column("Severity", style="bold")
    table.add_column("Count")

    colors = {"CRITICAL": "red", "HIGH": "yellow", "MEDIUM": "cyan", "LOW": "green", "INFO": "dim"}
    for sev, count in severity_counts.items():
        if count > 0:
            table.add_row(f"[{colors[sev]}]{sev}[/{colors[sev]}]", str(count))

    console.print(table)


if __name__ == "__main__":
    cli()
