# Module 01 — Rappels LLM : améliorer l'utilisation d'un LLM

Durée indicative du TP : 60 min. Suit le chapitre « Rappels sur les LLM » (prompt engineering, mémoire, RAG).

**Objectif** : sur une tâche unique, mesurer ce que chaque technique corrige, et ce qu'elle coûte.

**La tâche** : répondre aux questions d'une équipe sur un texte de loi récent, au format fiche (`REPONSE / DETAILS / SOURCE / CONFIANCE`). Le texte est postérieur à la date de coupure des modèles : sans RAG, le modèle ne peut pas répondre juste.

## Déroulé de `TP1.ipynb`

| Étape | Technique | TODO | Ce que la mesure montre |
|---|---|---|---|
| 0 | Prompt brut | aucun | forme libre, 500 mots, références absentes |
| 1 | Prompt engineering (persona, tâche, contraintes, exemple, délimiteurs) | texte des contraintes et de l'exemple one-shot | format 3/3, sources inventées avec « confiance haute » |
| 2 | Mémoire : aucune, buffer, résumé | texte de la consigne de résumé | le format tient ou pas d'un tour à l'autre, tokens par tour |
| 3 | RAG : indexer, retrouver, augmenter, générer | texte du message augmenté | faits 6/6, source juste 3/3, tokens ×4 |
| Fin | Tableau comparatif | | chaque étape corrige un défaut différent |

Bonus : sortie structurée Pydantic, changement de corpus.

## Mesure

`src/evaluation.py` : même jeu de questions à chaque étape (`data/corpus/<corpus>/questions.json`), et pour chaque réponse : format respecté, nombre de mots, faits attendus présents, source juste (le champ SOURCE mentionne le bon article, ce qui distingue une référence vraie d'une référence inventée), tokens en entrée et en sortie. `Banc.tableau()` produit le comparatif final.

Les TODO ne demandent que du texte (prompts, consignes, gabarit) : aucune connaissance de LangChain n'est nécessaire. La fonction `appeler()` définie en tête du notebook cache la construction des messages.

## Briques utilisées

- `common.llm.get_llm()` et `invoquer()` (nouvel essai sur erreur 429)
- `common.rag` : `indexer_corpus`, `rechercher`, `formater_contexte`, `questions_test`

```mermaid
flowchart LR
    Q[question] --> R[rechercher : dense + BM25, fusion RRF] --> C[formater_contexte] --> P[prompt système + passages + question] --> L[LLM] --> F[fiche]
```

## Corpus

Par défaut `loi-repost` (texte réel). Secours : `orion` (note de cadrage fictive). Bascule par `CORPUS = "..."` en tête du notebook ou `RAG_CORPUS` dans `.env`. Détails dans `data/corpus/*/README.md`.

## Budget d'appels

Environ 25 appels LLM et 2 à 3 minutes pour un passage complet du corrigé sur `ministral-8b-latest` (tier gratuit Mistral). Une pause d'une seconde est intégrée entre les questions du banc.

Résultat de référence sur `ministral-8b-latest` :

| Étape | Format OK | Mots | Faits justes | Source juste | Tokens entrée |
|---|---|---|---|---|---|
| 0 - prompt brut | 0/3 | 505 | 3/6 | 0/3 | 31 |
| 1 - prompt travaillé | 3/3 | 81 | 1/6 | 0/3 | 343 |
| 2 - mémoire aucune | 0/3 | 454 | 3/6 | 0/3 | 31 |
| 2 - mémoire buffer | 3/3 | 92 | 4/6 | 0/3 | 485 |
| 2 - mémoire résumé | 3/3 | 99 | 2/6 | 0/3 | 740 |
| 3 - RAG | 3/3 | 68 | 6/6 | 3/3 | 1427 |
