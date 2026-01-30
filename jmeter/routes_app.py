"""Example app for performance testing."""

from typing import Annotated

import msgspec.json
from dependency_injector.containers import WiringConfiguration
from dependency_injector.providers import (
    Container,
    Factory,
    Provider,
)
from dependency_injector.wiring import Provide, inject

from pulya.application import Application
from pulya.containers import BaseRequestContainer, CoreRequestContainer
from pulya.params import Body
from pulya.request import HttpRequest


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


def get_user_from_request(request: HttpRequest) -> str:
    # print("Get user for example")
    return f"<User {request.path}>"


def core_request(
    core: Container[CoreRequestContainer],
) -> Provider[HttpRequest]:
    return Factory(core.container.request.provided)


def core_headers(
    core: Container[CoreRequestContainer],
) -> Provider[HttpRequest]:
    return core.container.request.provided.headers


class RequestContainer(BaseRequestContainer):
    wiring_config = WiringConfiguration(
        modules=[__name__],
    )

    core = Container(CoreRequestContainer)

    request = core_request(core)
    headers = core_headers(core)

    user = Factory(get_user_from_request, request=request)


app = Application(RequestContainer)


@app.get("/")
async def index() -> dict[str, str]:
    return {"Hello": "World"}


@app.get("/test/{name}")
@inject
async def test(
    user: Annotated[str, Provide[RequestContainer.user]],
    name: str,
    headers: Annotated[list[tuple[str, str]], Provide["core.headers"]],
) -> dict[str, str]:
    return {"test": "ok", "user": user, "name": name, "headers": list(headers)}


@app.post("/echo")
async def echo(body: Annotated[EchoBody, Body()]) -> EchoBody:
    return body


for i in range(100):
    app.get("/some/{id}/and/{another}/%s/:other" % i)(index)

app.get("/last_route")(index)
