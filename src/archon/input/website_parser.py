from __future__ import annotations
import re
import httpx
from bs4 import BeautifulSoup
from .base import InputParser, ParsedInput


_REMOVE_TAGS = ["script", "style", "nav", "footer", "header", "aside"]
_REMOVE_CLASS_PATTERNS = ["cookie", "banner", "ad-"]


class WebsiteParser(InputParser):
    async def parse(self, source: str | bytes) -> ParsedInput:
        url = source if isinstance(source, str) else source.decode()
        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                html = response.text
        except httpx.RequestError as e:
            raise ValueError(f"Could not fetch {url}: {e}")

        soup = BeautifulSoup(html, "html.parser")

        # Remove noise tags
        for tag in _REMOVE_TAGS:
            for el in soup.find_all(tag):
                el.decompose()

        # Remove elements with noisy class names
        for pattern in _REMOVE_CLASS_PATTERNS:
            for el in soup.find_all(class_=re.compile(pattern, re.I)):
                el.decompose()

        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else url

        # Prefer <main> or <article>, fallback to <body>
        main = soup.find("main") or soup.find("article") or soup.find("body")
        raw_text = main.get_text(separator=" ", strip=True) if main else ""

        # Collapse whitespace and truncate
        cleaned = re.sub(r"\s{2,}", " ", raw_text)[:8000]

        return ParsedInput(
            source_type="website",
            title=title,
            content=cleaned,
            metadata={"url": url, "title": title},
        )
