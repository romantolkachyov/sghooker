from typing import TypeVar

from dependency_injector.containers import DeclarativeContainer

from pulya.application import Application

T = TypeVar("T", bound=DeclarativeContainer)


class SGHooker(Application[T]):
    pass
