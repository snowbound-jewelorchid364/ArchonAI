from __future__ import annotations
from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field
from .finding import Finding, Citation, Severity
from .artifact import Artifact


class ReviewPackage(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    run_id: str
    repo_url: str
    mode: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    duration_seconds: float
    executive_summary: str
    findings: list[Finding] = Field(default_factory=list)
    artifacts: list[Artifact] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    agent_statuses: dict[str, str] = Field(default_factory=dict)
    partial: bool = False
    model_version: str = ""
    prompt_version: str = ""
    share_token: str | None = None

    def all_findings(self) -> list[Finding]:
        return self.findings

    @property
    def critical_findings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == Severity.CRITICAL]

    @property
    def high_findings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == Severity.HIGH]

    @property
    def severity_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for f in self.findings:
            counts[f.severity.value] = counts.get(f.severity.value, 0) + 1
        return counts
