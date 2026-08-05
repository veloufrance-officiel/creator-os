# Dockerfile explicite -- contourne les phases auto-detectees par Railpack
# (voir historique du service : une commande "python -m alembic upgrade
# head" s'executait au demarrage sans etre presente nulle part dans la
# config ni le code -- hypothese la plus probable : phase "release"
# injectee par Railpack en detectant Alembic comme dependance). Un
# Dockerfile ne laisse aucune place a une etape auto-detectee : ce CMD
# est tout ce qui s'execute, point final. Les migrations tournent deja
# dans le lifespan FastAPI (app/main.py), rien d'autre a orchestrer ici.
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY app ./app
COPY alembic ./alembic
COPY migrations.cfg ./

RUN pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
