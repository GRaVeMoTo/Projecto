"""Project HTTP endpoints."""

from fastapi import APIRouter, status

from projecto.auth.dependencies import CurrentUser, DbSession
from projecto.projects.models import ProjectRole
from projecto.projects.schemas import (
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
)
from projecto.projects.service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate, user: CurrentUser, session: DbSession
) -> ProjectRead:
    """Create a new project. The creator becomes the owner."""
    service = ProjectService(session)
    project = await service.create(
        name=payload.name, description=payload.description, owner_id=user.id
    )
    return ProjectRead.from_project(project, ProjectRole.OWNER)


@router.get("", response_model=list[ProjectRead])
async def list_projects(user: CurrentUser, session: DbSession) -> list[ProjectRead]:
    """List all projects accessible to the current user."""
    service = ProjectService(session)
    projects = await service.list_for_user(user.id)
    return [ProjectRead.from_project(project, role) for project, role in projects]


@router.get("/{project_id}/info", response_model=ProjectRead)
async def get_project(project_id: int, user: CurrentUser, session: DbSession) -> ProjectRead:
    """Get a project's details if the user has access."""
    service = ProjectService(session)
    project, role = await service.get_for_user(project_id, user.id)
    return ProjectRead.from_project(project, role)


@router.put("/{project_id}/info", response_model=ProjectRead)
async def update_project(
    project_id: int,
    payload: ProjectUpdate,
    user: CurrentUser,
    session: DbSession,
) -> ProjectRead:
    """Update a project's details (any member may update)."""
    service = ProjectService(session)
    project, role = await service.update(
        project_id=project_id,
        user_id=user.id,
        name=payload.name,
        description=payload.description,
    )
    return ProjectRead.from_project(project, role)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: int, user: CurrentUser, session: DbSession) -> None:
    """Delete a project (owner only)."""
    service = ProjectService(session)
    await service.delete(project_id, user.id)
