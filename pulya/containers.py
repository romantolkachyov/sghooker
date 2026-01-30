from contextvars import ContextVar

from dependency_injector import containers
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Container, Dependency, Factory, Provider

from pulya.request import HttpRequest


class CoreRequestContainer(DeclarativeContainer):
    request_ctx = Dependency(ContextVar)
    request: Provider[HttpRequest] = Factory(request_ctx.provided.get.call())
    headers = Factory(request.provided.headers)


class BaseRequestContainer(containers.DeclarativeContainer):
    core: Container[CoreRequestContainer] = Container(CoreRequestContainer)
