from __future__ import annotations
import sys
from pathlib import Path
import pytest
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, str(Path(__file__).parents[1]))

from archon.core.models.finding import Finding, Severity, Citation
from archon.core.models.agent_output import AgentOutput
from archon.core.models.artifact import Artifact, ArtifactType
from archon.core.models.review_package import ReviewPackage
from archon.core.ports.vector_store_port import DocumentChunk
from archon.core.ports.repo_port import RepoFile


@pytest.fixture
def sample_citation():
    return Citation(
        url="https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password",
        title="OWASP: Use of hard-coded password",
        excerpt="Hard-coded credentials create a significant security risk",
        credibility_score=0.95,
    )


@pytest.fixture
def sample_finding(sample_citation):
    return Finding(
        id="test-001",
        title="Hardcoded secret in auth module",
        description="JWT secret is hardcoded in services/auth/jwt.py:47",
        severity=Severity.CRITICAL,
        domain="security",
        file_path="services/auth/jwt.py",
        line_number=47,
        recommendation="Load JWT secret from environment variable or secrets manager",
        confidence=0.95,
        from_codebase=True,
        citations=[sample_citation],
    )


@pytest.fixture
def sample_findings():
    return [
        Finding(id="SA-001", title="Missing error handling", description="No try/catch in api.py", severity=Severity.HIGH, domain="software-architect", recommendation="Add error handling", confidence=0.85, from_codebase=True),
        Finding(id="SEC-001", title="Hardcoded API key", description="API key in config.py:12", severity=Severity.CRITICAL, domain="security-architect", file_path="config.py", line_number=12, recommendation="Use env vars", confidence=0.95, from_codebase=True, citations=[Citation(url="https://owasp.org/example", title="OWASP", excerpt="Dont hardcode", credibility_score=0.9)]),
        Finding(id="CA-001", title="No autoscaling", description="EC2 without ASG", severity=Severity.MEDIUM, domain="cloud-architect", recommendation="Add ASG", confidence=0.75, from_codebase=False),
        Finding(id="DA-001", title="No backup strategy", description="RDS without backup", severity=Severity.HIGH, domain="data-architect", recommendation="Enable automated backups", confidence=0.8, from_codebase=True),
        Finding(id="IA-001", title="Sync HTTP calls", description="Blocking calls in handler", severity=Severity.MEDIUM, domain="integration-architect", file_path="handler.py", recommendation="Use async", confidence=0.7, from_codebase=True),
        Finding(id="AI-001", title="No model versioning", description="ML models not versioned", severity=Severity.LOW, domain="ai-architect", recommendation="Add MLflow", confidence=0.6, from_codebase=False),
    ]


@pytest.fixture
def sample_agent_output(sample_finding):
    return AgentOutput(domain="security", findings=[sample_finding], confidence=0.85, duration_seconds=12.5)


@pytest.fixture
def sample_artifact():
    return Artifact(id="adr-001", artifact_type=ArtifactType.ADR, title="Use PostgreSQL", content="# ADR-001", filename="adr-001.md")


@pytest.fixture
def sample_package(sample_findings, sample_artifact):
    return ReviewPackage(
        run_id="test-run-001", repo_url="https://github.com/test/repo", mode="review",
        duration_seconds=120.5, executive_summary="Architecture is generally sound.",
        findings=sample_findings, artifacts=[sample_artifact],
        citations=[Citation(url="https://owasp.org/example", title="OWASP", excerpt="Security ref", credibility_score=0.9)],
        agent_statuses={"software-architect": "COMPLETED", "cloud-architect": "COMPLETED", "security-architect": "COMPLETED", "data-architect": "COMPLETED", "integration-architect": "COMPLETED", "ai-architect": "COMPLETED"},
    )


@pytest.fixture
def partial_package(sample_findings):
    return ReviewPackage(
        run_id="test-partial-001", repo_url="https://github.com/test/repo", mode="review",
        duration_seconds=45.0, executive_summary="Partial review - cloud agent failed.",
        findings=sample_findings[:3], partial=True,
        agent_statuses={"software-architect": "COMPLETED", "cloud-architect": "FAILED", "security-architect": "COMPLETED", "data-architect": "PARTIAL", "integration-architect": "COMPLETED", "ai-architect": "COMPLETED"},
    )


@pytest.fixture
def mock_llm():
    llm = MagicMock()
    llm.complete = AsyncMock(return_value='{"findings": [], "artifacts": [], "confidence": 0.7}')
    return llm


@pytest.fixture
def mock_searcher():
    s = MagicMock()
    s.search = AsyncMock(return_value=[])
    return s


@pytest.fixture
def mock_repo_reader():
    r = MagicMock()
    r.get_files = AsyncMock(return_value=[
        RepoFile(path="main.py", content="import os\nSECRET = 'hardcoded'\nprint(SECRET)", size_bytes=50),
        RepoFile(path="api.py", content="from flask import Flask\napp = Flask(__name__)\n@app.route('/')\ndef index():\n    return 'ok'", size_bytes=90),
        RepoFile(path="requirements.txt", content="flask==2.0.0\nrequests==2.28.0", size_bytes=30),
    ])
    r.count_loc = AsyncMock(return_value=150)
    r.clone = AsyncMock(return_value="/tmp/archon-test")
    r.cleanup = AsyncMock(return_value=None)
    return r


@pytest.fixture
def sample_chunks():
    return [
        DocumentChunk(id="c1", content="import os\nSECRET = 'hardcoded'", file_path="main.py", metadata={"start_line": 1, "end_line": 2}),
        DocumentChunk(id="c2", content="from flask import Flask\napp = Flask(__name__)", file_path="api.py", metadata={"start_line": 1, "end_line": 2}),
        DocumentChunk(id="c3", content="flask==2.0.0\nrequests==2.28.0", file_path="requirements.txt", metadata={"start_line": 1, "end_line": 2}),
    ]
