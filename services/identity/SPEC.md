# services/identity — Spécification Sprint F1

Objectif du sprint : *« un créateur peut créer un compte dans un
environnement sécurisé »*. Voir [ADR-0004](../../docs/adr/0004-password-hashing-argon2id.md)
et [ADR-0005](../../docs/adr/0005-jwt-hs256-then-rs256.md) pour les
décisions structurantes déjà actées.

## Dans le périmètre F1

Inscription, connexion, rafraîchissement de session, déconnexion,
consultation du profil courant, RBAC minimal fonctionnel de bout en
bout, journal d'audit, connexion via Google (OAuth) — voir
[ADR-0006](../../docs/adr/0006-oauth-provider-abstraction-account-linking.md).

## Hors périmètre F1 (explicitement différé)

- **Autres providers OAuth** (GitHub, etc.) — l'abstraction le permet
  (`app/oauth/base.py`), seul Google est câblé pour l'instant. Ajouté
  au fil des besoins produit, pas par anticipation.
- **Row-Level Security PostgreSQL** — isolation tenant assurée par
  filtrage applicatif systématique (`tenant_id`) pour F1 ; RLS en
  défense en profondeur reste prévu (`SECURITY.md`) mais n'est pas
  bloquant pour ce sprint.
- **Agence gérant plusieurs créateurs dans un même tenant** — F1 crée
  un tenant personnel par utilisateur à l'inscription. Le cas
  multi-utilisateurs par tenant est prévu par le modèle de données
  mais pas exposé par une route d'invitation à ce stade.

## OAuth (Google) — flux

1. Client appelle `GET /auth/oauth/google/authorize` → reçoit
   `{authorization_url}` à ouvrir (redirection côté client, pas côté
   serveur — `apps/api`/`apps/web` n'existent pas encore, ce choix
   sera revalidé quand ils existeront).
2. Google redirige le navigateur vers
   `GET /auth/oauth/google/callback?code=...&state=...`.
3. Le service échange `code` contre les infos utilisateur chez Google,
   applique la politique de rattachement (ADR-0006), émet les mêmes
   tokens que le flux email/mot de passe.

`state` est un jeton signé à courte durée de vie (anti-CSRF), pas un
stockage serveur — cohérent avec l'architecture sans session côté
serveur pour l'access token.

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
| GET | `/auth/oauth/google/authorize` | Aucune | URL d'autorisation Google à ouvrir |
| GET | `/auth/oauth/google/callback` | Aucune (code+state en query) | Échange le code, connecte/crée le compte |

**Nécessite en production** : `GOOGLE_OAUTH_CLIENT_ID`,
`GOOGLE_OAUTH_CLIENT_SECRET` (app OAuth à créer sur Google Cloud
Console — hors de portée pour être fait depuis ce sandbox),
`OAUTH_REDIRECT_BASE_URL`. Sans ces variables réelles, les tests
passent (provider simulé) mais le flux réel contre Google ne
fonctionnera qu'une fois ces identifiants fournis.

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
