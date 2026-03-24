from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import Config
from app.models.like import Like
from app.models.notification import Notification
from app.models.post import Post
from app.models.user import User
from app.tasks.broker import broker

config = Config()


#Спеціально створив нове підключення до бази даних для задач щоб ізолювати його від основного підключення яке використовується в API
engine = create_async_engine(
    config.db.get_database_url("asyncpg").render_as_string(hide_password=False)
)
async_session = async_sessionmaker(engine, expire_on_commit=False)


@broker.task(task_name="post_liked")
async def create_like_notification_task(post_id: int, author_id: int, liked_by_user_id: int) -> None:
    async with async_session() as session:
        new_notification = Notification(
            user_id=author_id,
            post_id=post_id,
            liked_by_user_id=liked_by_user_id,
        )
        session.add(new_notification)
        await session.commit()
