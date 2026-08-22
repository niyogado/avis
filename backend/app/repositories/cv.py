from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.cv import CV


class CVRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, *, user_id, filename, path, content_type=None, size=None, extracted_text=None) -> CV:
        cv = CV(
            user_id=user_id,
            filename=filename,
            path=path,
            content_type=content_type,
            size=size,
            extracted_text=extracted_text,
        )
        self.session.add(cv)
        try:
            await self.session.commit()
            await self.session.refresh(cv)
        except IntegrityError:
            await self.session.rollback()
            raise
        return cv

    async def list_for_user(self, user_id):
        q = select(CV).where(CV.user_id == user_id).order_by(CV.created_at.desc())
        result = await self.session.execute(q)
        return result.scalars().all()

    async def get_for_user(self, user_id, cv_id):
        q = select(CV).where(CV.user_id == user_id, CV.id == cv_id)
        result = await self.session.execute(q)
        return result.scalar_one_or_none()

    async def update_analysis(self, cv: CV, *, analysis_json=None, status=None, error=None, analyzed_at=None) -> CV:
        cv.analysis_json = analysis_json
        cv.analysis_status = status
        cv.analysis_error = error
        cv.analyzed_at = analyzed_at
        self.session.add(cv)
        await self.session.commit()
        await self.session.refresh(cv)
        return cv
