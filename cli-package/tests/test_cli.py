"""Tests for ARCHON CLI."""
from click.testing import CliRunner
from archon_cli.main import cli


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "ARCHON" in result.output


def test_modes_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["modes"])
    assert result.exit_code == 0
    assert "review" in result.output
    assert "design" in result.output


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output
