"""Business logic for sharing projects with other users."""

from sqlalchemy.ext.asyncio import AsyncSession

from projecto.auth.repository import UserRepository
from projecto.projects.exceptions import ProjectOwnerRequiredError
from projecto.projects.models import ProjectMember, ProjectRole
from projecto.projects.repository import ProjectRepository
from projecto.projects.service import ProjectService
from projecto.sharing.exceptions import (
    AlreadyMemberError,
    InviteeNotFoundError,
)


class SharingService:
    """Service handling project invitations (owner-only access grants)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._projects = ProjectService(session)
        self._project_repo = ProjectRepository(session)
        self._users = UserRepository(session)

    async def invite(self, project_id: int, owner_id: int, invitee_login: str) -> ProjectMember:
        """Grant a user participant access to a project.

        Args:
            project_id: Target project id.
            owner_id: Id of the requesting user (must be the owner).
            invitee_login: Login of the user to invite.

        Returns:
            The created participant membership.

        Raises:
            ProjectNotFoundError: If the project does not exist.
            ProjectAccessDeniedError: If the requester is not a member.
            ProjectOwnerRequiredError: If the requester is not the owner.
            InviteeNotFoundError: If the invited login does not exist.
            AlreadyMemberError: If the invitee is already a member.
        """
        membership = await self._projects.get_membership(project_id, owner_id)
        if membership.role is not ProjectRole.OWNER:
            raise ProjectOwnerRequiredError

        invitee = await self._users.get_by_login(invitee_login)
        if invitee is None:
            raise InviteeNotFoundError

        existing = await self._project_repo.get_member(project_id, invitee.id)
        if existing is not None:
            raise AlreadyMemberError

        member = await self._project_repo.add_member(
            project_id=project_id,
            user_id=invitee.id,
            role=ProjectRole.PARTICIPANT,
        )
        await self._session.commit()
        await self._session.refresh(member)
        return member
