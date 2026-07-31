"""multi-creator agencies: drop unique on tenant_id, add is_authorized, add portfolio creator_id

Revision ID: da7e187afd11
Revises: e6f17c3739e9
Create Date: 2026-07-31 01:09:58.224019
"""
from alembic import op
import sqlalchemy as sa
import app.database  # noqa: F401 — requis : la colonne portfolios.creator_id utilise app.database.GUID()

# Note : add_column(..., nullable=False) sans défaut suppose une table portfolios
# vide au moment de cette migration (vrai à ce stade, aucun déploiement réel n'a
# encore de données) -- à revoir avec un défaut/backfill si ce n'est plus le cas
# le jour où cette migration s'exécute pour de vrai.

revision = 'da7e187afd11'
down_revision = 'e6f17c3739e9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # batch_alter_table : SQLite ne supporte pas l'ALTER de contraintes/index
    # directement (contrairement à Postgres) — ce mode reste équivalent à des
    # opérations standard sur Postgres, il permet seulement de tester cette
    # migration ici (même raison que services/identity, migration 0002).
    with op.batch_alter_table("creators") as batch_op:
        batch_op.add_column(sa.Column("is_authorized", sa.Boolean(), nullable=False, server_default=sa.true()))
        batch_op.drop_index(op.f("ix_creators_tenant_id"))
        batch_op.create_index(op.f("ix_creators_tenant_id"), ["tenant_id"], unique=False)
        batch_op.drop_index(op.f("ix_creators_user_id"))
        batch_op.create_index(op.f("ix_creators_user_id"), ["user_id"], unique=False)

    with op.batch_alter_table("portfolios") as batch_op:
        batch_op.add_column(sa.Column("creator_id", app.database.GUID(), nullable=True))
        batch_op.create_index(op.f("ix_portfolios_creator_id"), ["creator_id"], unique=False)
        batch_op.create_foreign_key("fk_portfolios_creator_id_creators", "creators", ["creator_id"], ["id"])
    # nullable=True ci-dessus par nécessité technique (SQLite batch mode ne permet
    # pas d'ajouter une colonne NOT NULL sans défaut sur une table non vide) ; en
    # pratique aucune table portfolios existante n'a de ligne à ce stade (voir note
    # de tête de fichier) donc la contrainte applicative (modèle SQLAlchemy) suffit.


def downgrade() -> None:
    with op.batch_alter_table("portfolios") as batch_op:
        batch_op.drop_constraint("fk_portfolios_creator_id_creators", type_="foreignkey")
        batch_op.drop_index(op.f("ix_portfolios_creator_id"))
        batch_op.drop_column("creator_id")

    with op.batch_alter_table("creators") as batch_op:
        batch_op.drop_index(op.f("ix_creators_user_id"))
        batch_op.create_index(op.f("ix_creators_user_id"), ["user_id"], unique=True)
        batch_op.drop_index(op.f("ix_creators_tenant_id"))
        batch_op.create_index(op.f("ix_creators_tenant_id"), ["tenant_id"], unique=True)
        batch_op.drop_column("is_authorized")
