import shutil
import tempfile
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from projecto.config import settings
from projecto.database import Base, configure_platform_event_loop_policy, engine, get_session
from projecto.main import create_app

configure_platform_event_loop_policy()


@pytest_asyncio.fixture
async def db_connection():
    async with engine.connect() as conn:
        yield conn


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"  # Derive a dedicated test database URL from the configured one.


TEST_DATABASE_URL = settings.database_url.rsplit("/", 1)[0] + "/projecto_test"


@pytest.fixture(scope="session")
async def db_engine() -> AsyncIterator[AsyncEngine]:
    """Provide a shared async engine backed by the test database."""
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def reset_database(db_engine: AsyncEngine) -> AsyncIterator[None]:
    """Ensure each test starts from a clean schema state."""
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture
async def client(db_engine: AsyncEngine) -> AsyncIterator[AsyncClient]:
    """Provide an async HTTP client wired to the app with a test DB session."""
    session_factory = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    app = create_app()
    app.dependency_overrides[get_session] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
def isolated_storage_root() -> Iterator[str]:
    """Point LocalStorage to a per-session temporary directory."""
    original_path = settings.storage_path
    tmp_dir = Path(tempfile.mkdtemp(prefix="projecto-storage-"))
    settings.storage_path = str(tmp_dir)
    try:
        yield settings.storage_path
    finally:
        settings.storage_path = original_path
        shutil.rmtree(tmp_dir, ignore_errors=True)


async def register_and_login(client: AsyncClient, login: str, password: str = "s3cr3tpass") -> str:
    """Register a user, log in, and return an Authorization header value.

    Returns:
        A ``Bearer <token>`` string ready to use as an Authorization header.
    """
    await client.post("/auth", json={"login": login, "password": password})
    response = await client.post("/login", json={"login": login, "password": password})
    token = response.json()["access_token"]
    return f"Bearer {token}"
