from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.auth import get_current_user
from app.database.session import get_db
from app.services.cv_service import CVService
from app.schemas.cv import CVOut
from fastapi import status

router = APIRouter(prefix="/cv")


@router.post("/upload", response_model=CVOut, status_code=status.HTTP_201_CREATED)
async def upload_cv(file: UploadFile = File(...), current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    service = CVService(db)
    cv = await service.save_cv(current_user.id, file)
    return cv


@router.get("/", response_model=list[CVOut])
async def list_cvs(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    repo = CVService(db)
    cvs = await repo.repo.list_for_user(current_user.id)
    return cvs
