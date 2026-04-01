from __future__ import annotations
import re
import sqlparse
from sqlparse.sql import Statement
from .base import InputParser, ParsedInput


def _extract_table_name(stmt: Statement) -> str | None:
    tokens = [t for t in stmt.flatten() if not t.is_whitespace]
    for i, tok in enumerate(tokens):
        if tok.ttype is sqlparse.tokens.Keyword and tok.normalized.upper() == "TABLE":
            for j in range(i + 1, len(tokens)):
                if tokens[j].ttype not in (sqlparse.tokens.Keyword, sqlparse.tokens.DDL):
                    name = tokens[j].value.strip("`\"[]")
                    if name:
                        return name
    return None


def _extract_columns_and_fks(sql_text: str) -> tuple[list[str], list[str]]:
    columns: list[str] = []
    fks: list[str] = []
    # Find content inside CREATE TABLE parens
    match = re.search(r"CREATE\s+TABLE[^(]*\((.*)\)", sql_text, re.IGNORECASE | re.DOTALL)
    if not match:
        return columns, fks
    body = match.group(1)
    for line in body.split(","):
        line = line.strip()
        if not line:
            continue
        upper = line.upper()
        if "FOREIGN KEY" in upper:
            ref = re.search(
                r"FOREIGN\s+KEY\s*\(([^)]+)\)\s*REFERENCES\s+([^\s(]+)\s*\(([^)]+)\)",
                line, re.IGNORECASE,
            )
            if ref:
                fks.append(f"{ref.group(1).strip()} -> {ref.group(2).strip()}.{ref.group(3).strip()}")
        elif not any(k in upper for k in ("PRIMARY KEY", "UNIQUE", "CHECK", "INDEX", "CONSTRAINT")):
            # First token is assumed to be column name
            col_name = re.split(r"\s+", line.strip("`\"[]"))[0].strip("`\"[]")
            if col_name:
                columns.append(col_name)
    return columns, fks


class SqlParser(InputParser):
    async def parse(self, source: str | bytes) -> ParsedInput:
        content = source if isinstance(source, str) else source.decode()
        statements = sqlparse.parse(content)

        tables: list[str] = []
        all_fks: list[str] = []

        for stmt in statements:
            if stmt.get_type() != "CREATE":
                continue
            flat = stmt.value.upper()
            if "TABLE" not in flat:
                continue
            table_name = _extract_table_name(stmt)
            if not table_name:
                continue
            tables.append(table_name)
            _, fks = _extract_columns_and_fks(stmt.value)
            # Prefix FK refs with table name
            for fk in fks:
                src, dst = fk.split(" -> ", 1)
                all_fks.append(f"{table_name}.{src.strip()} -> {dst}")

        relationship_str = (
            "Relationships: " + "; ".join(all_fks) + "."
            if all_fks
            else "No foreign key relationships detected."
        )
        summary = (
            f"Database schema with {len(tables)} tables: "
            + (", ".join(tables) if tables else "none")
            + ". "
            + relationship_str
        )

        return ParsedInput(
            source_type="sql",
            title="Database Schema",
            content=summary,
            metadata={"tables": tables, "relationships": all_fks},
        )
