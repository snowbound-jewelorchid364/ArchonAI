from __future__ import annotations
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


_FAKE_HTML = """
<html>
<head><title>ARCHON Platform</title></head>
<body>
  <nav>Navigation links here</nav>
  <main>
    <h1>Welcome to ARCHON</h1>
    <p>This is the main architecture review platform content.</p>
  </main>
  <footer>Footer content</footer>
</body>
</html>
"""


def _mock_response():
    resp = MagicMock()
    resp.text = _FAKE_HTML
    resp.raise_for_status = MagicMock()
    return resp


@pytest.mark.asyncio
async def test_website_parser_extracts_title():
    from archon.input.website_parser import WebsiteParser
    with patch("httpx.AsyncClient") as mock_client_cls:
        client_instance = AsyncMock()
        client_instance.get = AsyncMock(return_value=_mock_response())
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=client_instance)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        parsed = await WebsiteParser().parse("https://example.com")
    assert "ARCHON Platform" in parsed.title


@pytest.mark.asyncio
async def test_website_parser_removes_nav():
    from archon.input.website_parser import WebsiteParser
    with patch("httpx.AsyncClient") as mock_client_cls:
        client_instance = AsyncMock()
        client_instance.get = AsyncMock(return_value=_mock_response())
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=client_instance)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        parsed = await WebsiteParser().parse("https://example.com")
    assert "Navigation links here" not in parsed.content


@pytest.mark.asyncio
async def test_website_parser_bad_url():
    import httpx
    from archon.input.website_parser import WebsiteParser
    with patch("httpx.AsyncClient") as mock_client_cls:
        client_instance = AsyncMock()
        client_instance.get = AsyncMock(side_effect=httpx.ConnectError("refused"))
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=client_instance)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        with pytest.raises(ValueError, match="Could not fetch"):
            await WebsiteParser().parse("https://bad.invalid")
