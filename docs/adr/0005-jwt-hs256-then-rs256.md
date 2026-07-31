# ADR-0005 — Stratégie de signature JWT : HS256 pour F1, migration RS256 prévue

**Statut** : Accepté
**Date** : 2026-07-31
**Décideurs** : CTO / Architecture Creator OS — Sprint F1

## Contexte

`services/identity` émet des tokens consommés, à terme, par d'autres
services (`apps/api`, puis chaque `services/*` une fois implémenté). Deux
familles d'algorithmes JWT existent : symétrique (HS256, un seul secret
partagé pour signer et vérifier) et asymétrique (RS256, clé privée pour
signer chez `identity`, clé publique distribuée aux services qui
vérifient seulement).

À ce stade (Sprint F1), **aucun autre service n'existe encore** — rien ne
vérifie de token en dehors d'`identity` lui-même.

## Décision

**HS256** pour Sprint F1, secret unique via variable d'environnement
`JWT_SECRET` (voir `.env.example`).

**Engagement explicite** : migrer vers RS256 **avant** que tout second
service ait besoin de vérifier un token émis par `identity` (au plus
tard au sprint qui introduit le premier consommateur — probablement
`apps/api` en tant que gateway). Ce n'est pas une décision à revisiter
« si on y pense », c'est une dette actée avec un déclencheur précis.

## Alternatives envisagées

| Option | Rejetée car |
|---|---|
| RS256 dès F1 | Complexité de gestion de clés (rotation, distribution) injustifiée tant qu'un seul service existe — over-engineering au sens du principe Cost First |
| Pas de migration prévue, HS256 partout | Force à partager le secret de signature avec chaque nouveau service = surface d'attaque qui grandit à chaque service ajouté, et couplage fort |

## Conséquences

**Positives**
- Implémentation F1 simple, rapide, correcte pour le périmètre actuel.
- Trajectoire de migration explicite = pas de dette silencieuse.

**Négatives / à surveiller**
- **Ne pas oublier** ce déclencheur : le premier service qui a besoin de vérifier un token `identity` doit d'abord déclencher la migration RS256, pas la contourner en partageant `JWT_SECRET`.
- Durée de vie courte pour les access tokens (voir `services/identity/SPEC.md`) tant que la révocation immédiate n'est pas garantie autrement que par expiration.
