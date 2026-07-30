# Creator OS — Architecture V1

Version : 1.0
Statut : Fondation validée (Sprint F0)
Voir aussi : [ADR-0001](../adr/0001-monorepo-enterprise.md) ·
[ADR-0002](../adr/0002-ai-router-provider-agnostic.md) ·
[ADR-0003](../adr/0003-data-ownership-privacy-by-default.md) ·
[DOMAIN_MODEL](DOMAIN_MODEL.md) · [DATA_MODEL](DATA_MODEL.md) ·
[ROADMAP](ROADMAP.md) · [README_DSI](../../README_DSI.md) ·
[SECURITY](../../SECURITY.md)

## Vision

Creator OS n'est pas un concurrent de Canva. Le portfolio n'est qu'une
**interface**. Les véritables actifs de la plateforme sont : Creator Twin,
AI Router, Memory Engine, Media Intelligence, Connectors, Security &
Governance Layer, Billing & Quota System.

L'ambition V1 est un **Operating System for Creators** : une couche qui
comprend un créateur (Creator Twin), agit pour lui (AI Router, Connectors)
et se souvient de lui (Memory Engine) — le portfolio public n'étant qu'une
des sorties possibles de ce système, pas son cœur.

## Les 9 domaines V1

| Domaine | Service | Rôle |
|---|---|---|
| Identity | `services/identity` | Auth, IAM, RBAC, tenants, sessions, audit |
| Creator Twin | `services/creator` | Profil créateur enrichi, représentation vivante |
| Media Engine | `services/media` | Upload, compression, CDN, media kit |
| AI Core | `services/ai` | AI Router — voir ADR-0002 |
| Memory | `services/memory` | Mémoire IA persistante par créateur |
| Connectors | `services/connector` | Instagram, TikTok, Canva, futurs réseaux |
| Billing | `services/billing` | Abonnements, facturation |
| Quota | `services/quota` | Crédits, limites d'usage |
| Security | `services/security` | Politiques transverses, gouvernance |

La correspondance avec les domaines V0 (d'où vient chaque domaine, ce qui
change) est détaillée séparément dans
[`DOMAIN_MODEL.md`](DOMAIN_MODEL.md) — pour qu'aucune décision initiale ne
soit silencieusement perdue.

## Principes directeurs (Creator Constitution)

Chaque service listé ci-dessus doit être conforme aux six principes
fondamentaux du projet — détaillés dans `README_DSI.md` et appliqués
concrètement dans `SECURITY.md` :

Data Ownership · Privacy By Default · AI Governance · Cost First ·
Provider Agnostic · Security First

## Ce que ce document n'est pas

Ce n'est pas une spécification technique par service. Conformément à la
règle de travail du projet (*"Ne pas coder sans spécification, décision
architecture, test prévu, documentation mise à jour"* — voir
[`CONTRIBUTING.md`](../../CONTRIBUTING.md)), chaque service recevra sa
propre spécification au moment de son sprint d'implémentation. Sprint F1
ouvre ce cycle avec `services/identity`.
