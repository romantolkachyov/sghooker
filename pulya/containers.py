from contextvars import ContextVar
from typing import TypeVar

import msgspec
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    Dependency,
    Factory,
    Provider,
)

from pulya.request import HttpRequest

T = TypeVar("T")


class _BodyWrapper:
    def __init__(self, content: bytes):
        self.content = content

    def deserialize(self, body_arg_schema: type[T]) -> T:
        if not self.content:  # FIXME
            raise RuntimeError("Bad request FIXME")
            # return Response(
            #     status=HTTPStatus.BAD_REQUEST,
            #     content=msgspec.json.encode({"error": "Body is required."}),
            #     headers=[],
            # )
        return msgspec.json.decode(self.content, type=body_arg_schema)


class RequestContainer(DeclarativeContainer):
    request_ctx = Dependency(ContextVar)
    request: Provider[HttpRequest] = Factory(request_ctx.provided.get.call())
    headers = Factory(request.provided.headers)
    body = Factory(_BodyWrapper, request.provided.get_content.call())
