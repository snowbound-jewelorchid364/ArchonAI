from __future__ import annotations
import io
import pytest
import fitz


def _make_pdf_bytes(text: str = "Hello architecture world") -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


@pytest.mark.asyncio
async def test_pdf_parser_extracts_text():
    from archon.input.pdf_parser import PdfParser
    pdf_bytes = _make_pdf_bytes("Architecture review content")
    parsed = await PdfParser().parse(pdf_bytes)
    assert "Architecture" in parsed.content or len(parsed.content) > 0


@pytest.mark.asyncio
async def test_pdf_parser_returns_correct_source_type():
    from archon.input.pdf_parser import PdfParser
    parsed = await PdfParser().parse(_make_pdf_bytes())
    assert parsed.source_type == "pdf"


@pytest.mark.asyncio
async def test_pdf_parser_metadata_has_pages():
    from archon.input.pdf_parser import PdfParser
    parsed = await PdfParser().parse(_make_pdf_bytes())
    assert "pages" in parsed.metadata
    assert parsed.metadata["pages"] >= 1
