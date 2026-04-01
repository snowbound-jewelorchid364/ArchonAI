
import asyncio
import json
from typing import Any
from urllib.parse import quote

import httpx

from .config import MCPSettings


try:
    from mcp.server.fastmcp import FastMCP  # type: ignore
except Exception:
    FastMCP = None  # type: ignore


class _FallbackMCP:
    def __init__(self, name: str) -> None:
        self.name = name
        self.tools: dict[str, Any] = {}

    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator

    def run(self) -> None:
        return None


mcp = FastMCP("archon") if FastMCP is not None else _FallbackMCP("archon")
REGISTERED_TOOLS: list[str] = []


def _register_tool(func):
    REGISTERED_TOOLS.append(func.__name__)
    return mcp.tool()(func)


async def _request_json(method: str, path: str, *, json_body: dict | None = None) -> dict:
    settings = MCPSettings()
    base = settings.archon_api_url.rstrip("/")
    headers = {
        "Authorization": f"Bearer {settings.archon_api_key}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.request(method, f"{base}{path}", headers=headers, json=json_body)
        resp.raise_for_status()
        if not resp.text:
            return {}
        return resp.json()


@_register_tool
async def review_repo(repo_url: str, mode: str = "review"):
    """Trigger an ARCHON architecture review. Returns job_id."""
    data = await _request_json("POST", "/api/v1/reviews", json_body={"repo_url": repo_url, "mode": mode})
    return {
        "review_id": data.get("review_id"),
        "job_id": data.get("job_id"),
        "status": data.get("status", "QUEUED"),
    }


@_register_tool
async def get_findings(review_id: str, severity: str = "all"):
    """Get findings from a completed review. severity: critical|high|medium|low|all"""
    data = await _request_json("GET", f"/api/v1/reviews/{review_id}")
    findings = data.get("findings")
    if findings is None:
        findings = (data.get("package_json") or {}).get("findings", [])

    sev = severity.lower().strip()
    if sev in {"critical", "high", "medium", "low", "info"}:
        wanted = sev.upper()
        return [f for f in findings if str(f.get("severity", "")).upper() == wanted]
    return findings


@_register_tool
async def ask_architecture(review_id: str, question: str):
    """Ask a question grounded in a review's findings. Returns answer string."""
    settings = MCPSettings()
    base = settings.archon_api_url.rstrip("/")
    headers = {
        "Authorization": f"Bearer {settings.archon_api_key}",
        "Content-Type": "application/json",
    }

    chunks: list[str] = []
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream(
            "POST",
            f"{base}/api/v1/reviews/{review_id}/chat",
            headers=headers,
            json={"message": question},
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue
                payload = line[5:].strip()
                try:
                    event = json.loads(payload)
                except Exception:
                    continue
                if event.get("type") == "text":
                    chunks.append(str(event.get("data", "")))
                elif event.get("type") == "error":
                    return str(event.get("data", "Chat error"))
    return "".join(chunks).strip()


@_register_tool
async def get_health_score(repo_url: str):
    """Get the latest health score for a repo. Returns overall + per-domain scores."""
    repo_path = quote(repo_url, safe="")
    data = await _request_json("GET", f"/api/v1/health-score/{repo_path}/latest")
    return {
        "repo_url": data.get("repo_url", repo_url),
        "overall": data.get("overall", 0),
        "domains": data.get("domains", {}),
        "created_at": data.get("created_at"),
    }


@_register_tool
async def get_adrs(review_id: str):
    """List all ADR artifacts from a review. Returns title + content per ADR."""
    data = await _request_json("GET", f"/api/v1/reviews/{review_id}")
    artifacts = data.get("artifacts")
    if artifacts is None:
        artifacts = (data.get("package_json") or {}).get("artifacts", [])
    adrs = []
    for a in artifacts:
        a_type = str(a.get("artifact_type", "")).upper()
        if a_type == "ADR":
            adrs.append({"title": a.get("title", ""), "content": a.get("content", "")})
    return adrs



