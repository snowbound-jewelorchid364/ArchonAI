import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from archon.infrastructure.llm.claude_adapter import ClaudeAdapter
from archon.infrastructure.search.tavily_adapter import TavilyAdapter
from archon.infrastructure.search.exa_adapter import ExaAdapter
from archon.infrastructure.vector_store.in_memory_store import InMemoryVectorStore


class TestClaudeAdapter:
    def test_init_default(self):
        with patch("archon.infrastructure.llm.claude_adapter.settings") as mock_settings:
            mock_settings.anthropic_api_key = "test-key"
            mock_settings.agent_model = "claude-opus-4-5"
            adapter = ClaudeAdapter()
            assert adapter._model == "claude-opus-4-5"

    def test_init_custom_model(self):
        with patch("archon.infrastructure.llm.claude_adapter.settings") as mock_settings:
            mock_settings.anthropic_api_key = "test-key"
            mock_settings.agent_model = "claude-opus-4-5"
            adapter = ClaudeAdapter(model="claude-haiku-4-5")
            assert adapter._model == "claude-haiku-4-5"

    @pytest.mark.asyncio
    async def test_complete_calls_anthropic(self):
        with patch("archon.infrastructure.llm.claude_adapter.settings") as mock_settings:
            mock_settings.anthropic_api_key = "test-key"
            mock_settings.agent_model = "claude-opus-4-5"
            mock_settings.thinking_budget_default = "medium"
            adapter = ClaudeAdapter()
            mock_message = MagicMock()
            mock_message.content = [MagicMock(type="text", text="test response")]
            adapter._client = MagicMock()
            adapter._client.messages.create = AsyncMock(return_value=mock_message)
            result = await adapter.complete("system", "user")
            assert result == "test response"


class TestTavilyAdapter:
    def test_init(self):
        adapter = TavilyAdapter()
        assert hasattr(adapter, "search")

    @pytest.mark.asyncio
    async def test_search_is_async(self):
        adapter = TavilyAdapter()
        import inspect
        assert inspect.iscoroutinefunction(adapter.search)


class TestExaAdapter:
    def test_init(self):
        adapter = ExaAdapter()
        assert hasattr(adapter, "search")

    @pytest.mark.asyncio
    async def test_search_is_async(self):
        adapter = ExaAdapter()
        import inspect
        assert inspect.iscoroutinefunction(adapter.search)


class TestInMemoryVectorStore:
    def test_init(self):
        store = InMemoryVectorStore()
        assert store._chunks == []

    @pytest.mark.asyncio
    async def test_query_empty_returns_empty(self):
        store = InMemoryVectorStore()
        result = await store.query("test query")
        assert result == []

    def test_has_index_method(self):
        store = InMemoryVectorStore()
        import inspect
        assert inspect.iscoroutinefunction(store.index)

    def test_has_clear_method(self):
        store = InMemoryVectorStore()
        assert hasattr(store, "clear")
