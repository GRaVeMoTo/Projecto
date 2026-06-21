"""Integration tests for the authentication endpoints."""

from datetime import UTC, datetime, timedelta

import jwt
from httpx import AsyncClient

from projecto.config import settings


async def login_and_get_token(client: AsyncClient, login: str, password: str) -> str:
    """Register and log in a user, returning the bearer token."""
    await client.post("/auth", json={"login": login, "password": password})
    response = await client.post("/login", json={"login": login, "password": password})
    return response.json()["access_token"]


def encode_access_token(claims: dict[str, object]) -> str:
    """Build a signed access token for integration tests."""
    payload = {
        "type": "access",
        **claims,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def test_register_creates_user(client: AsyncClient) -> None:
    """Registering a new user returns 201 and the public user data."""
    response = await client.post(
        "/auth",
        json={"login": "alice", "password": "s3cr3tpass"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["login"] == "alice"
    assert "id" in body
    assert "created_at" in body
    assert "password" not in body
    assert "hashed_password" not in body


async def test_register_duplicate_login_conflicts(client: AsyncClient) -> None:
    """Registering an existing login returns 409."""
    payload = {"login": "bob", "password": "s3cr3tpass"}
    first = await client.post("/auth", json=payload)
    assert first.status_code == 201

    second = await client.post("/auth", json=payload)
    assert second.status_code == 409


async def test_register_short_password_rejected(client: AsyncClient) -> None:
    """A too-short password fails validation with 422."""
    response = await client.post(
        "/auth",
        json={"login": "carol", "password": "short"},
    )
    assert response.status_code == 422


async def test_login_returns_token(client: AsyncClient) -> None:
    """Logging in with valid credentials returns a bearer token."""
    await client.post("/auth", json={"login": "dave", "password": "s3cr3tpass"})

    response = await client.post(
        "/login",
        json={"login": "dave", "password": "s3cr3tpass"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str)
    assert len(body["access_token"]) > 0


async def test_login_wrong_password_unauthorized(client: AsyncClient) -> None:
    """Logging in with a wrong password returns 401."""
    await client.post("/auth", json={"login": "erin", "password": "s3cr3tpass"})

    response = await client.post(
        "/login",
        json={"login": "erin", "password": "wrong-password"},
    )
    assert response.status_code == 401


async def test_login_unknown_user_unauthorized(client: AsyncClient) -> None:
    """Logging in as a non-existent user returns 401."""
    response = await client.post(
        "/login",
        json={"login": "ghost", "password": "s3cr3tpass"},
    )
    assert response.status_code == 401


async def test_read_current_user_returns_profile(client: AsyncClient) -> None:
    """An authenticated user can read their own profile."""
    token = await login_and_get_token(client, "frank", "s3cr3tpass")

    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["login"] == "frank"
    assert "id" in body
    assert "created_at" in body
    assert "hashed_password" not in body


async def test_read_current_user_requires_token(client: AsyncClient) -> None:
    """The protected profile endpoint rejects missing tokens."""
    response = await client.get("/auth/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required."}


async def test_read_current_user_rejects_invalid_token(client: AsyncClient) -> None:
    """The protected profile endpoint rejects malformed tokens."""
    response = await client.get(
        "/auth/me",
        headers={"Authorization": "Bearer definitely-not-a-jwt"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid authentication token."}


async def test_read_current_user_rejects_expired_token(client: AsyncClient) -> None:
    """The protected profile endpoint rejects expired JWTs."""
    expired_token = encode_access_token(
        {
            "sub": "frank",
            "exp": datetime.now(UTC) - timedelta(minutes=1),
        }
    )

    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid authentication token."}


async def test_read_current_user_rejects_token_without_subject(client: AsyncClient) -> None:
    """The protected profile endpoint rejects tokens missing a valid subject."""
    token_without_subject = encode_access_token(
        {
            "exp": datetime.now(UTC) + timedelta(minutes=5),
        }
    )

    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token_without_subject}"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token subject."}
