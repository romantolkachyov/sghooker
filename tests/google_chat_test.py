from typing import Any

import pytest
from pytest_httpserver import HTTPServer

from sghooker import google_chat


@pytest.fixture
def mock_webhook_url(httpserver: HTTPServer) -> str:
    httpserver.expect_request("/webhook").respond_with_json(
        {"success": True}, status=200
    )
    return httpserver.url_for("/webhook")  # type: ignore[no-any-return]


async def test_send_message_success(
    mock_webhook_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(google_chat, "WEBHOOK_URL", mock_webhook_url)
    message_data = {"text": "test message"}

    await google_chat.send_message(message_data)


async def test_send_message_non_200_response(
    httpserver: HTTPServer,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    httpserver.expect_request("/webhook").respond_with_json(
        {"error": "Bad request"}, status=400
    )
    monkeypatch.setattr(google_chat, "WEBHOOK_URL", httpserver.url_for("/webhook"))

    message_data = {"text": "test message"}

    with caplog.at_level("ERROR"):
        await google_chat.send_message(message_data)

    assert len(caplog.records) == 1
    assert "Failed to send message to google chat" in caplog.records[0].message


async def test_send_message_no_webhook_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(google_chat, "WEBHOOK_URL", None)

    message_data: dict[str, Any] = {"text": "test message"}

    with pytest.raises(RuntimeError, match="WEBHOOK_URL not set"):
        await google_chat.send_message(message_data)


async def test_send_message_with_complex_data(
    httpserver: HTTPServer, monkeypatch: pytest.MonkeyPatch
) -> None:
    expected_data = {
        "cards_v2": [
            {
                "cardId": "test-card",
                "card": {
                    "header": {"title": "Test Title"},
                    "sections": [{"widgets": [{"textParagraph": {"text": "Test"}}]}],
                },
            }
        ]
    }

    httpserver.expect_request("/webhook").respond_with_json(
        {"success": True}, status=200
    )
    monkeypatch.setattr(google_chat, "WEBHOOK_URL", httpserver.url_for("/webhook"))

    await google_chat.send_message(expected_data)
