import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func

from app.database.base import Base


class CV(Base):
    __tablename__ = "cvs"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(1024), nullable=False)
    content_type = Column(String(128), nullable=True)
    size = Column(String(64), nullable=True)
    path = Column(String(2048), nullable=False)
    extracted_text = Column(Text, nullable=True)
    analysis_json = Column(JSON, nullable=True)
    analysis_status = Column(String(32), nullable=True)
    analysis_error = Column(Text, nullable=True)
    analyzed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
