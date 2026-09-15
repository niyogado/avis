from .ai_service import chat_with_ai
from ..ai.knowledge import build_context
from app.services.profile_service import ProfileService
from app.services.training_service import AITrainingService


def _clean_value(value):
    if value is None:
        return ''
    return str(value).strip()


async def build_user_context(db, user_id):
    profile_service = ProfileService(db)
    training_service = AITrainingService(db)

    profile = await profile_service.get_profile_for_user(user_id)
    trainings = await training_service.list_trainings(user_id, active_only=True)

    context_bits = []
    if profile:
        context_bits.append(f"User profile: full_name={_clean_value(profile.full_name)}; headline={_clean_value(profile.headline)}; summary={_clean_value(profile.summary)}; location={_clean_value(profile.location)}; phone={_clean_value(profile.phone)}")

    if trainings:
        training_lines = []
        for item in trainings[:8]:
            training_lines.append(f"- {item.title}: {item.content}")
        context_bits.append("Approved training context:\n" + "\n".join(training_lines))

    if not context_bits:
        context_bits.append("No verified profile or training context yet. Ask the user for their background and current career direction.")

    return "\n\n".join(context_bits)


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
- Do not invent user qualifications or experience.
- If information is missing, ask the user for it.
- Use the user's profile, CV, chat history, and approved training notes as context.
- Help users with career planning, CV refinement, interview prep, and job alignment.
- If a user shares new professional information, capture it as candidate profile knowledge and ask for review before applying a profile update.
- Keep responses grounded in verified evidence.

User message:
{message}
""".strip()


async def chat(message: str, user_id=None, db=None):
    user_context = ''
    if user_id and db is not None:
        user_context = await build_user_context(db, user_id)
    prompt = build_prompt(message, user_context)
    return chat_with_ai(prompt)