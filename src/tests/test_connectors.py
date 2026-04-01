from __future__ import annotations

import os
import sys
from types import ModuleType
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from archon.mcp.connector_registry import fetch_connector_context
from archon.mcp.connectors.aws_connector import AWSConnector
from archon.mcp.connectors.base import ConnectorContext
from archon.mcp.connectors.github_connector import GitHubConnector
from archon.mcp.connectors.slack_connector import SlackConnector


class _Resp:
    def __init__(self, payload: list[dict] | dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError("http error")

    def json(self):
        return self._payload


class _GitHubClient:
    def __init__(self, *args, **kwargs) -> None:
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url: str, headers=None, params=None):
        if url.endswith("/pulls"):
            return _Resp([
                {"number": 1, "title": "PR1", "user": {"login": "u1"}, "merged_at": None}
            ])
        if "/pulls/1/files" in url:
            return _Resp([{"filename": "a.py"}, {"filename": "b.py"}])
        if url.endswith("/commits"):
            return _Resp([
                {"commit": {"author": {"date": "2026-03-01T00:00:00Z"}}}
            ])
        if url.endswith("/contributors"):
            return _Resp([
                {"login": "dev1", "contributions": 42}
            ])
        if url.endswith("/issues"):
            return _Resp([
                {"number": 11, "title": "Arch debt", "labels": [{"name": "architecture"}]}
            ])
        return _Resp([], status_code=404)


def test_github_connector_parses_repo_url() -> None:
    owner, repo = GitHubConnector.parse_repo_url("https://github.com/owner/repo")
    assert owner == "owner"
    assert repo == "repo"


@pytest.mark.asyncio
async def test_github_connector_returns_context(monkeypatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    with patch("archon.mcp.connectors.github_connector.httpx.AsyncClient", _GitHubClient):
        ctx = await GitHubConnector().fetch(repo_url="https://github.com/owner/repo")
    assert isinstance(ctx, ConnectorContext)
    assert ctx.source == "github"
    assert "prs" in ctx.raw_data


@pytest.mark.asyncio
async def test_aws_connector_handles_missing_credentials(monkeypatch) -> None:
    monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)
    monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)
    ctx = await AWSConnector().fetch()
    assert ctx.source == "aws"
    assert ctx.raw_data["stacks"] == []
    assert ctx.raw_data["costs"] == []


@pytest.mark.asyncio
async def test_aws_connector_cost_explorer(monkeypatch) -> None:
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "k")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "s")

    class _Session:
        def __init__(self, *args, **kwargs):
            pass

        def client(self, service: str, region_name: str | None = None):
            if service == "ce":
                c = MagicMock()
                c.get_cost_and_usage.return_value = {
                    "ResultsByTime": [
                        {
                            "Groups": [
                                {
                                    "Keys": ["AmazonEC2"],
                                    "Metrics": {"UnblendedCost": {"Amount": "123.45"}},
                                }
                            ]
                        }
                    ]
                }
                return c
            if service == "cloudformation":
                c = MagicMock(); c.list_stacks.return_value = {"StackSummaries": []}; return c
            if service == "cloudwatch":
                c = MagicMock(); c.describe_alarms.return_value = {"MetricAlarms": []}; return c
            if service == "securityhub":
                c = MagicMock(); c.get_findings.return_value = {"Findings": []}; return c
            raise ValueError(service)

    fake_boto3 = ModuleType("boto3")
    fake_boto3.Session = _Session
    monkeypatch.setitem(sys.modules, "boto3", fake_boto3)

    ctx = await AWSConnector().fetch(aws_region="us-east-1")
    assert ctx.raw_data["costs"]
    assert ctx.raw_data["costs"][0]["service"] == "AmazonEC2"


@pytest.mark.asyncio
async def test_slack_post_hitl_checkpoint(monkeypatch) -> None:
    monkeypatch.setenv("SLACK_BOT_TOKEN", "x")
    posted: dict = {}

    class _WebClient:
        def __init__(self, token: str) -> None:
            self.token = token

        def chat_postMessage(self, **kwargs):
            posted.update(kwargs)
            return MagicMock(data={"ok": True})

    fake_slack = ModuleType("slack_sdk")
    fake_slack.WebClient = _WebClient
    monkeypatch.setitem(sys.modules, "slack_sdk", fake_slack)

    conn = SlackConnector()
    await conn.post_hitl_checkpoint("#arch", "rev1", "findings_ready", "Please approve")
    assert posted["channel"] == "#arch"
    assert posted["blocks"][1]["type"] == "actions"


@pytest.mark.asyncio
async def test_slack_post_health_digest(monkeypatch) -> None:
    monkeypatch.setenv("SLACK_BOT_TOKEN", "x")
    posted: dict = {}

    class _WebClient:
        def __init__(self, token: str) -> None:
            self.token = token

        def chat_postMessage(self, **kwargs):
            posted.update(kwargs)
            return MagicMock(data={"ok": True})

    fake_slack = ModuleType("slack_sdk")
    fake_slack.WebClient = _WebClient
    monkeypatch.setitem(sys.modules, "slack_sdk", fake_slack)

    conn = SlackConnector()
    await conn.post_health_digest("#arch", "https://github.com/o/r", 85, {"security": 80})
    assert posted["channel"] == "#arch"
    assert "Weekly Health Digest" in posted["blocks"][0]["text"]["text"]


@pytest.mark.asyncio
async def test_connector_registry_returns_none_for_unknown() -> None:
    out = await fetch_connector_context("unknown")
    assert out is None


@pytest.mark.asyncio
async def test_connector_registry_fetch_github() -> None:
    fake_ctx = ConnectorContext(source="github", summary="ok", raw_data={}, fetched_at="2026-01-01T00:00:00Z")
    with patch("archon.mcp.connectors.github_connector.GitHubConnector.fetch", new_callable=AsyncMock) as f:
        f.return_value = fake_ctx
        out = await fetch_connector_context("github", repo_url="https://github.com/o/r")
    assert out is not None
    assert out.source == "github"
