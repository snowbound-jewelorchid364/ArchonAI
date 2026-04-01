from __future__ import annotations
import json
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI, Depends

from api.routes.jobs import router
from api.schemas.auth import CurrentUser
from api.dependencies import require_user


mock_user = CurrentUser(user_id="u_1", email="a@b.com", plan="pro")

app = FastAPI()
app.include_router(router, prefix="/jobs")
app.dependency_overrides[require_user] = lambda: mock_user

client = TestClient(app, raise_server_exceptions=False)


class MockJob:
    def __init__(self, status="RUNNING", progress=None):
        self.id = "job-1"
        self.review_id = "rev-1"
        self.status = status
        self.progress = progress or {"agents": {"software-architect": "running"}}


class TestJobStatus:
    @patch("api.routes.jobs.get_job")
    def test_get_status(self, mock_get):
        mock_get.return_value = MockJob()
        resp = client.get("/jobs/job-1/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["job_id"] == "job-1"
        assert data["status"] == "RUNNING"

    @patch("api.routes.jobs.get_job")
    def test_not_found(self, mock_get):
        mock_get.return_value = None
        resp = client.get("/jobs/missing/status")
        assert resp.status_code == 404


class TestSSEStream:
    @patch("api.routes.jobs.get_job")
    def test_stream_emits_progress(self, mock_get):
        call_count = 0
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 1:
                return MockJob(status="RUNNING", progress={"agents": {"sa": "running"}})
            return MockJob(status="COMPLETED", progress={"agents": {"sa": "done"}})

        mock_get.side_effect = side_effect
        resp = client.get("/jobs/job-1/stream")
        assert resp.status_code == 200
        assert resp.headers.get("content-type", "").startswith("text/event-stream")

        lines = resp.text.strip().split("\n")
        events = []
        for line in lines:
            if line.startswith("data: "):
                events.append(json.loads(line[6:]))
        assert len(events) >= 2
        assert events[-1]["status"] == "COMPLETED"

    @patch("api.routes.jobs.get_job")
    def test_stream_job_not_found(self, mock_get):
        mock_get.return_value = None
        resp = client.get("/jobs/missing/stream")
        assert resp.status_code == 200
        assert "error" in resp.text

    @patch("api.routes.jobs.get_job")
    def test_stream_failed_job(self, mock_get):
        mock_get.return_value = MockJob(status="FAILED")
        resp = client.get("/jobs/job-1/stream")
        assert resp.status_code == 200
        lines = resp.text.strip().split("\n")
        has_done = any("done" in line for line in lines)
        assert has_done

    @patch("api.routes.jobs.get_job")
    def test_stream_partial_result(self, mock_get):
        mock_get.return_value = MockJob(status="PARTIAL", progress={
            "agents": {"sa": "done", "ca": "failed"}
        })
        resp = client.get("/jobs/job-1/stream")
        assert "PARTIAL" in resp.text

    @patch("api.routes.jobs.get_job")
    def test_stream_headers(self, mock_get):
        mock_get.return_value = MockJob(status="COMPLETED")
        resp = client.get("/jobs/job-1/stream")
        assert "no-cache" in resp.headers.get("cache-control", "")
