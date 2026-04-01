from __future__ import annotations

from pydantic import BaseModel, Field


DEFAULT_VENDOR_CRITERIA = [
    "performance",
    "cost",
    "lock-in risk",
    "support",
    "compliance",
    "scalability",
]


class VendorInput(BaseModel):
    use_case: str
    vendors: list[str]
    evaluation_criteria: list[str] = Field(default_factory=list)

    @property
    def criteria(self) -> list[str]:
        return self.evaluation_criteria or DEFAULT_VENDOR_CRITERIA


def choose_vendor_lead_agent(use_case: str) -> str:
    text = use_case.lower()
    data_words = ["data", "warehouse", "lake", "analytics", "etl", "database"]
    if any(word in text for word in data_words):
        return "data-architect"
    return "cloud-architect"


def build_vendor_focus(input_data: VendorInput) -> str:
    vendors = ", ".join(input_data.vendors)
    criteria = ", ".join(input_data.criteria)
    return (
        f"Evaluate these vendors for {input_data.use_case}: {vendors}. "
        f"Score each 1-5 on: {criteria}. Calculate 3-year TCO for each. "
        "Identify lock-in risks. Recommend one with rationale. "
        "Use only cited web sources - no hallucinated benchmarks."
    )
