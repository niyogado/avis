"""Models package."""

# Expose AI models so imports elsewhere can reference them and Alembic
# autogeneration can detect metadata when files are imported.
from app.models.user import User  # noqa: F401
from app.models.profile import Profile  # noqa: F401
from app.models.cv import CV  # noqa: F401
from app.models.ai_training import AITraining  # noqa: F401
from app.models.ai_chat_session import AIChatSession  # noqa: F401
from app.models.ai_chat_message import AIChatMessage  # noqa: F401
from app.models.ai_profile_update import AIProfileUpdate  # noqa: F401
from app.models.ai_memory import AIMemory  # noqa: F401
