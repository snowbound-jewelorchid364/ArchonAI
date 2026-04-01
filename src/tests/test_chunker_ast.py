from __future__ import annotations

import re

from archon.core.ports.repo_port import RepoFile
from archon.rag.chunker import chunk_files
from archon.config.settings import settings


def test_python_chunks_preserve_top_level_boundaries_with_tuned_window(monkeypatch) -> None:
    monkeypatch.setattr(settings, "rag_chunk_size", 4)
    monkeypatch.setattr(settings, "rag_chunk_overlap", 0)

    py_source = "\n".join([
        "def alpha():",
        "    x = 1",
        "    return x",
        "",
        "def beta():",
        "    y = 2",
        "    return y",
        "",
        "class Worker:",
        "    def run(self):",
        "        return 'ok'",
        "",
    ])

    chunks = chunk_files([RepoFile(path="sample.py", content=py_source, size_bytes=len(py_source))])

    assert len(chunks) >= 3
    chunk_text = [c.content for c in chunks]
    assert any("def alpha" in t for t in chunk_text)
    assert any("def beta" in t for t in chunk_text)
    assert any("class Worker" in t for t in chunk_text)
    for t in chunk_text:
        if "def alpha" in t:
            assert "def beta" not in t
        if "def beta" in t:
            assert "class Worker" not in t


def test_js_ts_chunks_preserve_boundaries_with_tuned_window(monkeypatch) -> None:
    monkeypatch.setattr(settings, "rag_chunk_size", 4)
    monkeypatch.setattr(settings, "rag_chunk_overlap", 0)

    ts_source = "\n".join([
        "function one() {",
        "  const x = 1;",
        "  return x;",
        "}",
        "function two() {",
        "  const y = 2;",
        "  return y;",
        "}",
        "class Service {",
        "  run() {",
        "    return 'ok';",
        "  }",
    ])

    chunks = chunk_files([RepoFile(path="sample.ts", content=ts_source, size_bytes=len(ts_source))])

    assert len(chunks) >= 3
    texts = [c.content for c in chunks]
    assert any("function one" in t for t in texts)
    assert any("function two" in t for t in texts)
    assert any("class Service" in t for t in texts)
    for t in texts:
        if "function one" in t:
            assert "function two" not in t
