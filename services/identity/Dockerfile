# Dockerfile explicite -- evite toute phase auto-detectee par Railpack (voir
# l'historique de deploiement : une commande "python -m alembic upgrade head"
# fantome s'executait au demarrage sans etre nulle part dans la config ni le
# code, y compris apres avoir retire toute invocation explicite). Les
# migrations tournent desormais dans le lifespan FastAPI (app/main.py) --
# ce Dockerfile n'a donc qu'une seule responsabilite : installer et lancer.
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY app ./app
COPY alembic ./alembic
COPY migrations.cfg ./

RUN pip install --no-cache-dir -e .

EXPOSE 8000

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
