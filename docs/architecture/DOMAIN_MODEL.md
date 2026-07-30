# Creator OS — Domain Model : migration V0 → V1

Complète [`ARCHITECTURE.md`](ARCHITECTURE.md). La documentation V0
(`docs/architecture/v0/`) est préservée telle quelle ; ce document trace
comment chacun de ses domaines se retrouve (ou non) dans l'architecture
V1, pour qu'aucune décision initiale ne soit silencieusement perdue.

| Domaine V0 | Devenir en V1 | Notes |
|---|---|---|
| `users` (table) | `services/identity` | Étendu : Tenant, Role, Permission, Session, OAuth, Audit Log (voir Sprint F1) |
| `Creator` | `services/creator` (Creator Twin) | Le profil devient une représentation enrichie, pas juste un CRUD |
| `Portfolio`, `PortfolioBlock` | `apps/web` (interface) | Le portfolio redevient une **vue**, pas un service ; structuré par `services/creator`, alimenté par `services/media` |
| `Asset` | `services/media` | Inchangé dans l'intention, service dédié désormais |
| `MediaKit` | `services/media` | Fusionné dans Media Engine |
| `Analytics` | `services/analytics` | Promu en service à part entière |
| `AIMemory` | `services/memory` | Renommé Memory Engine, portée étendue au-delà de la bio |
| `subscriptions` (table) | `services/billing` | Étendu en service complet |
| — (n'existait pas en V0) | `services/ai`, `services/connector`, `services/quota`, `services/security` | Nouveaux domaines V1, pas de dette à migrer |
| `Brand`, `Campaign` (domaines cités en V0, jamais spécifiés) | **Non tranché** | À statuer : sous-domaine de `creator`, ou service dédié si le volume le justifie. Ne pas coder avant décision (règle de travail du projet, voir `CONTRIBUTING.md`) |

## Pourquoi ce document existe séparément

`Brand` et `Campaign` en particulier ne doivent pas être « oubliés » par
simple absence de la liste des 9 domaines dans `ARCHITECTURE.md` — ils
sont ici explicitement marqués comme décision en attente, pas comme
domaine abandonné.
