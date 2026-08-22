from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Any


class CVOut(BaseModel):
    id: UUID
    user_id: UUID
    filename: str
    content_type: str | None
    size: str | None
    path: str
    extracted_text: str | None = None
    analysis_json: dict[str, Any] | None = None
    analysis_status: str | None = None
    analysis_error: str | None = None
    analyzed_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True
