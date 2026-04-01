"""Vendor comparison framework for Vendor Evaluator mode.

Provides structured scoring and comparison of technology vendors
across multiple evaluation criteria.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class VendorScore:
    """Score for a single vendor across one criterion."""
    criterion: str
    score: float  # 0.0 - 10.0
    weight: float = 1.0
    notes: str = ""


@dataclass
class VendorProfile:
    """Complete evaluation profile for a single vendor."""
    name: str
    scores: list[VendorScore] = field(default_factory=list)
    total_weighted_score: float = 0.0
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    lockin_risk: str = "MEDIUM"  # LOW | MEDIUM | HIGH | CRITICAL
    tco_year1: float = 0.0
    tco_year3: float = 0.0


@dataclass
class VendorComparison:
    """Full comparison across all evaluated vendors."""
    vendors: list[VendorProfile] = field(default_factory=list)
    criteria: list[str] = field(default_factory=list)
    recommended: str = ""
    recommendation_rationale: str = ""
    switch_cost_estimate: str = ""


class VendorComparator:
    """Framework for structured vendor evaluation and comparison."""

    DEFAULT_CRITERIA = [
        "performance",
        "scalability",
        "cost",
        "developer_experience",
        "ecosystem",
        "support",
        "security",
        "compliance",
        "migration_ease",
        "lockin_risk",
    ]

    DEFAULT_WEIGHTS: dict[str, float] = {
        "performance": 1.5,
        "scalability": 1.5,
        "cost": 2.0,
        "developer_experience": 1.0,
        "ecosystem": 1.0,
        "support": 0.8,
        "security": 1.5,
        "compliance": 1.0,
        "migration_ease": 1.2,
        "lockin_risk": 1.5,
    }

    def compare(
        self,
        vendors: list[VendorProfile],
        criteria: list[str] | None = None,
        weights: dict[str, float] | None = None,
    ) -> VendorComparison:
        criteria = criteria or self.DEFAULT_CRITERIA
        weights = weights or self.DEFAULT_WEIGHTS

        for vendor in vendors:
            weighted_sum = 0.0
            weight_total = 0.0
            for score in vendor.scores:
                w = weights.get(score.criterion, score.weight)
                weighted_sum += score.score * w
                weight_total += w
            vendor.total_weighted_score = round(weighted_sum / weight_total, 2) if weight_total > 0 else 0.0

        ranked = sorted(vendors, key=lambda v: v.total_weighted_score, reverse=True)
        recommended = ranked[0].name if ranked else ""
        rationale = ""
        if len(ranked) >= 2:
            diff = ranked[0].total_weighted_score - ranked[1].total_weighted_score
            rationale = (
                f"{ranked[0].name} scores {ranked[0].total_weighted_score}/10 vs "
                f"{ranked[1].name} at {ranked[1].total_weighted_score}/10 "
                f"(+{diff:.1f} advantage)"
            )

        return VendorComparison(
            vendors=ranked,
            criteria=criteria,
            recommended=recommended,
            recommendation_rationale=rationale,
        )

    def format_comparison_matrix(self, comparison: VendorComparison) -> str:
        if not comparison.vendors:
            return "No vendors to compare."

        headers = ["Criterion"] + [v.name for v in comparison.vendors]
        rows: list[list[str]] = []

        all_criteria = set()
        for v in comparison.vendors:
            for s in v.scores:
                all_criteria.add(s.criterion)

        for criterion in sorted(all_criteria):
            row = [criterion.replace("_", " ").title()]
            for vendor in comparison.vendors:
                score = next((s.score for s in vendor.scores if s.criterion == criterion), 0.0)
                row.append(f"{score:.1f}")
            rows.append(row)

        rows.append(["**TOTAL**"] + [f"**{v.total_weighted_score:.1f}**" for v in comparison.vendors])

        lines = ["| " + " | ".join(headers) + " |"]
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for row in rows:
            lines.append("| " + " | ".join(row) + " |")

        if comparison.recommended:
            lines.append(f"\n**Recommended:** {comparison.recommended}")
            if comparison.recommendation_rationale:
                lines.append(f"**Rationale:** {comparison.recommendation_rationale}")

        return "\n".join(lines)
