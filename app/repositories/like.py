from sqlalchemy import select
from app.models.like import Like
from app.repositories.base import BaseRepository

class LikeRepository(BaseRepository):
    async def add(self, like: Like) -> Like:
        self.session.add(like)
        return like

    async def get_by_user_and_post(self, user_id: int, post_id: int) -> Like | None:
        stmt = select(Like).where(Like.user_id == user_id, Like.post_id == post_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, like: Like) -> None:
        await self.session.delete(like)