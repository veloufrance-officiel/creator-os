.PHONY: up down install structure-check help

up: ## Démarre les dépendances d'infrastructure locales (Postgres, Valkey, MinIO)
	docker compose -f infrastructure/docker/docker-compose.yml up -d

down: ## Arrête les dépendances d'infrastructure locales
	docker compose -f infrastructure/docker/docker-compose.yml down

install: ## Installe les dépendances JS du monorepo
	pnpm install

structure-check: ## Valide la structure du repo par rapport à l'ADR-0001
	python3 scripts/check_structure.py

help: ## Affiche cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# Sprint F1+ : les cibles suivantes seront ajoutées au fil de l'implémentation
# réelle des services (lint/test Python par service, build apps/web, etc.)
# — volontairement absentes tant qu'elles n'exécuteraient rien de réel.
