"""Pydantic schemas for projects."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from projecto.projects.models import ProjectRole

if TYPE_CHECKING:
    from projecto.projects.models import Project


class ProjectCreate(BaseModel):
    """Request body for creating a project."""

    name: str = Field(min_length=1, max_length=255, examples=["Website redesign"])
    description: str = Field(default="", max_length=10_000, examples=["Q3 marketing site"])


class ProjectUpdate(BaseModel):
    """Request body for updating a project's details."""

    name: str = Field(min_length=1, max_length=255, examples=["Website redesign"])
    description: str = Field(default="", max_length=10_000, examples=["Q3 marketing site"])


class ProjectMemberRead(BaseModel):
    """Public representation of a project membership."""

    model_config = ConfigDict(from_attributes=True)

    user_id: int
    role: ProjectRole


class ProjectRead(BaseModel):
    """Public representation of a project, including the caller's role."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    owner_id: int
    created_at: datetime
    role: ProjectRole

    @classmethod
    def from_project(cls, project: Project, role: ProjectRole) -> ProjectRead:
        """Build a ProjectRead from a project and the caller's role."""
        return cls(
            id=project.id,
            name=project.name,
            description=project.description,
            owner_id=project.owner_id,
            created_at=project.created_at,
            role=role,
        )
