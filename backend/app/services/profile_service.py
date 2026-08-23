from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.profile import ProfileRepository
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfessionalContextPayload


class ProfileService:
    def __init__(self, db: AsyncSession):
        self.repo = ProfileRepository(db)

    async def get_profile_for_user(self, user_id):
        return await self.repo.get_by_user_id(user_id)

    async def upsert_profile(self, user_id, payload: ProfileCreate | ProfileUpdate):
        existing = await self.repo.get_by_user_id(user_id)
        data = payload.model_dump(exclude_unset=True, exclude_none=True)
        if existing:
            return await self.repo.update(existing, **data)
        return await self.repo.create(user_id=user_id, **data)

    async def get_professional_context(self, user_id) -> dict | None:
        profile = await self.repo.get_by_user_id(user_id)
        if not profile:
            return None
        context = profile.professional_context
        return context if isinstance(context, dict) else None

    async def save_professional_context(self, user_id, payload: ProfessionalContextPayload) -> dict:
        """Persist USER-CONFIRMED professional identity (CV Editor)."""
        profile = await self.repo.get_by_user_id(user_id)
        confirmed = payload.model_dump()
        confirmed["confirmed_at"] = datetime.now(timezone.utc).isoformat()
        data = {"professional_context": confirmed}
        if profile:
            await self.repo.update(profile, **data)
        else:
            await self.repo.create(user_id=user_id, **data)
        return confirmed
