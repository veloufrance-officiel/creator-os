# ADR-0002 — AI Router agnostique au fournisseur

**Statut** : Accepté
**Date** : 2026-07-31
**Décideurs** : CTO / Architecture Creator OS

## Contexte

Chaque appel IA de la plateforme (bio créateur, analyse de media kit,
Creator Twin, recommandations) n'a pas les mêmes exigences de coût, de
qualité ou de latence. Dépendre d'un seul fournisseur expose à trois
risques : lock-in commercial, absence de bascule en cas d'incident chez
ce fournisseur, et impossibilité d'arbitrer le coût par cas d'usage.

## Décision

Le service `services/ai` implémente un **AI Router** : une couche
d'abstraction unique par laquelle transitent tous les appels IA de la
plateforme. Le routeur sélectionne dynamiquement le provider (OpenAI,
Anthropic, Gemini, Mistral, ou modèle local) selon quatre critères,
dans cet ordre de priorité par défaut :

1. **Coût** — estimation avant exécution (principe *Cost First*)
2. **Qualité requise** — définie par le type de tâche
3. **Contexte** — taille, sensibilité, latence tolérée
4. **Quota utilisateur/tenant** — crédits restants

Aucun service métier n'appelle un SDK provider directement : tous passent
par `packages/sdk` → `services/ai`.

## Alternatives envisagées

| Option | Rejetée car |
|---|---|
| Intégration directe d'un SDK provider dans chaque service consommateur | Couplage fort, aucune bascule possible en cas d'incident, coût non pilotable de façon centralisée |
| Un seul fournisseur "stratégique" avec fallback manuel | Ne respecte pas le principe *Provider Agnostic* de la Creator Constitution, lock-in commercial |

## Conséquences

**Positives**
- Résilience : bascule automatique si un provider est en panne ou en rate limit.
- Optimisation de coût mesurable et centralisée (un seul endroit à instrumenter).
- Ajout d'un nouveau provider sans toucher aux services consommateurs.

**Négatives / à surveiller**
- La couche d'abstraction est elle-même un point critique : elle doit être testée, monitorée, et chaque décision de routing doit rester **explicable** (principe *AI Governance* — voir `SECURITY.md`).
- Nécessite un harnais d'évaluation continue pour comparer la qualité réelle entre providers, pas seulement le coût.
- La latence ajoutée par la couche de routing doit être mesurée et rester négligeable face au temps de génération du modèle.
