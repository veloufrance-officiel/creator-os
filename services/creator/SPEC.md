# services/creator — Spécification Sprint F2

Objectif : le créateur peut construire un profil enrichi (Creator Twin)
et un portfolio public structuré en blocs — reprend et étend le besoin
V0 (« portfolio professionnel en moins de 5 minutes »,
`docs/architecture/v0/PRODUCT_REQUIREMENTS.md`). Un tenant peut être un
créateur solo ou une **agence gérant plusieurs créateurs** — voir
[ADR-0009](../../docs/adr/0009-creator-twin-data-model-boundary.md) et
[ADR-0010](../../docs/adr/0010-multi-creator-agency-tenants.md)
(décisions structurantes).

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
| POST | `/creators` | Bearer | Ajoute un créateur géré par le tenant courant (agence ou solo) |
| GET | `/creators` | Bearer | Liste les créateurs du tenant courant |
| GET | `/creators/{id}` | Bearer | Détail d'un créateur du tenant courant |
| PATCH | `/creators/{id}` | Bearer | Met à jour le profil et/ou `is_authorized` (ADR-0010) |
| DELETE | `/creators/{id}` | Bearer | Supprime un créateur |
| POST | `/creators/{id}/portfolios` | Bearer | Crée un portfolio pour ce créateur (brouillon, non publié — ADR-0003) |
| GET | `/creators/{id}/portfolios` | Bearer | Liste les portfolios de ce créateur |
| GET | `/creators/{id}/portfolios/{pid}` | Bearer | Détail |
| PATCH | `/creators/{id}/portfolios/{pid}` | Bearer | Met à jour titre/slug/`is_published` |
| DELETE | `/creators/{id}/portfolios/{pid}` | Bearer | Supprime |
| POST | `/creators/{id}/portfolios/{pid}/blocks` | Bearer | Ajoute un bloc |
| PATCH | `/creators/{id}/portfolios/{pid}/blocks/{bid}` | Bearer | Met à jour un bloc |
| DELETE | `/creators/{id}/portfolios/{pid}/blocks/{bid}` | Bearer | Supprime un bloc |
| GET | `/public/portfolios/{slug}` | Aucune | Visible seulement si publié **et** créateur autorisé (404 identique sinon — jamais de fuite d'information, ADR-0010) |

## Agences multi-créateurs (ADR-0010)

Un tenant peut gérer plusieurs `Creator`. `Creator.is_authorized`
(défaut `True` à la création) contrôle la **visibilité publique** : un
créateur désautorisé disparaît de `/public/portfolios/{slug}` même si
son portfolio individuel reste `is_published`. L'agence garde un accès
interne complet (lecture/écriture) à un créateur désautorisé.

## Quota de créateurs par type de compte (ADR-0012)

`personal` : 1 · `team` : 10 · `enterprise` : illimité. Vérifié à la
création d'un créateur via un appel à `GET /tenant` sur `identity`
(transmet le token porteur de l'appelant). **Fail-open** si `identity`
est injoignable — le quota est une règle produit, pas une frontière de
sécurité, une panne d'`identity` ne doit pas bloquer la création.

**Différé** : quel utilisateur précis d'une agence multi-personnes peut
gérer quel créateur (délégation fine). Dépend d'un flow d'invitation
multi-utilisateurs côté `identity`, qui n'existe pas encore. D'ici là,
l'unique utilisateur du tenant gère tous ses créateurs.

## Tests prévus

Création de plusieurs créateurs sous un même tenant · désautorisation
d'un créateur (retire son portfolio publié du public, réautorisation le
restaure) · l'agence garde un accès interne à un créateur désautorisé ·
portfolio créé non publié par défaut · `/public/portfolios/{slug}`
retourne 404 sur un portfolio non publié, un créateur désautorisé, ou
un slug inexistant — jamais de distinction (pas de fuite d'information)
· blocs créés/modifiés/réordonnés/supprimés · isolation tenant complète
(créateurs, portfolios, désautorisation) · toutes les routes protégées
rejettent une requête sans token ou avec un token invalide · quota
respecté par palier (personal=1, team=10, enterprise=illimité),
message d'erreur explicite, et non bloquant si `identity` est injoignable
(fail-open, ADR-0012).
