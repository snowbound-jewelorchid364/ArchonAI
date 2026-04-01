#!/usr/bin/env python3
"""ARCHON CLI entry point."""
from __future__ import annotations
import argparse
import asyncio
import logging
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))


ALL_MODES = [
    "review", "design",
    "migration_planner", "compliance_auditor", "due_diligence", "incident_responder",
    "cost_optimiser", "pr_reviewer", "scaling_advisor", "drift_monitor",
    "feature_feasibility", "vendor_evaluator", "onboarding_accelerator", "sunset_planner",
    "idea_mode",
]



async def run_idea_mode(args) -> int:
    """Interactive Idea Mode -- no repo needed."""
    from dotenv import load_dotenv
    load_dotenv()
    import asyncio
    import uuid as _uuid
    from pathlib import Path as _Path

    from archon.config.settings import settings
    from archon.infrastructure.llm.claude_adapter import ClaudeAdapter
    from archon.infrastructure.search.tavily_adapter import TavilyAdapter
    from archon.infrastructure.search.exa_adapter import ExaAdapter
    from archon.infrastructure.vector_store.in_memory_store import InMemoryVectorStore
    from archon.rag.retriever import RAGRetriever
    from archon.engine.supervisor import Supervisor
    from archon.engine.runner import Runner
    from archon.engine.hitl.checkpoints import HITLMode
    from archon.engine.intake import INTAKE_QUESTIONS, run_intake
    from archon.engine.requirements_translator import translate
    from archon.engine.multi_option_designer import generate_options
    from archon.output.package_assembler import PackageAssembler

    import logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s - %(message)s")

    idea = args.idea
    print(f"\nARCHON Idea Mode")
    print(f"Idea: {idea}")
    print("=" * 60)
    print("I have a few quick questions. Press Enter after each answer.\n")

    answers: dict[str, str] = {}
    total = len(INTAKE_QUESTIONS)
    for i, (key, question) in enumerate(INTAKE_QUESTIONS, start=1):
        print(f"[{i}/{total}] {question}")
        try:
            answer = input("  > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")
            return 130
        if not answer:
            answer = "Not specified"
        answers[key] = answer
        print()

    print("Translating your answers to technical constraints...")
    try:
        brief = await run_intake(idea, answers)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1

    # Wire infrastructure
    store = InMemoryVectorStore(settings.embedding_model)
    retriever = RAGRetriever(store)
    llm = ClaudeAdapter()
    searchers = [TavilyAdapter(), ExaAdapter()]

    constraints = await translate(brief, llm)
    print(f"Constraints: {constraints.user_type}, {constraints.estimated_rps} rps, ${constraints.budget_monthly_usd}/mo, {constraints.timeline_weeks}wk")

    # Use brief as context string (no repo to index)
    brief_context = (
        f"Product idea: {brief.idea}\n"
        f"Users: {brief.users}\nCore value: {brief.core_value}\n"
        f"Y1 scale: {brief.scale_y1}\nY2 scale: {brief.scale_y2}\n"
        f"Budget: {brief.budget_monthly}\nTimeline: {brief.timeline}\nCompliance: {brief.compliance}"
    )
    repo_url = f"idea:{idea[:60]}"

    supervisor = Supervisor(llm, searchers, retriever)
    runner = Runner(supervisor)

    print("\nRunning 6 specialist agents in parallel (idea_mode)...")
    job_id = str(_uuid.uuid4())[:8]
    job, package = await runner.run(repo_url=repo_url, mode="idea_mode", job_id=job_id, hitl_mode=HITLMode.AUTOPILOT)

    print("\nGenerating 3 architecture options (Lean / Growth-Ready / Enterprise-Scale)...")
    options = await generate_options(package, constraints, llm)

    print("\n" + "=" * 60)
    print("ARCHITECTURE OPTIONS")
    print("=" * 60)
    for opt in options:
        print(f"\n{opt.name}: {opt.tagline}")
        print(f"  Cost:  {opt.monthly_cost_estimate}")
        print(f"  Team:  {opt.team_size}")
        print(f"  MVP:   {opt.time_to_mvp}")
        print(f"  Stack: {', '.join(opt.tech_stack[:5])}")
        for t in opt.key_tradeoffs:
            print(f"  - {t}")

    # Write output
    assembler = PackageAssembler()
    output_path = assembler.assemble(package, args.output_dir, fmt=args.format)
    print(f"\nFull report: {output_path}")
    return 0



