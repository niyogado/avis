from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import UserCreate, UserOut,userLogin
from app.services.auth_service import AuthService
from app.database.session import get_db
from app.schemas.auth import Token
from fastapi import HTTPException
from fastapi import status
from app.utils.jwt import create_access_token



router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user = await service.register_user(user_in)
    return user


@router.post("/login", response_model=Token)
async def login(payload: userLogin, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user = await service.authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(subject=str(user.id))
    return {"access_token": access_token, "token_type": "bearer"}
