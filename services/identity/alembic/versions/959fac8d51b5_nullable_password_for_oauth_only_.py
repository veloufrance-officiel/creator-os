"""nullable password for oauth-only accounts

Revision ID: 959fac8d51b5
Revises: 44a6f91d81f8
Create Date: 2026-07-31 00:31:15.375719
"""
from alembic import op
import sqlalchemy as sa


revision = '959fac8d51b5'
down_revision = '44a6f91d81f8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # batch_alter_table : SQLite ne supporte pas ALTER COLUMN directement (contrairement
    # à Postgres) — ce mode reste un simple ALTER COLUMN sur Postgres, il ne change rien
    # au comportement en production, il permet seulement de tester cette migration ici.
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("hashed_password", existing_type=sa.VARCHAR(length=255), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("hashed_password", existing_type=sa.VARCHAR(length=255), nullable=False)
