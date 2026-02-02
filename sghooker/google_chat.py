import logging
import os
from http import HTTPStatus
from typing import Any

import httpx

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

logger = logging.getLogger(__name__)


async def send_message(message_data: dict[str, Any]) -> None:
    async with httpx.AsyncClient() as client:
        if WEBHOOK_URL is None:
            raise RuntimeError("WEBHOOK_URL not set")
        resp = await client.post(
            WEBHOOK_URL,
            json=message_data,
        )
        if resp.status_code != HTTPStatus.OK:
            logger.error(
                "Failed to send message to google chat. Response: %s", resp.content
            )
