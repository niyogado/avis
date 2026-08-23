from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime


class ProfileBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileOut(ProfileBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="forbid")


PROFESSIONAL_LEVELS = {"student", "entry-level", "junior", "mid", "senior", "lead", "principal"}
WORK_PREFERENCES = {"remote", "hybrid", "onsite", "flexible"}


def _clean_str(value: str) -> str:
    return value.strip()


def _clean_list(value: list[str]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = item.strip()
        key = text.lower()
        if not text or key in seen:
            continue
        seen.add(key)
        cleaned.append(text)
    return cleaned


class ProfessionalContextPayload(BaseModel):
    """User-confirmed professional identity (CV Editor / Profile page).

    These fields are USER-CONFIRMED facts/intent. They take priority over
    CV evidence and AI inference everywhere AVIS builds context.
    """

    model_config = ConfigDict(extra="forbid")

    professional_level: Optional[str] = None
    primary_role: Optional[str] = Field(default=None, max_length=120)
    target_roles: list[str] = Field(default_factory=list, max_length=8)
    confirmed_skills: list[str] = Field(default_factory=list, max_length=60)
    career_interests: list[str] = Field(default_factory=list, max_length=8)
    preferred_locations: list[str] = Field(default_factory=list, max_length=10)
    work_preference: Optional[str] = None
    # Confirmed detail sections (Profile page). Each entry is a free-text line
    # the user has reviewed — overriding any AI/CV suggestion with the same meaning.
    experience: list[str] = Field(default_factory=list, max_length=20)
    education: list[str] = Field(default_factory=list, max_length=12)
    projects: list[str] = Field(default_factory=list, max_length=15)
    certifications: list[str] = Field(default_factory=list, max_length=15)
    achievements: list[str] = Field(default_factory=list, max_length=15)
    career_goals: Optional[str] = Field(default=None, max_length=2000)

    @field_validator("professional_level")
    @classmethod
    def _check_level(cls, v):
        if v is None:
            return None
        cleaned = v.strip().lower()
        if cleaned and cleaned not in PROFESSIONAL_LEVELS:
            raise ValueError(f"professional_level must be one of {sorted(PROFESSIONAL_LEVELS)}")
        return cleaned or None

    @field_validator("work_preference")
    @classmethod
    def _check_work_pref(cls, v):
        if v is None:
            return None
        cleaned = v.strip().lower()
        if cleaned and cleaned not in WORK_PREFERENCES:
            raise ValueError(f"work_preference must be one of {sorted(WORK_PREFERENCES)}")
        return cleaned or None

    @field_validator("primary_role", "career_goals")
    @classmethod
    def _clean_text(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator(
        "target_roles", "confirmed_skills", "career_interests", "preferred_locations",
        "experience", "education", "projects", "certifications", "achievements",
    )
    @classmethod
    def _clean_lists(cls, v):
        return _clean_list(v)


class ProfessionalContextOut(ProfessionalContextPayload):
    confirmed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, extra="forbid")
