# Fournisseurs LLM

Tout le code passe par `common.llm.get_llm()`. Le fournisseur se choisit avec une seule variable dans `.env` :

```
LLM_PROVIDER=mistral   # mistral | openai | ollama
```

Rien d'autre à changer : les notebooks ne dépendent d'aucun fournisseur.

## mistral (défaut)

- Compte gratuit sur <https://console.mistral.ai>, plan *Experiment*, sans carte bancaire, numéro de téléphone vérifié.
- Sur le plan Experiment, seuls certains modèles ont un débit non nul. Constaté en septembre 2026 (en-tête `x-ratelimit-limit-req-minute` des réponses) :

  | Modèle | Requêtes / min | Usage |
  |---|---|---|
  | `ministral-3b-latest` | 750 | très rapide, qualité limitée |
  | `ministral-8b-latest` | 188 | **défaut de la formation** |
  | `ministral-14b-latest` | 30 | meilleure qualité, débit à surveiller |
  | `codestral-latest` | 125 | code |
  | `mistral-small`, `mistral-medium`, `magistral`, `devstral` | **0** | 429 systématique |
  | `mistral-large` | refusé | 403, hors plan |

  Ces limites changent : vérifier sur <https://admin.mistral.ai/plateforme/limits>.
- Changer de modèle : `LLM_MODEL=mistralai:ministral-14b-latest` dans `.env`.
- Erreur 429 en cours de TP = débit dépassé : attendre et relancer (`common.llm.invoquer` le fait automatiquement). Erreur 429 dès le premier appel = modèle hors plan ou plan non activé, voir [DEPANNAGE.md](DEPANNAGE.md).

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
