from __future__ import annotations
import base64
import anthropic
from .base import InputParser, ParsedInput
from ..config.settings import settings

_VISION_PROMPT = (
    "You are an architecture advisor. Describe the architecture shown in this image in detail. "
    "List: (1) all visible components and services, (2) connections and data flows between them, "
    "(3) technology choices visible, (4) any cloud provider resources identified, "
    "(5) any potential architecture concerns you can see."
)


class ImageParser(InputParser):
    async def parse(self, source: str | bytes) -> ParsedInput:
        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

        if isinstance(source, bytes):
            b64 = base64.b64encode(source).decode("ascii")
            image_content = {
                "type": "image",
                "source": {"type": "base64", "media_type": "image/png", "data": b64},
            }
        else:
            image_content = {
                "type": "image",
                "source": {"type": "url", "url": source},
            }

        message = await client.messages.create(
            model=settings.agent_model,
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": [image_content, {"type": "text", "text": _VISION_PROMPT}],
                }
            ],
        )
        response_text = message.content[0].text
        return ParsedInput(
            source_type="image",
            title="Architecture Diagram",
            content=response_text,
        )
