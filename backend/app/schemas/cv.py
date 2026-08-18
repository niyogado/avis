from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class CVOut(BaseModel):
    id: UUID
    user_id: UUID
    filename: str
    content_type: str | None
    size: str | None
    path: str
    created_at: datetime

    class Config:
        orm_mode = True
