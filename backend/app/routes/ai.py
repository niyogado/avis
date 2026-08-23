from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.schemas.ai_training import AITrainingCreate, AITrainingOut
from app.services.chat_service import chat
from app.services.cv_service import CVService
from app.services.profile_service import ProfileService
from app.services.training_service import AITrainingService
from app.services.career_hub_service import CareerHubService
from app.services.opportunity_ai import enrich_opportunities, suggest_expansion_queries
from app.services.domain_intelligence import build_search_queries, infer_user_domain
from app.services.opportunity_service import resolve_routing, search_opportunities


router = APIRouter(
    prefix="/api/ai",
    tags=["AI"],
)


class ChatRequest(BaseModel):
    message: str


class ApplicationCreate(BaseModel):
    title: str
    company: str | None = None
    location: str | None = None
    source_url: str | None = None
    match_score: int | None = None
    match_reasons: list[str] | None = None
    notes: str | None = None


class JobAlertCreate(BaseModel):
    title: str
    query: str
    target_roles: list[str] | None = None


@router.post("/chat")
async def ai_chat(request: ChatRequest, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        from app.services.settings_service import SettingsService
        ai_options = await SettingsService(db).resolve_ai_options(current_user.id)
        response = await chat(request.message, user_id=current_user.id, db=db, ai_options=ai_options)
        return {"response": response}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get("/career-intelligence")
async def get_career_intelligence(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    service = CVService(db)
    profile_service = ProfileService(db)
    context = await service.get_professional_context(current_user.id)
    confirmation = await profile_service.get_professional_context(current_user.id)
    evidence = context.get('cv_evidence') or {}
    interpretation = context.get('ai_interpretation') or {}
    intent = context.get('career_intent') or {}
    confirmed = (context.get('confirmed_user_intent') or '').strip()

    if not context.get('cv') and not context.get('profile', {}).get('headline') and not confirmation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No profile available yet. Upload a CV or complete your profile first.")

    skills = evidence.get('skills') or context.get('skills') or []
    strengths = interpretation.get('strengths') or skills[:5]
    gaps = interpretation.get('gaps') or []
    directions = interpretation.get('career_directions') or []

    # USER-CONFIRMED identity drives the signal when present.
    confirmed_primary = (confirmation or {}).get('primary_role') or ''
    confirmed_targets = (confirmation or {}).get('target_roles') or []
    confirmed_level = (confirmation or {}).get('professional_level') or ''

    if confirmed_primary or confirmed_targets:
        if confirmed_primary:
            current_role = confirmed_primary
        elif directions:
            current_role = directions[0]
        else:
            current_role = ''
        target_label = ', '.join(confirmed_targets) if confirmed_targets else None
        if target_label and current_role:
            summary = (
                f"Where you are now: {current_role}"
                + (f" ({confirmed_level})" if confirmed_level else "")
                + f". Where you want to go: {target_label}. "
                + "AVIS compares your confirmed skills against this direction to identify what is missing."
            )
        elif target_label:
            summary = f"Your confirmed target: {target_label}. Analyze or confirm more of your profile so AVIS can map the path from where you are now."
        else:
            summary = f"Your confirmed professional role: {current_role}."
        signal = target_label or current_role
        source = 'user_confirmed'
    elif confirmed:
        summary = f"Your confirmed career intent is {confirmed}. CV evidence remains available as historical context."
        signal = confirmed
        source = 'user_confirmed'
    elif directions:
        summary = (
            "Your CV suggests: "
            + ', '.join(directions[:3])
            + ". Confirm which direction you are currently targeting."
        )
        signal = directions[0]
        source = 'ai_inference'
    else:
        summary = "AVIS has a profile, but needs CV analysis or a confirmed career intent before ranking a direction."
        signal = context['profile'].get('headline') or 'Professional identity'
        source = 'profile'

    return {
        'available': bool(evidence or confirmed),
        'career_signal': signal,
        'signal_source': source,
        'strong_evidence': strengths[:8] or skills[:8],
        'next_gaps': gaps[:5],
        'summary': summary,
        'cv_evidence': evidence,
        'ai_interpretation': interpretation,
        'confirmed_user_intent': confirmed,
        'ai_recommendation': intent,
        'user_confirmation': {
            'primary_role': confirmed_primary,
            'target_roles': confirmed_targets,
            'professional_level': confirmed_level,
            'confirmed_skills': (confirmation or {}).get('confirmed_skills') or [],
            'career_interests': (confirmation or {}).get('career_interests') or [],
            'preferred_locations': (confirmation or {}).get('preferred_locations') or [],
            'work_preference': (confirmation or {}).get('work_preference'),
        },
    }


MAX_CARDS_PER_BATCH = 30
EXPANSION_TERMS_PER_PAGE = 3


@router.get("/opportunities")
async def get_opportunities(
    page: int = 1,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CVService(db)
    profile_service = ProfileService(db)
    context = await service.get_professional_context(current_user.id)
    confirmation = await profile_service.get_professional_context(current_user.id)

    if not context.get('profile') and not context.get('cv'):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No profile is available yet.")

    # ---- Universal CV context (any profession/industry) -------------------
    confirmed_skills = (confirmation or {}).get('confirmed_skills') or context.get('skills') or []
    evidence_skills = context.get('cv_evidence', {}).get('skills') or []
    target_roles = (confirmation or {}).get('target_roles') or context.get('career_intent', {}).get('target_roles') or []
    preferred_locations = (confirmation or {}).get('preferred_locations') or []
    work_preference = (confirmation or {}).get('work_preference')

    if not preferred_locations:
        profile_location = (context.get('profile') or {}).get('location') or ''
        if profile_location:
            preferred_locations = [profile_location]

    routing = resolve_routing(preferred_locations, work_preference)

    user_context = {
        'profile': context.get('profile') or {},
        'cv_evidence': evidence_skills and {'skills': evidence_skills} or {},
        'career_intent': context.get('career_intent') or {},
        'user_confirmation': confirmation or {},
        'confirmed_user_intent': context.get('confirmed_user_intent') or '',
        'skills': confirmed_skills or evidence_skills,
    }

    # ---- Universal domain intelligence (any profession) --------------------
    # Infer the candidate's industry from their real CV evidence; build search
    # keywords dynamically from their own roles/titles/field of study. There
    # is NO hardcoded tech fallback anywhere in this path.
    user_domain = infer_user_domain({
        'headline': (context.get('profile') or {}).get('headline') or '',
        'skills': evidence_skills,
        'professional_profile': context.get('cv_evidence', {}).get('professional_profile'),
        'experience': context.get('cv_evidence', {}).get('experience'),
        'education': context.get('cv_evidence', {}).get('education'),
        'career_directions': target_roles,
    })

    safe_page = max(1, min(page, 8))
    queries_used: list[str] = []
    has_more = False

    if safe_page == 1:
        queries_used = build_search_queries(user_context)
        has_more = True  # expansion pages are always attempted next.
    else:
        # Expansion batches: adjacent titles/keywords from the candidate's field.
        expansion = suggest_expansion_queries(user_context)
        start = (safe_page - 2) * EXPANSION_TERMS_PER_PAGE
        queries_used = [
            str(term) for term in expansion[start:start + EXPANSION_TERMS_PER_PAGE]
        ]
        has_more = len(expansion) > start + EXPANSION_TERMS_PER_PAGE

    results: dict = {}
    jobs: list[dict] = []
    rejected_out_of_domain = 0
    if queries_used:
        # Local-physical domains (tourism, trades, agriculture): global
        # remote-only boards do not carry these roles, so AVIS skips them
        # unless the candidate explicitly prefers remote work.
        remote_preferred = (work_preference or '').strip().lower() == 'remote'
        include_remotive = routing['show_remotive'] and not (
            user_domain.local_physical and user_domain.confident and not remote_preferred
        )
        try:
            results = search_opportunities(
                queries=queries_used,
                limit_per_query=12,
                max_cards=MAX_CARDS_PER_BATCH,
                target_roles=target_roles,
                confirmed_skills=confirmed_skills,
                evidence_skills=evidence_skills,
                preferred_locations=preferred_locations,
                include_global_remote=include_remotive,
                user_domain=user_domain,
            )
        except RuntimeError as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Opportunity search failed: {exc}") from exc

        # AI inspection & summarizer: industry-tailored insights per card.
        jobs = enrich_opportunities(results.get('jobs') or [], user_context)
        rejected_out_of_domain = int(results.get('rejected_out_of_domain') or 0)

    queried = results.get('sources_queried') or []
    unavailable = results.get('sources_unavailable') or []
    message = routing['reason'] + (
        f' Searched {len(queries_used)} keyword set(s) across {len(queried)} live source(s); '
        f'{len(unavailable)} source(s) have no verified public access. '
        'Only listings matching your professional domain AND carrying a real application link are shown.'
    )
    if rejected_out_of_domain:
        message += f' {rejected_out_of_domain} out-of-domain listing(s) were filtered.'
    if safe_page > 1 and not jobs:
        has_more = False
        message = 'No further verified opportunities were found for this exploration batch. Try confirming more skills on your CV.'

    return {
        'available': bool(jobs),
        'jobs': jobs,
        'page': safe_page,
        'queries_used': queries_used,
        'has_more': has_more,
        'routing': {
            'intent': routing['intent'],
            'reason': routing['reason'],
        },
        'provider_statuses': results.get('provider_statuses') or [],
        'sources_queried': queried,
        'sources_unavailable': unavailable,
        'context': {
            'confirmed_user_intent': context.get('confirmed_user_intent') or '',
            'skills': confirmed_skills or evidence_skills,
            'target_roles': target_roles,
            'preferred_locations': preferred_locations,
            'inferred_domain': {
                'cluster': user_domain.cluster,
                'confidence': user_domain.confidence,
                'confident': user_domain.confident,
            },
        },
        'message': message,
    }


@router.get("/writer")
async def get_cv_writer_context(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    service = CVService(db)
    context = await service.get_professional_context(current_user.id)
    evidence = context.get('cv_evidence') or {}
    if not evidence and not context.get('profile', {}).get('headline'):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload and analyze a CV before using CV Writer.")

    bullets = []
    for group in (evidence.get('experience') or [])[:4]:
        bullets.append(group)
    for group in (evidence.get('projects') or [])[:3]:
        bullets.append(group)

    return {
        'available': True,
        'evidence': bullets,
        'skills': evidence.get('skills') or [],
        'confirmed_user_intent': context.get('confirmed_user_intent') or '',
        'professional_profile': evidence.get('professional_profile') or context['profile'].get('summary') or '',
        'ai_interpretation': context.get('ai_interpretation') or {},
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


def _serialize_application(item):
    return {
        'id': str(item.id),
        'title': item.title,
        'company': item.company,
        'location': item.location,
        'source_url': item.source_url,
        'match_score': item.match_score,
        'match_reasons': item.match_reasons or [],
        'status': item.status,
        'notes': item.notes,
        'created_at': item.created_at,
    }


def _serialize_alert(item):
    return {
        'id': str(item.id),
        'title': item.title,
        'query': item.query,
        'target_roles': item.target_roles or [],
        'is_active': item.is_active,
        'created_at': item.created_at,
    }


@router.get("/applications")
async def list_applications(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    items = await CareerHubService(db).list_applications(current_user.id)
    return {'items': [_serialize_application(item) for item in items]}


@router.post("/applications", status_code=status.HTTP_201_CREATED)
async def create_application(payload: ApplicationCreate, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    item = await CareerHubService(db).create_application(current_user.id, {
        **payload.model_dump(),
        'status': 'saved',
    })
    return _serialize_application(item)


@router.get("/job-alerts")
async def list_job_alerts(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    items = await CareerHubService(db).list_alerts(current_user.id)
    return {'items': [_serialize_alert(item) for item in items]}


@router.post("/job-alerts", status_code=status.HTTP_201_CREATED)
async def create_job_alert(payload: JobAlertCreate, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    item = await CareerHubService(db).create_alert(current_user.id, payload.model_dump())
    return _serialize_alert(item)

    