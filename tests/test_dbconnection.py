import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_database_connects(db_connection):
    result = await db_connection.execute(text("SELECT 1"))
    assert result.scalar() == 1

@pytest.mark.asyncio
async def test_postgres_version(db_connection):
    result = await db_connection.execute(text("SELECT version()"))
    version = result.scalar()
    assert "PostgreSQL" in version