"""Pydantic schemas for project sharing."""

from pydantic import BaseModel

from projecto.projects.models import ProjectRole


class InvitationRead(BaseModel):
    """Result of inviting a user to a project."""

    project_id: int
    user_id: int
    login: str
    role: ProjectRole
