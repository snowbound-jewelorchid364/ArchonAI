from __future__ import annotations
import fitz  # pymupdf
from .base import InputParser, ParsedInput


class PdfParser(InputParser):
    async def parse(self, source: str | bytes) -> ParsedInput:
        if isinstance(source, str):
            source = source.encode()
        doc = fitz.open(stream=source, filetype="pdf")
        pages_text: list[str] = []
        images: list[bytes] = []

        for page in doc:
            pages_text.append(page.get_text())
            if len(images) < 5:
                for img_info in page.get_images(full=True):
                    xref = img_info[0]
                    base_image = doc.extract_image(xref)
                    images.append(base_image["image"])
                    if len(images) >= 5:
                        break

        full_text = "\n\n---\n\n".join(pages_text)
        meta = {
            "pages": len(doc),
            "title": doc.metadata.get("title", ""),
        }
        title = meta["title"] or "PDF Document"
        return ParsedInput(
            source_type="pdf",
            title=title,
            content=full_text,
            metadata=meta,
            images=images,
        )
