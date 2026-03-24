from fastapi import HTTPException, status
import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy.exc import IntegrityError

from app.core.config import Config
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.uow.uow import UnitOfWork


settings = Config()


class AuthService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def register_user(self, email: str, password: str) -> User:
        async with self.uow:
            existing_user = await self.uow.users.get_by_email(email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Користувач із таким email вже існує",
                )

            hashed_password = get_password_hash(password)
            user = User(email=email, hashed_password=hashed_password)

            await self.uow.users.add(user)
            try:
                await self.uow.commit()
            except IntegrityError:
                await self.uow.rollback()
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Користувач із таким email вже існує",
                )

            await self.uow.session.refresh(user)
            return user

    async def authenticate_user(self, email: str, password: str) -> User:
        async with self.uow:
            user = await self.uow.users.get_by_email(email)
            if not user or not verify_password(password, user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Невірний email або пароль",
                )
            return user

    def create_tokens(self, user: User) -> dict:
        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def refresh_tokens(self, refresh_token: str) -> dict:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не вдалося перевірити refresh-токен",
        )

        try:
            payload = jwt.decode(
                refresh_token,
                settings.jwt.secret_key,
                algorithms=[settings.jwt.algorithm],
            )
            user_id: str | None = payload.get("sub")
            token_type: str | None = payload.get("type")

            if user_id is None or token_type != "refresh":
                raise credentials_exception
        except InvalidTokenError:
            raise credentials_exception

        async with self.uow:
            user = await self.uow.users.get_by_id(int(user_id))
            if user is None:
                raise credentials_exception
            return self.create_tokens(user)
