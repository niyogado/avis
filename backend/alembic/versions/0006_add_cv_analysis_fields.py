"""add cv analysis persistence fields

Revision ID: 0006_add_cv_analysis_fields
Revises: 0005_add_missing_profile_columns
Create Date: 2026-08-20
"""
from alembic import op
import sqlalchemy as sa


revision = '0006_add_cv_analysis_fields'
down_revision = '0005_add_missing_profile_columns'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('cvs', sa.Column('extracted_text', sa.Text(), nullable=True))
    op.add_column('cvs', sa.Column('analysis_json', sa.JSON(), nullable=True))
    op.add_column('cvs', sa.Column('analysis_status', sa.String(length=32), nullable=True))
    op.add_column('cvs', sa.Column('analysis_error', sa.Text(), nullable=True))
    op.add_column('cvs', sa.Column('analyzed_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('cvs', 'analyzed_at')
    op.drop_column('cvs', 'analysis_error')
    op.drop_column('cvs', 'analysis_status')
    op.drop_column('cvs', 'analysis_json')
    op.drop_column('cvs', 'extracted_text')
