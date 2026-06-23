"""Integration tests for the document endpoints."""

from httpx import AsyncClient

from projecto.storage import LocalStorage
from tests.conftest import register_and_login


async def _create_project(client: AsyncClient, auth: str, name: str = "Apollo") -> int:
    """Create a project and return its id."""
    response = await client.post(
        "/projects",
        json={"name": name, "description": ""},
        headers={"Authorization": auth},
    )
    return int(response.json()["id"])


async def test_upload_and_list_documents(client: AsyncClient) -> None:
    """Uploading a document returns 201 and it appears in the listing."""
    auth = await register_and_login(client, "alice")
    project_id = await _create_project(client, auth)

    upload = await client.post(
        f"/projects/{project_id}/documents",
        files={"file": ("notes.txt", b"hello world", "text/plain")},
        headers={"Authorization": auth},
    )
    assert upload.status_code == 201
    body = upload.json()
    assert body["filename"] == "notes.txt"
    assert body["content_type"] == "text/plain"
    assert body["size"] == len(b"hello world")
    assert body["project_id"] == project_id

    listing = await client.get(f"/projects/{project_id}/documents", headers={"Authorization": auth})
    assert listing.status_code == 200
    assert len(listing.json()) == 1


async def test_upload_requires_access(client: AsyncClient) -> None:
    """A non-member cannot upload to another user's project (403)."""
    alice = await register_and_login(client, "alice")
    bob = await register_and_login(client, "bob")
    project_id = await _create_project(client, alice)

    response = await client.post(
        f"/projects/{project_id}/documents",
        files={"file": ("x.txt", b"data", "text/plain")},
        headers={"Authorization": bob},
    )
    assert response.status_code == 403


async def test_list_documents_requires_access(client: AsyncClient) -> None:
    """A non-member cannot list another project's documents."""
    alice = await register_and_login(client, "alice")
    bob = await register_and_login(client, "bob")
    project_id = await _create_project(client, alice)

    response = await client.get(f"/projects/{project_id}/documents", headers={"Authorization": bob})
    assert response.status_code == 403


