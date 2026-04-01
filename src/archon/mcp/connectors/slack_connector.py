from __future__ import annotations

import os

from .base import MCPConnector, ConnectorContext, now_iso


class SlackConnector(MCPConnector):
    name = "slack"

    def __init__(self) -> None:
        self._token = os.getenv("SLACK_BOT_TOKEN", "")

    async def fetch(self, **kwargs) -> ConnectorContext:
        return ConnectorContext(
            source=self.name,
            summary="Slack connector is outbound only in Phase 9.",
            raw_data={},
            fetched_at=now_iso(),
        )

    async def post_hitl_checkpoint(
        self,
        channel: str,
        review_id: str,
        checkpoint_type: str,
        message: str,
    ) -> dict:
        from slack_sdk import WebClient

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*ARCHON Checkpoint: {checkpoint_type}*\n{message}",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Approve"},
                        "style": "primary",
                        "value": f"approve_{review_id}",
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Veto"},
                        "style": "danger",
                        "value": f"veto_{review_id}",
                    },
                ],
            },
        ]

        client = WebClient(token=self._token)
        resp = client.chat_postMessage(
            channel=channel,
            text=f"ARCHON checkpoint {checkpoint_type}",
            blocks=blocks,
        )
        return dict(resp.data) if hasattr(resp, "data") else {"ok": True}

    async def post_health_digest(
        self,
        channel: str,
        repo_url: str,
        score: float,
        domain_scores: dict,
    ) -> dict:
        from slack_sdk import WebClient

        domain_line = ", ".join(f"{k}: {v}" for k, v in sorted(domain_scores.items()))
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*ARCHON Weekly Health Digest*\n"
                        f"Repo: `{repo_url}`\n"
                        f"Overall: *{score}*\n"
                        f"Domains: {domain_line}"
                    ),
                },
            }
        ]

        client = WebClient(token=self._token)
        resp = client.chat_postMessage(
            channel=channel,
            text=f"ARCHON health digest for {repo_url}",
            blocks=blocks,
        )
        return dict(resp.data) if hasattr(resp, "data") else {"ok": True}
