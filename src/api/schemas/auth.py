from __future__ import annotations
from pydantic import BaseModel


class CurrentUser(BaseModel):
    user_id: str
    email: str
    plan: str = "starter"
