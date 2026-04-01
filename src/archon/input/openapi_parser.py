from __future__ import annotations
import json
import yaml
from .base import InputParser, ParsedInput


class OpenApiParser(InputParser):
    async def parse(self, source: str | bytes) -> ParsedInput:
        content = source if isinstance(source, str) else source.decode()

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            data = yaml.safe_load(content)

        info = data.get("info", {})
        title = info.get("title", "OpenAPI Spec")
        version = info.get("version", "unknown")

        paths: dict = data.get("paths", {})
        endpoint_lines: list[str] = []
        for path, methods in paths.items():
            if not isinstance(methods, dict):
                continue
            for method, op in methods.items():
                if method.lower() in {"get", "post", "put", "patch", "delete", "options", "head"}:
                    summary = op.get("summary", "") if isinstance(op, dict) else ""
                    endpoint_lines.append(f"  {method.upper()} {path}" + (f" - {summary}" if summary else ""))

        components = data.get("components", {})
        security_schemes = list(components.get("securitySchemes", {}).keys())

        summary = (
            f"OpenAPI spec: {title} v{version}. "
            f"{len(endpoint_lines)} endpoints across {len(paths)} paths. "
            f"Auth: {', '.join(security_schemes) if security_schemes else 'none'}. "
            f"Endpoints:\n" + "\n".join(endpoint_lines[:50])
        )

        return ParsedInput(
            source_type="openapi",
            title=title,
            content=summary,
            metadata={
                "endpoint_count": len(endpoint_lines),
                "auth_type": security_schemes,
                "title": title,
            },
        )
