# infrastructure/docker

Environnement de développement local : PostgreSQL, Redis, MinIO
(S3-compatible).

```bash
docker compose -f infrastructure/docker/docker-compose.yml up -d
```

Identifiants définis dans `docker-compose.yml` valables **uniquement en
local** (`local_dev_only`) — jamais réutilisés en environnement déployé.

Les Dockerfiles par service seront ajoutés dans `services/*/` au moment
de l'implémentation de chaque service (pas encore présents, Sprint F0 =
fondation uniquement).
