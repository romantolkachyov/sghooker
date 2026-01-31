from typing import Annotated, Any

from dependency_injector.wiring import Provide, inject

from pulya.params import Body, Header
from sghooker.app import SGHooker
from sghooker.containers import Container
from sghooker.schemas.issue_alert import IssueAlertWebhookBody
from sghooker.schemas.issue_created import IssueCreatedWebhookBody

app = SGHooker(Container)


@app.post("/inbox/sentry/{project}")
@inject
async def receive_webhook(
    project: str,
    body: Annotated[
        IssueAlertWebhookBody | IssueCreatedWebhookBody | None,
        Body(IssueAlertWebhookBody | IssueCreatedWebhookBody | None),
    ],
    sentry_resource: Annotated[str | None, Provide[Container.sentry_resource_header]],
    simple_header: Annotated[str | None, Header("x-simple-header")],
) -> dict[str, Any]:
    return {
        "success": True,
        "sentry_resource": sentry_resource,
        "simple_header": simple_header,
        "project": project,
        "body": body,
        "body_type": str(type(body)),
        "test": {},
    }


@app.get("/")
async def index() -> dict[str, str]:
    return {"app": "sghooker"}


@app.get("/healthcheck")
async def healthcheck() -> dict[str, bool]:
    return {"success": True}


@app.get("/readiness")
async def readiness() -> dict[str, bool]:
    return {"success": True}
