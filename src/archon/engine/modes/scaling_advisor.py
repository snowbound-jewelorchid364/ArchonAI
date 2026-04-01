from __future__ import annotations

from pydantic import BaseModel


class ScalingInput(BaseModel):
    repo_url: str
    current_rps: int
    target_rps: int
    apm_content: str = ""


def build_scaling_focus(input_data: ScalingInput) -> str:
    return (
        f"Identify top 3 bottlenecks that will break under {input_data.target_rps} RPS "
        f"(current: {input_data.current_rps} RPS). For each: component, failure mode, fix "
        "(with IaC if applicable), cost at scale.\n\n"
        f"APM context:\n{input_data.apm_content or 'n/a'}"
    )
