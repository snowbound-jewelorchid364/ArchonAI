from __future__ import annotations
from abc import ABC, abstractmethod
from pydantic import BaseModel


class DocumentChunk(BaseModel):
    id: str
    content: str
    file_path: str
    metadata: dict = {}


class VectorStorePort(ABC):
    @abstractmethod
    async def index(self, chunks: list[DocumentChunk]) -> None: ...

    @abstractmethod
    async def query(self, query: str, top_k: int = 5) -> list[DocumentChunk]: ...

    @abstractmethod
    async def clear(self) -> None: ...
