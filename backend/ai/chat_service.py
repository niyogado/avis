from .ai_service import chat_with_ai
from .knowledge import build_context


def build_prompt(message: str) -> str:
    context = build_context()

    return f"""
You are AVIS, an AI career assistant.

Use the following AVIS knowledge when answering the user:

{context}

Instructions:
- Give useful career-focused answers.
- Do not invent user qualifications or experience.
- If information is missing, ask the user for it.
- Give practical and clear recommendations.
- Help users with careers, CVs, skills, training, interviews, jobs,
  and professional development.

User message:
{message}
""".strip()


def chat(message: str):
    prompt = build_prompt(message)
    return chat_with_ai(prompt)