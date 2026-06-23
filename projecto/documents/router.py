"""Document HTTP endpoints."""

from fastapi import APIRouter, UploadFile, status
from fastapi.responses import Response

from projecto.auth.dependencies import CurrentUser, DbSession
from projecto.documents.schemas import DocumentRead
from projecto.documents.service import DocumentService

# Project-scoped document collection endpoints.
project_documents_router = APIRouter(prefix="/projects", tags=["documents"])

# Individual document endpoints.
documents_router = APIRouter(prefix="/documents", tags=["documents"])


@project_documents_router.get("/{project_id}/documents", response_model=list[DocumentRead])
async def list_documents(
    project_id: int, user: CurrentUser, session: DbSession
) -> list[DocumentRead]:
    """List all documents belonging to a project (if accessible)."""
    service = DocumentService(session)
    documents = await service.list_for_project(project_id, user.id)
    return [DocumentRead.model_validate(doc) for doc in documents]


@project_documents_router.post(
    "/{project_id}/documents",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    project_id: int,
    file: UploadFile,
    user: CurrentUser,
    session: DbSession,
) -> DocumentRead:
    """Upload a document to a project."""
    service = DocumentService(session)
    data = await file.read()
    document = await service.upload(
        project_id=project_id,
        user_id=user.id,
        filename=file.filename or "untitled",
        content_type=file.content_type or "application/octet-stream",
        data=data,
    )
    return DocumentRead.model_validate(document)


@documents_router.get("/{document_id}")
async def download_document(document_id: int, user: CurrentUser, session: DbSession) -> Response:
    """Download a document's content (if accessible)."""
    service = DocumentService(session)
    content = await service.download(document_id, user.id)
    return Response(
        content=content.data,
        media_type=content.content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{content.filename}"',
        },
    )


@documents_router.put("/{document_id}", response_model=DocumentRead)
async def replace_document(
    document_id: int,
    file: UploadFile,
    user: CurrentUser,
    session: DbSession,
) -> DocumentRead:
    """Replace a document's content."""
    service = DocumentService(session)
    data = await file.read()
    document = await service.replace(
        document_id=document_id,
        user_id=user.id,
        filename=file.filename or "untitled",
        content_type=file.content_type or "application/octet-stream",
        data=data,
    )
    return DocumentRead.model_validate(document)


@documents_router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: int, user: CurrentUser, session: DbSession) -> None:
    """Delete a document from its project."""
    service = DocumentService(session)
    await service.delete(document_id, user.id)
