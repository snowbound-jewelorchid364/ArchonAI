from __future__ import annotations
import asyncio
import logging

from src.archon.config.settings import settings
from src.archon.infrastructure.llm.claude_adapter import ClaudeAdapter
from src.archon.infrastructure.search.tavily_adapter import TavilyAdapter
from src.archon.infrastructure.search.exa_adapter import ExaAdapter
from src.archon.infrastructure.vector_store.in_memory_store import InMemoryVectorStore
from src.archon.infrastructure.github.github_reader import GitHubReader
from src.archon.rag.indexer import RAGIndexer
from src.archon.rag.retriever import RAGRetriever
from src.archon.engine.supervisor import Supervisor
from src.api.services.review_service import update_review_status, update_job_progress

logger = logging.getLogger(__name__)


async def process_review(
    review_id: str,
    job_id: str,
    repo_url: str,
    mode: str,
) -> None:
    github = GitHubReader()
    repo_path: str | None = None

    try:
        await update_job_progress(job_id, "RUNNING", {"agents": {}, "phase": "cloning"})
        await update_review_status(review_id, "RUNNING")

        # Clone
        repo_path = await github.clone(repo_url, job_id)
        loc = await github.count_loc(repo_path)
        logger.info("Review %s: cloned %s (%d LOC)", review_id, repo_url, loc)

        if loc > settings.max_loc:
            await update_review_status(
                review_id, "FAILED",
                error=f"Repo exceeds {settings.max_loc:,} LOC limit ({loc:,} measured)",
            )
            await update_job_progress(job_id, "FAILED")
            return

        # Index
        await update_job_progress(job_id, "RUNNING", {"agents": {}, "phase": "indexing"})
        store = InMemoryVectorStore(settings.embedding_model)
        indexer = RAGIndexer(github, store)
        chunk_count = await indexer.index(repo_path)
        logger.info("Review %s: indexed %d chunks", review_id, chunk_count)

        # Run agents
        await update_job_progress(job_id, "RUNNING", {"agents": {}, "phase": "agents"})
        retriever = RAGRetriever(store)
        llm = ClaudeAdapter()
        searchers = [TavilyAdapter(), ExaAdapter()]
        supervisor = Supervisor(llm, searchers, retriever)

        package = await supervisor.run(repo_url, mode, job_id=job_id)

        # Store results
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
        await update_job_progress(
            job_id,
            "COMPLETED",
            {"agents": package.agent_statuses, "phase": "done"},
        )
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

    logger.info("Review worker started — polling for jobs...")
    while True:
        # TODO: poll Redis queue for new jobs
        # job_data = await redis.dequeue("archon:reviews")
        # if job_data:
        #     await process_review(**job_data)
        await asyncio.sleep(5)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(worker_loop())
