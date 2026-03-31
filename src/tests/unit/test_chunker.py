from __future__ import annotations
from pathlib import Path
import pytest
from archon.rag.chunker import Chunker


def test_chunker_splits_large_file(tmp_path: Path):
    big_file = tmp_path / "big.py"
    big_file.write_text("\n".join([f"line_{i} = {i}" for i in range(500)]))
    chunker = Chunker(chunk_size=100, overlap=10)
    chunks = chunker.chunk_file(big_file)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.content) > 0
        assert chunk.file_path == str(big_file)


def test_chunker_skips_binary_files(tmp_path: Path):
    binary_file = tmp_path / "image.png"
    binary_file.write_bytes(b"\x89PNG\r\n\x1a\n")
    chunker = Chunker()
    chunks = chunker.chunk_file(binary_file)
    assert chunks == []


def test_chunker_handles_empty_file(tmp_path: Path):
    empty = tmp_path / "empty.py"
    empty.write_text("")
    chunker = Chunker()
    chunks = chunker.chunk_file(empty)
    assert chunks == []
