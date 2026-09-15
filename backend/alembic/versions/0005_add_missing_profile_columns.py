"""add missing profile columns

Revision ID: 0005_add_missing_profile_columns
Revises: 0004_create_ai_tables
Create Date: 2026-08-20
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0005_add_missing_profile_columns'
down_revision = '0004_create_ai_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('profiles', sa.Column('first_name', sa.String(length=100), nullable=True))
    op.add_column('profiles', sa.Column('last_name', sa.String(length=100), nullable=True))
    op.add_column('profiles', sa.Column('phone', sa.String(length=30), nullable=True))
    op.add_column('profiles', sa.Column('avatar_url', sa.String(length=2048), nullable=True))

    # Keep the user_id lookup path aligned with the SQLAlchemy model definition.
    op.create_index(op.f('ix_profiles_user_id'), 'profiles', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_profiles_user_id'), table_name='profiles')
    op.drop_column('profiles', 'avatar_url')
    op.drop_column('profiles', 'phone')
    op.drop_column('profiles', 'last_name')
    op.drop_column('profiles', 'first_name')
