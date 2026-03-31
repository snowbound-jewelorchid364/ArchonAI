from __future__ import annotations
from ..core.ports.vector_store_port import DocumentChunk
from ..core.ports.repo_port import RepoFile
from ..config.settings import settings
import uuid


def chunk_files(files: list[RepoFile]) -> list[DocumentChunk]:
    """Split repo files into overlapping chunks for embedding."""
    chunks: list[DocumentChunk] = []
    size = settings.rag_chunk_size
    overlap = settings.rag_chunk_overlap

    for file in files:
        lines = file.content.splitlines()
        i = 0
        while i < len(lines):
            window = lines[i : i + size]
            content = "\n".join(window).strip()
            if content:
                chunks.append(DocumentChunk(
                    id=str(uuid.uuid4()),
                    content=content,
                    file_path=file.path,
                    metadata={"start_line": i + 1, "end_line": i + len(window)},
                ))
            i += size - overlap
    return chunks
