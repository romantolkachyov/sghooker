from typing import Annotated

import msgspec.json
from dependency_injector.containers import (
    DeclarativeContainer,
    WiringConfiguration,
)
from dependency_injector.providers import Container
from dependency_injector.wiring import Provide, inject

from pulya.containers import CoreRequestContainer
from pulya.params import Body
from sghooker.app import SGHooker
from sghooker.schemas.issue_alert import IssueAlertWebhookBody
from sghooker.schemas.issue_created import IssueCreatedWebhookBody


class RequestContainer(DeclarativeContainer):
    wiring_config = WiringConfiguration(
        modules=[__name__],
    )

    core = Container(CoreRequestContainer)


app = SGHooker(RequestContainer)


@app.get("/")
async def index() -> dict[str, str]:
    return {"app": "sghooker"}


@app.post("/inbox/sentry/{project}")
@inject
async def receive_webhook(
    project: str,
    body: Annotated[IssueAlertWebhookBody | IssueCreatedWebhookBody, Body()],
    headers: Annotated[list[tuple[str, str]], Provide["core.headers"]],
) -> dict[str, bool]:
    return {"success": True}


@app.get("/healthcheck")
async def healthcheck() -> dict[str, bool]:
    return {"success": True}


@app.get("/readiness")
async def readiness() -> dict[str, bool]:
    return {"success": True}
