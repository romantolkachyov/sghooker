from asyncio import AbstractEventLoop
from http import HTTPMethod, HTTPStatus

import msgspec

from sghooker.responses import Response
from sghooker.routing import Router
from sghooker.rsgi import HTTPProtocol, Scope


class Application(Router):
    async def __rsgi__(self, scope: Scope, protocol: HTTPProtocol) -> None:
        assert scope.proto == "http"

        match = self.match_route(HTTPMethod(scope.method), scope.path)

        if match is None:
            protocol.response_bytes(
                status=HTTPStatus.NOT_FOUND,
                headers=[],
                body=msgspec.json.encode({"error": "Not found."}),
            )
            return

        route, match_dict = match

        validated_path_params = msgspec.convert(
            match_dict, type=route.path_params_schema, strict=False
        )

        handler_params = msgspec.structs.asdict(validated_path_params)

        if route.body_arg_name and route.body_arg_schema:
            body_content = await protocol()
            if not body_content:
                protocol.response_bytes(
                    status=HTTPStatus.BAD_REQUEST,
                    headers=[],
                    body=msgspec.json.encode({"error": "Body is required."}),
                )
                return
            handler_params[route.body_arg_name] = msgspec.json.decode(
                body_content, type=route.body_arg_schema
            )

        response = await route.handler(**handler_params)

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


class SGHooker(Application):
    pass
