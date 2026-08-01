# Dockerfile explicite -- l'auto-détection Railpack tentait d'exécuter `alembic`
# comme commande de release indépendamment de startCommand/preDeployCommand,
# sans que ces réglages ne suffisent à la contrôler. Un Dockerfile explicite
# retire toute ambiguïté sur ce qui s'installe et ce qui démarre.
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

RUN pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["sh", "-c", "python -m alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
