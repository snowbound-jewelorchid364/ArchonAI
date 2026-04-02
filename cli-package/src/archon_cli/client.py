"""ARCHON API client for CLI."""
from __future__ import annotations

import json
import os
import time
from typing import Any

import httpx


class ArchonAPIError(Exception):
    """Base CLI/API error."""


class ArchonConnectionError(ArchonAPIError):
    """Raised when the ARCHON API cannot be reached."""


class ArchonAuthError(ArchonAPIError):
    """Raised when auth is missing or invalid."""


class ArchonAPIClient:
    """HTTP client for ARCHON API."""

    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(
            base_url=self.api_url,
            headers=self._headers(api_key),
            timeout=httpx.Timeout(30.0, read=300.0),
        )

    @staticmethod
    def _headers(api_key: str) -> dict[str, str]:
        headers: dict[str, str] = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        try:
            response = self._client.request(method, path, **kwargs)
        except httpx.ConnectError as exc:
            raise ArchonConnectionError("Connection failed") from exc
        except httpx.TimeoutException as exc:
            raise ArchonConnectionError(f"ARCHON API request timed out for {self.api_url}.") from exc
        except httpx.HTTPError as exc:
            raise ArchonConnectionError(f"ARCHON API request failed: {exc}") from exc

        if response.status_code == 401:
            detail = _response_detail(response) or "Token expired"
            raise ArchonAuthError(detail)

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = _response_detail(response)
            message = detail or f"ARCHON API returned {response.status_code}."
            raise ArchonAPIError(message) from exc

        return response

    def validate_token(self) -> dict[str, Any]:
        response = self._request("GET", "/api/v1/auth/me")
        return response.json()

    def start_review(self, repo_url: str, mode: str, hitl_mode: str) -> dict[str, str]:
        response = self._request(
            "POST",
            "/api/v1/reviews",
            json={"repo_url": repo_url, "mode": mode, "hitl_mode": hitl_mode},
        )
        data = response.json()
        return {
            "review_id": data["review_id"],
            "job_id": data["job_id"],
        }

    def poll_review(self, review_id: str, timeout_seconds: int = 300, interval_seconds: int = 5) -> dict[str, Any]:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            review = self.get_review(review_id)
            if review.get("status") in {"COMPLETED", "FAILED", "PARTIAL"}:
                return review
            time.sleep(interval_seconds)
        raise ArchonAPIError("Review polling timed out")

    def get_review(self, review_id: str) -> dict[str, Any]:
        response = self._request("GET", f"/api/v1/reviews/{review_id}")
        return response.json()

    def get_history(self) -> list[dict[str, Any]]:
        response = self._request("GET", "/api/v1/reviews")
        return response.json()

    def download_package(self, review_id: str, output_dir: str) -> str:
        response = self._request("GET", f"/api/v1/packages/{review_id}/download")
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, f"archon-review-{review_id[:8]}.zip")
        with open(path, "wb") as handle:
            handle.write(response.content)
        return path

    def download_markdown(self, review_id: str, output_dir: str) -> str:
        review = self.get_review(review_id)
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, f"archon-review-{review_id[:8]}.md")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(review.get("markdown", "# No content"))
        return path


def _response_detail(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text.strip()
    if isinstance(payload, dict):
        detail = payload.get("detail")
        if isinstance(detail, str):
            return detail
    return ""
