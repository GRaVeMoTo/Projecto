from sqlalchemy.ext.asyncio import AsyncSession

from projecto.auth.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from projecto.auth.models import User
from projecto.auth.repository import UserRepository
from projecto.security import (
    create_access_token,
    hash_password,
    verify_password,
)


class AuthService:
    """Service handling user registration and authentication."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._users = UserRepository(session)

    async def register(self, login: str, password: str) -> User:
        """Register a new user.

        Args:
            login: Desired unique login.
            password: Plaintext password to hash and store.

        Returns:
            The newly created user.

        Raises:
            UserAlreadyExistsError: If the login is already taken.
        """
        existing = await self._users.get_by_login(login)
        if existing is not None:
            raise UserAlreadyExistsError

        user = await self._users.create(
            login=login,
            hashed_password=hash_password(password),
        )
        await self._session.commit()
        return user

    async def authenticate(self, login: str, password: str) -> str:
        """Authenticate a user and return a signed access token.

        Args:
            login: User login.
            password: Plaintext password.

        Returns:
            An encoded JWT access token.

        Raises:
            InvalidCredentialsError: If credentials are invalid.
        """
        user = await self._users.get_by_login(login)
        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError

        return create_access_token({"sub": user.login})

    async def get_by_login(self, login: str) -> User | None:
        """Return a user by login (used by dependencies)."""
        return await self._users.get_by_login(login)
