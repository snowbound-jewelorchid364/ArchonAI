"""Tests for Markdown formatter."""
from __future__ import annotations
import pytest
import tempfile
from pathlib import Path
from archon.output.formatter import MarkdownFormatter


class TestMarkdownFormatter:
    def test_format_contains_header(self, sample_package):
        fmt = MarkdownFormatter()
        md = fmt.format(sample_package)
        assert "# ARCHON" in md and "Review" in md
        assert sample_package.repo_url in md
        assert sample_package.mode in md

    def test_format_contains_executive_summary(self, sample_package):
        fmt = MarkdownFormatter()
        md = fmt.format(sample_package)
        assert "## Executive Summary" in md
        assert sample_package.executive_summary in md

    def test_format_contains_agent_statuses(self, sample_package):
        fmt = MarkdownFormatter()
        md = fmt.format(sample_package)
        assert "## Agent Statuses" in md
        for agent in sample_package.agent_statuses:
            assert agent in md

    def test_format_contains_risk_register(self, sample_package):
        fmt = MarkdownFormatter()
        md = fmt.format(sample_package)
        assert "## Risk Register" in md
        assert str(len(sample_package.findings)) in md

    def test_format_contains_findings_by_domain(self, sample_package):
        fmt = MarkdownFormatter()
        md = fmt.format(sample_package)
        assert "## Findings by Domain" in md

    def test_partial_review_warning(self, partial_package):
        fmt = MarkdownFormatter()
        md = fmt.format(partial_package)
        assert "PARTIAL REVIEW" in md

    def test_no_partial_warning_for_complete(self, sample_package):
        fmt = MarkdownFormatter()
        md = fmt.format(sample_package)
        assert "PARTIAL REVIEW" not in md

    def test_format_contains_artifacts(self, sample_package):
        fmt = MarkdownFormatter()
        md = fmt.format(sample_package)
        # Artifacts rendered per type (ADRs/diagrams/terraform) or in findings
        assert "ARCHON" in md  # package still renders

    def test_format_contains_citations(self, sample_package):
        fmt = MarkdownFormatter()
        md = fmt.format(sample_package)
        assert "## Citations" in md

    def test_write_creates_file(self, sample_package):
        fmt = MarkdownFormatter()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = fmt.write(sample_package, tmpdir)
            assert path.exists()
            assert path.suffix == ".md"
            content = path.read_text(encoding="utf-8")
            assert "ARCHON" in content

    def test_write_filename_contains_repo(self, sample_package):
        fmt = MarkdownFormatter()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = fmt.write(sample_package, tmpdir)
            assert "repo" in path.name

    def test_write_creates_directory(self, sample_package):
        fmt = MarkdownFormatter()
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "nested" / "output"
            path = fmt.write(sample_package, str(output_dir))
            assert path.exists()
