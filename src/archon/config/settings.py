from __future__ import annotations
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM
    anthropic_api_key: str = ""
    agent_model: str = "claude-opus-4-5"
    fast_model: str = "claude-haiku-4-5"

    # Thinking budget per mode category
    thinking_budget_default: str = "medium"
    thinking_budget_premium: str = "high"
    thinking_budget_fast: str = "low"

    # Web research
    tavily_api_key: str = ""
    exa_api_key: str = ""

    # GitHub
    github_token: str = ""

    # Database (Phase 2)
    database_url: str = "postgresql+asyncpg://localhost/archon"

    # Redis (Phase 2)
    redis_url: str = "redis://localhost:6379"

    # Clerk (Phase 2)
    clerk_secret_key: str = ""

    # Stripe (Phase 2)
    stripe_secret_key: str = ""

    # RAG
    embedding_model: str = "all-MiniLM-L6-v2"
    rag_chunk_size: int = 500
    rag_chunk_overlap: int = 50
    rag_top_k: int = 8

    # Limits
    max_loc: int = 500_000
    agent_timeout_seconds: int = 1200

    def thinking_budget_for_mode(self, mode: str) -> str:
        premium_modes = {"due_diligence", "compliance_auditor"}
        fast_modes = {"drift_monitor"}
        if mode in premium_modes:
            return self.thinking_budget_premium
        if mode in fast_modes:
            return self.thinking_budget_fast
        return self.thinking_budget_default

    def require_keys(self, *keys: str) -> None:
        missing = [k for k in keys if not getattr(self, k, "")]
        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")


@lru_cache
def get_settings() -> Settings:
    return Settings()


# Module-level singleton for convenience imports
settings = get_settings()
