from __future__ import annotations
from dataclasses import dataclass


@dataclass
class ModeConfig:
    name: str
    description: str
    active_agents: list[str]
    supervisor_focus: str
    output_sections: list[str]


# Phase 1 Modes
REVIEW = ModeConfig(
    name="review",
    description="Audit an existing codebase across all 6 architectural domains",
    active_agents=["software", "cloud", "security", "data", "integration", "ai"],
    supervisor_focus="diagnostic -- identify what is wrong, risky, or suboptimal",
    output_sections=["executive_summary", "findings", "adrs", "risk_register", "citations"],
)

DESIGN = ModeConfig(
    name="design",
    description="Design a new system from a brief or requirements doc",
    active_agents=["software", "cloud", "security", "data", "integration", "ai"],
    supervisor_focus="prescriptive -- propose what to build and how",
    output_sections=["executive_summary", "architecture_proposal", "adrs", "terraform_skeleton", "diagrams", "citations"],
)

MIGRATION_PLANNER = ModeConfig(
    name="migration_planner",
    description="Plan modernisation of legacy systems",
    active_agents=["integration", "cloud", "software", "data"],
    supervisor_focus="migration roadmap -- phased approach with rollback strategy",
    output_sections=["executive_summary", "current_state", "target_state", "migration_phases", "risk_register", "citations"],
)

COMPLIANCE_AUDITOR = ModeConfig(
    name="compliance_auditor",
    description="Audit codebase against SOC2/HIPAA/GDPR/PCI-DSS",
    active_agents=["security", "data", "cloud", "software"],
    supervisor_focus="compliance gaps -- what is missing, what is violated",
    output_sections=["executive_summary", "compliance_gaps", "remediation_plan", "evidence_map", "citations"],
)

DUE_DILIGENCE = ModeConfig(
    name="due_diligence",
    description="Technical due diligence package for investors or acquirers",
    active_agents=["software", "cloud", "security", "data", "integration", "ai"],
    supervisor_focus="external audience -- strengths, material risks, evidence gaps",
    output_sections=["executive_summary", "strengths", "material_risks", "evidence_gaps", "remediation_priorities", "citations"],
)

INCIDENT_RESPONDER = ModeConfig(
    name="incident_responder",
    description="Root cause analysis and remediation plan for a production incident",
    active_agents=["software", "cloud"],
    supervisor_focus="urgent -- RCA first, then immediate + long-term remediation",
    output_sections=["executive_summary", "timeline", "root_cause", "immediate_actions", "long_term_fixes", "citations"],
)

# Phase 3 Modes
COST_OPTIMISER = ModeConfig(
    name="cost_optimiser",
    description="Identify cloud cost savings and optimisation opportunities",
    active_agents=["cloud", "data"],
    supervisor_focus="cost reduction -- ranked savings, effort vs impact, IaC quick wins",
    output_sections=["executive_summary", "savings_opportunities", "effort_matrix", "iac_quick_wins", "cost_projection", "citations"],
)

PR_REVIEWER = ModeConfig(
    name="pr_reviewer",
    description="Review a pull request for architecture impact",
    active_agents=["software", "integration"],
    supervisor_focus="change impact -- blockers, warnings, suggestions on the PR diff",
    output_sections=["summary", "blockers", "warnings", "suggestions", "citations"],
)

SCALING_ADVISOR = ModeConfig(
    name="scaling_advisor",
    description="Scaling strategy for growth targets (10x/100x)",
    active_agents=["data", "cloud", "integration"],
    supervisor_focus="bottleneck ranking -- what breaks first at target scale",
    output_sections=["executive_summary", "bottleneck_ranking", "scaling_strategy", "autoscaling_iac", "load_test_plan", "cost_model", "citations"],
)

DRIFT_MONITOR = ModeConfig(
    name="drift_monitor",
    description="Weekly architecture drift detection",
    active_agents=["software", "cloud", "security", "data", "integration", "ai"],
    supervisor_focus="drift comparison -- what changed, what was expected, what was not",
    output_sections=["drift_summary", "expected_changes", "unexpected_changes", "stale_adrs", "citations"],
)

# Phase 4 Modes
FEATURE_FEASIBILITY = ModeConfig(
    name="feature_feasibility",
    description="Assess feasibility of a proposed feature against current architecture",
    active_agents=["software", "data"],
    supervisor_focus="feasibility verdict -- build/buy/defer, complexity, prerequisites",
    output_sections=["executive_summary", "feasibility_verdict", "complexity_estimate", "prerequisites", "risk_register", "citations"],
)

VENDOR_EVALUATOR = ModeConfig(
    name="vendor_evaluator",
    description="Compare vendors or technologies for a specific decision",
    active_agents=["cloud", "integration", "data"],
    supervisor_focus="comparison matrix -- TCO, lock-in risk, migration cost",
    output_sections=["executive_summary", "comparison_matrix", "lockin_risk", "tco_analysis", "recommendation", "citations"],
)

ONBOARDING_ACCELERATOR = ModeConfig(
    name="onboarding_accelerator",
    description="Generate personalised onboarding guide for new technical leaders",
    active_agents=["software", "cloud", "security", "data", "integration", "ai"],
    supervisor_focus="explanatory -- system map, learning path, known landmines",
    output_sections=["executive_summary", "system_map", "learning_path", "glossary", "landmines", "citations"],
)

SUNSET_PLANNER = ModeConfig(
    name="sunset_planner",
    description="Plan decommission of a service or component",
    active_agents=["integration", "data", "security"],
    supervisor_focus="shutdown sequence -- dependency map, data disposition, compliance",
    output_sections=["executive_summary", "dependency_map", "shutdown_sequence", "data_disposition", "compliance_checklist", "cost_savings", "citations"],
)


ALL_MODES: dict[str, ModeConfig] = {
    "review": REVIEW,
    "design": DESIGN,
    "migration_planner": MIGRATION_PLANNER,
    "compliance_auditor": COMPLIANCE_AUDITOR,
    "due_diligence": DUE_DILIGENCE,
    "incident_responder": INCIDENT_RESPONDER,
    "cost_optimiser": COST_OPTIMISER,
    "pr_reviewer": PR_REVIEWER,
    "scaling_advisor": SCALING_ADVISOR,
    "drift_monitor": DRIFT_MONITOR,
    "feature_feasibility": FEATURE_FEASIBILITY,
    "vendor_evaluator": VENDOR_EVALUATOR,
    "onboarding_accelerator": ONBOARDING_ACCELERATOR,
    "sunset_planner": SUNSET_PLANNER,
}


def get_mode(name: str) -> ModeConfig:
    if name not in ALL_MODES:
        available = ", ".join(sorted(ALL_MODES))
        raise ValueError(f"Unknown mode: {name!r}. Available: {available}")
    return ALL_MODES[name]
