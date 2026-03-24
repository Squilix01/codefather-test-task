import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete


from app.database.session import session_factory
from app.main import app
from app.models.like import Like
from app.models.notification import Notification
from app.models.post import Post
from app.models.user import User
from app.tasks.notifications import create_like_notification_task




@pytest_asyncio.fixture(autouse=True)
async def clean_db() -> None:
    async with session_factory() as session:
        await session.execute(delete(Notification))
        await session.execute(delete(Like))
        await session.execute(delete(Post))
        await session.execute(delete(User))
        await session.commit()


@pytest.fixture(autouse=True)
def disable_task_queue(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_kiq(*args, **kwargs) -> None:
        return None

    monkeypatch.setattr(create_like_notification_task, "kiq", fake_kiq)


@pytest_asyncio.fixture
async def client() -> AsyncClient: # type: ignore
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client


@pytest_asyncio.fixture
async def create_user(
    client: AsyncClient,
):
    async def _create_user(
        email: str | None = None,
        password: str = "StrongPass123",
    ) -> tuple[int, dict[str, str]]:
        safe_email = email or f"user_{uuid.uuid4().hex[:8]}@test.com"

        register_resp = await client.post(
            "/auth/register",
            json={"email": safe_email, "password": password},
        )
        assert register_resp.status_code == 201
        user_id = register_resp.json()["id"]

        login_resp = await client.post(
            "/auth/login",
            json={"email": safe_email, "password": password},
        )
        assert login_resp.status_code == 200
        access_token = login_resp.json()["access_token"]

        return user_id, {"Authorization": f"Bearer {access_token}"}

    return _create_user
