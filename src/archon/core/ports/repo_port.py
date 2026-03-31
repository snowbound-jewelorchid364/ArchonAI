from __future__ import annotations
from abc import ABC, abstractmethod
from pydantic import BaseModel


class RepoFile(BaseModel):
    path: str
    content: str
    size_bytes: int


class RepoMeta(BaseModel):
    url: str
    name: str
    default_branch: str
    loc_count: int
    file_count: int


class RepoPort(ABC):
    @abstractmethod
    async def clone(self, repo_url: str, job_id: str) -> str: ...

    @abstractmethod
    async def get_files(self, repo_path: str) -> list[RepoFile]: ...

    @abstractmethod
    async def count_loc(self, repo_path: str) -> int: ...

    @abstractmethod
    async def cleanup(self, repo_path: str) -> None: ...
