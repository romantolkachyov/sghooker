from typing import Any

import httpx
from asgiref.typing import ASGIApplication


class TestClient(httpx.AsyncClient):
    def __init__(
        self, app: ASGIApplication, base_url: str = "http://testserver", **kwargs: Any
    ) -> None:
        transport = httpx.ASGITransport(app=app)
        super().__init__(transport=transport, base_url=base_url, **kwargs)
