"""Utility functions for test fixture."""
from typing import Any

def validate_email(email: str) -> bool:
    return "@" in email and "." in email

def paginate(items: list[Any], page: int = 1, per_page: int = 20) -> dict:
    start = (page - 1) * per_page
    end = start + per_page
    return {"items": items[start:end], "total": len(items), "page": page}
