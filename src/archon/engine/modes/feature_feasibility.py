from __future__ import annotations

from pydantic import BaseModel


class FeatureInput(BaseModel):
    repo_url: str
    feature_brief: str
    deadline_weeks: int = 0


def build_feature_focus(input_data: FeatureInput) -> str:
    deadline = (
        f"Deadline: {input_data.deadline_weeks} weeks. "
        if input_data.deadline_weeks and input_data.deadline_weeks > 0
        else ""
    )
    return (
        f"Assess feasibility of: '{input_data.feature_brief}'. {deadline}"
        "Output: BUILD/BUY/DEFER verdict with rationale, complexity sizing "
        "(S=1-3 days, M=1-2 weeks, L=1-2 months, XL=3+ months), list of prerequisites "
        "that must exist first, risk register (top 3 risks with likelihood + impact), "
        "recommended approach."
    )
