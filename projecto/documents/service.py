"""Business logic for documents."""

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from projecto.documents.exceptions import DocumentNotFoundError
from projecto.documents.models import Document
from projecto.documents.repository import DocumentRepository
from projecto.projects.service import ProjectService
from projecto.storage import Storage, get_storage


@dataclass(frozen=True)
class DocumentContent:
    """A document's binary payload together with its metadata."""

    filename: str
    content_type: str
    data: bytes


class DocumentService:
    """Service handling document CRUD scoped to project access."""

    def __init__(self, session: AsyncSession, storage: Storage | None = None) -> None:
        self._session = session
        self._documents = DocumentRepository(session)
        self._projects = ProjectService(session)
        self._storage = storage if storage is not None else get_storage()

    async def list_for_project(self, project_id: int, user_id: int) -> list[Document]:
        """List a project's documents if the user has access.

        Raises:
            ProjectNotFoundError / ProjectAccessDeniedError via ProjectService.
        """
        await self._projects.get_membership(project_id, user_id)
        return await self._documents.list_for_project(project_id)

    async def upload(
        self,
        project_id: int,
        user_id: int,
        filename: str,
        content_type: str,
        data: bytes,
    ) -> Document:
        """Store a file and create its metadata row.

        Requires the user to be a member of the project.
        """
        await self._projects.get_membership(project_id, user_id)
        key = await self._storage.save(data)
        document = await self._documents.create(
            project_id=project_id,
            filename=filename,
            content_type=content_type or "application/octet-stream",
            size=len(data),
            storage_key=key,
            uploaded_by=user_id,
        )
        await self._session.commit()
        await self._session.refresh(document)
        return document

    async def _get_accessible(self, document_id: int, user_id: int) -> Document:
        """Return a document if the user can access its project."""
        document = await self._documents.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError
        # Reuse project access control; hide existence on no access.
        await self._projects.get_membership(document.project_id, user_id)
        return document

    async def get_metadata(self, document_id: int, user_id: int) -> Document:
        """Return a document's metadata if accessible."""
        return await self._get_accessible(document_id, user_id)

    async def download(self, document_id: int, user_id: int) -> DocumentContent:
        """Return a document's content and metadata if accessible."""
        document = await self._get_accessible(document_id, user_id)
        try:
            data = await self._storage.load(document.storage_key)
        except FileNotFoundError:
            raise DocumentNotFoundError from None
        return DocumentContent(
            filename=document.filename,
            content_type=document.content_type,
            data=data,
        )

    async def replace(
        self,
        document_id: int,
        user_id: int,
        filename: str,
        content_type: str,
        data: bytes,
    ) -> Document:
        """Replace a document's content, removing the previous blob."""
        document = await self._get_accessible(document_id, user_id)
        old_key = document.storage_key
        new_key = await self._storage.save(data)
        document.filename = filename
        document.content_type = content_type or "application/octet-stream"
        document.size = len(data)
        document.storage_key = new_key
        await self._session.commit()
        await self._session.refresh(document)
        await self._storage.delete(old_key)
        return document

    async def delete(self, document_id: int, user_id: int) -> None:
        """Delete a document's metadata and its stored blob."""
        document = await self._get_accessible(document_id, user_id)
        key = document.storage_key
        await self._documents.delete(document)
        await self._session.commit()
        await self._storage.delete(key)
