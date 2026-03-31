"""ARCHON API client for CLI."""
import os
import json
from typing import Any, Generator

import httpx


class ArchonAPIClient:
    """HTTP client for ARCHON API."""

    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(
            base_url=self.api_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=httpx.Timeout(30.0, read=300.0),
        )

    def start_review(self, repo_url: str, mode: str, hitl_mode: str) -> str:
        """Start a new review and return the job ID."""
        resp = self._client.post(
            "/api/v1/reviews",
            json={"repo_url": repo_url, "mode": mode, "hitl_mode": hitl_mode},
        )
        resp.raise_for_status()
        return resp.json()["job_id"]

    def stream_progress(self, job_id: str) -> Generator[dict, None, None]:
        """Stream SSE progress events for a job."""
        with httpx.Client(
            base_url=self.api_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=httpx.Timeout(None),
        ) as stream_client:
            with stream_client.stream("GET", f"/api/v1/jobs/{job_id}/stream") as resp:
                for line in resp.iter_lines():
                    if line.startswith("data: "):
                        data = line[6:].strip()
                        if data == "[DONE]":
                            return
                        try:
                            yield json.loads(data)
                        except json.JSONDecodeError:
                            continue

    def get_review(self, review_id: str) -> dict[str, Any]:
        """Get review results."""
        resp = self._client.get(f"/api/v1/reviews/{review_id}")
        resp.raise_for_status()
        return resp.json()

    def get_history(self) -> list[dict[str, Any]]:
        """Get review history."""
        resp = self._client.get("/api/v1/reviews")
        resp.raise_for_status()
        return resp.json()

    def download_package(self, review_id: str, output_dir: str) -> str:
        """Download review package as ZIP."""
        resp = self._client.get(f"/api/v1/packages/{review_id}/download")
        resp.raise_for_status()

        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, f"archon-review-{review_id[:8]}.zip")
        with open(path, "wb") as f:
            f.write(resp.content)
        return path

    def download_markdown(self, review_id: str, output_dir: str) -> str:
        """Download review as markdown."""
        review = self.get_review(review_id)
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, f"archon-review-{review_id[:8]}.md")
        with open(path, "w") as f:
            f.write(review.get("markdown", "# No content"))
        return path
