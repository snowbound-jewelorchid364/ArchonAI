from __future__ import annotations
from dataclasses import dataclass


@dataclass
class ModeConfig:
    name: str
    description: str
    active_agents: list[str]
    supervisor_focus: str
    output_sections: list[str]


REVIEW = ModeConfig(
    name="review",
    description="Audit an existing codebase across all 6 architectural domains",
    active_agents=["software", "cloud", "security", "data", "integration", "ai"],
    supervisor_focus="diagnostic — identify what is wrong, risky, or suboptimal",
    output_sections=["executive_summary", "findings", "adrs", "risk_register", "citations"],
)

DESIGN = ModeConfig(
    name="design",
    description="Design a new system from a brief or requirements doc",
    active_agents=["software", "cloud", "security", "data", "integration", "ai"],
    supervisor_focus="prescriptive — propose what to build and how",
    output_sections=["executive_summary", "architecture_proposal", "adrs", "terraform_skeleton", "diagrams", "citations"],
)

MIGRATION_PLANNER = ModeConfig(
    name="migration_planner",
    description="Plan modernisation of legacy systems",
    active_agents=["integration", "cloud", "software", "data"],
    supervisor_focus="migration roadmap — phased approach with rollback strategy",
    output_sections=["executive_summary", "current_state", "target_state", "migration_phases", "risk_register", "citations"],
)

COMPLIANCE_AUDITOR = ModeConfig(
    name="compliance_auditor",
    description="Audit codebase against SOC2/HIPAA/GDPR/PCI-DSS",
    active_agents=["security", "data", "cloud", "software"],
    supervisor_focus="compliance gaps — what is missing, what is violated",
    output_sections=["executive_summary", "compliance_gaps", "remediation_plan", "evidence_map", "citations"],
)

DUE_DILIGENCE = ModeConfig(
    name="due_diligence",
    description="Technical due diligence package for investors or acquirers",
    active_agents=["software", "cloud", "security", "data", "integration", "ai"],
    supervisor_focus="external audience — strengths, material risks, evidence gaps",
    output_sections=["executive_summary", "strengths", "material_risks", "evidence_gaps", "remediation_priorities", "citations"],
)

INCIDENT_RESPONDER = ModeConfig(
    name="incident_responder",
    description="Root cause analysis and remediation plan for a production incident",
    active_agents=["software", "cloud", "security"],
    supervisor_focus="urgent — RCA first, then immediate + long-term remediation",
    output_sections=["executive_summary", "timeline", "root_cause", "immediate_actions", "long_term_fixes", "citations"],
)

ALL_MODES: dict[str, ModeConfig] = {
    "review": REVIEW,
    "design": DESIGN,
    "migration_planner": MIGRATION_PLANNER,
    "compliance_auditor": COMPLIANCE_AUDITOR,
    "due_diligence": DUE_DILIGENCE,
    "incident_responder": INCIDENT_RESPONDER,
}


def get_mode(name: str) -> ModeConfig:
    if name not in ALL_MODES:
        raise ValueError(f"Unknown mode: {name!r}. Available: {list(ALL_MODES)}")
    return ALL_MODES[name]
