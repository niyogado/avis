from pydantic import BaseModel, ConfigDict, Field, field_validator
from uuid import UUID
from datetime import datetime

from app.services.ai_service import PROVIDERS, RESPONSE_STYLES, SUPPORTED_MODELS


class UserSettingsUpdate(BaseModel):
    """Application/AI/notification preferences (never includes secrets)."""

    model_config = ConfigDict(extra="forbid")

    ai_provider: str = Field(default="auto", max_length=32)
    ai_model: str = Field(default="", max_length=128)
    ai_fallback_enabled: bool = True
    ai_response_style: str = Field(default="balanced", max_length=16)
    notify_job_alerts: bool = True
    notify_application_updates: bool = True
    notify_career_recommendations: bool = True
    notify_system: bool = True

    @field_validator("ai_provider")
    @classmethod
    def _check_provider(cls, v):
        if v not in PROVIDERS:
            raise ValueError(f"ai_provider must be one of {list(PROVIDERS)}")
        return v

    @field_validator("ai_response_style")
    @classmethod
    def _check_style(cls, v):
        if v not in RESPONSE_STYLES:
            raise ValueError(f"ai_response_style must be one of {list(RESPONSE_STYLES)}")
        return v

    @field_validator("ai_model")
    @classmethod
    def _check_model(cls, v):
        # Model is validated against the provider in the service (needs both
        # fields together); here we only normalize whitespace.
        return (v or "").strip()


class UserSettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    ai_provider: str
    ai_model: str
    ai_fallback_enabled: bool
    ai_response_style: str
    notify_job_alerts: bool
    notify_application_updates: bool
    notify_career_recommendations: bool
    notify_system: bool
    created_at: datetime
    updated_at: datetime


class AIOptionsOut(BaseModel):
    """Static, safe AI options surfaced to the frontend (no secrets)."""

    providers: list[str]
    models: dict[str, list[str]]
    response_styles: list[str]
    availability: dict[str, bool]
