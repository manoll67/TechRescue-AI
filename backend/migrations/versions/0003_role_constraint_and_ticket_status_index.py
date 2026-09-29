"""Constrain user roles and index tickets by status.

Revision ID: 0003
Revises: 0002
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(sa.text("UPDATE users SET role = 'user' WHERE role NOT IN ('user', 'admin')"))
    op.create_check_constraint("ck_users_role", "users", "role IN ('user', 'admin')")
    op.create_index("ix_tickets_user_status", "tickets", ["user_id", "status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_tickets_user_status", table_name="tickets")
    op.drop_constraint("ck_users_role", "users", type_="check")
