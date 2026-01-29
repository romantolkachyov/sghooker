from typing import Literal, Mapping, Protocol, AsyncIterator


class Scope:
    proto: Literal["http", "ws"] = "http"
    #: a string containing the version of the RSGI spec
    rsgi_version: str
    #: a string containing the HTTP version (one of "1", "1.1" or "2")
    http_version: str
    #: a string in the format {address}:{port}, where host is the listening address for this server, and port is the integer listening port
    server: str
    #: a string in the format {address}:{port}, where host is the remote host's address and port is the remote port
    client: str
    #: URL scheme portion (one of "http" or "https")
    scheme: str
    #: the HTTP method name, uppercased
    method: str
    #: HTTP request target excluding any query string
    path: str
    #: URL portion after the ?
    query_string: str
    #: a mapping-like object, where key is the header name, and value is the header value; header names are always lower-case; a get_all method returns a list of all the header values for the given key
    headers: Mapping[str, str]
    #: an optional string containing the relevant pseudo-header (empty on HTTP versions prior to 2)
    authority: str | None


class Transport(Protocol):
    async def send_bytes(self, content: bytes) -> None: ...
    async def send_str(self, content: str) -> None: ...


class HTTPProtocol(Protocol):
    async def __call__(self) -> bytes:
        """__call__ to receive the entire body in bytes format."""
        ...

    async def __aiter__(self) -> AsyncIterator[bytes]:
        """__aiter__ to receive the body in bytes chunks."""
        ...

    async def client_disconnect(self) -> None:
        """Client_disconnect to watch for client disconnection."""
        ...

    def response_empty(self, status: int, headers: list[tuple[str, str]]) -> None:
        """Response_empty to send back an empty response."""
        ...

    def response_str(
        self, status: int, headers: list[tuple[str, str]], body: str
    ) -> None:
        """Response_str to send back a response with a str body."""
        ...

    def response_bytes(
        self, status: int, headers: list[tuple[str, str]], body: bytes
    ) -> None:
        """Response_bytes to send back a response with bytes body."""
        ...

    def response_file(
        self, status: int, headers: list[tuple[str, str]], file: str
    ) -> None:
        """Response_file to send back a file response (from its path)."""
        ...

    def response_file_range(
        self,
        status: int,
        headers: list[tuple[str, str]],
        file: str,
        start: int,
        end: int,
    ) -> None:
        """Response_file_range to send back a file range response (from its path)."""
        ...

    def response_stream(self, status: int, headers: list[tuple[str, str]]) -> Transport:
        """Response_stream to start a stream response."""
        ...
