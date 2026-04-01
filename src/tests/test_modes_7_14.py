"""Tests for Modes 7-14 implementation.

Tests cover:
- Mode configs exist and are complete
- Formatter renders all mode-specific sections
- Infrastructure tools (DiffAnalyzer, DriftDetector, VendorComparator)
- Agent routing per mode
"""
from __future__ import annotations
import pytest
from datetime import datetime

from archon.engine.modes.configs import ALL_MODES, get_mode, ModeConfig
from archon.output.formatter import MarkdownFormatter
from archon.core.models import ReviewPackage, Finding, Severity, Citation, Artifact, ArtifactType
from archon.infrastructure.tools.diff_analyzer import DiffAnalyzer, DiffSummary, FileDiff
from archon.infrastructure.tools.drift_detector import DriftDetector, DriftReport, DriftItem
from archon.infrastructure.tools.vendor_comparator import (
    VendorComparator, VendorComparison, VendorProfile, VendorScore,
)


# ── Fixtures ────────────────────────────────────────────────

@pytest.fixture
def sample_findings() -> list[Finding]:
    return [
        Finding(id="F-001", title="High Memory Usage", description="Service uses 4GB RAM",
                severity=Severity.HIGH, domain="cloud-architect", recommendation="Use caching",
                confidence=0.8, from_codebase=True),
        Finding(id="F-002", title="SQL Injection Risk", description="Unparameterised query in auth",
                severity=Severity.CRITICAL, domain="security-architect",
                file_path="src/auth/login.py", line_number=47,
                recommendation="Use parameterised queries", confidence=0.95, from_codebase=True),
        Finding(id="F-003", title="Missing ADR for DB choice", description="No ADR",
                severity=Severity.MEDIUM, domain="software-architect",
                recommendation="Write ADR-001", confidence=0.7, from_codebase=True),
        Finding(id="F-004", title="Cost savings on RDS", description="Oversized RDS instance",
                severity=Severity.HIGH, domain="cloud-architect",
                recommendation="Downsize to db.t3.medium", confidence=0.85, from_codebase=True),
        Finding(id="F-005", title="No vendor lock-in mitigation", description="Proprietary API",
                severity=Severity.MEDIUM, domain="integration-architect",
                recommendation="Add abstraction layer", confidence=0.7, from_codebase=False),
    ]


@pytest.fixture
def sample_package(sample_findings: list[Finding]) -> ReviewPackage:
    return ReviewPackage(
        run_id="test-run",
        repo_url="https://github.com/test/repo",
        mode="review",
        duration_seconds=120.5,
        executive_summary="Test summary.",
        findings=sample_findings,
        artifacts=[],
        citations=[],
        agent_statuses={"software-architect": "COMPLETED", "cloud-architect": "COMPLETED"},
        partial=False,
        model_version="test",
    )


@pytest.fixture
def formatter() -> MarkdownFormatter:
    return MarkdownFormatter()


# ── Mode Config Tests ───────────────────────────────────────

class TestModeConfigs:
    MODES_7_14 = [
        "cost_optimiser", "pr_reviewer", "scaling_advisor", "drift_monitor",
        "feature_feasibility", "vendor_evaluator", "onboarding_accelerator", "sunset_planner",
    ]

    def test_all_modes_registered(self):
        for mode in self.MODES_7_14:
            assert mode in ALL_MODES, f"Mode {mode} not in ALL_MODES"

    def test_mode_configs_complete(self):
        for mode_name in self.MODES_7_14:
            cfg = get_mode(mode_name)
            assert cfg.name == mode_name
            assert len(cfg.description) > 10
            assert len(cfg.active_agents) >= 2
            assert len(cfg.supervisor_focus) > 10
            assert len(cfg.output_sections) >= 4

    def test_cost_optimiser_agents(self):
        cfg = get_mode("cost_optimiser")
        assert "cloud" in cfg.active_agents
        assert "data" in cfg.active_agents

    def test_pr_reviewer_agents(self):
        cfg = get_mode("pr_reviewer")
        assert "software" in cfg.active_agents

    def test_scaling_advisor_agents(self):
        cfg = get_mode("scaling_advisor")
        assert "data" in cfg.active_agents
        assert "cloud" in cfg.active_agents

    def test_drift_monitor_uses_all_agents(self):
        cfg = get_mode("drift_monitor")
        assert len(cfg.active_agents) == 6

    def test_onboarding_uses_all_agents(self):
        cfg = get_mode("onboarding_accelerator")
        assert len(cfg.active_agents) == 6

    def test_sunset_planner_agents(self):
        cfg = get_mode("sunset_planner")
        assert "integration" in cfg.active_agents
        assert "security" in cfg.active_agents


