# services/identity — Spécification Sprint F1

Objectif du sprint : *« un créateur peut créer un compte dans un
environnement sécurisé »*. Voir [ADR-0004](../../docs/adr/0004-password-hashing-argon2id.md)
et [ADR-0005](../../docs/adr/0005-jwt-hs256-then-rs256.md) pour les
décisions structurantes déjà actées.

## Dans le périmètre F1

Inscription, connexion, rafraîchissement de session, déconnexion,
consultation du profil courant, RBAC minimal fonctionnel de bout en
bout, journal d'audit.

## Hors périmètre F1 (explicitement différé)

- **OAuth** (login social) — table `oauth_accounts` créée dans le
  modèle de données, aucune route implémentée. Dépend d'un choix de
  provider(s) et de l'enregistrement d'une app OAuth externe, non
  disponible pour ce sprint.
- **Row-Level Security PostgreSQL** — isolation tenant assurée par
  filtrage applicatif systématique (`tenant_id`) pour F1 ; RLS en
  défense en profondeur reste prévu (`SECURITY.md`) mais n'est pas
  bloquant pour ce sprint.
- **Agence gérant plusieurs créateurs dans un même tenant** — F1 crée
  un tenant personnel par utilisateur à l'inscription. Le cas
  multi-utilisateurs par tenant est prévu par le modèle de données
  mais pas exposé par une route d'invitation à ce stade.

## Entités (voir `app/models.py`)

`User`, `Tenant`, `Role`, `Permission`, `RolePermission`, `UserRole`,
`Session`, `AuditLog`, `OAuthAccount` (modèle présent, non utilisé).

## Flux d'authentification

1. **Inscription** — crée un `Tenant` personnel, un `User`, un `Role`
   *owner* pour ce tenant (avec toutes les permissions du catalogue F1),
   l'association `UserRole`. Retourne une paire de tokens (comme un
   login immédiat).
2. **Connexion** — vérifie le mot de passe (Argon2id). Échec : audit
   `user.login_failed`, aucune session créée, réponse générique (ne pas
   révéler si c'est l'email ou le mot de passe qui est incorrect).
   Succès : crée une `Session` (hash du refresh token stocké, jamais le
   token en clair), audit `user.login`.
3. **Rafraîchissement** — vérifie le refresh token contre le hash
   stocké, non expiré, non révoqué. Rotation : révoque l'ancienne
   session, en crée une nouvelle.
4. **Déconnexion** — révoque la session correspondant au refresh token
   fourni, audit `user.logout`.

## Endpoints

| Méthode | Route | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | Aucune | Créer compte + tenant personnel |
| POST | `/auth/login` | Aucune | Authentifier, émettre tokens |
| POST | `/auth/refresh` | Refresh token (body) | Rotation de session |
| POST | `/auth/logout` | Refresh token (body) | Révoquer une session |
| GET | `/me` | Bearer access token | Profil + rôles de l'utilisateur courant |
| GET | `/audit-logs` | Bearer + permission `identity:audit_log:read` | Journal d'audit du tenant courant |

## Tokens

- **Access token** (JWT, HS256, voir ADR-0005) : `sub` (user id),
  `tenant_id`, `roles` (codes), `exp` — durée de vie courte (15 min
  par défaut, configurable).
- **Refresh token** : chaîne aléatoire opaque (pas un JWT), seul son
  hash est persisté (`Session.refresh_token_hash`) — durée de vie plus
  longue (7 jours par défaut), rotation à chaque usage.

## Catalogue de permissions F1 (minimal, pour prouver le RBAC)

`identity:audit_log:read` — seule permission nécessaire pour exercer le
mécanisme RBAC de bout en bout ce sprint. Le catalogue s'enrichira
service par service (chaque nouveau service ajoute ses propres codes de
permission, pas `identity` en leur nom).

## Tests prévus (voir `tests/`)

Inscription réussie · connexion réussie · connexion échouée (mauvais
mot de passe, message générique) · `/me` sans token → 401 · `/me` avec
token → profil correct · refresh valide → nouveaux tokens, ancienne
session révoquée · refresh avec token révoqué → 401 · `/audit-logs`
sans permission → 403 · `/audit-logs` avec permission (owner) → 200 et
contient bien les événements générés par les tests précédents.
