from asyncio import AbstractEventLoop
from http import HTTPStatus
from typing import Any

import msgspec
from asgiref.typing import (
    ASGIReceiveCallable,
    ASGISendCallable,
    HTTPResponseBodyEvent,
    HTTPResponseStartEvent,
)
from asgiref.typing import (
    Scope as ASGIScope,
)

from pulya.request import ASGIHttpRequest, HttpRequest, RSGIHttpRequest
from pulya.responses import Response
from pulya.routing import Router
from pulya.rsgi import HTTPProtocol, Scope


class Application(Router):
    async def handle_http_request(self, request: HttpRequest) -> Any:
        match = self.match_route(request.method, request.path)

        if match is None:
            return Response(
                status=HTTPStatus.NOT_FOUND,
                headers=[],
                content=msgspec.json.encode({"error": "Not found."}),
            )

        route, match_dict = match
        validated_path_params = msgspec.convert(
            match_dict, type=route.path_params_schema, strict=False
        )

        handler_params = msgspec.structs.asdict(validated_path_params)

        if route.body_arg_name and route.body_arg_schema:
            body_content = await request.get_content()
            if not body_content:
                return Response(
                    status=HTTPStatus.BAD_REQUEST,
                    content=msgspec.json.encode({"error": "Body is required."}),
                    headers=[],
                )
            handler_params[route.body_arg_name] = msgspec.json.decode(
                body_content, type=route.body_arg_schema
            )

        return await route.handler(**handler_params)

    async def __call__(
        self, scope: ASGIScope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        assert scope["type"] == "http", "WS is not supported yet"

        response = await self.handle_http_request(ASGIHttpRequest(scope, receive))

        if isinstance(response, Response):
            await send(
                HTTPResponseStartEvent(
                    type="http.response.start",
                    status=response.status,
                    headers=[
                        (b"content-type", b"text/plain"),
                    ],
                    trailers=False,
                )
            )
            await send(
                HTTPResponseBodyEvent(
                    type="http.response.body", body=response.content, more_body=False
                )
            )
        elif isinstance(response, msgspec.Struct) or isinstance(
            response, (dict, list, str, int)
        ):
            await send(
                HTTPResponseStartEvent(
                    type="http.response.start",
                    status=HTTPStatus.OK,  # FIXME: get default status
                    headers=[
                        (b"content-type", b"text/plain"),
                    ],
                    trailers=False,
                )
            )
            await send(
                HTTPResponseBodyEvent(
                    type="http.response.body",
                    body=msgspec.json.encode(response),
                    more_body=False,
                )
            )
        else:
            raise RuntimeError(f"Unsupported response type {type(response)}")

    async def __rsgi__(self, scope: Scope, protocol: HTTPProtocol) -> None:
        assert scope.proto == "http", "WS is not supported yet"

        response = await self.handle_http_request(RSGIHttpRequest(scope, protocol))

        if isinstance(response, Response):
            protocol.response_bytes(
                status=response.status, headers=response.headers, body=response.content
            )
        elif isinstance(response, msgspec.Struct) or isinstance(
            response, (dict, list, str, int)
        ):
            protocol.response_bytes(
                status=HTTPStatus.OK, headers=[], body=msgspec.json.encode(response)
            )
        else:
            raise RuntimeError(f"Unsupported response type {type(response)}")

    def __rsgi_init__(self, loop: AbstractEventLoop) -> None:
        print("Do some init job")

    def __rsgi_del__(self, loop: AbstractEventLoop) -> None:
        print("Do some cleanup")
