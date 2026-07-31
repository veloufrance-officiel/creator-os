# ADR-0004 — Hachage des mots de passe : Argon2id

**Statut** : Accepté
**Date** : 2026-07-31
**Décideurs** : CTO / Architecture Creator OS — Sprint F1

## Contexte

`services/identity` doit stocker des identifiants de connexion. Le choix
de l'algorithme de hachage est difficile à changer une fois des mots de
passe réels stockés (nécessite une migration progressive à la prochaine
connexion de chaque utilisateur).

## Décision

**Argon2id** (bibliothèque `argon2-cffi`), paramètres par défaut de la
bibliothèque au démarrage (time_cost, memory_cost, parallelism), à
ajuster selon la charge réelle observée en production — pas avant.

## Alternatives envisagées

| Option | Rejetée car |
|---|---|
| bcrypt | Standard éprouvé, mais Argon2id est la recommandation actuelle de l'OWASP (résistant GPU/ASIC par le coût mémoire, pas seulement CPU) |
| SHA-256 / SHA-512 simple | Jamais adapté au hachage de mot de passe (trop rapide à calculer, pas de facteur de coût réglable) |

## Conséquences

**Positives**
- Aligné sur la recommandation actuelle de l'OWASP Password Storage Cheat Sheet.
- Résistant aux attaques par accélération matérielle (coût mémoire, pas seulement temps CPU).

**Négatives / à surveiller**
- Dépendance à une extension C (`argon2-cffi`) — à vérifier à chaque changement d'image Docker de base.
- Les paramètres de coût doivent être révisés si la charge de connexion augmente significativement (compromis latence/sécurité).
