# services/creator

**Rôle** : Creator Twin — profil créateur enrichi, structure du portfolio
(le portfolio affiché reste une vue dans `apps/web`, ce service en détient
la structure).

**Tables possédées** : `creators`, `creator_twins`, `portfolios`,
`portfolio_blocks`.

**Statut** : non démarré. Dépend de `services/identity` (Sprint F1).
