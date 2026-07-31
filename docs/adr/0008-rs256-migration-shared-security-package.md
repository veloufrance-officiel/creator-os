# ADR-0008 — Migration RS256 (déclencheur ADR-0005 atteint)

**Statut** : Accepté
**Date** : 2026-07-31
**Décideurs** : CTO / Architecture Creator OS — Sprint F2

## Contexte

[ADR-0005](0005-jwt-hs256-then-rs256.md) actait HS256 pour Sprint F1
avec un engagement explicite : migrer vers RS256 **avant** qu'un second
service ait besoin de vérifier un token émis par `identity`. Sprint F2
introduit `services/creator`, qui doit justement protéger ses routes par
le même access token — le déclencheur est atteint, pas anticipé par
prudence.

## Décision

1. `services/identity` génère/détient une paire de clés RSA, signe les
   access tokens en **RS256** avec la clé privée.
2. Nouvelle route publique (sans auth) `GET /.well-known/jwks.json` —
   expose la clé publique au format JWKS, avec un `kid` (id de clé,
   prépare une rotation future sans la faire maintenant — YAGNI au-delà).
3. Nouveau package partagé **`packages/security`** (Python, installable
   en dépendance locale par chemin depuis n'importe quel service) :
   `verify_identity_token(token)` — récupère et met en cache la JWKS
   d'`identity`, vérifie signature + `exp`, renvoie les claims. Tout
   service qui doit authentifier un appel via un token `identity`
   utilise ce package, n'écrit pas sa propre vérification.
4. `services/identity` continue de vérifier ses propres tokens
   localement (il détient déjà la clé, inutile de s'appeler
   lui-même en HTTP) — seuls les **autres** services utilisent
   `packages/security`.

**Gestion de la clé** : `JWT_PRIVATE_KEY_PEM` / `JWT_PUBLIC_KEY_PEM` en
variables d'environnement pour un déploiement réel. À défaut (dev
local), une paire est générée en mémoire au démarrage — explicitement
**non persistante** : toute session existante devient invalide au
redémarrage. Acceptable en dev, jamais en production (voir `SECURITY.md`,
à mettre à jour avant tout déploiement réel).

## Alternatives envisagées

| Option | Rejetée car |
|---|---|
| Rester en HS256, partager `JWT_SECRET` avec `services/creator` | Exactement ce qu'ADR-0005 avait identifié comme dette à ne pas laisser s'installer : chaque nouveau service élargirait la surface de fuite d'un secret symétrique unique |
| Chaque service réimplémente sa propre vérification JWKS | Duplication déjà observée en germe (le code de `app/oauth/oidc.py` dans `identity` fait déjà exactement ça pour Google/Apple) — `packages/security` centralise cette logique une fois pour toutes |
| Rotation de clé automatisée dès maintenant | Aucun besoin actuel (un seul environnement, pas encore d'incident à mitiger) — le `kid` prépare le terrain sans construire la mécanique de rotation prématurément |

## Conséquences

**Positives**
- Compromission d'un service consommateur (ex. bug dans `creator`) ne permet pas de forger des tokens — il n'a jamais la clé privée, seulement la publique.
- Ajout d'un troisième, quatrième service : aucune nouvelle décision à prendre, ils importent `packages/security` comme `creator` le fera.

**Négatives / à surveiller**
- Chaque service consommateur dépend désormais de la disponibilité réseau de `services/identity` pour sa toute première vérification (JWKS non encore en cache) — acceptable tant qu'il n'y a qu'un environnement, à surveiller (cache + fallback) si la charge ou la topologie réseau change.
- Les sessions actives au moment de ce déploiement (aucune en prod à ce stade, uniquement en dev) sont invalidées par le changement d'algorithme — sans impact réel puisqu'aucun environnement de production n'existe encore.
