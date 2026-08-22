"""create ai related tables

Revision ID: 0004_create_ai_tables
Revises: 0003_create_cvs
Create Date: 2026-08-20
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '0004_create_ai_tables'
down_revision = '0003_create_cvs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ai_trainings
    op.create_table(
        'ai_trainings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_ai_trainings_user_id', 'ai_trainings', ['user_id'])

    # ai_chat_sessions
    op.create_table(
        'ai_chat_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_ai_chat_sessions_user_id', 'ai_chat_sessions', ['user_id'])

    # ai_chat_messages
    op.create_table(
        'ai_chat_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_chat_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("role IN ('system','user','assistant','tool')", name='ck_ai_chat_messages_role'),
    )
    op.create_index('ix_ai_chat_messages_session_id', 'ai_chat_messages', ['session_id'])

    # ai_profile_updates
    op.create_table(
        'ai_profile_updates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('field_name', sa.String(length=100), nullable=False),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.CheckConstraint("source IN ('chat','training','cv','system')", name='ck_ai_profile_updates_source'),
        sa.CheckConstraint("status IN ('pending','approved','rejected','applied')", name='ck_ai_profile_updates_status'),
    )
    op.create_index('ix_ai_profile_updates_user_id', 'ai_profile_updates', ['user_id'])

    # ai_memories
    op.create_table(
        'ai_memories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('importance', sa.Integer(), server_default='1', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_ai_memories_user_id', 'ai_memories', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_ai_memories_user_id', table_name='ai_memories')
    op.drop_table('ai_memories')

    op.drop_index('ix_ai_profile_updates_user_id', table_name='ai_profile_updates')
    op.drop_table('ai_profile_updates')

    op.drop_index('ix_ai_chat_messages_session_id', table_name='ai_chat_messages')
    op.drop_table('ai_chat_messages')

    op.drop_index('ix_ai_chat_sessions_user_id', table_name='ai_chat_sessions')
    op.drop_table('ai_chat_sessions')

    op.drop_index('ix_ai_trainings_user_id', table_name='ai_trainings')
    op.drop_table('ai_trainings')
