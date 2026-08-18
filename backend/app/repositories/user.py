from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        q = select(User).where(User.email == email)
        result = await self.session.execute(q)
        return result.scalars().first()

    async def get_by_id(self, id_):
        q = select(User).where(User.id == id_)
        result = await self.session.execute(q)
        return result.scalars().first()

    async def create(
        self,
        email: str,
        hashed_password: str,
        first_name: str,
        last_name: str,
        username: str,
        phone: str,
    ):
        user = User(
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            username=username,
            phone=phone,
        )

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user