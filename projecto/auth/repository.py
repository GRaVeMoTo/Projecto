"""Data-access layer for users."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from projecto.auth.models import User


class UserRepository:
    """Repository encapsulating user persistence operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_login(self, login: str) -> User | None:
        """Return the user with the given login, or None."""
        result = await self._session.execute(select(User).where(User.login == login))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        """Return the user with the given id, or None."""
        return await self._session.get(User, user_id)

    async def create(self, login: str, hashed_password: str) -> User:
        """Persist and return a new user."""
        user = User(login=login, hashed_password=hashed_password)
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user
