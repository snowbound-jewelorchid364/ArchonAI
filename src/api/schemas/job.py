from __future__ import annotations
from pydantic import BaseModel


class JobStatus(BaseModel):
    job_id: str
    review_id: str
    status: str
    progress: dict | None = None


class AgentProgress(BaseModel):
    agent: str
    status: str
    finding_count: int = 0
    duration_seconds: float = 0.0
