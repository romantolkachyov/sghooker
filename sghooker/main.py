"""Main application module with webhook endpoints."""

import logging
from typing import Annotated, Any

import msgspec
from dependency_injector.wiring import Provide, inject
from pulya import Header, Pulya
from pulya.request import Request

from sghooker.chat_messages import (
    build_alert_event_message,
    build_error_created_message,
    build_issue_created_message,
    build_issue_resolved_message,
    build_issue_unresolved_message,
)
from sghooker.containers import Container
from sghooker.google_chat import send_message
from sghooker.schemas.alert_event import AlertEventWebhookBody
from sghooker.schemas.error_event import ErrorCreatedWebhookBody
from sghooker.schemas.issue_event import (
    IssueCreatedWebhookBody,
    IssueResolvedWebhookBody,
    IssueUnresolvedWebhookBody,
)
from sghooker.settings import DEBUG_WEBHOOK_BODY
from sghooker.webhook_decode import decode_webhook_body

app = Pulya(Container)

logger = logging.getLogger("sghooker")

_WEBHOOK_BODY_LOG_LIMIT = 32_768


def _log_webhook_body(content: bytes, sentry_resource: str | None) -> None:
    """Log raw webhook body when SGHOOKER_DEBUG_WEBHOOK_BODY is enabled."""
    body_text = content.decode("utf-8", errors="replace")
    if len(body_text) > _WEBHOOK_BODY_LOG_LIMIT:
        body_text = f"{body_text[:_WEBHOOK_BODY_LOG_LIMIT]}... (truncated, total {len(content)} bytes)"
    logger.info(
        "Webhook request body (resource=%s, bytes=%d): %s",
        sentry_resource,
        len(content),
        body_text,
    )


@app.post("/inbox/sentry/")
@inject
async def receive_webhook(
    raw_request: Annotated[Request, Provide[Container.request.request]],
    sentry_resource: Annotated[str | None, Header("Sentry-Hook-Resource")],
    grafana_url_template: Annotated[
        str | None,
        Provide[Container.grafana_url_template],
    ] = None,
    tracing_url_template: Annotated[
        str | None,
        Provide[Container.tracing_url_template],
    ] = None,
) -> dict[str, Any]:
    """Receive and process Sentry webhooks."""
    content = await raw_request.get_content()
    if DEBUG_WEBHOOK_BODY:
        _log_webhook_body(content, sentry_resource)
    try:
        body = decode_webhook_body(content, sentry_resource)
    except msgspec.ValidationError as exc:
        logger.warning("Skipping invalid webhook payload: %s", exc)
        return {"success": False, "skipped": True}

    if isinstance(body, AlertEventWebhookBody):
        result = build_alert_event_message(
            body,
            grafana_url_template=grafana_url_template,
            tracing_url_template=tracing_url_template,
        )
        await send_message(dict(result.render()))
    elif isinstance(body, ErrorCreatedWebhookBody):
        result = build_error_created_message(
            body,
            grafana_url_template=grafana_url_template,
            tracing_url_template=tracing_url_template,
        )
        await send_message(dict(result.render()))
    elif isinstance(body, IssueCreatedWebhookBody):
        result = build_issue_created_message(body)
        await send_message(dict(result.render()))
    elif isinstance(body, IssueResolvedWebhookBody):
        result = build_issue_resolved_message(body)
        await send_message(dict(result.render()))
    elif isinstance(body, IssueUnresolvedWebhookBody):
        result = build_issue_unresolved_message(body)
        await send_message(dict(result.render()))
    else:
        logger.warning("Unsupported webhook body type: %s", type(body))
        return {"success": False, "skipped": True}
    return {"success": True}


@app.get("/")
async def index() -> dict[str, str]:
    """Return basic app information."""
    return {"app": "sghooker"}


@app.get("/healthcheck")
async def healthcheck() -> dict[str, bool]:
    """Return health check status."""
    return {"success": True}


@app.get("/readiness")
async def readiness() -> dict[str, bool]:
    """Return readiness check status."""
    return {"success": True}
