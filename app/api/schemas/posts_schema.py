from pydantic import BaseModel, ConfigDict
from app.api.schemas.auth_schema import UserResponse


class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class PostResponse(PostBase):
    id: int
    author_id: int
    author: UserResponse 
    likes_count: int     

    model_config = ConfigDict(from_attributes=True)


class LikeToggleResponse(BaseModel):
    status: str
    action: str