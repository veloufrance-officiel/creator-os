# services/ai

**Rôle** : AI Core — implémente l'AI Router, voir
[ADR-0002](../../docs/adr/0002-ai-router-provider-agnostic.md). Seul point
d'entrée vers les fournisseurs IA (OpenAI, Anthropic, Gemini, Mistral,
modèles locaux) pour toute la plateforme.

**Tables possédées** : `ai_requests`, `ai_router_decisions`.

**Statut** : non démarré. Dépend de `services/quota` pour la vérification
de crédits avant appel.
