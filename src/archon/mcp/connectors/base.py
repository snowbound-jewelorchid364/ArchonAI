from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone

from pydantic import BaseModel


class ConnectorContext(BaseModel):
    """Context data returned by a connector, injected into agent system prompts."""

    source: str
    summary: str
    raw_data: dict
    fetched_at: str


class MCPConnector(ABC):
    name: str

    @abstractmethod
    async def fetch(self, **kwargs) -> ConnectorContext:
        """Fetch live data and return as ConnectorContext."""



def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
