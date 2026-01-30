"""Example app for performance testing."""

from typing import Annotated

import msgspec.json
from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import (
    Container,
    Factory,
)
from dependency_injector.wiring import Provide, inject

from pulya.application import Application
from pulya.containers import CoreRequestContainer
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


def provide_active_request(
    core: Container[CoreRequestContainer],
) -> Factory[HttpRequest]:
    return Factory(core.container.request.provided.get.call())


class RequestContainer(DeclarativeContainer):
    wiring_config = WiringConfiguration(
        modules=[__name__],
    )

    core = Container(CoreRequestContainer)

    request = provide_active_request(
        core
    )  # Factory(core.container.request.provided.get.call())

    user = Factory(get_user_from_request, request=request)


app = Application(RequestContainer)


@app.get("/")
async def index() -> dict[str, str]:
    return {"Hello": "World"}


@app.get("/test/{name}")
@inject
async def test(
    user: Annotated[str, Provide[RequestContainer.user]], name: str
) -> dict[str, str]:
    return {"test": "ok", "user": user, "name": name}


@app.post("/echo")
async def echo(body: Annotated[EchoBody, Body()]) -> EchoBody:
    return body


for i in range(100):
    app.get("/some/{id}/and/{another}/%s/:other" % i)(index)

app.get("/last_route")(index)
