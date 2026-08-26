"""Decode Sentry webhook payloads into typed bodies."""

from typing import Any

import msgspec

from sghooker.schemas.alert_event import AlertEventWebhookBody
from sghooker.schemas.error_event import ErrorCreatedWebhookBody
from sghooker.schemas.issue_event import (
    IssueCreatedWebhookBody,
    IssueResolvedWebhookBody,
    IssueUnresolvedWebhookBody,
)

WebhookBody = (
    AlertEventWebhookBody
    | ErrorCreatedWebhookBody
    | IssueCreatedWebhookBody
    | IssueResolvedWebhookBody
    | IssueUnresolvedWebhookBody
)


def decode_webhook_body(content: bytes, sentry_resource: str | None = None) -> WebhookBody:
    """Parse raw JSON into the matching Sentry webhook schema.

    ``error.created`` and ``issue.created`` both use ``action=created``; routing
    uses ``Sentry-Hook-Resource`` and ``data.error`` / ``data.issue`` keys.
    """
    raw: Any = msgspec.json.decode(content)
    if not isinstance(raw, dict):
        msg = "Webhook body must be a JSON object"
        raise msgspec.ValidationError(msg)

    action = raw.get("action")
    data = raw.get("data")
    if not isinstance(data, dict):
        msg = "Webhook body must contain a data object"
        raise msgspec.ValidationError(msg)

    if action == "triggered":
        return msgspec.convert(raw, AlertEventWebhookBody)

    if sentry_resource == "error" or "error" in data:
        return msgspec.convert(raw, ErrorCreatedWebhookBody)

    if action == "resolved":
        return msgspec.convert(raw, IssueResolvedWebhookBody)
    if action == "unresolved":
        return msgspec.convert(raw, IssueUnresolvedWebhookBody)

    if "issue" in data:
        return msgspec.convert(raw, IssueCreatedWebhookBody)

    msg = f"Unsupported webhook payload: action={action!r}, resource={sentry_resource!r}"
    raise msgspec.ValidationError(msg)
