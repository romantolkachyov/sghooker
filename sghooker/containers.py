"""Dependency injection containers for the application."""

import os

from dependency_injector import containers, providers
from pulya.containers import RequestContainer
from pulya.headers import Headers


class AppContainer(containers.DeclarativeContainer):
    """Main application container for global dependencies."""


def get_sentry_header(headers: Headers) -> str | None:
    """Get the Sentry-Hook-Resource header value.

    Args:
        headers: The request headers.

    Returns:
        The value of the Sentry-Hook-Resource header, or "Unknown" if not present.

    """
    return headers.get("Sentry-Hook-Resource", "Unknown")


class Container(containers.DeclarativeContainer):
    """Main dependency injection container."""

    wiring_config = containers.WiringConfiguration(
        packages=["sghooker"],
    )

    request = providers.Container(RequestContainer)

    grafana_url_template = providers.Object(os.getenv("GRAFANA_URL_TEMPLATE"))

    sentry_resource_header = providers.Factory(get_sentry_header, request.headers)
