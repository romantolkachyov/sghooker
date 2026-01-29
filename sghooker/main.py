from typing import Annotated, Any

import msgspec.json

from sghooker.app import SGHooker
from sghooker.params import Body

app = SGHooker()


class WebhookBody(msgspec.Struct):
    key1: str


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


@app.get("/json")
async def json() -> dict[str, Any]:
    return {"Example": "dict"}


@app.post("/echo")
async def echo(body: Annotated[EchoBody, Body()]) -> EchoBody:
    return body


# @app.post("/:id")
# async def by_id(id: int, body: Annotated[WebhookBody, Body()]) -> WebhookBody:
#     return WebhookBody(key1=f"Request key1: {body.key1} {id}")
#
#
# for i in range(100):
#     app.get("/some/:id/and/:another/%s/:other" % i)(index)


@app.post("/id/{id}")
async def by_id(id: int, body: Annotated[WebhookBody, Body()]) -> WebhookBody:
    return WebhookBody(key1=f"Request key1: {body.key1} {id}")


for i in range(100):
    app.get("/some/{id}/and/{another}/%s/:other" % i)(index)

app.get("/last_route")(index)
