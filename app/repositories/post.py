from typing import Sequence

from sqlalchemy import asc, desc, func, or_, select, update
from sqlalchemy.orm import selectinload

from app.models.like import Like
from app.models.post import Post
from app.repositories.base import BaseRepository


class PostRepository(BaseRepository):
    async def add(self, post: Post) -> Post:
        self.session.add(post)
        return post

    async def get_by_id(self, post_id: int, include_deleted: bool = False) -> Post | None:
        stmt = (
            select(Post)
            .options(
                selectinload(Post.author),
                selectinload(Post.likes),
            )
            .where(Post.id == post_id)
        )

        if not include_deleted:
            stmt = stmt.where(Post.deleted_at.is_(None))

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        limit: int,
        offset: int,
        author_id: int | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
        include_deleted: bool = False,
    ) -> Sequence[Post]:
        stmt = (
            select(Post)
            .options(
                selectinload(Post.author),
                selectinload(Post.likes),
            )
        )

        if not include_deleted:
            stmt = stmt.where(Post.deleted_at.is_(None))

        if author_id is not None:
            stmt = stmt.where(Post.author_id == author_id)

        if search:
            stmt = stmt.where(
                or_(
                    Post.title.ilike(f"%{search}%"),
                    Post.content.ilike(f"%{search}%"),
                )
            )

        if sort_by == "likes":
            stmt = stmt.outerjoin(Like, Like.post_id == Post.id).group_by(Post.id)
            if order == "asc":
                stmt = stmt.order_by(asc(func.count(Like.id)))
            else:
                stmt = stmt.order_by(desc(func.count(Like.id)))
        else:
            if order == "asc":
                stmt = stmt.order_by(asc(Post.created_at))
            else:
                stmt = stmt.order_by(desc(Post.created_at))

        stmt = stmt.limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete(self, post_id: int) -> None:
        stmt = (
            update(Post)
            .where(Post.id == post_id)
            .values(deleted_at=func.now())
        )
        await self.session.execute(stmt)
