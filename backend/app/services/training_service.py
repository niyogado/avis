from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_training import AITraining
from app.schemas.ai_training import AITrainingCreate


class AITrainingService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_training(
        self,
        user_id,
        payload: AITrainingCreate,
    ):
        training = AITraining(
            user_id=user_id,
            title=payload.title,
            content=payload.content,
            category=payload.category,
            is_active=payload.is_active,
        )

        self.db.add(training)
        await self.db.commit()
        await self.db.refresh(training)
        return training

    async def list_trainings(self, user_id, *, active_only: bool = True):
        stmt = select(AITraining).where(AITraining.user_id == user_id)
        if active_only:
            stmt = stmt.where(AITraining.is_active.is_(True))
        stmt = stmt.order_by(AITraining.updated_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_training(self, user_id, training_id):
        stmt = select(AITraining).where(
            AITraining.id == training_id,
            AITraining.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()