import json

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.database.session import get_db
from app.services.cv_service import (
    CVService,
    analyze_cv_with_ejochat,
    build_career_intent,
    validate_cv_analysis,
)
from app.schemas.ai_training import AITrainingCreate
from app.services.training_service import AITrainingService
from app.schemas.cv import CVOut
from app.utils.storage import StorageError


class CareerIntentPayload(BaseModel):
    current_intent: str = Field(..., min_length=2, max_length=255)

router = APIRouter(prefix="/cv")


@router.post("/upload", response_model=CVOut, status_code=status.HTTP_201_CREATED)
async def upload_cv(file: UploadFile = File(...), current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    from app.config.settings import settings

    allowed_types = set(settings.ALLOWED_UPLOAD_TYPES)
    if file.content_type not in allowed_types and not file.filename.lower().endswith(('.txt', '.pdf', '.docx')):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large")

    service = CVService(db)
    try:
        cv = await service.save_cv(current_user.id, file.filename, content, content_type=file.content_type)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return cv


@router.post("/{cv_id}/analyze", response_model=CVOut)
async def analyze_cv(
    cv_id: str,
    job_title: str | None = Form(default=None),
    job_description: str | None = Form(default=None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CVService(db)
    cv = await service.get_cv_for_user(current_user.id, cv_id)
    if not cv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV not found")

    extracted_text = (cv.extracted_text or '').strip()
    if not extracted_text:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="This CV has no extracted text to analyze.")

        profile = service.extract_profile_from_text(extracted_text)

    try:
        structured = validate_cv_analysis(analyze_cv_with_ejochat(extracted_text), profile)
    except (json.JSONDecodeError, ValueError) as exc:
        await service.mark_analysis_error(cv, str(exc))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Avis returned unparsable structured analysis. Please retry.") from exc
    except RuntimeError as exc:
        await service.mark_analysis_error(cv, str(exc))
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Avis is temporarily unavailable. Please retry in a moment.") from exc
    except Exception as exc:
        await service.mark_analysis_error(cv, "EjoChat analysis failed.")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Avis analysis failed. Please retry.") from exc

    analysis = service.match_profile_to_target(profile, job_title=job_title, job_description=job_description)
    evidence = structured['cv_evidence']
    interpretation = structured['ai_interpretation']
    existing_intent = ''
    if isinstance(cv.analysis_json, dict):
        existing_intent = str((cv.analysis_json.get('career_intent') or {}).get('current_intent') or '').strip()

    intent = build_career_intent(
        profile,
        current_role=profile.get('headline') or '',
        target_roles=interpretation.get('career_directions', []),
        learning_priorities=interpretation.get('gaps') or [],
        current_intent=existing_intent,
    )

    structured_training = {
        'skills': evidence.get('skills') or profile.get('skills', []),
        'career_signals': evidence.get('career_signals') or interpretation.get('career_signals') or [],
        'strengths': interpretation.get('strengths') or analysis.get('strong_areas', []),
        'gaps': interpretation.get('gaps') or analysis.get('potential_gaps', []),
        'career_directions': interpretation.get('career_directions') or [],
        'achievements': evidence.get('achievements') or [],
        'insights': evidence.get('insights') or interpretation.get('insights') or [],
    }

    training_service = AITrainingService(db)
    training_summary = (
        'Skills: ' + ', '.join(map(str, structured_training['skills'][:10])) + '. '
        'Career signals: ' + ', '.join(map(str, structured_training['career_signals'][:5])) + '. '
        'Strengths: ' + ', '.join(map(str, structured_training['strengths'][:5])) + '. '
        'Gaps: ' + ', '.join(map(str, structured_training['gaps'][:5])) + '. '
        'AI career directions, not confirmed user choices: ' + ', '.join(map(str, structured_training['career_directions'][:5]))
    )
    await training_service.create_training(
        current_user.id,
        AITrainingCreate(
            title='CV analysis',
            content=training_summary,
            category='cv_analysis',
            is_active=True,
        ),
    )

    persisted_analysis = {
        'profile': profile,
        'match_analysis': analysis,
        'search_profile': build_search_profile(profile, job_title=job_title, job_description=job_description),
        'career_intent': intent,
        'cv_evidence': evidence,
        'ai_interpretation': interpretation,
    }
    return await service.save_analysis(current_user.id, cv, persisted_analysis)


@router.post("/analyze", response_model=CVOut)
async def upload_and_analyze_cv(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cv = await upload_cv(file, current_user=current_user, db=db)
    return await analyze_cv(str(cv.id), current_user=current_user, db=db)


@router.post("/match")
async def match_cv_against_target(
    payload: dict,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CVService(db)
    context = await service.get_professional_context(current_user.id)
    evidence = context.get('cv_evidence') or {}
    if not evidence and not context.get('profile', {}).get('headline'):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No master profile found. Upload a CV first.")

    profile = {
        'full_name': context['profile'].get('full_name'),
        'headline': context['profile'].get('headline'),
        'location': context['profile'].get('location'),
        'summary': context['profile'].get('summary'),
        'skills': evidence.get('skills') or context.get('skills') or [],
        'soft_skills': [],
        'work_experience': evidence.get('experience') or context.get('experience') or [],
        'projects': evidence.get('projects') or [],
        'education': evidence.get('education') or [],
        'certifications': evidence.get('certifications') or [],
    }
    analysis = service.match_profile_to_target(
        profile,
        job_title=payload.get('job_title'),
        job_description=payload.get('job_description'),
    )
    return analysis


@router.get("/", response_model=list[CVOut])
async def list_cvs(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    repo = CVService(db)
    cvs = await repo.repo.list_for_user(current_user.id)
    return cvs


@router.get("/{cv_id}/file")
async def get_cv_file(cv_id: str, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    service = CVService(db)
    cv = await service.get_cv_for_user(current_user.id, cv_id)
    if not cv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV not found")
    try:
        service.read_original_file(cv)
    except StorageError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return FileResponse(
        cv.path,
        media_type=cv.content_type or 'application/octet-stream',
        filename=cv.filename,
        content_disposition_type='inline',
    )


@router.get("/{cv_id}/preview")
async def get_cv_preview(cv_id: str, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    service = CVService(db)
    cv = await service.get_cv_for_user(current_user.id, cv_id)
    if not cv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV not found")

    filename = (cv.filename or '').lower()
    media_type = (cv.content_type or '').lower()
    try:
        content = service.read_original_file(cv)
    except StorageError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    if filename.endswith('.pdf') or media_type == 'application/pdf':
        page_count = service.get_document_page_count(cv.filename, content, cv.content_type)
        return {
            'format': 'pdf',
            'page_count': page_count,
            'file_url': f'/api/cv/{cv.id}/file',
        }

    if filename.endswith('.docx') or media_type.endswith('wordprocessingml.document'):
        try:
            html = service.render_docx_preview(content)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
        return {
            'format': 'docx',
            'page_count': 1,
            'html': html,
        }

    raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Preview is only available for PDF and DOCX files.")


@router.post("/{cv_id}/intent", response_model=CVOut)
async def confirm_career_intent(
    cv_id: str,
    payload: CareerIntentPayload,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CVService(db)
    cv = await service.get_cv_for_user(current_user.id, cv_id)
    if not cv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV not found")
    return await service.confirm_career_intent(current_user.id, cv, payload.current_intent.strip())


def build_search_profile(profile: dict, job_title: str | None = None, job_description: str | None = None):
    skill_tags = [
        item.strip() for item in profile.get('skills', []) if isinstance(item, str) and item.strip()
    ]
    query = ' '.join(skill_tags)
    return {
        'target_role': job_title or profile.get('headline') or '',
        'skill_tags': skill_tags[:20],
        'experience_level': 'mid-senior' if profile.get('work_experience') else 'entry-level',
        'search_query': query,
    }
