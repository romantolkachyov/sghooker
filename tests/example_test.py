import httpx
import pytest


def test_client():
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        r = await client.get("/")
        assert r.status_code == 200
        assert r.text == "Hello World!"


def test_example() -> None:
    assert True is True
