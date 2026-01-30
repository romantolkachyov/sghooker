from contextvars import ContextVar

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    Dependency,
    Factory,
    Provider,
)

from pulya.request import HttpRequest


class CoreRequestContainer(DeclarativeContainer):
    request_ctx = Dependency(ContextVar)
    request: Provider[HttpRequest] = Factory(request_ctx.provided.get.call())
    headers = Factory(request.provided.headers)
