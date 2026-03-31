from __future__ import annotations
import os
import subprocess
import tempfile
from pathlib import Path
from ...core.ports.repo_port import RepoPort, RepoFile, RepoMeta
from ...config.settings import settings

EXCLUDED_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".next"}
TEXT_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".java", ".kt", ".rb", ".rs",
                   ".tf", ".yml", ".yaml", ".json", ".toml", ".md", ".sql", ".sh", ".env.example"}
MAX_FILE_BYTES = 200_000


class GitHubReader(RepoPort):
    async def clone(self, repo_url: str, job_id: str) -> str:
        repo_path = os.path.join(tempfile.gettempdir(), f"archon-agent-{job_id}")
        env = os.environ.copy()
        if settings.github_token:
            url = repo_url.replace("https://", f"https://{settings.github_token}@")
        else:
            url = repo_url
        subprocess.run(
            ["git", "clone", "--depth", "1", url, repo_path],
            check=True, capture_output=True, env=env,
        )
        return repo_path

    async def get_files(self, repo_path: str) -> list[RepoFile]:
        files: list[RepoFile] = []
        for path in Path(repo_path).rglob("*"):
            if any(excluded in path.parts for excluded in EXCLUDED_DIRS):
                continue
            if not path.is_file():
                continue
            if path.suffix not in TEXT_EXTENSIONS:
                continue
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                files.append(RepoFile(
                    path=str(path.relative_to(repo_path)),
                    content=content,
                    size_bytes=path.stat().st_size,
                ))
            except OSError:
                continue
        return files

    async def count_loc(self, repo_path: str) -> int:
        total = 0
        for path in Path(repo_path).rglob("*"):
            if any(excluded in path.parts for excluded in EXCLUDED_DIRS):
                continue
            if path.is_file() and path.suffix in TEXT_EXTENSIONS:
                try:
                    total += sum(1 for _ in path.open(encoding="utf-8", errors="ignore"))
                except OSError:
                    continue
        return total

    async def cleanup(self, repo_path: str) -> None:
        import shutil
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path, ignore_errors=True)
