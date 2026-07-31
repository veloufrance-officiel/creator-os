# ADR-0007 — Vérification d'ID token (OIDC) pour le sign-in natif multi-plateforme

**Statut** : Accepté
**Date** : 2026-07-31
**Décideurs** : CTO / Architecture Creator OS — Sprint F1 (suite)

## Contexte

Le produit doit à terme être déployable en application mobile (iOS,
Android) autant que sur PC/web. Deux contraintes en découlent :

1. Le sign-in natif iOS/Android (Google comme Apple) fonctionne par
   **ID token** obtenu directement sur l'appareil via le SDK du
   fournisseur — pas par redirection navigateur. Le flow
   « authorize + callback » déjà implémenté (`GoogleOAuthProvider`) est
   pensé pour un contexte web, pas pour une app native.
2. **Sign in with Apple** est quasi systématiquement exigé par Apple
   (App Store Review Guidelines 4.8) dès qu'un autre login social
   (ici Google) est proposé dans une app iOS. Ce n'est pas une option
   produit, c'est une contrainte de distribution.

Le flow Apple, y compris côté web, est de toute façon centré sur l'ID
token (contrairement à un simple `access_token` classique) — implémenter
la vérification d'ID token n'est donc pas seulement pour le mobile, c'est
la façon standard d'intégrer Apple, point.

## Décision

Ajout d'un second mécanisme, **complémentaire** au flow redirection
existant, pas un remplacement :

- `app/oauth/oidc.py` : vérification générique d'un ID token OIDC
  (signature via JWKS distant, `iss`, `aud`, expiration) — partagée
  par tous les providers qui en ont besoin.
- `OAuthProvider.verify_id_token(id_token) -> OAuthUserInfo` : ajouté
  au protocole partagé.
- `GoogleOAuthProvider` : implémente `verify_id_token` en plus du flow
  redirection déjà en place (les deux coexistent, usages différents).
- `AppleOAuthProvider` (nouveau) : implémente uniquement
  `verify_id_token`. Le flow redirection web d'Apple (qui exige un
  `client_secret` régénéré sous forme de JWT signé avec une clé privée
  Apple dédiée) est explicitement **hors périmètre** de ce sprint — le
  besoin exprimé est le sign-in natif, pas le bouton web Apple.
- Nouvelle route `POST /auth/oauth/{provider}/token` — reçoit
  `{id_token}` du client (obtenu par son SDK natif), vérifie, applique
  la même politique de rattachement de compte que le flow redirection
  (ADR-0006, réutilisé tel quel).
- **Audiences multiples** : chaque provider accepte une **liste**
  d'`aud` valides (`GOOGLE_OAUTH_CLIENT_IDS`, `APPLE_CLIENT_IDS`,
  séparées par virgules), pas une seule — un même provider a
  généralement un client ID différent par plateforme (web, iOS,
  Android). Un jeton émis pour n'importe laquelle de ces plateformes
  doit être accepté.

## Alternatives envisagées

| Option | Rejetée car |
|---|---|
| Ne garder que le flow redirection, l'utiliser aussi pour mobile | Mauvaise expérience native (webview + interception d'URL custom scheme), et ne correspond pas au flow natif standard Apple/Google |
| SDK officiel Apple/Google côté serveur pour la vérification | `PyJWT` + `PyJWKClient` suffit (JWKS + vérification de signature standard), évite une dépendance lourde par provider pour un besoin identique (vérifier un JWT OIDC) |
| Un seul client ID par provider | Ne fonctionne pas dès qu'il y a plus d'une plateforme (web + iOS a minima) |

## Conséquences

**Positives**
- Le même mécanisme sert web (via SDK JS) et natif mobile, pour Google et Apple.
- Ajout d'un futur provider OIDC-compatible = juste `iss`/JWKS URL/audiences, pas de nouvelle logique de vérification à écrire.

**Négatives / à surveiller**
- Apple encode `email_verified` sous forme de **chaîne** `"true"`/`"false"` (pas un booléen JSON) dans certains cas — à normaliser explicitement, source d'erreur classique si non géré.
- Le flow redirection web Apple reste à faire si un jour un bouton « Sign in with Apple » est voulu sur `apps/web` en plus du natif — ADR séparé le moment venu, ne pas anticiper.
- `PyJWKClient` met en cache les clés JWKS ; si Apple/Google effectue une rotation de clé, le cache doit être invalidé correctement (comportement par défaut de la librairie, à surveiller en prod plutôt qu'à réimplémenter).
