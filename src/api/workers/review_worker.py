from __future__ import annotations

import asyncio
import logging
import secrets

from src.api.services.review_service import update_job_progress, update_review_status
from src.archon.config.settings import settings
from src.archon.engine.modes.configs import build_mode_focus
from src.archon.engine.supervisor import Supervisor
from src.archon.infrastructure.github.github_reader import GitHubReader
from src.archon.infrastructure.llm.claude_adapter import ClaudeAdapter
from src.archon.infrastructure.search.exa_adapter import ExaAdapter
from src.archon.infrastructure.search.tavily_adapter import TavilyAdapter
from src.archon.infrastructure.vector_store.in_memory_store import InMemoryVectorStore
from src.archon.mcp.connector_registry import fetch_connector_context
from src.archon.memory.snapshot import build_memory_context
from src.archon.rag.indexer import RAGIndexer
from src.archon.rag.retriever import RAGRetriever
from src.db.connection import get_session
from src.db.models import ShareLinkRow

logger = logging.getLogger(__name__)


def _mode_focus_payload(mode: str, repo_url: str) -> dict:
    if mode == "pr_reviewer":
        return {
            "repo_url": repo_url,
            "pr_title": "Automated PR Review",
            "pr_diff": "Diff context not supplied by worker queue.",
            "pr_description": "",
        }
    if mode == "feature_feasibility":
        return {"repo_url": repo_url, "feature_brief": "Feature brief not supplied.", "deadline_weeks": 0}
    if mode == "cost_optimiser":
        return {"repo_url": repo_url, "cost_csv_content": "", "iac_content": ""}
    if mode == "vendor_evaluator":
        return {"use_case": "general architecture", "vendors": ["vendor-a", "vendor-b"], "evaluation_criteria": []}
    if mode == "scaling_advisor":
        return {"repo_url": repo_url, "current_rps": 0, "target_rps": 0, "apm_content": ""}
    if mode == "drift_monitor":
        return {"repo_url": repo_url, "previous_snapshot_id": "", "live_iac_content": ""}
    if mode == "onboarding_accelerator":
        return {"repo_url": repo_url, "focus_areas": [], "role": "engineer"}
    if mode == "sunset_planner":
        return {"repo_url": repo_url, "service_to_sunset": "unknown-service", "sunset_deadline": ""}
    return {"repo_url": repo_url}


async def process_review(
    review_id: str,
    job_id: str,
    repo_url: str,
    mode: str,
    user_id: str = "",
) -> None:
    github = GitHubReader()
    repo_path: str | None = None

    try:
        await update_job_progress(job_id, "RUNNING", {"agents": {}, "phase": "cloning"})
        await update_review_status(review_id, "RUNNING")

        repo_path = await github.clone(repo_url, job_id)
        loc = await github.count_loc(repo_path)
        logger.info("Review %s: cloned %s (%d LOC)", review_id, repo_url, loc)

        if loc > settings.max_loc:
            await update_review_status(
                review_id,
                "FAILED",
                error=f"Repo exceeds {settings.max_loc:,} LOC limit ({loc:,} measured)",
            )
            await update_job_progress(job_id, "FAILED")
            return

        await update_job_progress(job_id, "RUNNING", {"agents": {}, "phase": "indexing"})
        store = InMemoryVectorStore(settings.embedding_model)
        indexer = RAGIndexer(github, store)
        chunk_count = await indexer.index(repo_path)
        logger.info("Review %s: indexed %d chunks", review_id, chunk_count)

        await update_job_progress(job_id, "RUNNING", {"agents": {}, "phase": "agents"})
        retriever = RAGRetriever(store)
        llm = ClaudeAdapter()
        searchers = [TavilyAdapter(), ExaAdapter()]
        supervisor = Supervisor(llm, searchers, retriever)

        memory_context = ""
        if user_id:
            try:
                async with get_session() as session:
                    memory_context = await build_memory_context(session, user_id, repo_url)
            except Exception as exc:
                logger.warning("Review %s: memory context unavailable: %s", review_id, exc)

        connector_sections: list[str] = []
        for name in ["github", "aws"]:
            try:
                ctx = await fetch_connector_context(name, repo_url=repo_url)
                if ctx:
                    connector_sections.append(f"## Live {ctx.source.upper()} Data\n{ctx.summary}")
            except Exception as exc:
                logger.warning("Review %s: connector fetch failed (%s): %s", review_id, name, exc)
        connector_context = "\n\n".join(connector_sections)

        mode_focus = ""
        try:
            mode_focus = build_mode_focus(mode, _mode_focus_payload(mode, repo_url))
        except Exception as exc:
            logger.warning("Review %s: mode focus build failed for %s: %s", review_id, mode, exc)

        package = await supervisor.run(
            repo_url,
            mode,
            job_id=job_id,
            memory_context=memory_context,
            connector_context=connector_context,
            mode_focus_override=mode_focus,
        )

        share_token = secrets.token_urlsafe(32)
        package.share_token = share_token
        if user_id:
            async with get_session() as session:
                link = ShareLinkRow(
                    review_id=review_id,
                    user_id=user_id,
                    token=share_token,
                    is_active=True,
                )
                session.add(link)
                await session.commit()
            logger.info("Review %s: share token created", review_id)

        severity_counts = package.severity_counts
        await update_review_status(
            review_id,
            "PARTIAL" if package.partial else "COMPLETED",
            finding_count=len(package.findings),
            critical_count=severity_counts.get("CRITICAL", 0),
            high_count=severity_counts.get("HIGH", 0),
            confidence=sum(f.confidence for f in package.findings) / max(len(package.findings), 1),
            duration_seconds=package.duration_seconds,
            package_json=package.model_dump(mode="json"),
            agent_statuses=package.agent_statuses,
            executive_summary=package.executive_summary,
            partial=package.partial,
        )
        await update_job_progress(job_id, "COMPLETED", {"agents": package.agent_statuses, "phase": "done"})
        logger.info("Review %s completed: %d findings", review_id, len(package.findings))

    except Exception as exc:
        logger.exception("Review %s failed: %s", review_id, exc)
        await update_review_status(review_id, "FAILED", error=str(exc))
        await update_job_progress(job_id, "FAILED")
    finally:
        if repo_path:
            await github.cleanup(repo_path)


async def worker_loop() -> None:
    """Simple polling worker. Replace with Redis/BullMQ consumer in production."""
    from src.db.connection import init_db

    init_db(settings.database_url)

    logger.info("Review worker started - polling for jobs...")
    while True:
        await asyncio.sleep(5)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(worker_loop())

