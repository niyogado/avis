"""create cvs table

Revision ID: 0003_create_cvs
Revises: 0002_create_profiles
Create Date: 2026-08-18
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0003_create_cvs'
down_revision = '2abc9fcdde18'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'cvs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('filename', sa.String(length=1024), nullable=False),
        sa.Column('content_type', sa.String(length=128), nullable=True),
        sa.Column('size', sa.String(length=64), nullable=True),
        sa.Column('path', sa.String(length=2048), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('cvs')
