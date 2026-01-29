from typing import Annotated

import msgspec.json

from pulya.params import Body
from sghooker.app import SGHooker
from sghooker.schemas.issue_alert import IssueAlertWebhookBody

app = SGHooker()


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
    return {"Hello": "World"}


@app.post("/inbox/sentry/{project}")
async def receive_webhook(
    project: str, body: Annotated[IssueAlertWebhookBody, Body()]
) -> dict[str, bool]:
    return {"success": True}


@app.post("/echo")
async def echo(body: Annotated[EchoBody, Body()]) -> EchoBody:
    return body


for i in range(100):
    app.get("/some/{id}/and/{another}/%s/:other" % i)(index)

app.get("/last_route")(index)
