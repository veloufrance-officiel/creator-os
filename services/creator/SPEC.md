# services/creator — Spécification Sprint F2

Objectif : le créateur peut construire un profil enrichi (Creator Twin)
et un portfolio public structuré en blocs — reprend et étend le besoin
V0 (« portfolio professionnel en moins de 5 minutes »,
`docs/architecture/v0/PRODUCT_REQUIREMENTS.md`). Décisions structurantes
actées : [ADR-0009](../../docs/adr/0009-creator-twin-data-model-boundary.md).

## Dans le périmètre F2

Profil créateur enrichi (upsert), portfolios (CRUD), blocs de portfolio
(CRUD + réordonnancement), publication/dépublication, consultation
publique par slug.

## Hors périmètre F2 (explicitement différé)

- **Bio générée par IA** — le champ `bio` est un simple texte modifiable
  par le créateur. La génération IA (V0 : `POST /ai/generate-bio`)
  appellera cet endpoint d'update une fois `services/ai` (AI Router,
  [ADR-0002](../../docs/adr/0002-ai-router-provider-agnostic.md))
  implémenté — `creator` n'appelle jamais un fournisseur IA
  directement, conformément à ce principe déjà acté.
- **Upload de médias réel** — les blocs peuvent référencer une URL
  d'asset, mais l'upload/stockage/CDN est `services/media`, pas encore
  implémenté. Un bloc image accepte une URL externe pour l'instant.
- **Permissions fines par rôle** — voir ADR-0009 : isolation par tenant
  uniquement ce sprint.
- **Historique/versions du profil** — voir ADR-0009 : différé à
  `services/memory` si un besoin réel apparaît.

## Modèle de données

`Creator` (1 par tenant), `Portfolio` (plusieurs par creator, identifié
par un `slug` unique global), `PortfolioBlock` (ordonnés dans un
portfolio, `type` + `config` JSON — extensible sans migration pour
chaque nouveau type de bloc).

Types de bloc F2 : `bio`, `media_gallery` (liste d'URLs), `links`
(réseaux/liens externes), `contact`. La validation du contenu de
`config` par type est faite côté service, pas en contrainte SQL — un
nouveau type de bloc n'exige pas de migration.

## Authentification & autorisation

Toutes les routes sauf la consultation publique exigent un access token
`identity` valide, vérifié via `packages/security` (ADR-0008). Chaque
opération est scopée au `tenant_id` extrait du token — jamais de
paramètre `tenant_id` fourni par le client.

## Endpoints

| Méthode | Route | Auth | Description |
|---|---|---|---|
| PATCH | `/creators/me` | Bearer | Crée ou met à jour le profil du tenant courant (upsert) |
| GET | `/creators/me` | Bearer | Profil du tenant courant |
| POST | `/portfolios` | Bearer | Crée un portfolio (brouillon, non publié par défaut — Privacy By Default, ADR-0003) |
| GET | `/portfolios` | Bearer | Liste les portfolios du tenant courant |
| GET | `/portfolios/{id}` | Bearer | Détail d'un portfolio du tenant courant |
| PATCH | `/portfolios/{id}` | Bearer | Met à jour titre/slug/`is_published` |
| DELETE | `/portfolios/{id}` | Bearer | Supprime un portfolio |
| POST | `/portfolios/{id}/blocks` | Bearer | Ajoute un bloc |
| PATCH | `/portfolios/{id}/blocks/{block_id}` | Bearer | Met à jour un bloc (contenu et/ou position) |
| DELETE | `/portfolios/{id}/blocks/{block_id}` | Bearer | Supprime un bloc |
| GET | `/public/portfolios/{slug}` | Aucune | Portfolio publié uniquement (404 si non publié ou inexistant — jamais de distinction entre les deux, pour ne pas révéler l'existence d'un slug privé) |

## Tests prévus

Upsert profil (création puis mise à jour) · portfolio créé non publié
par défaut · `/public/portfolios/{slug}` retourne 404 sur un portfolio
non publié (même s'il existe) · 404 identique sur un slug inexistant
(pas de fuite d'information) · publication rend le portfolio accessible
publiquement · blocs créés/modifiés/réordonnés/supprimés · isolation
tenant (le tenant A ne peut ni lire ni modifier un portfolio du tenant
B) · toutes les routes protégées rejettent une requête sans token ou
avec un token invalide.
