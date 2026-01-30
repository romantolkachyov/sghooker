from pathlib import Path
from typing import Any, AsyncGenerator

import pytest
from anyio import open_file
from httpx import AsyncClient

from pulya.testing import TestClient
from sghooker.main import app

MOCKS_DIR = Path(__file__).parent / "mocks"


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, Any]:
    async with TestClient(app=app) as client:
        yield client


async def test_example(client: TestClient) -> None:
    r = await client.get("/")
    assert r.status_code == 200
    assert r.text == '{"app":"sghooker"}'


async def test_issue_alert_webhook(client: TestClient) -> None:
    async with await open_file(MOCKS_DIR / "alert_triggered.json") as fp:
        data = await fp.read()
    r = await client.post("/inbox/sentry/my-project", content=data)
    assert r.status_code == 200
