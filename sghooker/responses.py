from http import HTTPStatus


class Response:
    __slots__ = ["status", "content", "_headers"]

    default_content_type = "text/plain"

    def __init__(
        self,
        content: bytes,
        status: HTTPStatus = HTTPStatus.OK,
        headers: list[tuple[str, str]] | None = None,
    ) -> None:
        self.content = content
        self.status = status

        self._headers = [("content-type", self.default_content_type)]
        if headers:
            self.set_headers(headers)

    @property
    def headers(self) -> list[tuple[str, str]]:
        return self._headers

    def set_headers(self, headers: list[tuple[str, str]]) -> None:
        self._headers = headers
