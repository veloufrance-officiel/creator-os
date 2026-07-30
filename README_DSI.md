# Creator OS — Document de référence DSI / Investisseurs / Partenaires

*Ce document complète `README.md` (technique) avec une lecture stratégique,
non-technique. Statut : Sprint F0 — fondation posée, premier service
(Identity) en cours de cadrage.*

## Vision

Creator OS n'est pas positionné comme un concurrent direct de Canva ou
des outils de portfolio existants. Le portfolio public n'est qu'une
**interface** parmi d'autres sorties possibles d'un système plus large :
un *Operating System for Creators*, qui comprend le créateur (Creator
Twin), agit pour lui (routage IA, connecteurs vers ses plateformes), et
conserve une mémoire de son activité (Memory Engine).

Cette différenciation est structurante : elle oriente les investissements
techniques vers des actifs difficiles à répliquer (mémoire, orchestration
IA, intégrations) plutôt que vers l'éditeur de portfolio lui-même.

## Gouvernance — la Creator Constitution

Six principes engagent l'ensemble des équipes techniques, dès la
fondation, sans exception :

| Principe | Engagement concret |
|---|---|
| **Data Ownership** | Le créateur possède ses données : export, suppression, migration natifs sur chaque service qui en détient |
| **Privacy By Default** | Contenu privé par défaut, accès contrôlé, liens signés et expirables pour tout partage |
| **AI Governance** | Toute décision IA (quel modèle, pourquoi) est journalisée et explicable |
| **Cost First** | Estimation de coût avant tout traitement IA, consommation suivie par crédits/quotas |
| **Provider Agnostic** | Aucun fournisseur IA ne peut bloquer la plateforme (multi-provider par conception) |
| **Security First** | IAM, RBAC, audit logs, chiffrement, isolation tenant, RGPD — dès la fondation, pas en rattrapage |

Détail d'application : [`SECURITY.md`](SECURITY.md).

## Sécurité — synthèse

- Isolation stricte par tenant (une agence ou une marque ne peut jamais accéder aux données d'un autre tenant).
- Chiffrement en transit (TLS) et au repos.
- Journal d'audit sur toute action sensible.
- Conformité RGPD conçue dès la fondation (export/suppression/migration), pas ajoutée après coup — voir [ADR-0003](docs/adr/0003-data-ownership-privacy-by-default.md).
- Aucune certification externe engagée à ce stade (Sprint F0) ; feuille de route dans `SECURITY.md`.

## FinOps & gouvernance IA

L'architecture impose une estimation de coût **avant** chaque traitement
IA (principe *Cost First*), et un routage multi-fournisseur (OpenAI,
Anthropic, Gemini, Mistral, modèles locaux) qui arbitre entre coût,
qualité et quota disponible — voir [ADR-0002](docs/adr/0002-ai-router-provider-agnostic.md).

Conséquence directe pour le pilotage financier : le coût IA par créateur,
par fonctionnalité, et par fournisseur est mesurable dès la conception,
et non découvert a posteriori sur une facture cloud.

## Scalabilité

Architecture en monorepo (voir [ADR-0001](docs/adr/0001-monorepo-enterprise.md))
mais avec des services isolés, chacun conteneurisé indépendamment et
déployable sur Kubernetes (`infrastructure/kubernetes`) dès que le volume
d'un domaine le justifie. Le choix monorepo est un choix d'organisation
du code, pas une contrainte de déploiement : un service peut scaler seul.

## Registre de risques (Sprint F0)

| Risque | Mitigation |
|---|---|
| Dépendance à un fournisseur IA (prix, disponibilité) | AI Router multi-provider dès la conception (ADR-0002) |
| Non-conformité RGPD | Data Ownership natif par service, pas en rattrapage (ADR-0003) |
| Fuite de données inter-tenant | Isolation tenant à deux niveaux — applicatif + Row-Level Security base de données |
| Dette d'architecture (précipitation vers le code) | Règle de travail explicite : pas de code sans spécification, ADR, tests et documentation |
| Domaines non tranchés (Brand, Campaign hérités de la V0) | Explicitement non implémentés tant qu'une décision n'est pas actée — voir `docs/architecture/DOMAIN_MODEL.md` |

## Feuille de route

- **Sprint F0 (actuel)** — fondation : structure repo, documentation, CI/CD initial, environnement Docker, sécurité documentée.
- **Sprint F1** — Identity Service : un créateur peut créer un compte dans un environnement sécurisé (User, Tenant, Role, Permission, Session, OAuth, Audit Log).
- **Suivants** — Creator Twin, Media Engine, AI Core, Memory, Connectors, Billing, Quota, dans un ordre à confirmer selon priorités produit.

## Documents liés

[`README.md`](README.md) (technique) · [`SECURITY.md`](SECURITY.md) ·
[`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md) ·
[`docs/architecture/ROADMAP.md`](docs/architecture/ROADMAP.md) ·
[`docs/adr/`](docs/adr/) (décisions actées) · [`CHANGELOG.md`](CHANGELOG.md)
