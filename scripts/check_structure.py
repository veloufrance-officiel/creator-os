#!/usr/bin/env python3
"""
Vérifie que la structure du monorepo Creator OS respecte l'ADR-0001.

Sert de "test de fondation" tant qu'aucun service n'est implémenté
(Sprint F0). Utilisé par .github/workflows/ci.yml (job
structure-and-config-check) et par `make structure-check`.
"""
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_DIRS = [
    "apps/web", "apps/api", "apps/admin",
    "services/identity", "services/creator", "services/media",
    "services/connector", "services/ai", "services/memory",
    "services/billing", "services/quota", "services/analytics",
    "services/security",
    "packages/ui", "packages/types", "packages/sdk",
    "packages/security", "packages/config",
    "infrastructure/docker", "infrastructure/terraform", "infrastructure/kubernetes",
    "docs/architecture", "docs/architecture/v0", "docs/adr", "docs/security", "docs/dsi",
    "tests",
    "scripts",
    ".github/workflows", ".github/ISSUE_TEMPLATE",
]

REQUIRED_FILES = [
    "README.md", "README_DSI.md", "SECURITY.md", "CONTRIBUTING.md",
    "CHANGELOG.md", "NOTICE", ".gitignore", ".env.example",
    "package.json", "pnpm-workspace.yaml", "turbo.json", "Makefile",
    "docs/adr/0000-template.md",
    "docs/architecture/ARCHITECTURE.md",
    "docs/architecture/DOMAIN_MODEL.md",
    "docs/architecture/ROADMAP.md",
]

YAML_JSON_FILES = [
    "package.json",
    "pnpm-workspace.yaml",
    "turbo.json",
    "infrastructure/docker/docker-compose.yml",
    ".github/workflows/ci.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
]


def check_paths() -> list[str]:
    errors = []
    for d in REQUIRED_DIRS:
        if not (ROOT / d).is_dir():
            errors.append(f"Dossier manquant : {d}")
    for f in REQUIRED_FILES:
        if not (ROOT / f).is_file():
            errors.append(f"Fichier manquant : {f}")
    return errors


def check_syntax() -> list[str]:
    errors = []
    for rel in YAML_JSON_FILES:
        path = ROOT / rel
        if not path.is_file():
            continue  # déjà signalé par check_paths si requis
        try:
            if rel.endswith(".json"):
                json.loads(path.read_text())
            else:
                if yaml is None:
                    errors.append(f"PyYAML non installé, impossible de valider {rel}")
                    continue
                list(yaml.safe_load_all(path.read_text()))
        except Exception as exc:
            errors.append(f"Syntaxe invalide dans {rel} : {exc}")
    return errors


def main() -> None:
    errors = check_paths() + check_syntax()
    if errors:
        print("❌ Vérification de structure échouée :\n")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print(
        f"✅ Structure et configuration conformes "
        f"({len(REQUIRED_DIRS)} dossiers, {len(REQUIRED_FILES)} fichiers requis, "
        f"{len(YAML_JSON_FILES)} fichiers de config validés)."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
