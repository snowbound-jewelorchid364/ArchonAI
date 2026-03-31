from __future__ import annotations
from enum import Enum
from pydantic import BaseModel


class HITLMode(str, Enum):
    AUTOPILOT = "autopilot"       # No interruptions — run fully autonomous
    BALANCED = "balanced"         # 2 checkpoints: after indexing + after findings
    SUPERVISED = "supervised"     # 4 checkpoints: every major stage


class CheckpointType(str, Enum):
    REPO_INDEXED = "repo_indexed"         # After RAG indexing — confirm scope
    AGENTS_STARTED = "agents_started"     # After fan-out — confirm agents running
    FINDINGS_READY = "findings_ready"     # After all agents — review before merge
    PACKAGE_READY = "package_ready"       # Final review before output write


CHECKPOINTS_BY_MODE: dict[HITLMode, list[CheckpointType]] = {
    HITLMode.AUTOPILOT: [],
    HITLMode.BALANCED: [
        CheckpointType.REPO_INDEXED,
        CheckpointType.FINDINGS_READY,
    ],
    HITLMode.SUPERVISED: [
        CheckpointType.REPO_INDEXED,
        CheckpointType.AGENTS_STARTED,
        CheckpointType.FINDINGS_READY,
        CheckpointType.PACKAGE_READY,
    ],
}


class Checkpoint(BaseModel):
    type: CheckpointType
    message: str
    data: dict = {}
    approved: bool = False
    skipped: bool = False


def get_checkpoints(hitl_mode: HITLMode) -> list[CheckpointType]:
    return CHECKPOINTS_BY_MODE[hitl_mode]
