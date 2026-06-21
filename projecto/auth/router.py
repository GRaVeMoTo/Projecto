"""Authentication HTTP endpoints."""

from fastapi import APIRouter, status

from projecto.auth.dependencies import CurrentUser, DbSession
from projecto.auth.models import User
from projecto.auth.schemas import (
    TokenResponse,
    UserCreate,
    UserLogin,
    UserRead,
)
from projecto.auth.service import AuthService

router = APIRouter(tags=["auth"])


@router.post("/auth", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, session: DbSession) -> UserRead:
    """Create a new user account."""
    service = AuthService(session)
    user = await service.register(login=payload.login, password=payload.password)
    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, session: DbSession) -> TokenResponse:
    """Authenticate a user and return a JWT access token."""
    service = AuthService(session)
    token = await service.authenticate(login=payload.login, password=payload.password)
    return TokenResponse(access_token=token)


@router.get("/auth/me", response_model=UserRead)
async def read_current_user(current_user: CurrentUser) -> UserRead:
    """Return the currently authenticated user."""
    user = current_user
    assert isinstance(user, User)
    return UserRead.model_validate(user)
