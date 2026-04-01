"""Tests for HITL session management and checkpoints."""
from __future__ import annotations
import pytest
from archon.engine.hitl.checkpoints import (
    HITLMode, CheckpointType, get_checkpoints, CHECKPOINTS_BY_MODE, Checkpoint,
)
from archon.engine.hitl.session import HITLSession


class TestCheckpoints:
    def test_autopilot_has_no_checkpoints(self):
        cps = get_checkpoints(HITLMode.AUTOPILOT)
        assert cps == []

    def test_balanced_has_two_checkpoints(self):
        cps = get_checkpoints(HITLMode.BALANCED)
        assert len(cps) == 2
        assert CheckpointType.REPO_INDEXED in cps
        assert CheckpointType.FINDINGS_READY in cps

    def test_supervised_has_all_four(self):
        cps = get_checkpoints(HITLMode.SUPERVISED)
        assert len(cps) == 4

    def test_checkpoint_model(self):
        cp = Checkpoint(type=CheckpointType.REPO_INDEXED, message="Indexed 500 files")
        assert cp.approved is False
        assert cp.skipped is False
        assert cp.data == {}

    def test_hitl_mode_values(self):
        assert HITLMode.AUTOPILOT.value == "autopilot"
        assert HITLMode.BALANCED.value == "balanced"
        assert HITLMode.SUPERVISED.value == "supervised"

    def test_checkpoint_type_values(self):
        assert CheckpointType.REPO_INDEXED.value == "repo_indexed"
        assert CheckpointType.AGENTS_STARTED.value == "agents_started"
        assert CheckpointType.FINDINGS_READY.value == "findings_ready"
        assert CheckpointType.PACKAGE_READY.value == "package_ready"


class TestHITLSession:
    def test_create_session(self):
        session = HITLSession(job_id="test-001", hitl_mode=HITLMode.AUTOPILOT)
        assert session.job_id == "test-001"
        assert session.hitl_mode == HITLMode.AUTOPILOT
        assert session.checkpoints == []

    def test_needs_checkpoint_autopilot(self):
        session = HITLSession(job_id="j1", hitl_mode=HITLMode.AUTOPILOT)
        assert session.needs_checkpoint(CheckpointType.REPO_INDEXED) is False
        assert session.needs_checkpoint(CheckpointType.FINDINGS_READY) is False

    def test_needs_checkpoint_balanced(self):
        session = HITLSession(job_id="j2", hitl_mode=HITLMode.BALANCED)
        assert session.needs_checkpoint(CheckpointType.REPO_INDEXED) is True
        assert session.needs_checkpoint(CheckpointType.FINDINGS_READY) is True
        assert session.needs_checkpoint(CheckpointType.AGENTS_STARTED) is False

    def test_needs_checkpoint_supervised(self):
        session = HITLSession(job_id="j3", hitl_mode=HITLMode.SUPERVISED)
        assert session.needs_checkpoint(CheckpointType.REPO_INDEXED) is True
        assert session.needs_checkpoint(CheckpointType.AGENTS_STARTED) is True
        assert session.needs_checkpoint(CheckpointType.FINDINGS_READY) is True
        assert session.needs_checkpoint(CheckpointType.PACKAGE_READY) is True

    def test_record_checkpoint(self):
        session = HITLSession(job_id="j4", hitl_mode=HITLMode.SUPERVISED)
        cp = session.record_checkpoint(CheckpointType.REPO_INDEXED, {"files": 100})
        assert cp.type == CheckpointType.REPO_INDEXED
        assert cp.data == {"files": 100}
        assert len(session.checkpoints) == 1

    @pytest.mark.asyncio
    async def test_wait_for_approval(self):
        session = HITLSession(job_id="j5", hitl_mode=HITLMode.SUPERVISED)
        cp = session.record_checkpoint(CheckpointType.REPO_INDEXED, {})
        result = await session.wait_for_approval(cp, timeout=1.0)
        assert result is True
        assert cp.approved is True