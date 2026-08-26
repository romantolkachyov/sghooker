"""Error event schema models for Sentry webhook payloads."""

import msgspec

from sghooker.schemas.alert_event import Breadcrumbs, Contexts, EventException, Extra


class ErrorData(msgspec.Struct):
    """Data about a Sentry error event."""

    title: str
    culprit: str
    web_url: str
    level: str
    tags: list[tuple[str, str]] = []
    url: str | None = None
    issue_url: str | None = None
    issue_id: str | None = None
    message: str | None = None
    platform: str | None = None
    release: str | None = None
    environment: str | None = None
    exception: EventException | None = None
    contexts: Contexts | None = None
    breadcrumbs: Breadcrumbs | None = None
    extra: Extra | None = None
    timestamp: float | None = None
    datetime: str | None = None
    event_id: str | None = None


class ErrorWebhookData(msgspec.Struct):
    """Data payload for an error webhook."""

    error: ErrorData


class ErrorCreatedWebhookBody(msgspec.Struct):
    """Sentry error.created webhook body.

    https://docs.sentry.io/integrations/integration-platform/webhooks/errors/
    """

    data: ErrorWebhookData
