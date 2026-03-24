from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.models.like import Like
from app.tasks.notifications import create_like_notification_task
from app.uow.uow import UnitOfWork


class LikeService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def like_post(self, user_id: int, post_id: int) -> dict:
        async with self.uow:
            post = await self.uow.posts.get_by_id(post_id)
            if not post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пост не знайдено",
                )

            existing_like = await self.uow.likes.get_by_user_and_post(
                user_id=user_id,
                post_id=post_id,
            )
            if existing_like:
                return {"status": "ok", "action": "вже_вподобано"}

            new_like = Like(user_id=user_id, post_id=post_id)
            await self.uow.likes.add(new_like)

            try:
                await self.uow.commit()

                if post.author_id != user_id:
                    await create_like_notification_task.kiq(
                        post_id=post.id,
                        author_id=post.author_id,
                        liked_by_user_id=user_id,
                    )
            except IntegrityError:
                await self.uow.rollback()
                return {"status": "ok", "action": "вже_вподобано"}

            return {"status": "ok", "action": "вподобано"}

    async def unlike_post(self, user_id: int, post_id: int) -> dict:
        async with self.uow:
            post = await self.uow.posts.get_by_id(post_id)
            if not post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пост не знайдено",
                )

            existing_like = await self.uow.likes.get_by_user_and_post(
                user_id=user_id,
                post_id=post_id,
            )
            if not existing_like:
                return {"status": "ok", "action": "вже_не_вподобано"}

            await self.uow.likes.delete(existing_like)
            await self.uow.commit()
            return {"status": "ok", "action": "не_вподобано"}
