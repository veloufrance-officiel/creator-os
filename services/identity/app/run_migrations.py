"""Lance les migrations Alembic -- fichier reel plutot qu'un 'python -c', pour
eviter les subtilites de sys.path propres a -c/-I rencontrees en deploiement.
Invocation : python -m app.run_migrations (depuis la racine du service)."""
import os

from alembic import command
from alembic.config import Config

if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cfg = Config(os.path.join(root, "alembic.ini"))
    command.upgrade(cfg, "head")
    print("Migrations OK.")
