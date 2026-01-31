from typing import TypeVar

from dependency_injector.containers import DeclarativeContainer

from pulya.application import Pulya

T = TypeVar("T", bound=DeclarativeContainer)


class SGHooker(Pulya[T]):
    pass
