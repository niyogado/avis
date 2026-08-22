from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AITrainingCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    category: str | None = Field(default=None, max_length=100)
    is_active: bool = True


class AITrainingOut(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    content: str
    category: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)