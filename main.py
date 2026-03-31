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
]


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
    from archon.output.formatter import MarkdownFormatter

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

        # Write output
        formatter = MarkdownFormatter()
        output_dir = args.output_dir
        output_path = formatter.write(package, output_dir)

        counts = package.severity_counts
        print(f"\nReview complete.")
        print(f"Findings: {len(package.findings)} "
              f"({counts.get('CRITICAL', 0)} critical, {counts.get('HIGH', 0)} high)")
        print(f"Output:   {output_path}")

        if package.partial:
            failed = [k for k, v in package.agent_statuses.items() if v == "FAILED"]
            print(f"Warning:  Partial review - failed agents: {', '.join(failed)}")

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
  python main.py --repo https://github.com/user/repo --mode compliance_auditor
  python main.py --brief "SaaS video platform, 10k users" --mode design
""",
    )
    parser.add_argument("--repo", help="GitHub repo URL to analyse")
    parser.add_argument("--brief", help="Product brief for design mode (no repo needed)")
    parser.add_argument(
        "--mode", default="review", choices=ALL_MODES,
        help="Analysis mode (default: review)",
    )
    parser.add_argument("--output-dir", default="./output", help="Output directory")
    parser.add_argument("--force", action="store_true", help="Bypass 500k LOC limit")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--hitl", default="autopilot", choices=["autopilot", "balanced", "supervised"],
        help="Human-in-the-loop mode (default: autopilot)",
    )
    args = parser.parse_args()
    sys.exit(asyncio.run(run(args)))


if __name__ == "__main__":
    main()
