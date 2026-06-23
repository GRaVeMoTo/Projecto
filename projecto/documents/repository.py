"""Data-access layer for documents."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from projecto.documents.models import Document


class DocumentRepository:
    """Repository encapsulating document persistence operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        project_id: int,
        filename: str,
        content_type: str,
        size: int,
        storage_key: str,
        uploaded_by: int | None,
    ) -> Document:
        """Persist and return a new document metadata row."""
        document = Document(
            project_id=project_id,
            filename=filename,
            content_type=content_type,
            size=size,
            storage_key=storage_key,
            uploaded_by=uploaded_by,
        )
        self._session.add(document)
        await self._session.flush()
        await self._session.refresh(document)
        return document

    async def get_by_id(self, document_id: int) -> Document | None:
        """Return the document with the given id, or None."""
        return await self._session.get(Document, document_id)

    async def list_for_project(self, project_id: int) -> list[Document]:
        """Return all documents belonging to a project, ordered by id."""
        stmt = select(Document).where(Document.project_id == project_id).order_by(Document.id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, document: Document) -> None:
        """Delete a document metadata row."""
        await self._session.delete(document)
