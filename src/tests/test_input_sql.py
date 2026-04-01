from __future__ import annotations
import pytest

_SQL_SCHEMA = """
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE
);

CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT,
    total DECIMAL(10,2),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""


@pytest.mark.asyncio
async def test_sql_parser_extracts_tables():
    from archon.input.sql_parser import SqlParser
    parsed = await SqlParser().parse(_SQL_SCHEMA)
    assert "users" in parsed.metadata["tables"]
    assert "orders" in parsed.metadata["tables"]


@pytest.mark.asyncio
async def test_sql_parser_detects_foreign_keys():
    from archon.input.sql_parser import SqlParser
    parsed = await SqlParser().parse(_SQL_SCHEMA)
    assert len(parsed.metadata["relationships"]) > 0


@pytest.mark.asyncio
async def test_sql_parser_returns_schema_summary():
    from archon.input.sql_parser import SqlParser
    parsed = await SqlParser().parse(_SQL_SCHEMA)
    assert "tables" in parsed.content.lower()
    assert parsed.source_type == "sql"