async def run_idea_mode(args) -> int:
    """Interactive Idea Mode -- no repo needed."""
    from dotenv import load_dotenv
    load_dotenv()
    import asyncio
    import uuid as _uuid
    from pathlib import Path as _Path

    from archon.config.settings import settings
    from archon.infrastructure.llm.claude_adapter import ClaudeAdapter
    from archon.infrastructure.search.tavily_adapter import TavilyAdapter
    from archon.infrastructure.search.exa_adapter import ExaAdapter
    from archon.infrastructure.vector_store.in_memory_store import InMemoryVectorStore
    from archon.rag.retriever import RAGRetriever
    from archon.engine.supervisor import Supervisor
    from archon.engine.runner import Runner
    from archon.engine.hitl.checkpoints import HITLMode
    from archon.engine.intake import INTAKE_QUESTIONS, run_intake
    from archon.engine.requirements_translator import translate
    from archon.engine.multi_option_designer import generate_options
    from archon.output.package_assembler import PackageAssembler

    import logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s - %(message)s")

    idea = args.idea
    print(f"\nARCHON Idea Mode")
    print(f"Idea: {idea}")
    print("=" * 60)
    print("I have a few quick questions. Press Enter after each answer.\n")

    answers: dict[str, str] = {}
    total = len(INTAKE_QUESTIONS)
    for i, (key, question) in enumerate(INTAKE_QUESTIONS, start=1):
        print(f"[{i}/{total}] {question}")
        try:
            answer = input("  > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")
            return 130
        if not answer:
            answer = "Not specified"
        answers[key] = answer
        print()

    print("Translating your answers to technical constraints...")
    try:
        brief = await run_intake(idea, answers)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1

    # Wire infrastructure
    store = InMemoryVectorStore(settings.embedding_model)
    retriever = RAGRetriever(store)
    llm = ClaudeAdapter()
    searchers = [TavilyAdapter(), ExaAdapter()]

    constraints = await translate(brief, llm)
    print(f"Constraints: {constraints.user_type}, {constraints.estimated_rps} rps, ${constraints.budget_monthly_usd}/mo, {constraints.timeline_weeks}wk")

    # Use brief as context string (no repo to index)
    brief_context = (
        f"Product idea: {brief.idea}\n"
        f"Users: {brief.users}\nCore value: {brief.core_value}\n"
        f"Y1 scale: {brief.scale_y1}\nY2 scale: {brief.scale_y2}\n"
        f"Budget: {brief.budget_monthly}\nTimeline: {brief.timeline}\nCompliance: {brief.compliance}"
    )
    repo_url = f"idea:{idea[:60]}"

    supervisor = Supervisor(llm, searchers, retriever)
    runner = Runner(supervisor)

    print("\nRunning 6 specialist agents in parallel (idea_mode)...")
    job_id = str(_uuid.uuid4())[:8]
    job, package = await runner.run(repo_url=repo_url, mode="idea_mode", job_id=job_id, hitl_mode=HITLMode.AUTOPILOT)

    print("\nGenerating 3 architecture options (Lean / Growth-Ready / Enterprise-Scale)...")
    options = await generate_options(package, constraints, llm)

    print("\n" + "=" * 60)
    print("ARCHITECTURE OPTIONS")
    print("=" * 60)
    for opt in options:
        print(f"\n{opt.name}: {opt.tagline}")
        print(f"  Cost:  {opt.monthly_cost_estimate}")
        print(f"  Team:  {opt.team_size}")
        print(f"  MVP:   {opt.time_to_mvp}")
        print(f"  Stack: {', '.join(opt.tech_stack[:5])}")
        for t in opt.key_tradeoffs:
            print(f"  - {t}")

    # Write output
    assembler = PackageAssembler()
    output_path = assembler.assemble(package, args.output_dir, fmt=args.format)
    print(f"\nFull report: {output_path}")
    return 0


