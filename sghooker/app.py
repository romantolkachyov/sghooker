from typing import TypeVar

from pulya.application import Application
from pulya.containers import BaseRequestContainer

T = TypeVar("T", bound=BaseRequestContainer)


class SGHooker(Application[T]):
    pass
