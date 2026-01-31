from http import HTTPMethod
from typing import Protocol

from asgiref.typing import ASGIReceiveCallable, HTTPScope

from pulya.headers import ASGIHeaders, Headers, RSGIHeaders
from pulya.rsgi import HTTPProtocol, Scope


class HttpRequest(Protocol):
    @property
    def method(self) -> HTTPMethod: ...

    @property
    def path(self) -> str: ...

    @property
    def headers(self) -> Headers: ...

    async def get_content(self) -> bytes:
        """Read whole request body."""
        pass


class RSGIHttpRequest(HttpRequest):
    __slots__ = ("_scope", "_protocol")

    def __init__(self, scope: Scope, protocol: HTTPProtocol) -> None:
        self._scope = scope
        self._protocol = protocol

    @property
    def method(self) -> HTTPMethod:
        return HTTPMethod(self._scope.method)

    @property
    def path(self) -> str:
        return self._scope.path

    @property
    def headers(self) -> Headers:
        return RSGIHeaders(self._scope.headers)

    async def get_content(self) -> bytes:
        return await self._protocol()


class ASGIHttpRequest(HttpRequest):
    __slots__ = ("_scope", "_receive")

    def __init__(self, scope: HTTPScope, receive: ASGIReceiveCallable) -> None:
        self._scope = scope
        self._receive = receive

    @property
    def method(self) -> HTTPMethod:
        return HTTPMethod(self._scope["method"])

    @property
    def path(self) -> str:
        return self._scope["path"]

    @property
    def headers(self) -> Headers:
        return ASGIHeaders(self._scope["headers"])

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
