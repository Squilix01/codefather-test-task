import pytest
from httpx import AsyncClient

from app.database.session import session_factory
from app.models.notification import Notification


@pytest.mark.asyncio
async def test_get_notifications_and_mark_read(
    client: AsyncClient,
    create_user,
) -> None:
    owner_id, owner_headers = await create_user(email="owner_notif@example.com")
    liker_id, _ = await create_user(email="liker_notif@example.com")

    create_post_resp = await client.post(
        "/posts/",
        json={"title": "Пост для сповіщень", "content": "Контент поста"},
        headers=owner_headers,
    )
    assert create_post_resp.status_code == 201
    post_id = create_post_resp.json()["id"]

    async with session_factory() as session:
        notification = Notification(
            user_id=owner_id,
            post_id=post_id,
            liked_by_user_id=liker_id,
            is_read=False,
        )
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        notification_id = notification.id

    get_resp = await client.get("/notifications/", headers=owner_headers)
    assert get_resp.status_code == 200
    body = get_resp.json()
    assert len(body) == 1
    assert body[0]["id"] == notification_id
    assert body[0]["is_read"] is False

    mark_resp = await client.patch(
        f"/notifications/{notification_id}/read",
        headers=owner_headers,
    )
    assert mark_resp.status_code == 200
    mark_body = mark_resp.json()
    assert isinstance(mark_body.get("message"), str)
    assert mark_body["message"]

    get_after_resp = await client.get("/notifications/", headers=owner_headers)
    assert get_after_resp.status_code == 200
    assert get_after_resp.json()[0]["is_read"] is True


@pytest.mark.asyncio
async def test_mark_read_returns_404_for_foreign_notification(
    client: AsyncClient,
    create_user,
) -> None:
    owner_id, owner_headers = await create_user(email="owner_foreign@example.com")
    second_user_id, second_headers = await create_user(email="second_foreign@example.com")

    create_post_resp = await client.post(
        "/posts/",
        json={"title": "Чужий пост для сповіщень", "content": "Контент поста"},
        headers=owner_headers,
    )
    assert create_post_resp.status_code == 201
    post_id = create_post_resp.json()["id"]

    async with session_factory() as session:
        notification = Notification(
            user_id=owner_id,
            post_id=post_id,
            liked_by_user_id=second_user_id,
            is_read=False,
        )
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        notification_id = notification.id

    foreign_resp = await client.patch(
        f"/notifications/{notification_id}/read",
        headers=second_headers,
    )
    assert foreign_resp.status_code == 404
    body = foreign_resp.json()
    assert "detail" in body
