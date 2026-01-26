from typing import Annotated, Any

import msgspec.json

from sghooker.entrypoints.web.app import SGHooker
from sghooker.entrypoints.web.params import Body

app = SGHooker()


class WebhookBody(msgspec.Struct):
    key1: str


@app.get("/json")
async def json() -> dict[str, Any]:
    return {"Example": "dict"}


@app.post("/:id")
async def index(id: int, body: Annotated[WebhookBody, Body()]) -> WebhookBody:
    return WebhookBody(key1=f"Request key1: {body.key1} {id}")
