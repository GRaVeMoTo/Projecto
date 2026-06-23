"""Pydantic schemas for documents."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentRead(BaseModel):
    """Public metadata representation of a document."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    filename: str
    content_type: str
    size: int
    uploaded_by: int | None
    created_at: datetime
