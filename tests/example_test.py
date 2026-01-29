import time
from typing import Any, AsyncGenerator

import httpx
import pytest
from httpx import AsyncClient

from sghooker.main import app


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, Any]:
    transport = httpx.ASGITransport(app=app)  # type: ignore[arg-type]
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        yield client


async def test_example(client: AsyncClient) -> None:
    r = await client.get("/")
    assert r.status_code == 200
    assert r.text == '{"Hello":"World"}'


async def test_timeit(client: AsyncClient) -> None:
    r = await client.get("/json")
    assert r.status_code == 200
