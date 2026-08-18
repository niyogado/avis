from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.profile import Profile


class ProfileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id):
        q = select(Profile).where(Profile.user_id == user_id)
        result = await self.session.execute(q)
        return result.scalars().first()

    async def create(self, *, user_id, **data) -> Profile:
        profile = Profile(user_id=user_id, **data)
        self.session.add(profile)
        try:
            await self.session.commit()
            await self.session.refresh(profile)
        except IntegrityError:
            await self.session.rollback()
            raise
        return profile

    async def update(self, profile: Profile, **data) -> Profile:
        for k, v in data.items():
            setattr(profile, k, v)
        try:
            await self.session.commit()
            await self.session.refresh(profile)
        except IntegrityError:
            await self.session.rollback()
            raise
        return profile
