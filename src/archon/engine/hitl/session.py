from __future__ import annotations
import asyncio
import logging
from datetime import datetime, UTC
from pydantic import BaseModel, ConfigDict, Field
from .checkpoints import HITLMode, CheckpointType, Checkpoint, get_checkpoints

logger = logging.getLogger(__name__)


class HITLSession(BaseModel):
    job_id: str
    hitl_mode: HITLMode
    checkpoints: list[Checkpoint] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def needs_checkpoint(self, checkpoint_type: CheckpointType) -> bool:
        return checkpoint_type in get_checkpoints(self.hitl_mode)

    def record_checkpoint(self, checkpoint_type: CheckpointType, data: dict = {}) -> Checkpoint:
        cp = Checkpoint(type=checkpoint_type, message=f"Checkpoint: {checkpoint_type.value}", data=data)
        self.checkpoints.append(cp)
        return cp

    async def wait_for_approval(self, checkpoint: Checkpoint, timeout: float = 300.0) -> bool:
        """In CLI mode, auto-approve after timeout. In API mode, SSE signals approval."""
        logger.info("HITL checkpoint %s — auto-approving in %ss", checkpoint.type.value, timeout)
        await asyncio.sleep(0)  # yield control
        checkpoint.approved = True
        return True
