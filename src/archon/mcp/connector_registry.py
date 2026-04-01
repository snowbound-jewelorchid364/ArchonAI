from __future__ import annotations

import logging

from .connectors.base import ConnectorContext
from .connectors.github_connector import GitHubConnector
from .connectors.aws_connector import AWSConnector
from .connectors.slack_connector import SlackConnector

logger = logging.getLogger(__name__)

CONNECTORS = {
    "github": GitHubConnector,
    "aws": AWSConnector,
    "slack": SlackConnector,
}


async def fetch_connector_context(connector_name: str, **kwargs) -> ConnectorContext | None:
    """Fetch context from a named connector. Returns None if connector not found or fetch fails."""
    cls = CONNECTORS.get(connector_name)
    if not cls:
        return None
    try:
        connector = cls()
        return await connector.fetch(**kwargs)
    except Exception as exc:
        logger.warning("connector fetch failed | connector=%s | err=%s", connector_name, exc)
        return None
