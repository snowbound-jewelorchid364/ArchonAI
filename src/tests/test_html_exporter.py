from __future__ import annotations
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))

from archon.output.html_exporter import render_html, HTMLExporter, MERMAID_CDN


def test_render_html_contains_health_score(sample_package):
    html = render_html(sample_package)
    assert "Health Score" in html


def test_render_html_contains_mermaid_script(sample_package):
    html = render_html(sample_package)
    assert MERMAID_CDN in html or "mermaid" in html


def test_render_html_contains_findings(sample_package):
    html = render_html(sample_package)
    for f in sample_package.findings:
        assert f.title in html


def test_render_html_contains_executive_summary(sample_package):
    html = render_html(sample_package)
    assert sample_package.executive_summary in html


def test_render_html_filter_selects(sample_package):
    html = render_html(sample_package)
    assert "filterSeverity" in html
    assert "filterDomain" in html


def test_render_html_dark_mode_toggle(sample_package):
    html = render_html(sample_package)
    assert "toggleTheme" in html


def test_render_html_is_string(sample_package):
    html = render_html(sample_package)
    assert isinstance(html, str)
    assert html.startswith("<!DOCTYPE html>")


def test_html_exporter_write(sample_package, tmp_path):
    exporter = HTMLExporter()
    path = exporter.write(sample_package, str(tmp_path))
    assert path.exists()
    assert path.suffix == ".html"
    content = path.read_text(encoding="utf-8")
    assert "ARCHON" in content
