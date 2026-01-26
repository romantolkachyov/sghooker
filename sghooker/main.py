from typing import Annotated, Any

import msgspec.json

from sghooker.app import SGHooker
from sghooker.params import Body

app = SGHooker()


class WebhookBody(msgspec.Struct):
    key1: str


@app.get("/")
async def index() -> dict[str, str]:
    return {"Hello": "World"}


@app.get("/json")
async def json() -> dict[str, Any]:
    return {"Example": "dict"}


@app.post("/:id")
async def by_id(id: int, body: Annotated[WebhookBody, Body()]) -> WebhookBody:
    return WebhookBody(key1=f"Request key1: {body.key1} {id}")