# ── Formatter Section Tests ─────────────────────────────────

class TestFormatterSections:
    def test_all_modes_render(self, formatter, sample_package):
        for mode_name in ALL_MODES:
            sample_package.mode = mode_name
            output = formatter.format(sample_package)
            assert "# ARCHON" in output
            assert len(output) > 100

    def test_cost_optimiser_sections(self, formatter, sample_package):
        sample_package.mode = "cost_optimiser"
        output = formatter.format(sample_package)
        assert "## Savings Opportunities" in output
        assert "## Effort vs Savings Matrix" in output
        assert "## IaC Quick Wins" in output
        assert "## Cost Projection" in output

    def test_pr_reviewer_sections(self, formatter, sample_package):
        sample_package.mode = "pr_reviewer"
        output = formatter.format(sample_package)
        assert "## Summary" in output
        assert "## Blockers" in output
        assert "## Warnings" in output
        assert "## Suggestions" in output

    def test_scaling_advisor_sections(self, formatter, sample_package):
        sample_package.mode = "scaling_advisor"
        output = formatter.format(sample_package)
        assert "## Bottleneck Ranking" in output
        assert "## Scaling Strategy" in output
        assert "## Load Test Plan" in output

    def test_drift_monitor_sections(self, formatter, sample_package):
        sample_package.mode = "drift_monitor"
        output = formatter.format(sample_package)
        assert "## Drift Summary" in output
        assert "## Expected Changes" in output
        assert "## Unexpected Changes" in output

    def test_feature_feasibility_sections(self, formatter, sample_package):
        sample_package.mode = "feature_feasibility"
        output = formatter.format(sample_package)
        assert "## Feasibility Verdict" in output
        assert "## Complexity Estimate" in output
        assert "## Prerequisites" in output

    def test_vendor_evaluator_sections(self, formatter, sample_package):
        sample_package.mode = "vendor_evaluator"
        output = formatter.format(sample_package)
        assert "## Comparison Matrix" in output
        assert "## Lock-in Risk Register" in output
        assert "## Total Cost of Ownership" in output

    def test_onboarding_sections(self, formatter, sample_package):
        sample_package.mode = "onboarding_accelerator"
        output = formatter.format(sample_package)
        assert "## System Map" in output
        assert "## Learning Path" in output
        assert "## Glossary" in output
        assert "## Known Landmines" in output

    def test_sunset_planner_sections(self, formatter, sample_package):
        sample_package.mode = "sunset_planner"
        output = formatter.format(sample_package)
        assert "## Dependency Map" in output
        assert "## Shutdown Sequence" in output
        assert "## Data Disposition Plan" in output
        assert "## Compliance Checklist" in output

    def test_feasibility_verdict_defer(self, formatter, sample_package):
        """3+ CRITICAL findings should produce DEFER verdict."""
        sample_package.mode = "feature_feasibility"
        sample_package.findings = [
            Finding(id=f"C-{i}", title=f"Critical {i}", description="Bad",
                    severity=Severity.CRITICAL, domain="test",
                    recommendation="Fix", confidence=0.9, from_codebase=True)
            for i in range(4)
        ]
        output = formatter.format(sample_package)
        assert "DEFER" in output

    def test_complexity_estimate_xl(self, formatter, sample_package):
        """Many findings should produce XL complexity."""
        sample_package.mode = "feature_feasibility"
        sample_package.findings = [
            Finding(id=f"F-{i}", title=f"Finding {i}", description="Issue",
                    severity=Severity.CRITICAL, domain="test",
                    recommendation="Fix", confidence=0.9, from_codebase=True)
            for i in range(5)
        ]
        output = formatter.format(sample_package)
        assert "XL" in output

    def test_migration_planner_sections(self, formatter, sample_package):
        sample_package.mode = "migration_planner"
        output = formatter.format(sample_package)
        assert "## Current State" in output
        assert "## Target State" in output
        assert "## Migration Phases" in output

    def test_compliance_auditor_sections(self, formatter, sample_package):
        sample_package.mode = "compliance_auditor"
        output = formatter.format(sample_package)
        assert "## Compliance Gaps" in output
        assert "## Remediation Plan" in output

    def test_incident_responder_sections(self, formatter, sample_package):
        sample_package.mode = "incident_responder"
        output = formatter.format(sample_package)
        assert "## Root Cause Analysis" in output
        assert "## Immediate Actions" in output
        assert "## Long-Term Fixes" in output


