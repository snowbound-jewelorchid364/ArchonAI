from __future__ import annotations

from pydantic import BaseModel


class DriftInput(BaseModel):
    repo_url: str
    previous_snapshot_id: str = ""
    live_iac_content: str = ""


def build_drift_focus(input_data: DriftInput) -> str:
    return (
        "Compare current codebase state against previous architecture snapshot. Identify: "
        "new components not in snapshot, removed components, changed interfaces, new security "
        "exposures, cost changes. Output as drift report.\n\n"
        f"Repo: {input_data.repo_url}\n"
        f"Previous snapshot: {input_data.previous_snapshot_id or 'none'}\n"
        f"Live IaC:\n{input_data.live_iac_content or 'n/a'}"
    )
