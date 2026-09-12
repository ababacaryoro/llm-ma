# Fournisseurs LLM

Tout le code passe par `common.llm.get_llm()`. Le fournisseur se choisit avec une seule variable dans `.env` :

```
LLM_PROVIDER=mistral   # mistral | openai | ollama
```

Rien d'autre à changer : les notebooks ne dépendent d'aucun fournisseur.

## mistral (défaut)

- Compte gratuit sur <https://console.mistral.ai>, plan *Experiment*, sans carte bancaire.
- Modèle par défaut : `mistral-small-latest`. Surchargeable avec `LLM_MODEL` dans `.env`.
- Limite : quelques requêtes par seconde et un quota mensuel. Suffisant pour les exercices unitaires. Sur les boucles multi-agents (10 à 30 appels par run), attendre entre deux exécutions.
- Erreur 429 = limite de débit atteinte : attendre et relancer la cellule.

## openai (si une clé est fournie)

- Le formateur peut distribuer une clé temporaire, plafonnée, révoquée en fin de formation.
- `LLM_PROVIDER=openai` et `OPENAI_API_KEY=<clé>` dans `.env`.
- Modèle par défaut : classe « mini ». Plus rapide que le tier gratuit Mistral sur les runs multi-agents.

## ollama (local, hors ligne)

- Installer Ollama (<https://ollama.com>), puis `ollama pull qwen3:4b`. Prévoir 8 Go de RAM.
- `LLM_PROVIDER=ollama`, aucune clé.
- Qualité de tool calling limitée sur les petits modèles : certains exercices échoueront par moments. C'est en soi un enseignement (robustesse, module industrialisation).

## Autres tiers gratuits

Groq, Google AI Studio, OpenRouter proposent des accès gratuits avec quotas, changeants d'un mois à l'autre. `init_chat_model` les supporte via le package d'intégration correspondant (`uv add langchain-groq`, etc.), puis `LLM_MODEL=groq:<modèle>`. Non utilisés en séance.

## Garde-fous budget

Présents dans le code, à conserver :

- `max_tokens` borné à chaque appel (défaut 1024, `LLM_MAX_TOKENS` dans `.env`) ;
- `temperature=0` par défaut ;
- `recursion_limit` explicite sur chaque graphe LangGraph ;
- traces Langfuse pour voir le coût par run.

Un système multi-agents multiplie les appels. Ces garde-fous sont un point du module industrialisation.
