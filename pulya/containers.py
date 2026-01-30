from contextvars import ContextVar

from dependency_injector import containers
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Container, Dependency

from pulya.request import HttpRequest


class CoreRequestContainer(DeclarativeContainer):
    request: Dependency[ContextVar[HttpRequest]] = Dependency(ContextVar)


class BaseRequestContainer(containers.DeclarativeContainer):
    core: Container[CoreRequestContainer] = Container(CoreRequestContainer)
