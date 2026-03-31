from __future__ import annotations
from pydantic import BaseModel, Field
from .finding import Finding, Citation
from .artifact import Artifact


class AgentOutput(BaseModel):
    domain: str
    findings: list[Finding] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    artifacts: list[Artifact] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    duration_seconds: float
    error: str | None = None
    partial: bool = False
