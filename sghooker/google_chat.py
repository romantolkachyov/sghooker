"""Google Chat webhook client."""

import logging
import os
from http import HTTPStatus
from typing import Any

import httpx

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

logger = logging.getLogger(__name__)


async def send_message(message_data: dict[str, Any]) -> None:
    """Send a message to Google Chat via webhook.

    Args:
        message_data: The message data to send.

    Raises:
        RuntimeError: If the WEBHOOK_URL environment variable is not set.

    """
    async with httpx.AsyncClient() as client:
        if WEBHOOK_URL is None:
            error_msg = "WEBHOOK_URL not set"
            raise RuntimeError(error_msg)
        resp = await client.post(
            WEBHOOK_URL,
            json=message_data,
        )
        if resp.status_code != HTTPStatus.OK:
            logger.error(
                "Failed to send message to google chat. Response: %s",
                resp.content,
            )
