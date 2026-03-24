from fastapi import APIRouter, Depends, status

from app.api.schemas.auth_schema import RefreshTokenRequest, UserCreate, UserLogin, UserResponse, TokenResponse
from app.api.depends import get_auth_service 
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service) 
):
    user = await auth_service.register_user(email=user_data.email, password=user_data.password)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin, 
    auth_service: AuthService = Depends(get_auth_service) 
):
    user = await auth_service.authenticate_user(
        email=credentials.email, 
        password=credentials.password
    )
    tokens = auth_service.create_tokens(user)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service) 
):
    return await auth_service.refresh_tokens(request.refresh_token)