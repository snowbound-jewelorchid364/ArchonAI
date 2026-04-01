from __future__ import annotations

import os
from collections import Counter
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import httpx

from .base import ConnectorContext, MCPConnector, now_iso


class GitHubConnector(MCPConnector):
    name = "github"

    @staticmethod
    def parse_repo_url(repo_url: str) -> tuple[str, str]:
        parsed = urlparse(repo_url)
        path = parsed.path.strip("/")
        parts = [p for p in path.split("/") if p]
        if len(parts) < 2:
            raise ValueError(f"Invalid GitHub repo URL: {repo_url}")
        return parts[0], parts[1].replace(".git", "")

    async def fetch(self, **kwargs) -> ConnectorContext:
        repo_url = kwargs.get("repo_url", "")
        token = kwargs.get("github_token") or os.getenv("GITHUB_TOKEN", "")

        empty = {"prs": [], "commits": {}, "contributors": [], "issues": []}
        if not repo_url:
            return ConnectorContext(
                source=self.name,
                summary="No repository URL provided for GitHub connector.",
                raw_data=empty,
                fetched_at=now_iso(),
            )
        if not token:
            return ConnectorContext(
                source=self.name,
                summary="GitHub token not configured. Returning empty GitHub context.",
                raw_data=empty,
                fetched_at=now_iso(),
            )

        owner, repo = self.parse_repo_url(repo_url)
        base = f"https://api.github.com/repos/{owner}/{repo}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        prs: list[dict] = []
        commits_by_week: dict[str, int] = {}
        contributors: list[dict] = []
        issues: list[dict] = []

        async with httpx.AsyncClient(timeout=20.0) as client:
            try:
                resp = await client.get(
                    f"{base}/pulls",
                    headers=headers,
                    params={"state": "all", "sort": "updated", "direction": "desc", "per_page": 10},
                )
                resp.raise_for_status()
                for pr in resp.json():
                    files_changed = 0
                    number = pr.get("number")
                    if number is not None:
                        try:
                            f_resp = await client.get(f"{base}/pulls/{number}/files", headers=headers)
                            if f_resp.status_code == 200:
                                files_changed = len(f_resp.json())
                        except Exception:
                            files_changed = 0
                    prs.append(
                        {
                            "title": pr.get("title", ""),
                            "author": (pr.get("user") or {}).get("login", ""),
                            "merged_at": pr.get("merged_at"),
                            "files_changed": files_changed,
                        }
                    )
            except Exception:
                prs = []

            try:
                since = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
                c_resp = await client.get(
                    f"{base}/commits",
                    headers=headers,
                    params={"since": since, "per_page": 100},
                )
                c_resp.raise_for_status()
                counter: Counter[str] = Counter()
                for c in c_resp.json():
                    date_str = (((c.get("commit") or {}).get("author") or {}).get("date"))
                    if not date_str:
                        continue
                    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    week_key = f"{dt.isocalendar().year}-W{dt.isocalendar().week:02d}"
                    counter[week_key] += 1
                commits_by_week = dict(counter)
            except Exception:
                commits_by_week = {}

            try:
                t_resp = await client.get(f"{base}/contributors", headers=headers, params={"per_page": 5})
                t_resp.raise_for_status()
                contributors = [
                    {
                        "login": c.get("login", ""),
                        "commits": c.get("contributions", 0),
                    }
                    for c in t_resp.json()[:5]
                ]
            except Exception:
                contributors = []

            try:
                by_label: dict[int, dict] = {}
                for label in ["tech-debt", "architecture"]:
                    i_resp = await client.get(
                        f"{base}/issues",
                        headers=headers,
                        params={"state": "open", "labels": label, "per_page": 20},
                    )
                    if i_resp.status_code != 200:
                        continue
                    for item in i_resp.json():
                        if "pull_request" in item:
                            continue
                        by_label[item.get("number", 0)] = {
                            "number": item.get("number"),
                            "title": item.get("title", ""),
                            "labels": [l.get("name") for l in item.get("labels", []) if isinstance(l, dict)],
                        }
                issues = [v for _, v in sorted(by_label.items(), key=lambda kv: kv[0], reverse=True)]
            except Exception:
                issues = []

        summary = (
            f"Fetched GitHub context for {owner}/{repo}. "
            f"Found {len(prs)} recent PRs, {len(commits_by_week)} weekly commit buckets, "
            f"{len(contributors)} top contributors, and {len(issues)} open tech-debt/architecture issues."
        )
        return ConnectorContext(
            source=self.name,
            summary=summary,
            raw_data={
                "prs": prs,
                "commits": commits_by_week,
                "contributors": contributors,
                "issues": issues,
            },
            fetched_at=now_iso(),
        )
