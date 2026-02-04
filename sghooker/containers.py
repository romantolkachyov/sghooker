import os

from dependency_injector import containers, providers
from pulya.containers import RequestContainer
from pulya.headers import Headers


class AppContainer(containers.DeclarativeContainer):
    pass


def get_sentry_header(headers: Headers) -> str | None:
    return headers.get("Sentry-Hook-Resource", "Unknown")


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=["sghooker"],
    )

    request = providers.Container(RequestContainer)

    grafana_url_template = providers.Object(os.getenv("GRAFANA_URL_TEMPLATE"))

    sentry_resource_header = providers.Factory(get_sentry_header, request.headers)
