"""tenant account type (personal team enterprise)

Revision ID: 00d5be2357a8
Revises: 959fac8d51b5
Create Date: 2026-07-31 06:05:42.958778
"""
from alembic import op
import sqlalchemy as sa


revision = '00d5be2357a8'
down_revision = '959fac8d51b5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # server_default : les tenants déjà existants (aucun à ce stade, mais la
    # migration reste correcte si ce n'était plus vrai) reçoivent 'personal' par
    # défaut plutôt que de faire échouer l'ajout d'une colonne NOT NULL.
    op.add_column(
        "tenants", sa.Column("account_type", sa.String(length=20), nullable=False, server_default="personal")
    )


def downgrade() -> None:
    op.drop_column("tenants", "account_type")
