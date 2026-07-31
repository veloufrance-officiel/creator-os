# ADR-0006 — OAuth : abstraction provider et politique de rattachement de compte

**Statut** : Accepté
**Date** : 2026-07-31
**Décideurs** : CTO / Architecture Creator OS — Sprint F1 (suite)

## Contexte

`services/identity` doit permettre la connexion via un fournisseur externe
(« Sign in with Google » pour commencer — voir SPEC.md pour le choix du
premier provider). Deux questions structurantes se posent : comment ne
pas coupler le code à un seul fournisseur, et que faire quand l'email
renvoyé par le fournisseur correspond déjà à un compte existant.

## Décision

**Abstraction** : une interface `OAuthProvider` (`app/oauth/base.py`)
que chaque fournisseur implémente (`GoogleOAuthProvider` en premier).
Aucun code métier ne dépend directement du SDK d'un fournisseur.

**Rattachement de compte** : à la réception du callback,

1. Si `(provider, provider_account_id)` correspond déjà à un
   `oauth_accounts` existant → connexion sur le compte lié.
2. Sinon, si un `User` existe déjà avec cet email **ET** que le
   fournisseur certifie l'email vérifié (`email_verified`) → rattache
   ce nouveau moyen de connexion à ce compte existant.
3. Sinon, si un `User` existe déjà avec cet email mais **sans**
   confirmation de vérification → **rejet explicite** (409), pas de
   création d'un second compte (email unique en base) et pas de
   rattachement silencieux (justement ce que ce principe vise à
   empêcher). Message : se connecter par mot de passe, ou réessayer
   une fois l'email vérifié chez le fournisseur.
4. Sinon (aucun `User` existant pour cet email) → crée un nouveau
   compte (même chemin que l'inscription email/mot de passe : tenant
   personnel, rôle owner), sans mot de passe (voir ci-dessous).

**Mot de passe optionnel** : un compte créé uniquement via OAuth n'a pas
de mot de passe (`users.hashed_password` devient nullable — migration
`0002`). La connexion par mot de passe sur un tel compte échoue
explicitement (message : utiliser la connexion sociale), plutôt que de
générer un mot de passe fantôme inutilisable.

## Alternatives envisagées

| Option | Rejetée car |
|---|---|
| Rattacher sur email sans vérifier `email_verified` | Un attaquant pourrait créer un compte chez le fournisseur avec l'email de quelqu'un d'autre non vérifié et détourner un compte existant |
| Toujours créer un nouveau compte, jamais rattacher | Mauvaise expérience : un créateur qui s'est inscrit par email puis tente « Sign in with Google » se retrouverait avec deux comptes séparés |
| Générer un mot de passe aléatoire caché pour les comptes OAuth | Champ menteur (laisse croire qu'un mot de passe existe), aucune valeur ajoutée vs nullable |

## Conséquences

**Positives**
- Ajouter un second provider (GitHub, etc.) n'impacte pas la logique de rattachement, seulement une nouvelle classe `OAuthProvider`.
- Pas de doublon de compte pour un même email vérifié.

**Négatives / à surveiller**
- Dépend entièrement de la fiabilité du flag `email_verified` du fournisseur — si un fournisseur ne le fournit pas de façon fiable, ne pas activer le rattachement automatique pour ce fournisseur (à vérifier au cas par cas avant d'ajouter un nouveau provider).
- Migration `0002` sur une colonne déjà en usage (F1 core) : sans risque tant qu'aucune donnée de prod n'existe encore, à surveiller si ce n'est plus vrai au moment où ce sprint s'exécute réellement.
