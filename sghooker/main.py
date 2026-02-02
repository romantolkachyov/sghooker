import logging
from typing import Annotated, Any

from dependency_injector.wiring import inject
from pulya import Body, Header, Pulya

from sghooker.chat_messages import (
    build_issue_alert_message,
    build_issue_created_message,
)
from sghooker.containers import Container
from sghooker.google_chat import send_message
from sghooker.schemas.issue_alert import IssueAlertWebhookBody
from sghooker.schemas.issue_created import IssueCreatedWebhookBody

app = Pulya(Container)

logger = logging.getLogger("sghooker")


@app.post("/inbox/sentry/")
@inject
async def receive_webhook(
    body: Annotated[
        IssueAlertWebhookBody | IssueCreatedWebhookBody | None,
        Body(IssueAlertWebhookBody | IssueCreatedWebhookBody | None),
    ],
    sentry_resource: Annotated[str | None, Header("Sentry-Hook-Resource")],
) -> dict[str, Any]:
    if isinstance(body, IssueAlertWebhookBody):
        result = build_issue_alert_message(body)
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
    return {"app": "sghooker"}


@app.get("/healthcheck")
async def healthcheck() -> dict[str, bool]:
    return {"success": True}


@app.get("/readiness")
async def readiness() -> dict[str, bool]:
    return {"success": True}
