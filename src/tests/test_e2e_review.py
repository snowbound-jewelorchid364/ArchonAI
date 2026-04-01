from __future__ import annotations

import io
import shutil
import tempfile
import uuid
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from archon.core.models import AgentOutput, Finding, ReviewPackage, Severity
from archon.core.ports.repo_port import RepoFile
from archon.core.ports.vector_store_port import DocumentChunk
from archon.engine.supervisor import Supervisor
from archon.output.zip_builder import ZipPackageBuilder
from archon.rag.indexer import RAGIndexer


def _finding(domain: str) -> Finding:
    return Finding(
        id=str(uuid.uuid4()),
        title=f"{domain} finding",
        description="desc",
        severity=Severity.HIGH,
        domain=domain,
        recommendation="fix",
        confidence=0.9,
    )


def _output(domain: str) -> AgentOutput:
    return AgentOutput(
        domain=domain,
        findings=[_finding(domain)],
        confidence=0.9,
        duration_seconds=0.1,
    )


class RepoReader:
    def __init__(self, root: Path) -> None:
        self.root = root

    async def get_files(self, repo_path: str) -> list[RepoFile]:
        files: list[RepoFile] = []
        for p in self.root.rglob("*.py"):
            text = p.read_text(encoding="utf-8")
            files.append(RepoFile(path=p.relative_to(self.root).as_posix(), content=text, size_bytes=len(text)))
        return files


@pytest.mark.asyncio
async def test_e2e_review_pipeline_clone_index_agents_merge_zip() -> None:
    fixture_root = Path(__file__).parent / "fixtures" / "sample_repos" / "python_fastapi"
    with tempfile.TemporaryDirectory() as td:
        cloned = Path(td) / "cloned_repo"
        shutil.copytree(fixture_root, cloned)

        captured_chunks: list[DocumentChunk] = []

        class Store:
            async def index(self, chunks: list[DocumentChunk]) -> None:
                captured_chunks.extend(chunks)

            async def query(self, query: str, top_k: int = 5) -> list[DocumentChunk]:
                return captured_chunks[:top_k]

            async def clear(self) -> None:
                captured_chunks.clear()

        indexer = RAGIndexer(RepoReader(cloned), Store())
        chunk_count = await indexer.index(str(cloned))
        assert chunk_count > 0

        llm = AsyncMock()
        llm.complete = AsyncMock(return_value="Executive summary")
        supervisor = Supervisor(llm, [MagicMock()], MagicMock())

        domains = [
            "software-architect",
            "cloud-architect",
            "security-architect",
            "data-architect",
            "integration-architect",
            "ai-architect",
        ]
        agents = []
        for d in domains:
            a = MagicMock()
            a.domain = d
            a.run = AsyncMock(return_value=_output(d))
            agents.append(a)

        with patch.object(supervisor, "_build_agents", return_value=agents):
            package = await supervisor.run("https://github.com/test/repo", "review")

        data = ZipPackageBuilder().build(package)
        assert data

        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            names = zf.namelist()
            assert any(n.endswith("README.md") for n in names)
            assert any("/findings/" in n for n in names)
            assert any(n.endswith("risk-register.md") for n in names)
            assert any(n.endswith("citations.md") for n in names)
