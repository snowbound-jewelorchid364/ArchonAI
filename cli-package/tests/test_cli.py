"""Tests for ARCHON CLI."""
from __future__ import annotations

import io
import sys
from pathlib import Path
from unittest.mock import MagicMock

import httpx
from click.testing import CliRunner
from rich.console import Console

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from archon_cli.client import ArchonAuthError, ArchonConnectionError
from archon_cli.main import cli
import archon_cli.sse_display as sse_display


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "ARCHON" in result.output


def test_modes_command() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["modes"])
    assert result.exit_code == 0
    assert "review" in result.output
    assert "design" in result.output


def test_version() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_login_success(monkeypatch) -> None:
    runner = CliRunner()
    saved: dict[str, str] = {}

    class FakeClient:
        def __init__(self, api_url: str, api_key: str):
            self.api_url = api_url
            self.api_key = api_key

        def validate_token(self) -> dict[str, str]:
            return {"user_id": "u_1", "email": "dev@archon.ai", "plan": "pro"}

    def fake_save_config(api_url: str, api_key: str) -> None:
        saved["api_url"] = api_url
        saved["api_key"] = api_key

    monkeypatch.setattr("archon_cli.main.ArchonAPIClient", FakeClient)
    monkeypatch.setattr("archon_cli.main.save_config", fake_save_config)

    result = runner.invoke(cli, ["login", "--api-url", "https://api.archon.dev", "--api-key", "token-123"])
    assert result.exit_code == 0
    assert "Logged in." in result.output
    assert saved == {"api_url": "https://api.archon.dev", "api_key": "token-123"}


def test_login_failure(monkeypatch) -> None:
    runner = CliRunner()

    class FakeClient:
        def __init__(self, api_url: str, api_key: str):
            self.api_url = api_url
            self.api_key = api_key

        def validate_token(self) -> dict[str, str]:
            raise ArchonAuthError("bad token")

    monkeypatch.setattr("archon_cli.main.ArchonAPIClient", FakeClient)

    result = runner.invoke(cli, ["login", "--api-url", "https://api.archon.dev", "--api-key", "bad"])
    assert result.exit_code != 0
    assert "Login failed:" in result.output


def test_logout(monkeypatch) -> None:
    runner = CliRunner()
    called = {"value": False}

    def fake_clear_config() -> None:
        called["value"] = True

    monkeypatch.setattr("archon_cli.main.clear_config", fake_clear_config)

    result = runner.invoke(cli, ["logout"])
    assert result.exit_code == 0
    assert called["value"] is True
    assert "Logged out." in result.output


def test_status_not_logged_in(monkeypatch) -> None:
    runner = CliRunner()

    class FakeConfig:
        api_url = "https://api.archon.dev"
        api_key = ""

    monkeypatch.setattr("archon_cli.main.get_config", lambda: FakeConfig())

    result = runner.invoke(cli, ["status"])
    assert result.exit_code == 0
    assert "Not logged in." in result.output


def test_run_requires_login(monkeypatch) -> None:
    runner = CliRunner()

    class FakeConfig:
        api_url = "https://api.archon.dev"
        api_key = ""

    monkeypatch.setattr("archon_cli.main.get_config", lambda: FakeConfig())

    result = runner.invoke(cli, ["run", "https://github.com/org/repo"])
    assert result.exit_code != 0
    assert "No API key configured." in result.output


def test_review_offline(monkeypatch) -> None:
    runner = CliRunner()

    class FakeConfig:
        api_url = "https://api.archon.dev"
        api_key = "token"

    class FakeClient:
        def __init__(self, api_url: str, api_key: str):
            self.api_url = api_url
            self.api_key = api_key

        def start_review(self, repo_url: str, mode: str, hitl: str):
            raise ArchonConnectionError("Connection failed")

    monkeypatch.setattr("archon_cli.main.get_config", lambda: FakeConfig())
    monkeypatch.setattr("archon_cli.main.ArchonAPIClient", FakeClient)

    result = runner.invoke(cli, ["run", "https://github.com/org/repo"])
    assert result.exit_code != 0
    assert "Connection failed" in result.output


def test_review_expired_token(monkeypatch) -> None:
    runner = CliRunner()

    class FakeConfig:
        api_url = "https://api.archon.dev"
        api_key = "expired"

    class FakeClient:
        def __init__(self, api_url: str, api_key: str):
            self.api_url = api_url
            self.api_key = api_key

        def start_review(self, repo_url: str, mode: str, hitl: str):
            raise ArchonAuthError("Token expired")

    monkeypatch.setattr("archon_cli.main.get_config", lambda: FakeConfig())
    monkeypatch.setattr("archon_cli.main.ArchonAPIClient", FakeClient)

    result = runner.invoke(cli, ["run", "https://github.com/org/repo"])
    assert result.exit_code != 0
    assert "Token expired" in result.output


def test_review_no_stream_flag(monkeypatch) -> None:
    runner = CliRunner()
    calls = {"stream": 0, "poll": 0}

    class FakeConfig:
        api_url = "https://api.archon.dev"
        api_key = "token"

    class FakeClient:
        def __init__(self, api_url: str, api_key: str):
            self.api_url = api_url
            self.api_key = api_key

        def start_review(self, repo_url: str, mode: str, hitl: str):
            return {"review_id": "r1", "job_id": "j1"}

        def poll_review(self, review_id: str):
            calls["poll"] += 1
            return {"findings": [], "status": "COMPLETED"}

        def download_package(self, review_id: str, output_dir: str):
            return "out.zip"

        def download_markdown(self, review_id: str, output_dir: str):
            return "out.md"

    def fake_stream(url: str, token: str) -> None:
        calls["stream"] += 1

    monkeypatch.setattr("archon_cli.main.get_config", lambda: FakeConfig())
    monkeypatch.setattr("archon_cli.main.ArchonAPIClient", FakeClient)
    monkeypatch.setattr("archon_cli.main.stream_review_progress", fake_stream)

    result = runner.invoke(cli, ["run", "https://github.com/org/repo", "--no-stream"])
    assert result.exit_code == 0
    assert calls == {"stream": 0, "poll": 1}


def test_sse_display_renders_table(monkeypatch) -> None:
    output = io.StringIO()
    sse_display.console = Console(file=output, force_terminal=False, color_system=None)

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def iter_lines(self):
            return iter([
                'event: agent_update',
                'data: {"agent": "software-architect", "status": "RUNNING", "findings_count": 0}',
                'event: agent_update',
                'data: {"agent": "cloud-architect", "status": "COMPLETED", "findings_count": 4}',
                'event: done',
                'data: Review finished',
            ])

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def stream(self, method: str, url: str):
            return FakeResponse()

    monkeypatch.setattr(sse_display.httpx, 'Client', FakeClient)

    sse_display.stream_review_progress('http://test/api/v1/jobs/j1/stream', 'token')
    rendered = output.getvalue()
    assert 'software-architect' in rendered
    assert 'cloud-architect' in rendered
    assert 'Review finished' in rendered
