"""Example app for performance testing."""

from typing import Annotated

import msgspec.json

from pulya.application import Application
from pulya.params import Body

app = Application()


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


@app.post("/echo")
async def echo(body: Annotated[EchoBody, Body()]) -> EchoBody:
    return body


for i in range(100):
    app.get("/some/{id}/and/{another}/%s/:other" % i)(index)

app.get("/last_route")(index)
