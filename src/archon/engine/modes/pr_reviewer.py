from __future__ import annotations

from pydantic import BaseModel


class PRReviewInput(BaseModel):
    pr_diff: str
    pr_title: str
    pr_description: str = ""
    repo_url: str = ""


def build_pr_focus(input_data: PRReviewInput) -> str:
    return (
        "Review this PR diff only - not the full codebase. Complete in under 2 minutes. "
        "Categorise every finding as BLOCKER (must fix before merge), WARNING (should fix), "
        "or SUGGESTION (optional). For each finding include: file path + line number from the "
        "diff, specific code reference, one-sentence fix.\n\n"
        f"Repo: {input_data.repo_url or 'unknown'}\n"
        f"PR title: {input_data.pr_title}\n"
        f"PR description: {input_data.pr_description or 'n/a'}\n\n"
        f"Diff:\n{input_data.pr_diff}"
    )
