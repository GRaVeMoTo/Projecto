"""Data-access layer for projects and memberships."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from projecto.projects.models import (
    Project,
    ProjectMember,
    ProjectRole,
)


class ProjectRepository:
    """Repository encapsulating project persistence operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, name: str, description: str, owner_id: int) -> Project:
        """Persist and return a new project owned by the given user."""
        project = Project(name=name, description=description, owner_id=owner_id)
        self._session.add(project)
        await self._session.flush()
        await self._session.refresh(project)
        return project

    async def get_by_id(self, project_id: int) -> Project | None:
        """Return the project with the given id, or None."""
        return await self._session.get(Project, project_id)

    async def list_for_user(self, user_id: int) -> list[tuple[Project, ProjectRole]]:
        """Return all projects the user is a member of with their role.

        Results are ordered by project id.
        """
        stmt = (
            select(Project, ProjectMember.role)
            .join(ProjectMember, ProjectMember.project_id == Project.id)
            .where(ProjectMember.user_id == user_id)
            .order_by(Project.id)
        )
        result = await self._session.execute(stmt)
        return [(project, role) for project, role in result.all()]

    async def delete(self, project: Project) -> None:
        """Delete a project (cascades to memberships)."""
        await self._session.delete(project)

    async def add_member(self, project_id: int, user_id: int, role: ProjectRole) -> ProjectMember:
        """Add a membership row linking a user to a project with a role."""
        member = ProjectMember(project_id=project_id, user_id=user_id, role=role)
        self._session.add(member)
        await self._session.flush()
        await self._session.refresh(member)
        return member

    async def get_member(self, project_id: int, user_id: int) -> ProjectMember | None:
        """Return the membership of a user in a project, or None."""
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
