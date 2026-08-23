"""create user_settings for per-user AI and notification preferences

Revision ID: 0009_create_user_settings
Revises: 0008_add_professional_context
Create Date: 2026-08-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '0009_create_user_settings'
down_revision = '0008_add_professional_context'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'user_settings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('ai_provider', sa.String(length=32), nullable=False, server_default='auto'),
        sa.Column('ai_model', sa.String(length=128), nullable=False, server_default=''),
        sa.Column('ai_fallback_enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('ai_response_style', sa.String(length=16), nullable=False, server_default='balanced'),
        sa.Column('notify_job_alerts', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('notify_application_updates', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('notify_career_recommendations', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('notify_system', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_user_settings_user_id', 'user_settings', ['user_id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_user_settings_user_id', table_name='user_settings')
    op.drop_table('user_settings')
