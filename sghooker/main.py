from typing import Annotated

import msgspec.json

from pulya.containers import BaseRequestContainer
from pulya.params import Body
from sghooker.app import SGHooker
from sghooker.schemas.issue_alert import IssueAlertWebhookBody
from sghooker.schemas.issue_created import IssueCreatedWebhookBody

app = SGHooker(BaseRequestContainer)


class EchoBodyItem(msgspec.Struct):
    a: str
    b: str
    c: str
    d: str
    e: str
    f: str
    g: str


class EchoBody(msgspec.Struct):
    items: list[EchoBodyItem]


@app.get("/")
async def index() -> dict[str, str]:
    return {"app": "sghooker"}


@app.get("/healthcheck")
async def healthcheck() -> dict[str, bool]:
    return {"success": True}


@app.get("/readiness")
async def readiness() -> dict[str, bool]:
    return {"success": True}


@app.post("/inbox/sentry/{project}")
async def receive_webhook(
    project: str,
    body: Annotated[IssueAlertWebhookBody | IssueCreatedWebhookBody, Body()],
) -> dict[str, bool]:
    return {"success": True}
