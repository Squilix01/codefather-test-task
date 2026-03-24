from typing import List, Literal

from fastapi import APIRouter, Depends, Query, status

from app.api.depends import get_current_user, get_like_service, get_post_service
from app.api.schemas.posts_schema import (
    LikeToggleResponse,
    PostCreate,
    PostResponse,
    PostUpdate,
)
from app.models.user import User
from app.services.likes_service import LikeService
from app.services.post_service import PostService

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service),
):
    return await post_service.create_post(
        title=post_data.title,
        content=post_data.content,
        author_id=current_user.id,
    )


@router.get("/", response_model=List[PostResponse])
async def get_posts(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    author_id: int | None = Query(None, ge=1),
    search: str | None = Query(None, min_length=1),
    sort: Literal["created_at", "likes"] = Query("created_at"),
    order: Literal["asc", "desc"] = Query("desc"),
    include_deleted: bool = Query(False),
    post_service: PostService = Depends(get_post_service),
):
    return await post_service.get_posts(
        limit=limit,
        offset=offset,
        author_id=author_id,
        search=search,
        sort_by=sort,
        order=order,
        include_deleted=include_deleted,
    )


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    include_deleted: bool = Query(False),
    post_service: PostService = Depends(get_post_service),
):
    return await post_service.get_post(post_id=post_id, include_deleted=include_deleted)


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service),
):
    return await post_service.update_post(
        post_id=post_id,
        user_id=current_user.id,
        title=post_data.title,
        content=post_data.content,
    )


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service),
):
    await post_service.delete_post(post_id=post_id, user_id=current_user.id)


@router.post("/{post_id}/like", response_model=LikeToggleResponse)
async def like_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    like_service: LikeService = Depends(get_like_service),
):
    return await like_service.like_post(user_id=current_user.id, post_id=post_id)


@router.delete("/{post_id}/like", response_model=LikeToggleResponse)
async def unlike_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    like_service: LikeService = Depends(get_like_service),
):
    return await like_service.unlike_post(user_id=current_user.id, post_id=post_id)
