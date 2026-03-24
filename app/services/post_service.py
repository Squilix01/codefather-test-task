from fastapi import HTTPException, status

from app.models.post import Post
from app.uow.uow import UnitOfWork


class PostService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create_post(self, title: str, content: str, author_id: int) -> Post:
        async with self.uow:
            post = Post(title=title, content=content, author_id=author_id)
            await self.uow.posts.add(post)
            await self.uow.commit()
            new_post = await self.uow.posts.get_by_id(post.id)
            return new_post

    async def get_posts(
        self,
        limit: int,
        offset: int,
        author_id: int | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
        include_deleted: bool = False,
    ):
        async with self.uow:
            return await self.uow.posts.get_all(
                limit=limit,
                offset=offset,
                author_id=author_id,
                search=search,
                sort_by=sort_by,
                order=order,
                include_deleted=include_deleted,
            )

    async def get_post(self, post_id: int, include_deleted: bool = False) -> Post:
        async with self.uow:
            post = await self.uow.posts.get_by_id(
                post_id=post_id,
                include_deleted=include_deleted,
            )
            if not post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пост не знайдено",
                )
            return post

    async def update_post(
        self,
        post_id: int,
        user_id: int,
        title: str | None = None,
        content: str | None = None,
    ) -> Post:
        async with self.uow:
            post = await self.uow.posts.get_by_id(post_id=post_id)
            if not post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пост не знайдено",
                )

            if post.author_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Недостатньо прав для редагування цього поста",
                )

            if title is not None:
                post.title = title
            if content is not None:
                post.content = content

            await self.uow.commit()
            updated_post = await self.uow.posts.get_by_id(post.id)
            return updated_post

    async def delete_post(self, post_id: int, user_id: int) -> None:
        async with self.uow:
            post = await self.uow.posts.get_by_id(post_id=post_id)
            if not post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пост не знайдено",
                )

            if post.author_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Недостатньо прав для видалення цього поста",
                )

            await self.uow.posts.delete(post_id=post_id)
