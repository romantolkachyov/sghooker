from abc import ABC, abstractmethod
from http import HTTPMethod

from asgiref.typing import ASGIReceiveCallable, HTTPScope

from pulya.rsgi import HTTPProtocol, Scope


class HttpRequest(ABC):
    method: HTTPMethod
    path: str

    @abstractmethod
    async def get_content(self) -> bytes:
        """Read all request body."""
        pass


class RSGIHttpRequest(HttpRequest):
    __slots__ = ("_scope", "_protocol")

    def __init__(self, scope: Scope, protocol: HTTPProtocol) -> None:
        self._scope = scope
        self._protocol = protocol

        self.method = HTTPMethod(scope.method)
        self.path = scope.path

    async def get_content(self) -> bytes:
        return await self._protocol()


class ASGIHttpRequest(HttpRequest):
    __slots__ = ("_scope", "_receive")

    def __init__(self, scope: HTTPScope, receive: ASGIReceiveCallable) -> None:
        self._scope = scope
        self._receive = receive

        self.method = HTTPMethod(scope["method"])
        self.path = scope["path"]

    async def get_content(self) -> bytes:
        body = b""
        more_body = True
        while more_body:
            message = await self._receive()
            if message["type"] == "http.request":
                body += message.get("body", b"")
                more_body = message.get("more_body", False)
            else:
                raise RuntimeError(f"Unsupported ASGI message type {message['type']}")
        return body
