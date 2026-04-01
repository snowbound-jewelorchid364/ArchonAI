from __future__ import annotations
import json
from collections.abc import AsyncGenerator
from pydantic import BaseModel


INTAKE_QUESTIONS: list[tuple[str, str]] = [
    ("users",      "Who will use this? (e.g. consumers, businesses, internal team)"),
    ("core_value", "What's the one thing it does that users can't do without it?"),
    ("scale",      "How many people do you expect in year 1 and year 2?"),
    ("budget",     "What's your monthly cloud/infrastructure budget? (rough estimate is fine)"),
    ("timeline",   "When do you need the first version live?"),
    ("compliance", "Any legal or industry requirements? (e.g. HIPAA, GDPR, PCI, or none)"),
]

_REQUIRED_KEYS = {key for key, _ in INTAKE_QUESTIONS}


class ProductBrief(BaseModel):
    idea: str
    users: str
    core_value: str
    scale_y1: str
    scale_y2: str
    budget_monthly: str
    timeline: str
    compliance: str
    raw_answers: dict[str, str]


async def run_intake(idea: str, answers: dict[str, str]) -> ProductBrief:
    """Validate answers and assemble a ProductBrief."""
    missing = _REQUIRED_KEYS - set(answers.keys())
    if missing:
        raise ValueError(f"Missing answers for: {sorted(missing)}")

    scale_raw = answers.get("scale", "")
    parts = [p.strip() for p in scale_raw.replace("and", ",").split(",") if p.strip()]
    scale_y1 = parts[0] if len(parts) >= 1 else scale_raw
    scale_y2 = parts[1] if len(parts) >= 2 else scale_raw

    return ProductBrief(
        idea=idea,
        users=answers["users"],
        core_value=answers["core_value"],
        scale_y1=scale_y1,
        scale_y2=scale_y2,
        budget_monthly=answers["budget"],
        timeline=answers["timeline"],
        compliance=answers["compliance"],
        raw_answers=answers,
    )


async def stream_next_question(
    key: str,
    question: str,
    index: int,
    total: int,
) -> AsyncGenerator[str, None]:
    """Yield a single SSE event for a question."""
    payload = json.dumps({"type": "question", "key": key, "data": question, "index": index, "total": total})
    yield f"data: {payload}\n\n"


async def stream_all_questions() -> AsyncGenerator[str, None]:
    """Yield SSE events for all intake questions in order."""
    total = len(INTAKE_QUESTIONS)
    for i, (key, question) in enumerate(INTAKE_QUESTIONS, start=1):
        payload = json.dumps({"type": "question", "key": key, "data": question, "index": i, "total": total})
        yield f"data: {payload}\n\n"
    ready = json.dumps({"type": "ready", "data": "Great! I have everything I need. Starting your architecture..."})
    yield f"data: {ready}\n\n"
