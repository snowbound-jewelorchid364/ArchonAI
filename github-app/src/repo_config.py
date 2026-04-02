from __future__ import annotations

import ast
import base64
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RepoConfig:
    review_branches: list[str] = field(default_factory=lambda: ["main"])
    ignore_patterns: list[str] = field(default_factory=list)
    max_files: int = 100


def parse_repo_config(content: str) -> RepoConfig:
    data: dict[str, Any] = {}
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not value:
            continue
        if key in {"review_branches", "ignore_patterns"}:
            try:
                parsed = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                parsed = []
            if isinstance(parsed, list):
                data[key] = [str(item) for item in parsed]
        elif key == "max_files":
            try:
                data[key] = int(value)
            except ValueError:
                pass

    return RepoConfig(
        review_branches=data.get("review_branches", ["main"]),
        ignore_patterns=data.get("ignore_patterns", []),
        max_files=max(1, data.get("max_files", 100)),
    )


def decode_github_content(payload: dict[str, Any]) -> str:
    encoded = payload.get("content", "")
    if not encoded:
        return ""
    return base64.b64decode(encoded).decode("utf-8")
