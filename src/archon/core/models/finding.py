from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class Citation(BaseModel):
    url: HttpUrl
    title: str
    excerpt: str = Field(max_length=300)
    published_date: str | None = None
    credibility_score: float = Field(ge=0.0, le=1.0, default=0.5)


class Finding(BaseModel):
    id: str
    title: str
    description: str
    severity: Severity
    domain: str
    file_path: str | None = None
    line_number: int | None = None
    recommendation: str
    citations: list[Citation] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    from_codebase: bool = True
