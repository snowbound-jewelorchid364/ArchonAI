"""Finding feedback schemas."""
from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    finding_id: str
    helpful: bool
    comment: str = ""


class FeedbackResponse(BaseModel):
    id: str
    review_id: str
    finding_id: str
    helpful: bool
    comment: str
    created_at: str


class FeedbackSummary(BaseModel):
    review_id: str
    total: int = 0
    helpful_count: int = 0
    unhelpful_count: int = 0
    comments: list[str] = Field(default_factory=list)
