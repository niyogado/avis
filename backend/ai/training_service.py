from .knowledge import build_context
from .ai_service import chat_with_ai


def generate_training_prompt(
    topic: str,
    level: str = "beginner",
    goal: str | None = None,
) -> str:
    context = build_context()

    goal_text = goal if goal else "general career development"

    return f"""
You are AVIS, an AI career training assistant.

AVIS knowledge:
{context}

Create a practical training lesson for the user.

Topic: {topic}
Level: {level}
Career goal: {goal_text}

The lesson should contain:
1. A clear explanation of the topic.
2. Important concepts the learner should understand.
3. Practical examples.
4. A short exercise or activity.
5. A few questions to check understanding.
6. A suggested next step.

Keep the content useful for career development.
""".strip()


def generate_training(
    topic: str,
    level: str = "beginner",
    goal: str | None = None,
):
    prompt = generate_training_prompt(
        topic=topic,
        level=level,
        goal=goal,
    )

    return chat_with_ai(prompt)