# ── DiffAnalyzer Tests ──────────────────────────────────────

class TestDiffAnalyzer:
    SAMPLE_DIFF = """diff --git a/src/auth/login.py b/src/auth/login.py
index abc1234..def5678 100644
--- a/src/auth/login.py
+++ b/src/auth/login.py
@@ -10,6 +10,8 @@ def login(username, password):
     user = db.query(username)
+    if not user:
+        raise AuthError("not found")
     return generate_token(user)
-    # old comment
diff --git a/docker/Dockerfile b/docker/Dockerfile
new file mode 100644
--- /dev/null
+++ b/docker/Dockerfile
@@ -0,0 +1,3 @@
+FROM python:3.11
+COPY . /app
+CMD ["python", "main.py"]
diff --git a/old_service.py b/old_service.py
deleted file mode 100644
--- a/old_service.py
+++ /dev/null
@@ -1,5 +0,0 @@
-def old():
-    pass
"""

    def test_parse_basic(self):
        analyzer = DiffAnalyzer()
        summary = analyzer.analyse(self.SAMPLE_DIFF)
        assert summary.files_changed == 3

    def test_additions_deletions(self):
        analyzer = DiffAnalyzer()
        summary = analyzer.analyse(self.SAMPLE_DIFF)
        assert summary.total_additions == 5
        assert summary.total_deletions == 3

    def test_new_file_detected(self):
        analyzer = DiffAnalyzer()
        summary = analyzer.analyse(self.SAMPLE_DIFF)
        new_files = [f for f in summary.file_diffs if f.is_new]
        assert len(new_files) == 1
        assert "Dockerfile" in new_files[0].path

    def test_deleted_file_detected(self):
        analyzer = DiffAnalyzer()
        summary = analyzer.analyse(self.SAMPLE_DIFF)
        deleted = [f for f in summary.file_diffs if f.is_deleted]
        assert len(deleted) == 1

    def test_domain_detection(self):
        analyzer = DiffAnalyzer()
        summary = analyzer.analyse(self.SAMPLE_DIFF)
        assert "security" in summary.affected_domains  # auth file
        assert "cloud" in summary.affected_domains  # docker file

    def test_empty_diff(self):
        analyzer = DiffAnalyzer()
        summary = analyzer.analyse("")
        assert summary.files_changed == 0
        assert summary.total_additions == 0

    def test_format_for_agent(self):
        analyzer = DiffAnalyzer()
        summary = analyzer.analyse(self.SAMPLE_DIFF)
        text = analyzer.format_for_agent(summary)
        assert "3 files changed" in text
        assert "MODIFIED" in text or "NEW" in text


# ── DriftDetector Tests ─────────────────────────────────────

