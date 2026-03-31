from __future__ import annotations
from enum import Enum
from pydantic import BaseModel


class ArtifactType(str, Enum):
    ADR = "ADR"
    TERRAFORM = "TERRAFORM"
    DIAGRAM = "DIAGRAM"
    RUNBOOK = "RUNBOOK"


class Artifact(BaseModel):
    id: str
    artifact_type: ArtifactType
    title: str
    content: str
    filename: str
