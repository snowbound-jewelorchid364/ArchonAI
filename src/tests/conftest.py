from __future__ import annotations
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from archon.core.models.finding import Finding, Severity, Citation
from archon.core.models.agent_output import AgentOutput


@pytest.fixture
def sample_finding() -> Finding:
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
        citations=[
            Citation(
                url="https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password",
                title="OWASP: Use of hard-coded password",
                excerpt="Hard-coded credentials create a significant security risk",
                credibility_score=0.95,
            )
        ],
    )


@pytest.fixture
def sample_agent_output(sample_finding) -> AgentOutput:
    return AgentOutput(
        domain="security",
        findings=[sample_finding],
        confidence=0.85,
        duration_seconds=12.5,
    )


@pytest.fixture
def mock_llm() -> AsyncMock:
    llm = AsyncMock()
    llm.complete.return_value = "Mock LLM response"
    return llm


@pytest.fixture
def mock_searcher() -> AsyncMock:
    searcher = AsyncMock()
    searcher.search.return_value = []
    return searcher


@pytest.fixture
def small_repo(tmp_path: Path) -> Path:
    """Create a minimal fake repo for testing."""
    (tmp_path / "main.py").write_text("import os\nSECRET = 'hardcoded'\n")
    (tmp_path / "requirements.txt").write_text("flask==2.0.0\n")
    (tmp_path / "Dockerfile").write_text("FROM python:3.11\n")
    return tmp_path
