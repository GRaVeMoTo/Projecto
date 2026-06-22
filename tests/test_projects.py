"""Integration tests for the project endpoints."""

from httpx import AsyncClient

from tests.conftest import register_and_login


async def test_create_project_makes_creator_owner(client: AsyncClient) -> None:
    """Creating a project returns 201 with the caller as owner."""
    auth = await register_and_login(client, "alice")
    response = await client.post(
        "/projects",
        json={"name": "Apollo", "description": "Moon mission"},
        headers={"Authorization": auth},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Apollo"
    assert body["description"] == "Moon mission"
    assert body["role"] == "owner"
    assert "id" in body
    assert "owner_id" in body


async def test_create_project_requires_auth(client: AsyncClient) -> None:
    """Creating a project without a token returns 401."""
    response = await client.post("/projects", json={"name": "X", "description": ""})
    assert response.status_code == 401


async def test_list_projects_only_returns_accessible(client: AsyncClient) -> None:
    """Listing returns only projects the user is a member of."""
    alice = await register_and_login(client, "alice")
    bob = await register_and_login(client, "bob")

    await client.post(
        "/projects",
        json={"name": "Alice project", "description": ""},
        headers={"Authorization": alice},
    )

    bob_list = await client.get("/projects", headers={"Authorization": bob})
    assert bob_list.status_code == 200
    assert bob_list.json() == []

    alice_list = await client.get("/projects", headers={"Authorization": alice})
    assert len(alice_list.json()) == 1
    assert alice_list.json()[0]["name"] == "Alice project"


async def test_get_project_info(client: AsyncClient) -> None:
    """Owner can fetch project details."""
    auth = await register_and_login(client, "alice")
    created = await client.post(
        "/projects",
        json={"name": "Apollo", "description": "Moon"},
        headers={"Authorization": auth},
    )
    project_id = created.json()["id"]

    response = await client.get(f"/projects/{project_id}/info", headers={"Authorization": auth})
    assert response.status_code == 200
    assert response.json()["id"] == project_id


async def test_get_project_info_not_found(client: AsyncClient) -> None:
    """Fetching a missing project returns 404."""
    auth = await register_and_login(client, "alice")
    response = await client.get("/projects/999/info", headers={"Authorization": auth})
    assert response.status_code == 404


async def test_get_project_info_no_access(client: AsyncClient) -> None:
    """A non-member cannot access another user's project (403)."""
    alice = await register_and_login(client, "alice")
    bob = await register_and_login(client, "bob")
    created = await client.post(
        "/projects",
        json={"name": "Secret", "description": ""},
        headers={"Authorization": alice},
    )
    project_id = created.json()["id"]

    response = await client.get(f"/projects/{project_id}/info", headers={"Authorization": bob})
    assert response.status_code == 403


async def test_update_project(client: AsyncClient) -> None:
    """Owner can update project details."""
    auth = await register_and_login(client, "alice")
    created = await client.post(
        "/projects",
        json={"name": "Old", "description": "old"},
        headers={"Authorization": auth},
    )
    project_id = created.json()["id"]

    response = await client.put(
        f"/projects/{project_id}/info",
        json={"name": "New", "description": "new"},
        headers={"Authorization": auth},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New"
    assert response.json()["description"] == "new"


async def test_delete_project_as_owner(client: AsyncClient) -> None:
    """Owner can delete a project."""
    auth = await register_and_login(client, "alice")
    created = await client.post(
        "/projects",
        json={"name": "Doomed", "description": ""},
        headers={"Authorization": auth},
    )
    project_id = created.json()["id"]

    response = await client.delete(f"/projects/{project_id}", headers={"Authorization": auth})
    assert response.status_code == 204

    after = await client.get(f"/projects/{project_id}/info", headers={"Authorization": auth})
    assert after.status_code == 404


async def test_delete_project_requires_owner(client: AsyncClient) -> None:
    """A non-member cannot delete a project (403)."""
    alice = await register_and_login(client, "alice")
    bob = await register_and_login(client, "bob")
    created = await client.post(
        "/projects",
        json={"name": "Owned", "description": ""},
        headers={"Authorization": alice},
    )
    project_id = created.json()["id"]

    response = await client.delete(f"/projects/{project_id}", headers={"Authorization": bob})
    assert response.status_code == 403
