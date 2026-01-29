from typing import Any, AsyncGenerator

import pytest
from httpx import AsyncClient

from pulya.testing import TestClient
from sghooker.main import app


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, Any]:
    async with TestClient(app=app) as client:
        yield client


async def test_example(client: AsyncClient) -> None:
    r = await client.get("/")
    assert r.status_code == 200
    assert r.text == '{"Hello":"World"}'


async def test_timeit(client: AsyncClient) -> None:
    r = await client.get("/json")
    assert r.status_code == 200
