from typing import Annotated, Any

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

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

    core = providers.Container(RequestContainer)

    sentry_resource_header = providers.Factory(get_sentry_header, core.headers)


app = SGHooker(Container)


@app.get("/")
async def index() -> dict[str, str]:
    return {"app": "sghooker"}


@app.post("/inbox/sentry/{project}")
@inject
async def receive_webhook(
    project: str,
    body: Annotated[
        IssueAlertWebhookBody | IssueCreatedWebhookBody,
        Provide[
            RequestContainer.body.provided.deserialize.call(
                IssueAlertWebhookBody | IssueCreatedWebhookBody
            )
        ],
    ],
    sentry_resource: Annotated[str | None, Provide[Container.sentry_resource_header]],
) -> dict[str, Any]:
    return {
        "success": True,
        "sentry_resource": sentry_resource,
        "project": project,
        "body": body,
        "body_type": str(type(body)),
        "test": {},
    }


@app.get("/healthcheck")
async def healthcheck() -> dict[str, bool]:
    return {"success": True}


@app.get("/readiness")
async def readiness() -> dict[str, bool]:
    return {"success": True}
