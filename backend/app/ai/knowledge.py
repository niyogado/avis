AVIS_KNOWLEDGE = {
    "platform": {
        "name": "AVIS",
        "description": (
            "AVIS is an AI-powered career platform that helps users "
            "understand their skills, improve their careers, discover "
            "relevant jobs, and apply for opportunities, AViS only respond in english."
        ),
    },

    "career_guidance": {
        "skills": (
            "Users should identify their technical skills, soft skills, "
            "education, experience, certifications, projects, and career goals."
        ),
        "job_search": (
            "Job recommendations should consider the user's skills, "
            "experience, education, interests, and career goals."
        ),
        "cv": (
            "A CV should clearly present a person's contact information, "
            "professional summary, education, skills, experience, "
            "certifications, and relevant projects."
        ),
    },

    "training": {
        "interview": (
            "Interview preparation should include common interview questions, "
            "role-specific questions, communication practice, and feedback."
        ),
        "skills": (
            "Training recommendations should identify skill gaps and suggest "
            "learning activities that help the user reach their career goals."
        ),
    },
}


def get_knowledge() -> dict:
    """Return the knowledge available to the AVIS AI."""
    return AVIS_KNOWLEDGE


def build_context() -> str:
    """Convert AVIS knowledge into context for the AI model."""
    sections = []

    for category, content in AVIS_KNOWLEDGE.items():
        sections.append(f"{category.upper()}:")

        if isinstance(content, dict):
            for key, value in content.items():
                sections.append(f"- {key}: {value}")
        else:
            sections.append(f"- {content}")

    return "\n".join(sections)