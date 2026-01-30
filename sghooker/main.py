from typing import Annotated

from dependency_injector.containers import (
    DeclarativeContainer,
    WiringConfiguration,
)
from dependency_injector.providers import Container, Factory
from dependency_injector.wiring import Provide, inject

from pulya.containers import CoreRequestContainer
from pulya.params import Body
from sghooker.app import SGHooker
from sghooker.schemas.issue_alert import IssueAlertWebhookBody
from sghooker.schemas.issue_created import IssueCreatedWebhookBody


def get_sentry_header(headers: list[tuple[str, str]]) -> str:
    # FIXME: suboptimal, wrap headers in Headers
    for header in headers:
        if header[0] == "x-sentry-resource":
            return header[1]
    return "Unknown"


class RequestContainer(DeclarativeContainer):
    wiring_config = WiringConfiguration(
        modules=[__name__],
    )

    core = Container(CoreRequestContainer)

    sentry_resource_header = Factory(get_sentry_header, core.headers)


app = SGHooker(RequestContainer)


@app.get("/")
@inject
async def index() -> dict[str, str]:
    return {"app": "sghooker"}


@app.post("/inbox/sentry/{project}")
@inject
async def receive_webhook(
    project: str,
    body: Annotated[IssueAlertWebhookBody | IssueCreatedWebhookBody, Body()],
    sentry_resource: Annotated[str, Provide[RequestContainer.sentry_resource_header]],
) -> dict[str, bool]:
    return {"success": True, "sentry_resource": sentry_resource}


@app.get("/healthcheck")
async def healthcheck() -> dict[str, bool]:
    return {"success": True}


@app.get("/readiness")
async def readiness() -> dict[str, bool]:
    return {"success": True}
