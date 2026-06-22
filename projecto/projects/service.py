"""Business logic for projects."""

from sqlalchemy.ext.asyncio import AsyncSession

from projecto.projects.exceptions import (
    ProjectAccessDeniedError,
    ProjectNotFoundError,
    ProjectOwnerRequiredError,
)
from projecto.projects.models import Project, ProjectMember, ProjectRole
from projecto.projects.repository import ProjectRepository


class ProjectService:
    """Service handling project CRUD and access control."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._projects = ProjectRepository(session)

    async def create(self, name: str, description: str, owner_id: int) -> Project:
        """Create a project and register the creator as its owner.

        Args:
            name: Project name.
            description: Project description.
            owner_id: Id of the creating user (becomes owner).

        Returns:
            The newly created project.
        """
        project = await self._projects.create(name=name, description=description, owner_id=owner_id)
        await self._projects.add_member(
            project_id=project.id, user_id=owner_id, role=ProjectRole.OWNER
        )
        await self._session.commit()
        await self._session.refresh(project)
        return project

    async def list_for_user(self, user_id: int) -> list[tuple[Project, ProjectRole]]:
        """Return all projects the user can access with their role."""
        return await self._projects.list_for_user(user_id)

    async def get_membership(self, project_id: int, user_id: int) -> ProjectMember:
        """Resolve the user's membership in a project.

        Args:
            project_id: Target project id.
            user_id: Requesting user id.

        Returns:
            The user's membership.

        Raises:
            ProjectNotFoundError: If the project does not exist.
            ProjectAccessDeniedError: If the user is not a member.
        """
        project = await self._projects.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError

        member = await self._projects.get_member(project_id, user_id)
        if member is None:
            raise ProjectAccessDeniedError
        return member

    async def get_for_user(self, project_id: int, user_id: int) -> tuple[Project, ProjectRole]:
        """Return a project and the requesting user's role within it.

        Raises:
            ProjectNotFoundError: If the project does not exist.
            ProjectAccessDeniedError: If the user has no access.
        """
        member = await self.get_membership(project_id, user_id)
        project = await self._projects.get_by_id(project_id)
        assert project is not None  # guaranteed by get_membership
        return project, member.role

    async def update(
        self, project_id: int, user_id: int, name: str, description: str
    ) -> tuple[Project, ProjectRole]:
        """Update a project's details.

        Any member (owner or participant) may update details.

        Raises:
            ProjectNotFoundError: If the project does not exist.
            ProjectAccessDeniedError: If the user has no access.
        """
        member = await self.get_membership(project_id, user_id)
        project = await self._projects.get_by_id(project_id)
        assert project is not None
        project.name = name
        project.description = description
        await self._session.commit()
        await self._session.refresh(project)
        return project, member.role

    async def delete(self, project_id: int, user_id: int) -> None:
        """Delete a project. Only the owner may do this.

        Raises:
            ProjectNotFoundError: If the project does not exist.
            ProjectAccessDeniedError: If the user has no access.
            ProjectOwnerRequiredError: If the user is not the owner.
        """
        member = await self.get_membership(project_id, user_id)
        if member.role is not ProjectRole.OWNER:
            raise ProjectOwnerRequiredError

        project = await self._projects.get_by_id(project_id)
        assert project is not None
        await self._projects.delete(project)
        await self._session.commit()
