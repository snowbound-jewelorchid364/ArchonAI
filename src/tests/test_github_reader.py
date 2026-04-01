"""Tests for GitHubReader."""
from __future__ import annotations
import os
import pytest
from pathlib import Path
from archon.infrastructure.github.github_reader import GitHubReader, EXCLUDED_DIRS, TEXT_EXTENSIONS, MAX_FILE_BYTES


class TestGitHubReader:
    def test_excluded_dirs(self):
        assert ".git" in EXCLUDED_DIRS
        assert "node_modules" in EXCLUDED_DIRS
        assert "__pycache__" in EXCLUDED_DIRS

    def test_text_extensions(self):
        assert ".py" in TEXT_EXTENSIONS
        assert ".ts" in TEXT_EXTENSIONS
        assert ".json" in TEXT_EXTENSIONS
        assert ".md" in TEXT_EXTENSIONS

    def test_max_file_bytes(self):
        assert MAX_FILE_BYTES == 200_000

    @pytest.mark.asyncio
    async def test_get_files_from_fixture(self):
        reader = GitHubReader()
        fixture_path = str(Path(__file__).parent / "fixtures" / "sample_repos" / "node_app")
        files = await reader.get_files(fixture_path)
        names = [f.path for f in files]
        assert any("index.js" in n for n in names)

    @pytest.mark.asyncio
    async def test_get_files_python_fixture(self):
        reader = GitHubReader()
        fixture_path = str(Path(__file__).parent / "fixtures" / "sample_repos" / "python_fastapi")
        files = await reader.get_files(fixture_path)
        names = [f.path for f in files]
        assert any("main.py" in n for n in names)

    @pytest.mark.asyncio
    async def test_count_loc(self):
        reader = GitHubReader()
        fixture_path = str(Path(__file__).parent / "fixtures" / "sample_repos" / "python_fastapi")
        loc = await reader.count_loc(fixture_path)
        assert loc > 0

    @pytest.mark.asyncio
    async def test_get_files_excludes_pycache(self, tmp_path):
        (tmp_path / "__pycache__").mkdir()
        (tmp_path / "__pycache__" / "mod.py").write_text("cached")
        (tmp_path / "app.py").write_text("print(1)")
        reader = GitHubReader()
        files = await reader.get_files(str(tmp_path))
        paths = [f.path for f in files]
        assert not any("__pycache__" in p for p in paths)
        assert any("app.py" in p for p in paths)

    @pytest.mark.asyncio
    async def test_cleanup(self, tmp_path):
        test_dir = tmp_path / "archon-test"
        test_dir.mkdir()
        (test_dir / "file.txt").write_text("test")
        reader = GitHubReader()
        await reader.cleanup(str(test_dir))
        assert not test_dir.exists()