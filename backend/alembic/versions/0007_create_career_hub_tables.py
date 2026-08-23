"""create applications and job_alerts tables

Revision ID: 0007_create_career_hub_tables
Revises: 0006_add_cv_analysis_fields
Create Date: 2026-08-22
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '0007_create_career_hub_tables'
down_revision = '0006_add_cv_analysis_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'applications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('company', sa.String(length=255), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('source_url', sa.String(length=2048), nullable=True),
        sa.Column('match_score', sa.Integer(), nullable=True),
        sa.Column('match_reasons', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='saved'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_applications_user_id', 'applications', ['user_id'])

    op.create_table(
        'job_alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('query', sa.String(length=512), nullable=False),
        sa.Column('target_roles', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_job_alerts_user_id', 'job_alerts', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_job_alerts_user_id', table_name='job_alerts')
    op.drop_table('job_alerts')
    op.drop_index('ix_applications_user_id', table_name='applications')
    op.drop_table('applications')
