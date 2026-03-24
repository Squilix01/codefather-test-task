import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient) -> None:
    register_resp = await client.post(
        "/auth/register",
        json={"email": "test_avt@example.com", "password": "StrongPass123"},
    )
    assert register_resp.status_code == 201
    register_body = register_resp.json()
    assert register_body["email"] == "test_avt@example.com"
    assert "id" in register_body

    login_resp = await client.post(
        "/auth/login",
        json={"email": "test_avt@example.com", "password": "StrongPass123"},
    )
    assert login_resp.status_code == 200
    login_body = login_resp.json()
    assert "access_token" in login_body
    assert "refresh_token" in login_body
    assert login_body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_409(client: AsyncClient) -> None:
    payload = {"email": "dublikat@example.com", "password": "StrongPass123"}

    first_resp = await client.post("/auth/register", json=payload)
    assert first_resp.status_code == 201

    second_resp = await client.post("/auth/register", json=payload)
    assert second_resp.status_code == 409
    body = second_resp.json()
    assert isinstance(body.get("detail"), str)
    assert body["detail"]
