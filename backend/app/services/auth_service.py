from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.profile import ProfileRepository
from app.repositories.user import UserRepository
from app.utils.security import hash_password, verify_password
from app.schemas.auth import UserCreate


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)
        self.profile_repo = ProfileRepository(db)

    async def register_user(self, user_in: UserCreate):
        existing = await self.repo.get_by_email(user_in.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists",
            )

        hashed = hash_password(user_in.password)
        user = await self.repo.create(
            email=user_in.email,
            hashed_password=hashed,
            first_name=user_in.first_name,
            last_name=user_in.last_name,
            username=user_in.username,
            phone=user_in.phone,
        )

        full_name = ' '.join(filter(None, [user.first_name, user.last_name])).strip() or user.username

        await self.profile_repo.create(
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=full_name,
            headline='',
            summary='',
            location='',
            phone=user.phone,
            avatar_url='',
        )

        return user

    async def authenticate_user(self, email: str, password: str):
        user = await self.repo.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
