import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func

from app.database.base import Base


class UserSettings(Base):
    """Per-user application behaviour ('How AVIS works for me').

    Career identity lives on profiles.professional_context; this table only
    stores application/AI/notification preferences.
    """

    __tablename__ = "user_settings"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    ai_provider = Column(String(32), nullable=False, server_default="auto")
    ai_model = Column(String(128), nullable=False, server_default="")
    ai_fallback_enabled = Column(Boolean, nullable=False, server_default="true")
    ai_response_style = Column(String(16), nullable=False, server_default="balanced")
    notify_job_alerts = Column(Boolean, nullable=False, server_default="true")
    notify_application_updates = Column(Boolean, nullable=False, server_default="true")
    notify_career_recommendations = Column(Boolean, nullable=False, server_default="true")
    notify_system = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)