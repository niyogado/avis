"""merge profile and user migrations

Revision ID: 2abc9fcdde18
Revises: 0002_create_profiles, 7dfd60a27c7a
Create Date: 2026-08-18 13:28:15.289114

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2abc9fcdde18'
down_revision: Union[str, Sequence[str], None] = '0002_create_profiles'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
