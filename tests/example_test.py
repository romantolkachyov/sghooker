"""Example integration tests."""

from collections.abc import AsyncGenerator
from http import HTTPStatus
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

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
    assert r.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK}, got {r.status_code}"
    assert r.text == '{"app":"sghooker"}', f"Unexpected response: {r.text}"


@patch("sghooker.main.send_message", AsyncMock(status_code=200))
async def test_error_created_webhook(client: TestClient) -> None:
    """Test error.created webhook endpoint."""
    async with await open_file(MOCKS_DIR / "error_created.json") as fp:
        data = await fp.read()
    r = await client.post(
        "/inbox/sentry/",
        content=data,
        headers={"Sentry-Hook-Resource": "error"},
    )
    assert r.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK}, got {r.status_code}"
    assert r.json() == {"success": True}


@patch("sghooker.main.send_message", AsyncMock(status_code=200))
async def test_issue_created_webhook(client: TestClient) -> None:
    """Test issue.created webhook endpoint."""
    async with await open_file(MOCKS_DIR / "issue_created.json") as fp:
        data = await fp.read()
    r = await client.post(
        "/inbox/sentry/",
        content=data,
        headers={"Sentry-Hook-Resource": "issue"},
    )
    assert r.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK}, got {r.status_code}"


@patch("sghooker.main.send_message", AsyncMock(status_code=200))
@patch("sghooker.main.DEBUG_WEBHOOK_BODY", new=True)
@patch("sghooker.main.logger")
async def test_debug_webhook_body_logging(
    mock_logger: MagicMock,
    client: TestClient,
) -> None:
    """SGHOOKER_DEBUG_WEBHOOK_BODY logs the raw request body."""
    payload = b'{"action":"created","data":{"error":{"title":"x"}}}'
    r = await client.post(
        "/inbox/sentry/",
        content=payload,
        headers={"Sentry-Hook-Resource": "error"},
    )
    assert r.status_code == HTTPStatus.OK
    mock_logger.info.assert_called_once()
    assert mock_logger.info.call_args.args[0] == "Webhook request body (resource=%s, bytes=%d): %s"
    assert mock_logger.info.call_args.args[1] == "error"
    assert payload.decode() in mock_logger.info.call_args.args[3]


@patch("sghooker.main.send_message", AsyncMock(status_code=200))
async def test_alert_event_webhook(client: TestClient) -> None:
    """Test alert event webhook endpoint."""
    async with await open_file(MOCKS_DIR / "alert_triggered.json") as fp:
        data = await fp.read()
    r = await client.post("/inbox/sentry/", content=data)
    assert r.status_code == HTTPStatus.OK, f"Expected status {HTTPStatus.OK}, got {r.status_code}"