class TestDriftDetector:
    def test_detect_removed_file(self):
        detector = DriftDetector()
        baseline = {"a.py": "print('hello')", "b.py": "print('world')"}
        current = {"a.py": "print('hello')"}
        report = detector.compare(baseline, current)
        assert report.total_drifts == 1
        assert len(report.unexpected_changes) == 1
        assert report.unexpected_changes[0].drift_type == "removed"

    def test_detect_added_file(self):
        detector = DriftDetector()
        baseline = {"a.py": "old"}
        current = {"a.py": "old", "new.py": "new code"}
        report = detector.compare(baseline, current)
        added = [d for d in report.unexpected_changes if d.drift_type == "added"]
        assert len(added) == 1

    def test_detect_modified_file(self):
        detector = DriftDetector()
        baseline = {"a.py": "version1"}
        current = {"a.py": "version2"}
        report = detector.compare(baseline, current)
        modified = [d for d in report.unexpected_changes if d.drift_type == "modified"]
        assert len(modified) == 1

    def test_known_changes_expected(self):
        detector = DriftDetector()
        baseline = {"a.py": "v1"}
        current = {"a.py": "v2"}
        report = detector.compare(baseline, current, known_changes=["a.py"])
        assert len(report.expected_changes) == 1
        assert len(report.unexpected_changes) == 0

    def test_no_drift(self):
        detector = DriftDetector()
        files = {"a.py": "same"}
        report = detector.compare(files, files)
        assert report.total_drifts == 0

    def test_stale_adr_detection(self):
        detector = DriftDetector()
        baseline = {"src/auth.py": "old", "docs/adr-001.md": "Decision about auth.py"}
        current = {"src/auth.py": "new", "docs/adr-001.md": "Decision about auth.py"}
        report = detector.compare(baseline, current)
        assert len(report.stale_adrs) >= 1

    def test_format_for_agent(self):
        detector = DriftDetector()
        baseline = {"a.py": "v1"}
        current = {"a.py": "v2", "b.py": "new"}
        report = detector.compare(baseline, current)
        text = detector.format_for_agent(report)
        assert "Drift Report" in text
        assert "Unexpected" in text


# ── VendorComparator Tests ──────────────────────────────────

class TestVendorComparator:
    def test_basic_comparison(self):
        comparator = VendorComparator()
        vendors = [
            VendorProfile(name="PostgreSQL", scores=[
                VendorScore(criterion="performance", score=8.0),
                VendorScore(criterion="cost", score=9.0),
            ]),
            VendorProfile(name="MongoDB", scores=[
                VendorScore(criterion="performance", score=7.0),
                VendorScore(criterion="cost", score=6.0),
            ]),
        ]
        result = comparator.compare(vendors)
        assert result.recommended == "PostgreSQL"

    def test_weighted_scoring(self):
        comparator = VendorComparator()
        vendors = [
            VendorProfile(name="A", scores=[
                VendorScore(criterion="cost", score=10.0),
                VendorScore(criterion="performance", score=2.0),
            ]),
            VendorProfile(name="B", scores=[
                VendorScore(criterion="cost", score=5.0),
                VendorScore(criterion="performance", score=9.0),
            ]),
        ]
        # cost weight=2.0, perf weight=1.5 => A: (10*2+2*1.5)/3.5=6.57, B: (5*2+9*1.5)/3.5=6.71
        result = comparator.compare(vendors)
        assert result.recommended == "B"

    def test_empty_vendors(self):
        comparator = VendorComparator()
        result = comparator.compare([])
        assert result.recommended == ""

    def test_comparison_matrix_format(self):
        comparator = VendorComparator()
        vendors = [
            VendorProfile(name="X", scores=[VendorScore(criterion="cost", score=8.0)]),
            VendorProfile(name="Y", scores=[VendorScore(criterion="cost", score=6.0)]),
        ]
        result = comparator.compare(vendors)
        matrix = comparator.format_comparison_matrix(result)
        assert "| Criterion |" in matrix
        assert "X" in matrix
        assert "Y" in matrix
        assert "**Recommended:**" in matrix

    def test_single_vendor(self):
        comparator = VendorComparator()
        vendors = [
            VendorProfile(name="Solo", scores=[VendorScore(criterion="cost", score=7.0)]),
        ]
        result = comparator.compare(vendors)
        assert result.recommended == "Solo"
        assert result.recommendation_rationale == ""
