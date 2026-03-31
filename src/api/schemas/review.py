from __future__ import annotations
from pydantic import BaseModel, HttpUrl


class ReviewRequest(BaseModel):
    repo_url: HttpUrl
    mode: str = "review"
    brief: str | None = None


class ReviewResponse(BaseModel):
    review_id: str
    job_id: str
    status: str
    message: str


class ReviewListItem(BaseModel):
    id: str
    repo_url: str
    mode: str
    status: str
    finding_count: int
    critical_count: int
    high_count: int
    created_at: str
    completed_at: str | None = None


class ReviewDetail(BaseModel):
    id: str
    repo_url: str
    mode: str
    status: str
    finding_count: int
    critical_count: int
    high_count: int
    confidence: float
    duration_seconds: float
    cost_usd: float
    executive_summary: str | None = None
    agent_statuses: dict | None = None
    partial: bool = False
    error: str | None = None
    created_at: str
    completed_at: str | None = None
