"""add profiles.professional_context for user-confirmed career data

Revision ID: 0008_add_professional_context
Revises: 0007_create_career_hub_tables
Create Date: 2026-08-23
"""
from alembic import op
import sqlalchemy as sa


revision = '0008_add_professional_context'
down_revision = '0007_create_career_hub_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('profiles', sa.Column('professional_context', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('profiles', 'professional_context')
