"""Tests for RAG chunker."""
from __future__ import annotations
import pytest
from archon.rag.chunker import chunk_files
from archon.core.ports.repo_port import RepoFile


class TestChunkFiles:
    def test_single_file_single_chunk(self):
        files = [RepoFile(path="small.py", content="line1\nline2", size_bytes=10)]
        chunks = chunk_files(files)
        assert len(chunks) >= 1
        assert chunks[0].file_path == "small.py"
        assert "line1" in chunks[0].content

    def test_empty_file_list(self):
        chunks = chunk_files([])
        assert chunks == []

    def test_empty_content_file(self):
        files = [RepoFile(path="empty.py", content="", size_bytes=0)]
        chunks = chunk_files(files)
        assert chunks == []

    def test_multiple_files(self):
        files = [
            RepoFile(path="a.py", content="import os", size_bytes=10),
            RepoFile(path="b.py", content="import sys", size_bytes=10),
        ]
        chunks = chunk_files(files)
        paths = {c.file_path for c in chunks}
        assert "a.py" in paths
        assert "b.py" in paths

    def test_large_file_produces_multiple_chunks(self):
        content = "\n".join(f"line {i}" for i in range(1000))
        files = [RepoFile(path="big.py", content=content, size_bytes=len(content))]
        chunks = chunk_files(files)
        assert len(chunks) > 1

    def test_chunk_has_metadata(self):
        files = [RepoFile(path="test.py", content="a\nb\nc", size_bytes=5)]
        chunks = chunk_files(files)
        assert "start_line" in chunks[0].metadata
        assert "end_line" in chunks[0].metadata

    def test_chunk_ids_unique(self):
        content = "\n".join(f"line {i}" for i in range(100))
        files = [RepoFile(path="x.py", content=content, size_bytes=len(content))]
        chunks = chunk_files(files)
        ids = [c.id for c in chunks]
        assert len(ids) == len(set(ids))
