"""Main application module with webhook endpoints."""

import logging
from typing import Annotated, Any

from dependency_injector.wiring import Provide, inject
from pulya import Body, Header, Pulya

from sghooker.chat_messages import (
    build_alert_event_message,
    build_issue_created_message,
)
from sghooker.containers import Container
from sghooker.google_chat import send_message
from sghooker.schemas.alert_event import AlertEventWebhookBody
from sghooker.schemas.issue_event import (
    IssueCreatedWebhookBody,
    IssueResolvedWebhookBody,
    IssueUnresolvedWebhookBody,
)

app = Pulya(Container)

logger = logging.getLogger("sghooker")

WebHookBodyUnion = (
    AlertEventWebhookBody | IssueCreatedWebhookBody | IssueResolvedWebhookBody | IssueUnresolvedWebhookBody | None
)


@app.post("/inbox/sentry/")
@inject
async def receive_webhook(
    body: Annotated[
        WebHookBodyUnion,
        Body(WebHookBodyUnion),
    ],
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
    """Receive and process Sentry webhooks.

    Args:
        body: The webhook body payload.
        sentry_resource: The Sentry-Hook-Resource header (unused but validated).
        grafana_url_template: Optional Grafana URL template for log links.
        tracing_url_template: Optional tracing URL template for trace links.

    Returns:
        A dictionary indicating success or failure.

    """
    del sentry_resource  # Unused but validated by the header check
    if isinstance(body, AlertEventWebhookBody):
        result = build_alert_event_message(
            body,
            grafana_url_template=grafana_url_template,
            tracing_url_template=tracing_url_template,
        )
        await send_message(dict(result.render()))
    elif isinstance(body, IssueCreatedWebhookBody):
        result = build_issue_created_message(body)
        await send_message(dict(result.render()))
    else:
        logger.error("Unsupported body type %s", type(body))
        return {"success": False}
    return {"success": True}


@app.get("/")
async def index() -> dict[str, str]:
    """Return basic app information.

    Returns:
        A dictionary with the app name.

    """
    return {"app": "sghooker"}


@app.get("/healthcheck")
async def healthcheck() -> dict[str, bool]:
    """Return health check status.

    Returns:
        A dictionary indicating the service is healthy.

    """
    return {"success": True}


@app.get("/readiness")
async def readiness() -> dict[str, bool]:
    """Return readiness check status.

    Returns:
        A dictionary indicating the service is ready.

    """
    return {"success": True}
