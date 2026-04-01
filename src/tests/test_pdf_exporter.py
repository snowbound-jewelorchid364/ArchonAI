from __future__ import annotations
import sys
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parents[1]))

from archon.output.pdf_exporter import PDFExporter, _executive_summary_html, _body_of


# WeasyPrint requires native GTK libs (Pango/Cairo) not present in CI/Windows.
# We mock the C-level call so the test validates our logic, not the native stack.
def _mock_weasyprint():
    fake_html_cls = MagicMock()
    fake_instance = MagicMock()
    fake_instance.write_pdf.return_value = b"%PDF-1.4 fake pdf bytes"
    fake_html_cls.return_value = fake_instance
    return fake_html_cls


def test_pdf_export_returns_bytes(sample_package):
    exporter = PDFExporter()
    fake = _mock_weasyprint()
    with patch.dict("sys.modules", {"weasyprint": MagicMock(HTML=fake)}):
        result = exporter.export(sample_package)
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_pdf_export_starts_with_pdf_header(sample_package):
    exporter = PDFExporter()
    fake = _mock_weasyprint()
    with patch.dict("sys.modules", {"weasyprint": MagicMock(HTML=fake)}):
        result = exporter.export(sample_package)
    assert result[:4] == b"%PDF"


def test_pdf_exporter_write(sample_package, tmp_path):
    exporter = PDFExporter()
    fake = _mock_weasyprint()
    with patch.dict("sys.modules", {"weasyprint": MagicMock(HTML=fake)}):
        path = exporter.write(sample_package, str(tmp_path))
    assert path.exists()
    assert path.suffix == ".pdf"
    assert path.stat().st_size > 0


def test_executive_summary_html_contains_score(sample_package):
    html = _executive_summary_html(sample_package)
    assert "Health Score" in html


def test_executive_summary_html_contains_repo(sample_package):
    html = _executive_summary_html(sample_package)
    assert "github.com/test/repo" in html


def test_body_of_extracts_body(tmp_path):
    html = "<html><head></head><body><p>Hello</p></body></html>"
    result = _body_of(html)
    assert "<p>Hello</p>" in result
    assert "<html" not in result
