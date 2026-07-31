# ADR-0012 — Quota de créateurs par type de compte (team ≤ 10, enterprise illimité)

**Statut** : Accepté — précise [ADR-0011](0011-tenant-account-types.md)
**Date** : 2026-07-31
**Décideurs** : CTO / Architecture Creator OS

## Contexte

ADR-0011 laissait `team`/`enterprise` sans différence de comportement,
faute de définition produit. Définition reçue : **team = petite agence,
10 créateurs maximum ; enterprise = au-dessus de ce quota**. `personal`
n'était pas rediscuté explicitement mais la logique du seuil (solo →
petite agence → grande agence) implique **1 créateur maximum**.

Problème technique à trancher : `account_type` vit dans `Tenant`
(`services/identity`), la limite s'applique à la création de `Creator`
(`services/creator`) — deux services distincts (ADR-0009 : pas de base
partagée présumée, pas de FK cross-service).

## Décision

**Quotas** (constante dans `services/creator`, pas dans `identity` —
c'est une règle métier du domaine Creator, pas de l'identité) :

| `account_type` | Max créateurs |
|---|---|
| `personal` | 1 |
| `team` | 10 |
| `enterprise` | Illimité |

**Vérification en temps réel, pas via le JWT.** À la création d'un
créateur, `services/creator` appelle `GET /tenant` sur `services/identity`
en transmettant le **même token porteur** que l'appelant (pas de nouveau
mécanisme d'auth service-à-service). Rejeté plutôt qu'embarquer
`account_type` dans les claims du token : l'access token vit 15 minutes
(ADR-0005) — quelqu'un qui vient de passer de `team` à `enterprise`
précisément *parce qu'il a heurté le quota* attend un déblocage immédiat,
pas une attente pouvant aller jusqu'à 15 minutes.

**Fail-open sur indisponibilité d'Identity.** Si l'appel à `GET /tenant`
échoue (réseau, timeout, Identity indisponible), la création n'est
**pas bloquée** — le quota est une règle métier/produit, pas une
frontière de sécurité (l'isolation tenant, elle, reste appliquée
localement dans tous les cas). Un `identity` indisponible ne doit pas
transformer une panne d'un service en panne d'un autre pour une
vérification non critique.

## Alternatives envisagées

| Option | Rejetée car |
|---|---|
| `account_type` dans les claims JWT | Fenêtre de désynchronisation jusqu'à 15 min après un changement de palier — mauvaise expérience exactement au moment où l'utilisateur vient de payer pour débloquer plus de créateurs |
| Fail-closed si `identity` injoignable | Transforme une vérification de quota (non sécuritaire) en dépendance dure entre deux services censés rester indépendants (ADR-0001, ADR-0009) |
| Quota stocké côté `identity` | `identity` ne connaît pas le concept de « créateur » — c'est un objet du domaine `creator`, la règle doit vivre à côté de ce qu'elle contraint |

## Conséquences

**Positives**
- Toujours à jour : pas de fenêtre de désynchronisation après un changement de palier.
- N'introduit pas de couplage dur entre `identity` et `creator` (dégradation gracieuse).

**Négatives / à surveiller**
- Un appel HTTP synchrone de plus sur le chemin de création d'un créateur (pas sur les autres opérations) — latence à surveiller si le volume grossit ; un cache court (quelques secondes) serait le premier levier si ça devient un problème réel, pas construit par anticipation.
- Le comportement fail-open signifie qu'un tenant pourrait dépasser son quota pendant une panne d'`identity` — acceptable pour une règle produit, à revisiter seulement si ça devient un vecteur d'abus observé en pratique.
