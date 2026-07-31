# ADR-0011 — Type de compte à l'inscription : perso / team / entreprise

**Statut** : Accepté
**Date** : 2026-07-31
**Décideurs** : CTO / Architecture Creator OS — Sprint Identity (retour F1)

## Contexte

Proposition : demander, avant la fin de l'inscription, si le compte est
**perso**, **team**, ou **entreprise** — pour regrouper les choix et les
processus d'onboarding selon le profil.

Idée saine et un motif SaaS classique (Slack, Notion, Linear font tous
ce choix à l'inscription). Elle recoupe une frontière qui existe déjà :
`Tenant` est *déjà* la limite compte/facturation, et
[ADR-0010](0010-multi-creator-agency-tenants.md) permet déjà à un
tenant de gérer plusieurs créateurs, indépendamment de ce choix. Deux
points à trancher avant de coder plutôt qu'après :

1. **Team vs Entreprise** n'a aucune différence fonctionnelle définie à
   ce stade (sièges illimités ? SSO ? support dédié ? facturation
   différente ?). Sans réponse produit, inventer une distinction
   maintenant serait arbitraire.
2. **Team et Entreprise supposent presque toujours plusieurs
   utilisateurs sur un même tenant** — or l'invitation multi-utilisateurs
   n'existe pas encore (différé depuis Sprint F1, reconfirmé en
   ADR-0010). Le choix peut être capturé maintenant sans que la
   fonctionnalité derrière existe encore entièrement.

## Décision

**Validé, avec un périmètre volontairement réduit à de la
classification pour l'instant** — pas de comportement différent entre
`team` et `entreprise` tant qu'aucun besoin concret ne le justifie
(Cost First). Concrètement :

1. `Tenant.account_type` (`personal` | `team` | `enterprise`).
2. **Inscription email/mot de passe** : champ **requis** dans
   `POST /auth/register` — le contrat d'API force le choix, conforme à
   « avant l'inscription finale ».
3. **Inscription OAuth** (Google/Apple, ADR-0007) : pas d'étape
   interactive possible dans ce flow (redirection/token en un temps) →
   défaut `personal`. Modifiable ensuite (point 4).
4. Nouveau : `GET /tenant`, `PATCH /tenant` — consulter/changer le type
   de compte après coup (nécessaire : sans ça, un compte créé par OAuth
   ne pourrait jamais devenir team/entreprise). Changement audité
   (`tenant.account_type_changed`).
5. **Aucune limite de nombre de créateurs par type** — `personal`
   n'interdit pas plusieurs `Creator` (ADR-0010 reste inchangé) ; c'est
   une classification, pas une contrainte technique. Si un vrai besoin
   de plafond par palier apparaît, ADR séparé.
6. **Toujours différé** : invitation multi-utilisateurs par tenant.
   Choisir `team`/`entreprise` classe l'intention, ne débloque pas
   encore la fonctionnalité derrière.

## Alternatives envisagées

| Option | Rejetée car |
|---|---|
| Distinguer déjà team/entreprise par une limite de sièges, SSO, etc. | Aucune spécification produit de ces limites à ce stade — inventer serait arbitraire, à corriger une fois défini |
| `account_type` optionnel avec défaut silencieux | Contredit l'intention explicite : un choix fait *avant* la fin de l'inscription, pas une valeur implicite |
| Bloquer `personal` à un seul créateur | Ajoute une contrainte non demandée ; le besoin exprimé était de classer les comptes, pas de limiter techniquement |

## Conséquences

**Positives**
- Classification disponible dès maintenant pour la Billing future (Sprint suivant) sans retrofit de données.
- `GET/PATCH /tenant` couvre aussi le cas OAuth (sinon sans issue).

**Négatives / à surveiller**
- `team` et `enterprise` sont aujourd'hui identiques en comportement — ne pas laisser cette ambiguïté s'installer trop longtemps sans définition produit, ou la classification perd sa valeur.
- Ce choix ne doit pas être confondu avec la délégation multi-utilisateurs (toujours différée) : documenté explicitement pour éviter la confusion la prochaine fois que ce sujet revient.
