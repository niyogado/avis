import asyncio
import sys
from pathlib import Path

# Add backend/ to Python path so Alembic can import app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from app.config.settings import settings
from app.database.base import Base

# Import models so Alembic can detect them
from app.models.user import User  # noqa: F401
from app.models.profile import Profile  # noqa: F401
from app.models.cv import CV  # noqa: F401
from app.models.ai_training import AITraining  # noqa: F401
from app.models.ai_chat_session import AIChatSession  # noqa: F401
from app.models.ai_chat_message import AIChatMessage  # noqa: F401
from app.models.ai_profile_update import AIProfileUpdate  # noqa: F401
from app.models.ai_memory import AIMemory  # noqa: F401
from app.models.application import Application  # noqa: F401
from app.models.job_alert import JobAlert  # noqa: F401
from app.models.user_settings import UserSettings  # noqa: F401


config = context.config

target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in offline mode."""
    url = settings.DATABASE_URL

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection):
    """Run migrations using a synchronous connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """Run migrations using the async SQLAlchemy engine."""
    connectable = create_async_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online():
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
