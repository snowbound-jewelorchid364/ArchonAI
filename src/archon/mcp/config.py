from __future__ import annotations

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class MCPSettings(BaseSettings):
    archon_api_url: str = "http://localhost:8000"
    archon_api_key: str = ""

    model_config = ConfigDict(env_prefix="ARCHON_")
