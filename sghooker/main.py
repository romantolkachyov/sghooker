from typing import Annotated, Any

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
from mypy.types import UnionType

from pulya.containers import RequestContainer
from pulya.headers import Headers
from sghooker.app import SGHooker
from sghooker.schemas.issue_alert import IssueAlertWebhookBody
from sghooker.schemas.issue_created import IssueCreatedWebhookBody


def get_sentry_header(headers: Headers) -> str | None:
    return headers.get("x-sentry-resource", "Unknown")


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[__name__],
    )

    request = providers.Container(RequestContainer)

    sentry_resource_header = providers.Factory(get_sentry_header, request.headers)


app = SGHooker(Container)


def Body(_type: type | UnionType) -> Any:
    return Provide[RequestContainer.body.provided.deserialize.call(_type)]


def Header(name: str, default: None = None) -> Any:
    return Provide[RequestContainer.headers.provided.get.call(name, default)]


@app.post("/inbox/sentry/{project}")
@inject
async def receive_webhook(
    project: str,
    body: Annotated[
        IssueAlertWebhookBody | IssueCreatedWebhookBody | None,
        Body(IssueAlertWebhookBody | IssueCreatedWebhookBody | None),
    ],
    sentry_resource: Annotated[str | None, Provide[Container.sentry_resource_header]],
    simple_header: Annotated[str | None, Header("x-simple-header")],
) -> dict[str, Any]:
    return {
        "success": True,
        "sentry_resource": sentry_resource,
        "simple_header": simple_header,
        "project": project,
        "body": body,
        "body_type": str(type(body)),
        "test": {},
    }


@app.get("/")
async def index() -> dict[str, str]:
    return {"app": "sghooker"}


@app.get("/healthcheck")
async def healthcheck() -> dict[str, bool]:
    return {"success": True}


@app.get("/readiness")
async def readiness() -> dict[str, bool]:
    return {"success": True}
