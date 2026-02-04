"""Example integration tests."""

from collections.abc import AsyncGenerator
from http import HTTPStatus
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from anyio import open_file
from asgiref.typing import LifespanShutdownEvent, LifespanStartupEvent
from httpx import AsyncClient
from pulya.testing import TestClient

from sghooker.main import app

MOCKS_DIR = Path(__file__).parent / "mocks"


async def _startup_event_receive() -> LifespanStartupEvent:
    """Return a startup event for lifespan testing."""
    return {"type": "lifespan.startup"}


async def _shutdown_event_receive() -> LifespanShutdownEvent:
    """Return a shutdown event for lifespan testing."""
    return {"type": "lifespan.shutdown"}


async def _fake_send(_event: dict[str, Any]) -> None:
    """Fake send function for testing."""


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, Any]:
    """Create a test client fixture."""
    async with TestClient(app=app) as client:
        yield client


async def test_example(client: TestClient) -> None:
    """Test basic app endpoint."""
    r = await client.get("/")
    if r.status_code != HTTPStatus.OK:
        error_msg = f"Expected status {HTTPStatus.OK}, got {r.status_code}"
        raise AssertionError(error_msg)
    if r.text != '{"app":"sghooker"}':
        error_msg = f"Unexpected response: {r.text}"
        raise AssertionError(error_msg)


@patch("sghooker.main.send_message", AsyncMock(status_code=200))
async def test_alert_event_webhook(client: TestClient) -> None:
    """Test alert event webhook endpoint."""
    async with await open_file(MOCKS_DIR / "alert_triggered.json") as fp:
        data = await fp.read()
    r = await client.post("/inbox/sentry/", content=data)
    if r.status_code != HTTPStatus.OK:
        error_msg = f"Expected status {HTTPStatus.OK}, got {r.status_code}"
        raise AssertionError(error_msg)
