"""fix notifications defaults and nullability

Revision ID: 7f9d2b4c1a8e
Revises: 941d9367c604
Create Date: 2026-03-24 15:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7f9d2b4c1a8e"
down_revision: Union[str, Sequence[str], None] = "941d9367c604"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("UPDATE notifications SET created_at = now() WHERE created_at IS NULL")
    op.execute("UPDATE notifications SET is_read = false WHERE is_read IS NULL")

    op.alter_column(
        "notifications",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )
    op.alter_column(
        "notifications",
        "is_read",
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=sa.text("false"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "notifications",
        "is_read",
        existing_type=sa.Boolean(),
        nullable=True,
        server_default=None,
    )
    op.alter_column(
        "notifications",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=True,
        server_default=sa.text("now()"),
    )