async def run(args: argparse.Namespace) -> int:
    from dotenv import load_dotenv
    load_dotenv()

    from archon.config.settings import settings
    from archon.infrastructure.llm.claude_adapter import ClaudeAdapter
    from archon.infrastructure.search.tavily_adapter import TavilyAdapter
    from archon.infrastructure.search.exa_adapter import ExaAdapter
    from archon.infrastructure.vector_store.in_memory_store import InMemoryVectorStore
    from archon.infrastructure.github.github_reader import GitHubReader
    from archon.rag.indexer import RAGIndexer
    from archon.rag.retriever import RAGRetriever
    from archon.engine.supervisor import Supervisor
    from archon.engine.runner import Runner
    from archon.engine.hitl.checkpoints import HITLMode
    from archon.output.package_assembler import PackageAssembler

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    logger = logging.getLogger("archon.cli")

    repo_url = args.repo or ""
    if args.brief:
        repo_url = f"brief://{args.brief.replace(' ', '-')[:60]}"

    # Validate URL
    if args.repo and not args.repo.startswith("https://github.com/"):
        print("Error: Only github.com HTTPS URLs are supported.")
        return 1

    if not args.repo and not args.brief:
        print("Error: Provide --repo or --brief.")
        return 1

    job_id = str(uuid.uuid4())[:8]
    github = GitHubReader()
    repo_path: str | None = None

    try:
        if args.repo:
            print(f"Cloning {args.repo}...")
            repo_path = await github.clone(args.repo, job_id)

            print("Counting lines of code...")
            loc = await github.count_loc(repo_path)
            print(f"Repository: {loc:,} LOC")

            if loc > settings.max_loc and not args.force:
                print(
                    f"Error: Repo exceeds {settings.max_loc:,} LOC limit ({loc:,} measured).\n"
                    "Use --force to proceed."
                )
                return 1

        # Index codebase
        print("Indexing codebase into RAG...")
        store = InMemoryVectorStore(settings.embedding_model)
        indexer = RAGIndexer(github, store)
        chunk_count = await indexer.index(repo_path or ".")
        print(f"Indexed {chunk_count:,} chunks.")

        # Wire up all components
        retriever = RAGRetriever(store)
        llm = ClaudeAdapter()
        searchers = [TavilyAdapter(), ExaAdapter()]
        supervisor = Supervisor(llm, searchers, retriever)
        runner = Runner(supervisor)

        print(f"Running 6 specialist agents in parallel (mode: {args.mode})...")
        job, package = await runner.run(
            repo_url=repo_url, mode=args.mode, job_id=job_id,
            hitl_mode=HITLMode(args.hitl),
        )

        # Write primary output
        assembler = PackageAssembler()
        output_dir = args.output_dir
        output_path = assembler.assemble(package, output_dir, fmt=args.format)

        counts = package.severity_counts
        print(f"\nReview complete.")
        print(f"Findings: {len(package.findings)} "
              f"({counts.get('CRITICAL', 0)} critical, {counts.get('HIGH', 0)} high)")
        print(f"Output:   {output_path}")

        if package.partial:
            failed = [k for k, v in package.agent_statuses.items() if v == "FAILED"]
            print(f"Warning:  Partial review - failed agents: {', '.join(failed)}")

        # GitHub Issues
        if args.github_issues:
            if not args.repo:
                print("Warning: --github-issues requires --repo to derive the target repository.")
            else:
                from archon.output.github_issues import push_findings_to_github
                repo_slug = args.repo.replace("https://github.com/", "").rstrip("/")
                print("Pushing HIGH+ findings to GitHub Issues...")
                urls = await push_findings_to_github(package, repo_slug)
                print(f"Created {len(urls)} GitHub issue(s).")
                for u in urls:
                    print(f"  {u}")

        # GitHub ADRs
        if args.github_adrs:
            if not args.repo:
                print("Warning: --github-adrs requires --repo to derive the target repository.")
            else:
                from archon.output.github_adr import commit_adrs_to_github
                repo_slug = args.repo.replace("https://github.com/", "").rstrip("/")
                print("Committing ADRs to /docs/adr/ in repository...")
                committed = await commit_adrs_to_github(package, repo_slug)
                print(f"Committed {len(committed)} ADR(s): {', '.join(committed)}")

        # Slack digest
        if args.slack_webhook:
            from archon.output.slack_notifier import send_slack_digest
            print("Sending Slack digest...")
            ok = await send_slack_digest(package, args.slack_webhook)
            print("Slack digest sent." if ok else "Slack digest failed (check webhook URL).")

        return 0

    except KeyboardInterrupt:
        print("\nAborted by user.")
        return 130
    except Exception as exc:
        logger.exception("Fatal error: %s", exc)
        print(f"Error: {exc}")
        return 1
    finally:
        if repo_path:
            await github.cleanup(repo_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="archon",
        description="ARCHON - Autonomous AI Architecture Co-Pilot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python main.py --repo https://github.com/user/repo --mode review
  python main.py --repo https://github.com/user/repo --mode review --format html
  python main.py --repo https://github.com/user/repo --mode review --format pdf
  python main.py --repo https://github.com/user/repo --mode review --format json
  python main.py --repo https://github.com/user/repo --mode review --github-issues
  python main.py --repo https://github.com/user/repo --mode review --github-adrs
  python main.py --repo https://github.com/user/repo --mode review --slack-webhook https://hooks.slack.com/...
  python main.py --brief "SaaS video platform, 10k users" --mode design
""",
    )
    parser.add_argument("--idea", metavar="DESCRIPTION", help="Product idea for Idea Mode (no repo needed)")
    parser.add_argument("--idea", metavar="DESCRIPTION", help="Product idea for Idea Mode (no repo needed)")
    parser.add_argument("--repo", help="GitHub repo URL to analyse")
    parser.add_argument("--brief", help="Product brief for design mode (no repo needed)")
    parser.add_argument(
        "--mode", default="review", choices=ALL_MODES,
        help="Analysis mode (default: review)",
    )
    parser.add_argument(
        "--format", default="zip", choices=["zip", "html", "pdf", "json", "yaml"],
        help="Output format (default: zip)",
    )
    parser.add_argument("--output-dir", default="./output", help="Output directory")
    parser.add_argument("--force", action="store_true", help="Bypass 500k LOC limit")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--hitl", default="autopilot", choices=["autopilot", "balanced", "supervised"],
        help="Human-in-the-loop mode (default: autopilot)",
    )
    parser.add_argument(
        "--github-issues", action="store_true",
        help="Push HIGH+ findings as GitHub Issues (requires GITHUB_TOKEN)",
    )
    parser.add_argument(
        "--github-adrs", action="store_true",
        help="Commit ADR artifacts to /docs/adr/ in the repo (requires GITHUB_TOKEN)",
    )
    parser.add_argument(
        "--slack-webhook", metavar="URL",
        help="Send a Slack digest to this incoming webhook URL",
    )
    args = parser.parse_args()
    if args.idea:
        args.mode = "idea_mode"
        sys.exit(asyncio.run(run_idea_mode(args)))
    sys.exit(asyncio.run(run(args)))


if __name__ == "__main__":
    main()
