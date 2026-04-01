from __future__ import annotations
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field


class ParsedInput(BaseModel):
    source_type: str
    title: str = ""
    content: str
    metadata: dict = Field(default_factory=dict)
    images: list[bytes] = Field(default_factory=list)


class InputParser(ABC):
    @abstractmethod
    async def parse(self, source: str | bytes) -> ParsedInput: ...
