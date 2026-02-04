"""Tests for Google Chat webhook client."""

from http import HTTPStatus
from typing import Any

import pytest
from pytest_httpserver import HTTPServer

from sghooker import google_chat


@pytest.fixture
def mock_webhook_url(httpserver: HTTPServer) -> str:
    """Create a mock webhook URL for testing."""
    httpserver.expect_request("/webhook").respond_with_json(
        {"success": True},
        status=HTTPStatus.OK,
    )
    return httpserver.url_for("/webhook")  # type: ignore[no-any-return]


async def test_send_message_success(
    mock_webhook_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test successful message sending."""
    monkeypatch.setattr(google_chat, "WEBHOOK_URL", mock_webhook_url)
    message_data = {"text": "test message"}

    await google_chat.send_message(message_data)


async def test_send_message_non_200_response(
    httpserver: HTTPServer,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test handling of non-200 response from webhook."""
    httpserver.expect_request("/webhook").respond_with_json(
        {"error": "Bad request"},
        status=HTTPStatus.BAD_REQUEST,
    )
    monkeypatch.setattr(google_chat, "WEBHOOK_URL", httpserver.url_for("/webhook"))

    message_data = {"text": "test message"}

    with caplog.at_level("ERROR"):
        await google_chat.send_message(message_data)

    if len(caplog.records) != 1:
        error_msg = f"Expected 1 log record, got {len(caplog.records)}"
        raise AssertionError(error_msg)
    if "Failed to send message to google chat" not in caplog.records[0].message:
        error_msg = f"Unexpected log message: {caplog.records[0].message}"
        raise AssertionError(error_msg)


async def test_send_message_no_webhook_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test error handling when webhook URL is not set."""
    monkeypatch.setattr(google_chat, "WEBHOOK_URL", None)

    message_data: dict[str, Any] = {"text": "test message"}

    with pytest.raises(RuntimeError, match="WEBHOOK_URL not set"):
        await google_chat.send_message(message_data)


async def test_send_message_with_complex_data(
    httpserver: HTTPServer,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test sending complex card data to webhook."""
    expected_data = {
        "cards_v2": [
            {
                "cardId": "test-card",
                "card": {
                    "header": {"title": "Test Title"},
                    "sections": [{"widgets": [{"textParagraph": {"text": "Test"}}]}],
                },
            },
        ],
    }

    httpserver.expect_request("/webhook").respond_with_json(
        {"success": True},
        status=HTTPStatus.OK,
    )
    monkeypatch.setattr(google_chat, "WEBHOOK_URL", httpserver.url_for("/webhook"))

    await google_chat.send_message(expected_data)
