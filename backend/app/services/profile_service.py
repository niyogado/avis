from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.profile import ProfileRepository
from app.schemas.profile import ProfileCreate, ProfileUpdate


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
