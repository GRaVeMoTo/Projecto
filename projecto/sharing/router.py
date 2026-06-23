"""Project sharing endpoints."""

from fastapi import APIRouter, Query, status

from projecto.auth.dependencies import CurrentUser, DbSession
from projecto.sharing.schemas import InvitationRead
from projecto.sharing.service import SharingService

router = APIRouter(prefix="/projects", tags=["sharing"])


@router.post(
    "/{project_id}/invite",
    response_model=InvitationRead,
    status_code=status.HTTP_201_CREATED,
)
async def invite_user(
    project_id: int,
    user: CurrentUser,
    session: DbSession,
    invitee_login: str = Query(alias="user", description="Login of the user to invite"),
) -> InvitationRead:
    """Grant another user participant access to a project (owner only)."""
    service = SharingService(session)
    member = await service.invite(
        project_id=project_id,
        owner_id=user.id,
        invitee_login=invitee_login,
    )
    return InvitationRead(
        project_id=member.project_id,
        user_id=member.user_id,
        login=invitee_login,
        role=member.role,
    )
