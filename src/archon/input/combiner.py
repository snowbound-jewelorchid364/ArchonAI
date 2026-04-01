from __future__ import annotations
from .base import ParsedInput


def merge_inputs(inputs: list[ParsedInput]) -> str:
    if not inputs:
        return ""
    sections = []
    for inp in inputs:
        header = "## Input: " + inp.title + " (type: " + inp.source_type + ")"
        sections.append(header + "\n\n" + inp.content)
    return "\n\n---\n\n".join(sections)
