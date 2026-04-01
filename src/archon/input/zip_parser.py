from __future__ import annotations
import io
import zipfile
from .base import InputParser, ParsedInput
from .combiner import merge_inputs

_SKIP_DIRS = {"__pycache__", ".git", "node_modules", ".venv", "venv"}
_MAX_FILES = 10


def _should_skip(path: str) -> bool:
    parts = path.replace("\\", "/").split("/")
    return any(part in _SKIP_DIRS for part in parts)


class ZipParser(InputParser):
    async def parse(self, source: str | bytes) -> ParsedInput:
        raw = source if isinstance(source, bytes) else source.encode("latin-1")
        parsed_inputs: list[ParsedInput] = []
        parsed_types: list[str] = []

        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            names = [n for n in zf.namelist() if not n.endswith("/") and not _should_skip(n)]
            for name in names[:_MAX_FILES]:
                ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
                try:
                    data = zf.read(name)
                except Exception:
                    continue

                result: ParsedInput | None = None

                if ext in ("tf", "hcl"):
                    from .iac_parser import IaCParser
                    result = await IaCParser().parse(data.decode("utf-8", errors="replace"))
                elif ext in ("yaml", "yml"):
                    text = data.decode("utf-8", errors="replace")
                    if "AWSTemplateFormatVersion" in text:
                        from .iac_parser import IaCParser
                        result = await IaCParser().parse(text)
                    else:
                        from .openapi_parser import OpenApiParser
                        try:
                            result = await OpenApiParser().parse(text)
                        except Exception:
                            pass
                elif ext == "sql":
                    from .sql_parser import SqlParser
                    result = await SqlParser().parse(data.decode("utf-8", errors="replace"))
                elif ext == "pdf":
                    from .pdf_parser import PdfParser
                    result = await PdfParser().parse(data)
                elif ext == "json":
                    text = data.decode("utf-8", errors="replace")
                    from .openapi_parser import OpenApiParser
                    try:
                        result = await OpenApiParser().parse(text)
                    except Exception:
                        pass

                if result:
                    parsed_inputs.append(result)
                    parsed_types.append(result.source_type)

        combined = merge_inputs(parsed_inputs)
        return ParsedInput(
            source_type="zip",
            title="Uploaded Archive",
            content=combined,
            metadata={"file_count": len(parsed_inputs), "parsed_types": parsed_types},
        )
