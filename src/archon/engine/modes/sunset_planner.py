from __future__ import annotations

from pydantic import BaseModel


class SunsetInput(BaseModel):
    repo_url: str
    service_to_sunset: str
    sunset_deadline: str = ""


def build_sunset_focus(input_data: SunsetInput) -> str:
    return (
        f"Plan decommission of service: '{input_data.service_to_sunset}'. Produce: full dependency map "
        "(what calls it, what it calls), ordered shutdown sequence (steps with rollback at each), "
        "data disposition plan (what to archive vs delete), GDPR deletion checklist, comms plan "
        f"(who to notify + when). Deadline: {input_data.sunset_deadline or 'not specified'}."
    )
