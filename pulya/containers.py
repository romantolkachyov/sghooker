from contextvars import ContextVar

from dependency_injector import containers
from dependency_injector.providers import Dependency

from pulya.request import HttpRequest


class BaseRequestContainer(containers.DeclarativeContainer):
    request: Dependency[ContextVar[HttpRequest]] = Dependency(ContextVar)
