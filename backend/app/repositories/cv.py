from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.cv import CV


class CVRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, *, user_id, filename, path, content_type=None, size=None) -> CV:
        cv = CV(user_id=user_id, filename=filename, path=path, content_type=content_type, size=size)
        self.session.add(cv)
        try:
            await self.session.commit()
            await self.session.refresh(cv)
        except IntegrityError:
            await self.session.rollback()
            raise
        return cv

    async def list_for_user(self, user_id):
        q = select(CV).where(CV.user_id == user_id)
        result = await self.session.execute(q)
        return result.scalars().all()
