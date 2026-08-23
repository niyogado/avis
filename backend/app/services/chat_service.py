from .ai_service import chat_with_ai
from ..ai.knowledge import build_context
from app.services.cv_service import CVService

CHAT_SYSTEM_PROMPT = """
You are AVIS, an AI career assistant inside the AVIS platform.

Core rules:
- Always respond in English, regardless of any other language instruction.
- Be accurate; never invent user qualifications, employers, or experience.
- Keep responses focused and professional.
""".strip()


async def build_user_context(db, user_id):
    service = CVService(db)
    context = await service.get_professional_context(user_id)
    has_confirmation = bool(context.get('user_confirmation'))
    if not context.get('cv') and not context.get('profile', {}).get('headline') and not has_confirmation:
        return "No verified profile or CV analysis yet. Ask the user for their background and current career direction. Distinguish CV evidence, AI inference, and user-confirmed intent."
    return service.format_context_for_ai(context)


def build_prompt(message: str, user_context: str | None = None) -> str:
    context = build_context()
    extra_context = user_context or 'No user context available yet.'

    return f"""
You are AVIS, an AI career assistant.

Use the following AVIS knowledge when answering the user:

{context}

Use the authenticated user's verified context below before making any claim about skills, experience, or career direction:

{extra_context}

Instructions:
- Focus on user profile understanding, career guidance, and professional context.
- Treat training data as persistent user knowledge capture, not lesson generation.
- Distinguish three layers: CV evidence (facts in the CV), AI inference (possible directions), and user-confirmed intent (what the user chose).
- Never overwrite or ignore user-confirmed intent because the CV suggests something else.
- Do not invent user qualifications or experience.
- If information is missing, ask the user for it.
- If career direction is inferred but not confirmed, ask which direction they are targeting.
- Help users with career planning, CV refinement, interview prep, and job alignment.
- If a user shares new professional information, capture it as candidate profile knowledge and ask for review before applying a profile update.
- Keep responses grounded in verified evidence.
- Do not claim you performed an action such as applying for a job, searching a live job board, or saving an alert unless a backend tool result is provided.

User message:
{message}
""".strip()


async def chat(message: str, user_id=None, db=None, ai_options: dict | None = None):
    user_context = ''
    if user_id and db is not None:
        user_context = await build_user_context(db, user_id)
    prompt = build_prompt(message, user_context)
    options = ai_options or {}
    return chat_with_ai(
        prompt,
        system=CHAT_SYSTEM_PROMPT,
        provider=options.get('provider', 'auto'),
        model=options.get('model'),
        style=options.get('style', 'balanced'),
        allow_fallback=options.get('allow_fallback', True),
    )
