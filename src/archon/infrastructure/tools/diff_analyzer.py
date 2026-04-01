"""PR diff analyzer for PR Reviewer mode.

Parses unified diff format and extracts structured information about
changed files, added/removed lines, and affected components.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class FileDiff:
    """A single file's diff information."""
    path: str
    added_lines: int = 0
    removed_lines: int = 0
    hunks: list[str] = field(default_factory=list)
    is_new: bool = False
    is_deleted: bool = False
    is_renamed: bool = False
    old_path: str | None = None


@dataclass
class DiffSummary:
    """Aggregated diff analysis."""
    files_changed: int = 0
    total_additions: int = 0
    total_deletions: int = 0
    file_diffs: list[FileDiff] = field(default_factory=list)
    affected_domains: list[str] = field(default_factory=list)


class DiffAnalyzer:
    """Parses unified diff text into structured DiffSummary."""

    DOMAIN_PATTERNS: dict[str, list[str]] = {
        "security": ["auth", "crypto", "secret", "token", "jwt", "oauth", "password", "permission", "rbac"],
        "data": ["model", "schema", "migration", "db", "database", "query", "orm", "repository"],
        "cloud": ["docker", "terraform", "k8s", "kubernetes", "helm", "deploy", "infra", "aws", "gcp", "azure", "ci", "cd"],
        "integration": ["api", "route", "endpoint", "webhook", "event", "queue", "message", "grpc", "graphql"],
        "ai": ["ml", "embed", "vector", "llm", "agent", "prompt", "rag"],
        "software": ["config", "util", "helper", "test", "spec", "lib", "core", "service"],
    }

    def analyse(self, diff_text: str) -> DiffSummary:
        if not diff_text or not diff_text.strip():
            return DiffSummary()

        file_diffs: list[FileDiff] = []
        current: FileDiff | None = None
        current_hunk: list[str] = []

        for line in diff_text.splitlines():
            if line.startswith("diff --git"):
                if current:
                    if current_hunk:
                        current.hunks.append("\n".join(current_hunk))
                    file_diffs.append(current)
                match = re.search(r"b/(.+)$", line)
                path = match.group(1) if match else "unknown"
                current = FileDiff(path=path)
                current_hunk = []
            elif current is not None:
                if line.startswith("new file"):
                    current.is_new = True
                elif line.startswith("deleted file"):
                    current.is_deleted = True
                elif line.startswith("rename from"):
                    current.is_renamed = True
                    current.old_path = line.split("rename from ", 1)[-1].strip()
                elif line.startswith("@@"):
                    if current_hunk:
                        current.hunks.append("\n".join(current_hunk))
                    current_hunk = [line]
                elif line.startswith("+") and not line.startswith("+++"):
                    current.added_lines += 1
                    current_hunk.append(line)
                elif line.startswith("-") and not line.startswith("---"):
                    current.removed_lines += 1
                    current_hunk.append(line)
                else:
                    current_hunk.append(line)

        if current:
            if current_hunk:
                current.hunks.append("\n".join(current_hunk))
            file_diffs.append(current)

        affected = self._detect_domains(file_diffs)

        return DiffSummary(
            files_changed=len(file_diffs),
            total_additions=sum(f.added_lines for f in file_diffs),
            total_deletions=sum(f.removed_lines for f in file_diffs),
            file_diffs=file_diffs,
            affected_domains=affected,
        )

    def _detect_domains(self, diffs: list[FileDiff]) -> list[str]:
        domains: set[str] = set()
        for fd in diffs:
            path_lower = fd.path.lower()
            for domain, patterns in self.DOMAIN_PATTERNS.items():
                if any(p in path_lower for p in patterns):
                    domains.add(domain)
        return sorted(domains) if domains else ["software"]

    def format_for_agent(self, summary: DiffSummary) -> str:
        parts = [
            f"PR Diff: {summary.files_changed} files changed, "
            f"+{summary.total_additions} -{summary.total_deletions}",
            f"Affected domains: {', '.join(summary.affected_domains)}",
            "",
        ]
        for fd in summary.file_diffs:
            status = "NEW" if fd.is_new else "DELETED" if fd.is_deleted else "MODIFIED"
            parts.append(f"  {status} {fd.path} (+{fd.added_lines} -{fd.removed_lines})")
        return "\n".join(parts)
