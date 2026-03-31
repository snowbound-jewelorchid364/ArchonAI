from __future__ import annotations
from pydantic import BaseModel


class PortalSessionResponse(BaseModel):
    url: str


class WebhookResponse(BaseModel):
    received: bool


class PlanInfo(BaseModel):
    plan: str
    runs_used: int
    runs_limit: int
    stripe_customer_id: str | None = None
