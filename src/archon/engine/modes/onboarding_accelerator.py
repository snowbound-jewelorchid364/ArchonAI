from __future__ import annotations

from pydantic import BaseModel, Field


class OnboardingInput(BaseModel):
    repo_url: str
    focus_areas: list[str] = Field(default_factory=list)
    role: str = "engineer"


def build_onboarding_focus(input_data: OnboardingInput) -> str:
    focus = ", ".join(input_data.focus_areas) if input_data.focus_areas else "all domains"
    return (
        f"Generate an onboarding guide for a new {input_data.role}. Include: annotated system map "
        "(components + how they connect), first-week learning path (day-by-day), first-month "
        "milestones, known landmines (gotchas, tech debt to avoid, tribal knowledge), key people/teams "
        f"per domain. Focus areas: {focus}."
    )
