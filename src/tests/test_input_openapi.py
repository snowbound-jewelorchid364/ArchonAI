from __future__ import annotations
import json
import pytest

_OPENAPI_JSON = json.dumps({
    "openapi": "3.0.0",
    "info": {"title": "ARCHON API", "version": "1.0.0"},
    "paths": {
        "/reviews": {
            "get": {"summary": "List reviews"},
            "post": {"summary": "Create review"},
        },
        "/reviews/{id}": {
            "get": {"summary": "Get review"},
        },
    },
    "components": {
        "securitySchemes": {
            "BearerAuth": {"type": "http", "scheme": "bearer"},
            "ApiKey": {"type": "apiKey", "in": "header", "name": "X-API-Key"},
        }
    },
})

_OPENAPI_YAML = """
openapi: "3.0.0"
info:
  title: Widget Service
  version: "2.1"
paths:
  /widgets:
    get:
      summary: List widgets
    post:
      summary: Create widget
"""


@pytest.mark.asyncio
async def test_openapi_parser_json():
    from archon.input.openapi_parser import OpenApiParser
    parsed = await OpenApiParser().parse(_OPENAPI_JSON)
    assert parsed.metadata["endpoint_count"] > 0


@pytest.mark.asyncio
async def test_openapi_parser_yaml():
    from archon.input.openapi_parser import OpenApiParser
    parsed = await OpenApiParser().parse(_OPENAPI_YAML)
    assert parsed.title == "Widget Service"


@pytest.mark.asyncio
async def test_openapi_parser_auth_detection():
    from archon.input.openapi_parser import OpenApiParser
    parsed = await OpenApiParser().parse(_OPENAPI_JSON)
    assert "BearerAuth" in parsed.metadata["auth_type"]
    assert "ApiKey" in parsed.metadata["auth_type"]
