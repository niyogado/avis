import json

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.database.session import get_db
from app.services.ai_service import chat_with_ai
from app.services.cv_service import CVService, build_career_intent, parse_ai_json_response, validate_cv_analysis
from app.schemas.ai_training import AITrainingCreate
from app.services.training_service import AITrainingService
from app.schemas.cv import CVOut

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

    ai_prompt = f"""
You are AVIS, a career intelligence assistant. Analyze the CV below and return only valid JSON.

Rules:
- Return a JSON object with exactly two top-level keys: cv_evidence and ai_interpretation.
- cv_evidence must contain: professional_profile, skills, experience, education, projects, certifications, career_signals.
- ai_interpretation must contain: strengths, gaps, career_signals, career_directions.
- cv_evidence must include only facts directly supported by the CV text.
- ai_interpretation may infer possible career directions, but do not present them as confirmed user choices.
- Keep all list fields as arrays of strings.
- Do not invent credentials or employers.

CV text:
{extracted_text[:20000]}
""".strip()

    try:
        raw_response = chat_with_ai(ai_prompt)
        parsed = parse_ai_json_response(raw_response)
        structured = validate_cv_analysis(parsed, profile)
    except json.JSONDecodeError as exc:
        await service.mark_analysis_error(cv, "EjoChat returned invalid JSON.")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="EjoChat returned invalid JSON. Please retry.") from exc
    except ValueError as exc:
        await service.mark_analysis_error(cv, str(exc))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except Exception as exc:
        await service.mark_analysis_error(cv, "EjoChat analysis failed.")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="EjoChat analysis failed. Please retry.") from exc

    analysis = service.match_profile_to_target(profile, job_title=job_title, job_description=job_description)
    evidence = structured['cv_evidence']
    interpretation = structured['ai_interpretation']
    intent = build_career_intent(
        profile,
        current_role=job_title or profile.get('headline') or '',
        target_roles=[job_title] if job_title else interpretation.get('career_directions', []),
        learning_priorities=[] if not job_description else [chunk.strip() for chunk in job_description.split(',') if chunk.strip()][:5],
        current_intent='',
    )

    structured_training = {
        'skills': evidence.get('skills') or profile.get('skills', []),
        'career_signals': evidence.get('career_signals') or interpretation.get('career_signals') or [],
        'strengths': interpretation.get('strengths') or analysis.get('strong_areas', []),
        'gaps': interpretation.get('gaps') or analysis.get('potential_gaps', []),
        'career_directions': interpretation.get('career_directions') or [],
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
    profile_obj = await service.get_master_profile(current_user.id)
    if not profile_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No master profile found. Upload a CV first.")

    profile = {
        'full_name': profile_obj.full_name,
        'headline': profile_obj.headline,
        'location': profile_obj.location,
        'phone': profile_obj.phone,
        'summary': profile_obj.summary,
        'skills': [
            'python', 'sql', 'postgresql', 'aws', 'docker', 'airflow', 'leadership'
        ],
        'soft_skills': ['leadership', 'communication'],
        'work_experience': [],
        'projects': [],
        'education': [],
        'certifications': [],
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
