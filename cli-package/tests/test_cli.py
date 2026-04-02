"""Tests for ARCHON CLI."""
from __future__ import annotations

import sys
from pathlib import Path

from click.testing import CliRunner

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from archon_cli.client import ArchonAuthError
from archon_cli.main import cli


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
