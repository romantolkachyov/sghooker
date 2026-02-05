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


class TraceContext(msgspec.Struct):
    """Trace context information."""

    trace_id: str | None = None
    otel_trace_id: str | None = None
    span_id: str | None = None
    status: str | None = None
    type: str | None = None


class Contexts(msgspec.Struct):
    """Event contexts."""

    trace: TraceContext | None = None


class BreadcrumbData(msgspec.Struct):
    """Data within a breadcrumb."""

    otel_trace_id: str | None = msgspec.field(name="otelTraceID", default=None)
    otel_span_id: str | None = msgspec.field(name="otelSpanID", default=None)


class Breadcrumb(msgspec.Struct):
    """A single breadcrumb entry."""

    data: BreadcrumbData | None = None


class Breadcrumbs(msgspec.Struct):
    """Container for breadcrumb values (top-level breadcrumbs field)."""

    values: list[Breadcrumb] | None = None


class MetaBreadcrumbValues(msgspec.Struct):
    """Values within _meta.breadcrumbs (dict structure for metadata)."""


class MetaBreadcrumbs(msgspec.Struct):
    """Container for breadcrumb metadata in _meta field."""

    values: dict[str, MetaBreadcrumbValues] | None = None


class Meta(msgspec.Struct):
    """Event metadata."""

    breadcrumbs: MetaBreadcrumbs | None = None


class Extra(msgspec.Struct):
    """Additional data for the alert event, including OpenTelemetry trace ID."""

    otel_trace_id: str | None = msgspec.field(name="otelTraceID", default=None)


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
    contexts: Contexts | None = None
    breadcrumbs: Breadcrumbs | None = None
    _meta: Meta | None = None
    extra: Extra | None = None
    timestamp: float | None = None  # Unix timestamp with milliseconds
    datetime: str | None = None  # ISO 8601 format like "2019-08-19T21:06:17.677000Z"


class AlertEventData(msgspec.Struct):
    """Data payload for an alert event webhook."""

    event: AlertEvent
    triggered_rule: str


class AlertEventWebhookBody(msgspec.Struct, tag="triggered", tag_field="action"):
    """Sentry issue alert webhook body.

    https://docs.sentry.io/organization/integrations/integration-platform/webhooks/issue-alerts/
    """

    data: AlertEventData
