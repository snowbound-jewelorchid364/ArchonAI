import pytest
from archon.core.models.finding import Finding, Severity, Citation
from archon.core.models.review_package import ReviewPackage
from archon.output.formatter import MarkdownFormatter


def _make_finding(severity=Severity.HIGH, domain="software"):
    return Finding(
        id=domain[:2].upper() + "-001", title="Test Finding", severity=severity,
        description="Test desc", recommendation="Fix it", domain=domain,
        confidence=0.8, from_codebase=True, citations=[]
    )


def _make_package(mode="review", findings=None):
    return ReviewPackage(
        run_id="test-run",
        repo_url="https://github.com/test/repo",
        mode=mode,
        duration_seconds=30.0,
        executive_summary="Test summary",
        findings=findings or [_make_finding()],
    )


class TestMarkdownFormatter:
    def test_format_review(self):
        fmt = MarkdownFormatter()
        result = fmt.format(_make_package("review"))
        assert "ARCHON" in result

    def test_format_design(self):
        fmt = MarkdownFormatter()
        result = fmt.format(_make_package("design"))
        assert "ARCHON" in result

    def test_format_includes_severity(self):
        fmt = MarkdownFormatter()
        findings = [_make_finding(Severity.CRITICAL)]
        result = fmt.format(_make_package(findings=findings))
        assert "CRITICAL" in result

    def test_format_all_14_modes(self):
        from archon.engine.modes.configs import ALL_MODES
        fmt = MarkdownFormatter()
        for mode_name in ALL_MODES:
            result = fmt.format(_make_package(mode=mode_name))
            assert len(result) > 50, f"Mode {mode_name} produced too short output"

    def test_write_creates_file(self, tmp_path):
        fmt = MarkdownFormatter()
        path = fmt.write(_make_package(), output_dir=str(tmp_path))
        assert path.exists()
        content = path.read_text()
        assert "ARCHON" in content

    def test_write_filename_format(self, tmp_path):
        fmt = MarkdownFormatter()
        path = fmt.write(_make_package(), output_dir=str(tmp_path))
        assert path.name.startswith("archon-review-repo-")
        assert path.suffix == ".md"
