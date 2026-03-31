from __future__ import annotations
from pydantic import BaseModel


class PackageMetadata(BaseModel):
    review_id: str
    repo_url: str
    mode: str
    finding_count: int
    file_count: int
    size_bytes: int
    download_url: str
