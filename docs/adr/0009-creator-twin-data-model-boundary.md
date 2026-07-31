# ADR-0009 — Creator Twin : modèle de données et frontière avec Identity

**Statut** : Accepté
**Date** : 2026-07-31
**Décideurs** : CTO / Architecture Creator OS — Sprint F2

## Contexte

`docs/architecture/DATA_MODEL.md` esquissait deux tables séparées,
`creators` et `creator_twins`, sans justification concrète autre que le
nom marketing « Creator Twin ». Au moment d'implémenter, aucune
différence fonctionnelle réelle ne justifie deux tables : ce serait de
la complexité artificielle. Par ailleurs, `services/creator` doit
référencer des utilisateurs et tenants qui appartiennent à
`services/identity`, un service distinct.

## Décision

**Une seule table `creators`**, avec le champ enrichi (niche, ton,
audience, bio) — pas de table `creator_twins` séparée. « Creator Twin »
est réalisé comme un profil enrichi, pas comme une entité à part. Une
séparation (ex. historique de versions) sera introduite plus tard si un
besoin concret apparaît (typiquement porté par `services/memory`, pas
anticipé ici) — voir `docs/architecture/DATA_MODEL.md`, mis à jour en
conséquence par ce commit.

**Aucune contrainte de clé étrangère vers les tables d'Identity.**
`creators.user_id` et `creators.tenant_id` sont des UUID simples, pas
des `ForeignKey`. Le principe déjà posé dans `DATA_MODEL.md` (« chaque
table appartient à un seul service, pas d'accès direct cross-service »)
s'applique dès la première paire de services, pas seulement quand ce
sera physiquement forcé par des bases séparées. L'appartenance d'un
`user_id` est garantie par la vérification du token (`packages/security`,
ADR-0008), pas par une contrainte SQL.

**Autorisation : isolation par tenant, pas de permission fine pour
l'instant.** Il n'existe qu'un seul rôle par tenant (`owner`, voir
Sprint F1) — vérifier un code de permission `creator:*` n'apporterait
rien tant qu'il n'y a rien à distinguer. `services/creator` vérifie
seulement que l'appelant agit sur les données de **son propre**
`tenant_id` (extrait du token). Des permissions fines seront
introduites si/quand un vrai besoin de rôles multiples par tenant
apparaît (ex. agence avec plusieurs collaborateurs) — pas avant.

**Base de données** : partagée avec `identity` pour l'instant (même
instance Postgres, voir `infrastructure/docker`), séparation physique
en bases distinctes différée — coût faible à faire plus tard, aucune
valeur à le faire avant qu'un vrai déploiement le justifie (Cost First).
L'absence de FK cross-service (ci-dessus) rend cette séparation future
non-cassante : aucune contrainte ne dépend du partage physique actuel.

## Alternatives envisagées

| Option | Rejetée car |
|---|---|
| `creators` + `creator_twins` séparées | Aucune différence fonctionnelle actuelle ne justifie la complexité ; nom marketing pris au pied de la lettre sans besoin réel |
| FK vers `identity.users` | Couplage fort entre bases de données de deux services censés être indépendants — contredit le principe déjà écrit dans `DATA_MODEL.md` |
| Permissions `creator:*` dès maintenant | Rien à distinguer avec un seul rôle par tenant — over-engineering au sens Cost First |
| Bases Postgres séparées dès ce sprint | Coût d'infrastructure (init multi-DB, gestion de deux `DATABASE_URL`) sans bénéfice réel avant un déploiement multi-environnement |

## Conséquences

**Positives**
- Modèle de données honnête : ce qui existe reflète un besoin réel, pas une anticipation non fondée.
- Migration future vers des bases séparées sans rupture (pas de FK à défaire).

**Négatives / à surveiller**
- L'intégrité référentielle `user_id`/`tenant_id` n'est **pas** garantie par Postgres côté `creator` — un bug applicatif pourrait écrire un `user_id` inexistant. Acceptable tant que le volume est faible et la revue de code humaine ; à réévaluer (validation applicative renforcée, ou événementiel) si ça devient un vrai risque opérationnel.
- Si plusieurs rôles par tenant deviennent réels, il faudra une vraie politique de permissions `creator:*` — pas transposable automatiquement depuis le catalogue `identity` actuel (catalogues de permissions par service, pas centralisés — cohérent avec l'indépendance des services).