async def test_upload_document_project_not_found(client: AsyncClient) -> None:
    """Uploading to a missing project returns 404 with app error details."""
    auth = await register_and_login(client, "alice")
    response = await client.post(
        "/projects/999/documents",
        files={"file": ("notes.txt", b"hello world", "text/plain")},
        headers={"Authorization": auth},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found."}


async def test_download_document(client: AsyncClient) -> None:
    """Downloading returns the original bytes and content type."""
    auth = await register_and_login(client, "alice")
    project_id = await _create_project(client, auth)
    upload = await client.post(
        f"/projects/{project_id}/documents",
        files={"file": ("data.bin", b"\x00\x01\x02binary", "application/octet-stream")},
        headers={"Authorization": auth},
    )
    document_id = upload.json()["id"]

    download = await client.get(f"/documents/{document_id}", headers={"Authorization": auth})
    assert download.status_code == 200
    assert download.content == b"\x00\x01\x02binary"
    assert 'filename="data.bin"' in download.headers["content-disposition"]


async def test_download_document_not_found(client: AsyncClient) -> None:
    """Downloading a missing document returns 404."""
    auth = await register_and_login(client, "alice")
    response = await client.get("/documents/999", headers={"Authorization": auth})
    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found."}


async def test_download_document_no_access(client: AsyncClient) -> None:
    """A non-member cannot download another project's document (403)."""
    alice = await register_and_login(client, "alice")
    bob = await register_and_login(client, "bob")
    project_id = await _create_project(client, alice)
    upload = await client.post(
        f"/projects/{project_id}/documents",
        files={"file": ("secret.txt", b"top secret", "text/plain")},
        headers={"Authorization": alice},
    )
    document_id = upload.json()["id"]

    response = await client.get(f"/documents/{document_id}", headers={"Authorization": bob})
    assert response.status_code == 403


async def test_replace_document(client: AsyncClient) -> None:
    """Replacing a document updates content and metadata."""
    auth = await register_and_login(client, "alice")
    project_id = await _create_project(client, auth)
    upload = await client.post(
        f"/projects/{project_id}/documents",
        files={"file": ("v1.txt", b"version one", "text/plain")},
        headers={"Authorization": auth},
    )
    document_id = upload.json()["id"]

    replace = await client.put(
        f"/documents/{document_id}",
        files={"file": ("v2.txt", b"version two!", "text/plain")},
        headers={"Authorization": auth},
    )
    assert replace.status_code == 200
    assert replace.json()["filename"] == "v2.txt"
    assert replace.json()["size"] == len(b"version two!")

    download = await client.get(f"/documents/{document_id}", headers={"Authorization": auth})
    assert download.content == b"version two!"


async def test_replace_document_requires_access(client: AsyncClient) -> None:
    """A non-member cannot replace another project's document."""
    alice = await register_and_login(client, "alice")
    bob = await register_and_login(client, "bob")
    project_id = await _create_project(client, alice)
    upload = await client.post(
        f"/projects/{project_id}/documents",
        files={"file": ("secret.txt", b"version one", "text/plain")},
        headers={"Authorization": alice},
    )
    document_id = upload.json()["id"]

    response = await client.put(
        f"/documents/{document_id}",
        files={"file": ("hack.txt", b"tampered", "text/plain")},
        headers={"Authorization": bob},
    )
    assert response.status_code == 403


async def test_delete_document(client: AsyncClient) -> None:
    """Deleting a document removes it (subsequent download is 404)."""
    auth = await register_and_login(client, "alice")
    project_id = await _create_project(client, auth)
    upload = await client.post(
        f"/projects/{project_id}/documents",
        files={"file": ("gone.txt", b"bye", "text/plain")},
        headers={"Authorization": auth},
    )
    document_id = upload.json()["id"]

    delete = await client.delete(f"/documents/{document_id}", headers={"Authorization": auth})
    assert delete.status_code == 204

    after = await client.get(f"/documents/{document_id}", headers={"Authorization": auth})
    assert after.status_code == 404

    listing = await client.get(f"/projects/{project_id}/documents", headers={"Authorization": auth})
    assert listing.status_code == 200
    assert listing.json() == []


async def test_delete_document_requires_access(client: AsyncClient) -> None:
    """A non-member cannot delete another project's document."""
    alice = await register_and_login(client, "alice")
    bob = await register_and_login(client, "bob")
    project_id = await _create_project(client, alice)
    upload = await client.post(
        f"/projects/{project_id}/documents",
        files={"file": ("secret.txt", b"keep me", "text/plain")},
        headers={"Authorization": alice},
    )
    document_id = upload.json()["id"]

    response = await client.delete(f"/documents/{document_id}", headers={"Authorization": bob})
    assert response.status_code == 403


async def test_download_document_missing_blob_returns_not_found(client: AsyncClient) -> None:
    """Missing storage blobs are surfaced as app-level 404 errors."""
    auth = await register_and_login(client, "alice")
    project_id = await _create_project(client, auth)
    storage = LocalStorage()
    existing_files = set(storage._root.iterdir())
    upload = await client.post(
        f"/projects/{project_id}/documents",
        files={"file": ("lost.txt", b"hello", "text/plain")},
        headers={"Authorization": auth},
    )
    document = upload.json()

    new_files = set(storage._root.iterdir()) - existing_files
    assert len(new_files) == 1
    storage_file = new_files.pop()
    storage_file.unlink()

    response = await client.get(f"/documents/{document['id']}", headers={"Authorization": auth})
    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found."}


async def test_documents_require_auth(client: AsyncClient) -> None:
    """Document endpoints reject unauthenticated requests with 401."""
    response = await client.get("/documents/1")
    assert response.status_code == 401
