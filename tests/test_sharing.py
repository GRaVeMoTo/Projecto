"""Integration tests for the project sharing endpoints."""

from httpx import AsyncClient

from tests.conftest import register_and_login


async def create_project(client: AsyncClient, auth_header: str, name: str = "Alpha") -> int:
    response = await client.post(
        "/projects",
        json={"name": name, "description": ""},
        headers={"Authorization": auth_header},
    )
    response.raise_for_status()
    return response.json()["id"]


async def test_owner_can_invite_participant(client: AsyncClient) -> None:
    """Project owner can invite another user as participant."""
    owner = await register_and_login(client, "alice")
    await register_and_login(client, "bob")
    project_id = await create_project(client, owner)

    response = await client.post(
        f"/projects/{project_id}/invite",
        params={"user": "bob"},
        headers={"Authorization": owner},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == project_id
    assert body["login"] == "bob"
    assert body["role"] == "participant"


async def test_invite_requires_authentication(client: AsyncClient) -> None:
    """Inviting without a token returns 401."""
    response = await client.post("/projects/1/invite", params={"user": "bob"})
    assert response.status_code == 401


async def test_invite_requires_owner_role(client: AsyncClient) -> None:
    """Participants cannot invite others; only owners can."""
    owner = await register_and_login(client, "alice")
    participant = await register_and_login(client, "bob")
    await register_and_login(client, "charlie")
    project_id = await create_project(client, owner)

    await client.post(
        f"/projects/{project_id}/invite",
        params={"user": "bob"},
        headers={"Authorization": owner},
    )

    response = await client.post(
        f"/projects/{project_id}/invite",
        params={"user": "charlie"},
        headers={"Authorization": participant},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Only the project owner can perform this action."


async def test_invite_missing_user_returns_not_found(client: AsyncClient) -> None:
    """Inviting a non-existent login returns 404."""
    owner = await register_and_login(client, "alice")
    project_id = await create_project(client, owner)

    response = await client.post(
        f"/projects/{project_id}/invite",
        params={"user": "no-such-user"},
        headers={"Authorization": owner},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "The user to invite does not exist."


async def test_invite_duplicate_member_returns_conflict(client: AsyncClient) -> None:
    """Inviting an existing participant returns 409."""
    owner = await register_and_login(client, "alice")
    await register_and_login(client, "bob")
    project_id = await create_project(client, owner)

    first = await client.post(
        f"/projects/{project_id}/invite",
        params={"user": "bob"},
        headers={"Authorization": owner},
    )
    assert first.status_code == 201

    duplicate = await client.post(
        f"/projects/{project_id}/invite",
        params={"user": "bob"},
        headers={"Authorization": owner},
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "User is already a member of this project."


async def test_invite_missing_project_returns_not_found(client: AsyncClient) -> None:
    """Inviting on a non-existent project yields 404."""
    owner = await register_and_login(client, "alice")
    await register_and_login(client, "bob")

    response = await client.post(
        "/projects/999/invite",
        params={"user": "bob"},
        headers={"Authorization": owner},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found."


async def test_invite_by_non_member_forbidden(client: AsyncClient) -> None:
    """Users without membership cannot invite others."""
    owner = await register_and_login(client, "alice")
    stranger = await register_and_login(client, "eve")
    await register_and_login(client, "bob")
    project_id = await create_project(client, owner)

    response = await client.post(
        f"/projects/{project_id}/invite",
        params={"user": "bob"},
        headers={"Authorization": stranger},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have access to this project."


async def test_invited_user_can_access_project_after_invite(client: AsyncClient) -> None:
    """Inviting a user grants them access to the project list."""
    owner = await register_and_login(client, "alice")
    invitee = await register_and_login(client, "bob")
    project_id = await create_project(client, owner, name="Shared project")

    response = await client.post(
        f"/projects/{project_id}/invite",
        params={"user": "bob"},
        headers={"Authorization": owner},
    )
    assert response.status_code == 201

    listing = await client.get("/projects", headers={"Authorization": invitee})
    assert listing.status_code == 200
    projects = listing.json()
    assert any(project["id"] == project_id for project in projects)


async def test_owner_cannot_invite_themselves(client: AsyncClient) -> None:
    """Owner inviting their own login returns conflict."""
    owner = await register_and_login(client, "alice")
    project_id = await create_project(client, owner)

    response = await client.post(
        f"/projects/{project_id}/invite",
        params={"user": "alice"},
        headers={"Authorization": owner},
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "User is already a member of this project."
