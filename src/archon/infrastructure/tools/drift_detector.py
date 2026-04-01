"""Architecture drift detector for Drift Monitor mode.

Compares current codebase state against a previous architecture snapshot
to identify unexpected changes, stale ADRs, and manual console changes.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class DriftItem:
    """A single detected drift between baseline and current state."""
    component: str
    drift_type: str  # "added" | "removed" | "modified" | "config_changed"
    description: str
    expected: bool = False
    severity: str = "MEDIUM"  # CRITICAL | HIGH | MEDIUM | LOW | INFO
    file_path: str | None = None


@dataclass
class DriftReport:
    """Full drift analysis between two snapshots."""
    baseline_date: str | None = None
    scan_date: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    total_drifts: int = 0
    expected_changes: list[DriftItem] = field(default_factory=list)
    unexpected_changes: list[DriftItem] = field(default_factory=list)
    stale_adrs: list[str] = field(default_factory=list)
    summary: str = ""


class DriftDetector:
    """Detects architecture drift between a baseline snapshot and current state."""

    def compare(
        self,
        baseline_files: dict[str, str],
        current_files: dict[str, str],
        known_changes: list[str] | None = None,
    ) -> DriftReport:
        known = set(known_changes or [])
        drifts: list[DriftItem] = []

        # Detect removed files
        for path in baseline_files:
            if path not in current_files:
                drifts.append(DriftItem(
                    component=path,
                    drift_type="removed",
                    description=f"File removed: {path}",
                    expected=path in known,
                    severity="HIGH",
                    file_path=path,
                ))

        # Detect added files
        for path in current_files:
            if path not in baseline_files:
                drifts.append(DriftItem(
                    component=path,
                    drift_type="added",
                    description=f"New file: {path}",
                    expected=path in known,
                    severity="LOW",
                    file_path=path,
                ))

        # Detect modified files
        for path in baseline_files:
            if path in current_files and baseline_files[path] != current_files[path]:
                drifts.append(DriftItem(
                    component=path,
                    drift_type="modified",
                    description=f"File modified: {path}",
                    expected=path in known,
                    severity="MEDIUM",
                    file_path=path,
                ))

        expected = [d for d in drifts if d.expected]
        unexpected = [d for d in drifts if not d.expected]

        # Find stale ADRs (ADR files that reference changed components)
        stale = self._find_stale_adrs(baseline_files, current_files, drifts)

        return DriftReport(
            total_drifts=len(drifts),
            expected_changes=expected,
            unexpected_changes=unexpected,
            stale_adrs=stale,
            summary=f"{len(unexpected)} unexpected changes, {len(expected)} expected changes, {len(stale)} potentially stale ADRs",
        )

    def _find_stale_adrs(
        self,
        baseline: dict[str, str],
        current: dict[str, str],
        drifts: list[DriftItem],
    ) -> list[str]:
        stale: list[str] = []
        changed_components = {d.component for d in drifts}
        adr_files = {p: c for p, c in current.items() if "adr" in p.lower() and p.endswith(".md")}
        for adr_path, content in adr_files.items():
            content_lower = content.lower()
            for comp in changed_components:
                comp_name = comp.rsplit("/", 1)[-1].split(".")[0]
                if comp_name.lower() in content_lower:
                    stale.append(f"{adr_path} (references changed component: {comp})")
                    break
        return stale

    def format_for_agent(self, report: DriftReport) -> str:
        parts = [
            f"Drift Report: {report.total_drifts} total drifts",
            f"  Unexpected: {len(report.unexpected_changes)}",
            f"  Expected: {len(report.expected_changes)}",
            f"  Stale ADRs: {len(report.stale_adrs)}",
            "",
        ]
        if report.unexpected_changes:
            parts.append("Unexpected changes:")
            for d in report.unexpected_changes:
                parts.append(f"  [{d.severity}] {d.drift_type}: {d.component}")
        if report.stale_adrs:
            parts.append("Potentially stale ADRs:")
            for a in report.stale_adrs:
                parts.append(f"  - {a}")
        return "\n".join(parts)
