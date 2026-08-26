"""Tests for webhook payload decoding."""

from pathlib import Path

import msgspec
import pytest

from sghooker.schemas.alert_event import AlertEventWebhookBody
from sghooker.schemas.error_event import ErrorCreatedWebhookBody
from sghooker.schemas.issue_event import IssueCreatedWebhookBody
from sghooker.webhook_decode import decode_webhook_body

MOCKS_DIR = Path(__file__).parent / "mocks"


def test_decode_error_created() -> None:
    """error.created must not be parsed as issue.created."""
    content = (MOCKS_DIR / "error_created.json").read_bytes()
    body = decode_webhook_body(content, sentry_resource="error")
    assert isinstance(body, ErrorCreatedWebhookBody)


def test_decode_issue_created() -> None:
    """issue.created stays distinct from error.created."""
    content = (MOCKS_DIR / "issue_created.json").read_bytes()
    body = decode_webhook_body(content, sentry_resource="issue")
    assert isinstance(body, IssueCreatedWebhookBody)


def test_decode_alert_triggered() -> None:
    """Issue alert triggered payload is routed to alert schema."""
    content = (MOCKS_DIR / "alert_triggered.json").read_bytes()
    body = decode_webhook_body(content, sentry_resource="event_alert")
    assert isinstance(body, AlertEventWebhookBody)


def test_decode_invalid_payload_returns_validation_error() -> None:
    """Unknown payloads raise ValidationError for the handler to skip."""
    with pytest.raises(msgspec.ValidationError):
        decode_webhook_body(b"{}", sentry_resource=None)
