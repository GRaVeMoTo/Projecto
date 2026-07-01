"""Auth-specific FastAPI dependencies."""

from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from projecto.auth.models import User
from projecto.auth.service import AuthService
from projecto.database import get_session
from projecto.exceptions import UnauthorizedError
from projecto.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)

DbSession = Annotated[AsyncSession, Depends(get_session)]
BearerToken = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]


def get_token_subject(credentials: BearerToken) -> str:
    """Extract and validate the subject (login) from a bearer token.

    Args:
        credentials: The bearer credentials from the Authorization header.

    Returns:
        The token subject (user login).

    Raises:
        UnauthorizedError: If the token is missing or invalid.
    """
    if credentials is None:
        raise UnauthorizedError("Authentication required.")

    try:
        claims = decode_access_token(credentials.credentials)
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Invalid authentication token.") from None
    subject = claims.get("sub")
    if not subject or not isinstance(subject, str):
        raise UnauthorizedError("Invalid token subject.")
    return subject


CurrentSubject = Annotated[str, Depends(get_token_subject)]


async def get_current_user(subject: CurrentSubject, session: DbSession) -> User:
    """Resolve the authenticated user from the JWT subject.

    Args:
        subject: The login extracted from a valid JWT.
        session: Database session.

    Returns:
        The authenticated User.

    Raises:
        UnauthorizedError: If no matching active user exists.
    """
    service = AuthService(session)
    user = await service.get_by_login(subject)
    if user is None:
        raise UnauthorizedError("User no longer exists.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
