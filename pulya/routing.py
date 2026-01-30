from collections import defaultdict
from http import HTTPMethod
from typing import Any, Callable, Mapping, Protocol, TypeVar, get_args, get_type_hints

import msgspec
from matchit import Router as MatchitRouter

from pulya.params import Body

T = TypeVar("T", bound=Callable[..., Any])


class CreateRouteSignature(Protocol):
    def __call__(self, url_pattern: str) -> Callable[[T], T]:
        """Helpful method"""
        ...


class Route:
    __slots__ = [
        "method",
        "url_pattern",
        "handler",
        "body_arg_name",
        "body_arg_schema",
        "handler_type_hint",
        "path_params_schema",
    ]

    def __init__(
        self, method: HTTPMethod, url_pattern: str, handler: Callable[..., Any]
    ):
        self.method = method
        self.handler = handler
        self.url_pattern = url_pattern

        self.handler_type_hint = get_type_hints(handler, include_extras=True)

        # handle body
        self.body_arg_name = None
        self.body_arg_schema = None
        for k, param in self.handler_type_hint.items():
            param_args = get_args(param)
            for arg in param_args:
                if isinstance(arg, Body):
                    if self.body_arg_name:
                        raise RuntimeError("Handler can't consume two bodies at once")
                    self.body_arg_name = k
                    self.body_arg_schema = param_args[0]
                    continue

        fields = set(self.handler_type_hint.keys())
        if "user" in fields:  # FIXME
            fields.remove("user")
        if "headers" in fields:  # FIXME
            fields.remove("headers")
        fields.remove("return")
        if self.body_arg_name:
            fields.remove(self.body_arg_name)
        self.path_params_schema = msgspec.defstruct("PathParams", fields=fields)


class _MethodFactory:
    def __init__(self, method: HTTPMethod):
        self.method = method

    def __get__(self, instance: "Router", owner: type) -> CreateRouteSignature:
        def _method(url_pattern: str) -> Callable[[T], T]:
            def _inner(handler: T) -> T:
                instance.add_route(
                    self.method, url_pattern=url_pattern, handler=handler
                )
                return handler

            return _inner

        return _method


class Router:
    def __init__(self) -> None:
        self._routers_by_method: dict[HTTPMethod, MatchitRouter[Route]] = defaultdict(
            lambda: MatchitRouter()
        )

    get = _MethodFactory(HTTPMethod.GET)
    post = _MethodFactory(HTTPMethod.POST)
    put = _MethodFactory(HTTPMethod.PUT)
    delete = _MethodFactory(HTTPMethod.DELETE)

    def add_route(
        self, method: HTTPMethod, url_pattern: str, handler: Callable[..., Any]
    ) -> None:
        route = Route(method=method, url_pattern=url_pattern, handler=handler)
        self._routers_by_method[method].insert(url_pattern, route)

    def match_route(
        self, method: HTTPMethod, path: str
    ) -> tuple[Route, Mapping[str, str]] | None:
        res = self._routers_by_method[method].at(path)
        return res.value, res.params
