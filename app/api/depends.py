from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import InvalidTokenError

from app.core.config import Config
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.likes_service import LikeService
from app.services.notifications_service import NotificationService
from app.services.post_service import PostService
from app.uow.uow import UnitOfWork

settings = Config()

security = HTTPBearer(auto_error=False)


async def get_uow() -> UnitOfWork:
    return UnitOfWork()


def get_auth_service(uow: UnitOfWork = Depends(get_uow)) -> AuthService:
    return AuthService(uow)


def get_notification_service(uow: UnitOfWork = Depends(get_uow)) -> NotificationService:
    return NotificationService(uow)


def get_post_service(uow: UnitOfWork = Depends(get_uow)) -> PostService:
    return PostService(uow)


def get_like_service(uow: UnitOfWork = Depends(get_uow)) -> LikeService:
    return LikeService(uow)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    uow: UnitOfWork = Depends(get_uow),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не вдалося перевірити облікові дані",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise credentials_exception

    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.jwt.secret_key, algorithms=[settings.jwt.algorithm])
        user_id: str | None = payload.get("sub")
        token_type: str | None = payload.get("type")

        if user_id is None or token_type != "access":
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    async with uow:
        user = await uow.users.get_by_id(int(user_id))
        if user is None:
            raise credentials_exception

        return user
