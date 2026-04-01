from __future__ import annotations

from pydantic import BaseModel


class CostOptimiserInput(BaseModel):
    repo_url: str
    cost_csv_content: str = ""
    iac_content: str = ""


def build_cost_focus(input_data: CostOptimiserInput) -> str:
    return (
        f"Repo: {input_data.repo_url}. Identify top 5 cost reduction opportunities. For each: "
        "current monthly cost, projected saving, implementation effort (hours), IaC change required. "
        "Rank by saving/effort ratio.\n\n"
        f"Cost CSV context:\n{input_data.cost_csv_content or 'n/a'}\n\n"
        f"IaC context:\n{input_data.iac_content or 'n/a'}"
    )
