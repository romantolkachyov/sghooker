from pathlib import Path
from typing import Any, AsyncGenerator

import pytest
from anyio import open_file
from asgiref.typing import LifespanShutdownEvent, LifespanStartupEvent
from httpx import AsyncClient

from pulya.testing import TestClient
from sghooker.main import app

MOCKS_DIR = Path(__file__).parent / "mocks"


async def _startup_event_receive() -> LifespanStartupEvent:
    return {"type": "lifespan.startup"}


async def _shutdown_event_receive() -> LifespanShutdownEvent:
    return {"type": "lifespan.shutdown"}


async def _fake_send(event: Any) -> None:
    pass


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, Any]:
    async with TestClient(app=app) as client:
        await app(
            {
                "type": "lifespan",
                "asgi": {"spec_version": "3.0", "version": "3.0"},
                "state": {},
            },
            _startup_event_receive,
            _fake_send,
        )
        yield client
        await app(
            {
                "type": "lifespan",
                "asgi": {"spec_version": "3.0", "version": "3.0"},
                "state": {},
            },
            _shutdown_event_receive,
            _fake_send,
        )


async def test_example(client: TestClient) -> None:
    r = await client.get("/")
    assert r.status_code == 200
    assert r.text == '{"app":"sghooker"}'


async def test_issue_alert_webhook(client: TestClient) -> None:
    async with await open_file(MOCKS_DIR / "alert_triggered.json") as fp:
        data = await fp.read()
    r = await client.post("/inbox/sentry/my-project", content=data)
    assert r.status_code == 200
