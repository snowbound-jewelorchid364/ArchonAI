"""Tests for PgVectorStore SQL correctness.

Validates SQL uses $N placeholders (asyncpg), table names are validated,
and abstract methods are implemented.
"""
import re
import pytest
from archon.infrastructure.vector_store.pgvector_store import PgVectorStore, _validate_table


# ---- Table Name Validation ----

def test_validate_table_valid():
    assert _validate_table("archon_embeddings") == "archon_embeddings"
    assert _validate_table("my_table_123") == "my_table_123"


def test_validate_table_rejects_injection():
    with pytest.raises(ValueError):
        _validate_table("table; DROP TABLE users")
    with pytest.raises(ValueError):
        _validate_table("")
    with pytest.raises(ValueError):
        _validate_table("123_starts_with_number")


# ---- SQL Template Correctness ----

def test_add_documents_sql_has_numbered_placeholders():
    """Verify the INSERT SQL uses $1-$5 asyncpg placeholders, not %s or ?."""
    import inspect
    source = inspect.getsource(PgVectorStore.add_documents)
    # Must contain $1 through $5
    for i in range(1, 6):
        assert f"${i}" in source, f"Missing ${i} in add_documents SQL"
    # Must NOT contain %s or ? placeholders
    assert "%s" not in source
    assert "VALUES(?" not in source


def test_query_sql_has_numbered_placeholders():
    source = __import__("inspect").getsource(PgVectorStore.query)
    for i in range(1, 4):
        assert f"${i}" in source, f"Missing ${i} in query SQL"
    assert "%s" not in source


def test_delete_collection_sql_has_placeholder():
    source = __import__("inspect").getsource(PgVectorStore.delete_collection)
    assert "$1" in source


def test_count_sql_has_placeholder():
    source = __import__("inspect").getsource(PgVectorStore.count)
    assert "$1" in source


# ---- Abstract Methods Implemented ----

def test_has_index_method():
    assert hasattr(PgVectorStore, "index")
    assert callable(getattr(PgVectorStore, "index"))


def test_has_clear_method():
    assert hasattr(PgVectorStore, "clear")
    assert callable(getattr(PgVectorStore, "clear"))


def test_instantiation_succeeds():
    """Can instantiate without abstract method errors."""
    store = PgVectorStore("postgres://localhost/test")
    assert store._collection == "archon_embeddings"
