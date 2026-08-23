import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func

from app.database.base import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    full_name = Column(String(255), nullable=True)
    headline = Column(String(255), nullable=True)
    summary = Column(String, nullable=True)
    location = Column(String(255), nullable=True)
    phone = Column(String(30), nullable=True)
    avatar_url = Column(String(2048), nullable=True)
    # User-confirmed professional identity (CV Editor). Highest-priority
    # source for AVIS context: overrides CV evidence and AI inference.
    professional_context = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
