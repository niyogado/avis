from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.schemas.ai_training import AITrainingCreate, AITrainingOut
from app.services.chat_service import chat
from app.services.cv_service import CVService, build_career_intent
from app.services.training_service import AITrainingService


router = APIRouter(
    prefix="/api/ai",
    tags=["AI"],
)


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
async def ai_chat(request: ChatRequest, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        response = await chat(request.message, user_id=current_user.id, db=db)
        return {"response": response}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get("/career-intelligence")
async def get_career_intelligence(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    service = CVService(db)
    profile = await service.get_master_profile(current_user.id)

    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No profile available yet. Upload a CV or complete your profile first.")

    profile_data = {
        'headline': profile.headline or '',
        'summary': profile.summary or '',
        'skills': [],
        'soft_skills': [],
        'work_experience': [],
        'education': [],
        'projects': [],
        'certifications': [],
    }

    text_blob = ' '.join(filter(None, [profile.headline, profile.summary, profile.location]))
    keywords = {
        'python': 'python',
        'fastapi': 'fastapi',
        'postgresql': 'postgresql',
        'sql': 'sql',
        'aws': 'aws',
        'docker': 'docker',
        'kubernetes': 'kubernetes',
        'backend': 'backend',
        'api': 'api',
        'data': 'data',
        'product': 'product',
        'cloud': 'cloud',
        'ai': 'ai',
        'machine learning': 'machine learning',
    }
    detected = []
    lower = text_blob.lower()
    for key, label in keywords.items():
        if key in lower:
            detected.append(label)
    profile_data['skills'] = sorted(set(detected))

    strong_evidence = profile_data['skills'][:5] or ['Professional capability', 'Relevant product work']
    gaps = [
        'cloud deployment',
        'production observability',
        'system design',
    ]
    for gap in gaps:
        if gap not in lower:
            break
    else:
        gaps = []

    direction = 'backend engineering'
    if 'ai' in lower or 'machine learning' in lower:
        direction = 'AI engineering'
    elif 'data' in lower:
        direction = 'data engineering'

    intent = build_career_intent(
        profile_data,
        current_role=profile.headline or direction,
        target_roles=[direction],
        learning_priorities=gaps,
        current_intent=(profile.summary or f"I want to grow in {direction}.").strip(),
    )

    return {
        'available': True,
        'career_signal': direction,
        'strong_evidence': strong_evidence,
        'next_gaps': gaps[:3],
        'summary': f"Your strongest professional evidence is concentrated around {direction}.",
        'ai_recommendation': intent,
    }


@router.get("/opportunities")
async def get_opportunities(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    service = CVService(db)
    profile = await service.get_master_profile(current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No profile is available yet.")

    jobs = []
    profile_text = ' '.join(filter(None, [profile.headline, profile.summary, profile.location])).lower()
    if 'python' in profile_text or 'backend' in profile_text or 'fastapi' in profile_text:
        jobs.append({
            'title': 'Backend Engineer',
            'company': 'Not configured',
            'location': 'No live provider configured',
            'fit': 'Profile-driven only',
            'skills': ['Python', 'FastAPI', 'PostgreSQL'],
            'gap': 'No live job source is configured',
            'status': 'unavailable',
        })

    return {
        'available': False,
        'jobs': jobs,
        'message': 'No live job source is configured for AVIS. Add a provider to enable job search.'
    }


@router.post("/training", response_model=AITrainingOut, status_code=status.HTTP_201_CREATED)
async def create_training(
    payload: AITrainingCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AITrainingService(db)
    return await service.create_training(current_user.id, payload)


@router.get("/training", response_model=list[AITrainingOut])
async def list_training(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AITrainingService(db)
    return await service.list_trainings(current_user.id)

    