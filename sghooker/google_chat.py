import os
from typing import Any

import httpx

WEBHOOK_URL = os.getenv("WEBHOOK_URL")


async def send_message(message_data: dict[str, Any]) -> None:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            WEBHOOK_URL,
            json=message_data,
        )
        print("Status: ", resp.status_code, "\nContent:", resp.content)
