from collections import defaultdict
from http import HTTPMethod
from typing import Iterable

from asgiref.typing import ASGIReceiveCallable, HTTPScope

from pulya.headers import Headers
from pulya.request import Request


class ASGIRequest(Request):
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


class ASGIHeaders(Headers):
    def __init__(self, headers: Iterable[tuple[bytes, bytes]]) -> None:
        self._headers = defaultdict(list)
        for k, v in headers:
            self.add(k.decode(), v.decode())
