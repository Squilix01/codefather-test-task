import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_post_requires_auth(client: AsyncClient) -> None:
    resp = await client.post(
        "/posts/",
        json={"title": "Без авторизації", "content": "Контент без авторизації"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_soft_delete_and_include_deleted(
    client: AsyncClient,
    create_user,
) -> None:
    _, owner_headers = await create_user(email="owner_soft@example.com")

    create_resp = await client.post(
        "/posts/",
        json={"title": "Тест soft delete", "content": "Тіло поста"},
        headers=owner_headers,
    )
    assert create_resp.status_code == 201
    post_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/posts/{post_id}", headers=owner_headers)
    assert delete_resp.status_code == 204

    hidden_resp = await client.get(f"/posts/{post_id}")
    assert hidden_resp.status_code == 404

    visible_resp = await client.get(f"/posts/{post_id}?include_deleted=true")
    assert visible_resp.status_code == 200


@pytest.mark.asyncio
async def test_like_unlike_idempotent_cycle(
    client: AsyncClient,
    create_user,
) -> None:
    _, owner_headers = await create_user(email="owner_like@example.com")
    _, liker_headers = await create_user(email="liker_like@example.com")

    post_resp = await client.post(
        "/posts/",
        json={"title": "Тест лайків", "content": "Контент для лайків"},
        headers=owner_headers,
    )
    assert post_resp.status_code == 201
    post_id = post_resp.json()["id"]

    like_1 = await client.post(f"/posts/{post_id}/like", headers=liker_headers)
    assert like_1.status_code == 200
    like_1_body = like_1.json()
    assert like_1_body["status"] == "ok"
    assert "action" in like_1_body

    like_2 = await client.post(f"/posts/{post_id}/like", headers=liker_headers)
    assert like_2.status_code == 200
    like_2_body = like_2.json()
    assert like_2_body["status"] == "ok"
    assert "action" in like_2_body
    assert like_2_body["action"] != like_1_body["action"]

    unlike_1 = await client.delete(f"/posts/{post_id}/like", headers=liker_headers)
    assert unlike_1.status_code == 200
    unlike_1_body = unlike_1.json()
    assert unlike_1_body["status"] == "ok"
    assert "action" in unlike_1_body

    unlike_2 = await client.delete(f"/posts/{post_id}/like", headers=liker_headers)
    assert unlike_2.status_code == 200
    unlike_2_body = unlike_2.json()
    assert unlike_2_body["status"] == "ok"
    assert "action" in unlike_2_body
    assert unlike_2_body["action"] != unlike_1_body["action"]

    like_3 = await client.post(f"/posts/{post_id}/like", headers=liker_headers)
    assert like_3.status_code == 200
    like_3_body = like_3.json()
    assert like_3_body["status"] == "ok"
    assert like_3_body["action"] == like_1_body["action"]
