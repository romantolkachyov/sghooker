"""Alert event schema models for Sentry webhook payloads."""

import msgspec


class FrameInfo(msgspec.Struct):
    """Information about a single frame in a stack trace."""

    abs_path: str
    in_app: bool
    lineno: int
    context_line: str | None = None


class StacktraceInfo(msgspec.Struct):
    """Information about a stack trace."""

    frames: list[FrameInfo]


class ExceptionData(msgspec.Struct):
    """Data about an exception including type, value, and stacktrace."""

    type: str
    value: str
    stacktrace: StacktraceInfo


class EventException(msgspec.Struct):
    """Container for multiple exception values."""

    values: list[ExceptionData]


class AlertEvent(msgspec.Struct):
    """An alert event from Sentry."""

    message: str
    culprit: str
    issue_url: str
    web_url: str
    level: str
    title: str
    tags: list[tuple[str, str]]
    release: str | None = None
    environment: str | None = None
    exception: EventException | None = None


class AlertEventData(msgspec.Struct):
    """Data payload for an alert event webhook."""

    event: AlertEvent
    triggered_rule: str


class AlertEventWebhookBody(msgspec.Struct, tag="triggered", tag_field="action"):
    """Sentry issue alert webhook body.

    https://docs.sentry.io/organization/integrations/integration-platform/webhooks/issue-alerts/
    """

    data: AlertEventData
