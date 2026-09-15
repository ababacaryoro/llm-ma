# Dépannage

Les cas rencontrés le plus souvent. Si le problème n'est pas dans la liste, prévenir le formateur avec le message d'erreur complet.

## Installation

| Symptôme | Cause probable | Remède |
|---|---|---|
| PowerShell : *Impossible de charger le fichier… UnauthorizedAccess* | Politique d'exécution des scripts | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`, puis relancer la commande |
| `uv: command not found` après installation | `PATH` non rechargé | Fermer complètement le terminal (et VS Code), rouvrir. Sinon, correctif `PATH` de la section 4 d'[INSTALLATION.md](INSTALLATION.md) |
| `uv sync` échoue derrière un proxy ou un pare-feu | Accès réseau bloqué | Faire autoriser `github.com`, `pypi.org`, `files.pythonhosted.org`, `astral.sh`, `huggingface.co`, `api.mistral.ai`, `cloud.langfuse.com`. Si un proxy est imposé, le renseigner avant de relancer (ci-dessous) |
| `uv sync` très lent ou coupé | Connexion lente | `UV_HTTP_TIMEOUT=120` avant la commande, ou relancer : uv reprend où il s'est arrêté |
| `onnxruntime … doesn't have a wheel` | Lock antérieur au correctif multiplateforme | `git pull` puis `uv sync` |
| Aucune installation possible sur le poste (droits refusés) | Poste verrouillé | Parcours B, Codespaces (section 10 d'[INSTALLATION.md](INSTALLATION.md)) |
| Codespace lent ou figé | Machine 2 cœurs saturée | *Codespaces → Stop*, puis *Change machine type → 4 cœurs* |

Proxy :

```bash
# macOS / Linux
export HTTPS_PROXY=http://<serveur>:<port>
```

```powershell
# Windows (PowerShell)
$env:HTTPS_PROXY = "http://<serveur>:<port>"
```

Diagnostic Mistral sans passer par Python (remplacer la clé) :

```bash
curl -s -D - -o /dev/null https://api.mistral.ai/v1/chat/completions \
  -H "Authorization: Bearer $MISTRAL_API_KEY" -H "Content-Type: application/json" \
  -d '{"model":"ministral-8b-latest","messages":[{"role":"user","content":"pong"}],"max_tokens":3}' \
  | grep -iE "^(HTTP|x-ratelimit-limit-req-minute)"
```

`HTTP/2 200` et une limite supérieure à 0 : la clé et le plan sont bons, le problème est ailleurs. `429` avec `x-ratelimit-limit-req-minute: 0` : ce modèle n'est pas couvert par le plan.

## VS Code et notebooks

| Symptôme | Cause probable | Remède |
|---|---|---|
| `.venv` absent de la liste des interpréteurs | Environnement non détecté | Relancer `uv sync`, puis palette → *Developer: Reload Window*. Sinon *Enter interpreter path* : `.venv/bin/python` (macOS/Linux) ou `.venv\Scripts\python.exe` (Windows) |
| Le notebook ne trouve pas de noyau | Noyau non sélectionné | Bouton *Select Kernel* en haut à droite → *Python Environments…* → `.venv` |
| *Import could not be resolved* alors que la bibliothèque est installée | Mauvais interpréteur | Reprendre la section 7 d'[INSTALLATION.md](INSTALLATION.md), puis recharger la fenêtre |
| Le `.env` a été modifié mais le notebook garde l'ancienne valeur | Variables déjà chargées dans le noyau | Relancer la cellule d'imports : `get_llm()` relit `.env` à chaque appel. Sinon *Restart Kernel* |
| `ModuleNotFoundError: common` dans un notebook | Notebook lancé depuis le mauvais dossier | Les notebooks s'exécutent depuis la racine du dépôt (réglage `jupyter.notebookFileRoot` dans `.vscode/settings.json`). Vérifier que le dossier ouvert dans VS Code est bien `llm-ma` et pas un sous-dossier |

## Exécution des TP

| Symptôme | Cause probable | Remède |
|---|---|---|
| `check-env` : *module manquant* | `uv sync` non lancé | `uv sync` à la racine du dépôt |
| `OSError: ... MISTRAL_API_KEY est absent de votre .env` | `.env` manquant ou vide | Copier `env.example` en `.env`, renseigner la clé |
| Erreur 401 du fournisseur LLM | Clé invalide ou révoquée | Vérifier la clé dans la console du fournisseur, en recréer une |
| Erreur 429 Mistral **dès le premier appel**, y compris `check-env` | Plan *Experiment* non activé, ou modèle hors plan gratuit (`mistral-small`, `medium`…) | Vérifier le plan sur <https://admin.mistral.ai/plans> (vérification par téléphone), puis les limites sur <https://admin.mistral.ai/plateforme/limits>. Laisser `LLM_MODEL` vide ou sur un `ministral-*`. Diagnostic : la commande ci-dessous affiche la limite effective ; `0` = modèle ou plan non couvert |
| Erreur 429 (*rate limit*) Mistral en cours de TP | Tier gratuit limité en débit | Attendre quelques secondes et relancer la cellule. Éviter de relancer un notebook entier en boucle |
| Réponse vide ou tronquée | `max_tokens` atteint | Augmenter `LLM_MAX_TOKENS` dans `.env` (défaut 1024) |
| Premier appel à `indexer_corpus()` très long | Téléchargement des modèles d'embeddings (~230 Mo) | Normal la première fois. `uv run check-env` le fait en amont |
| `draw_mermaid_png` échoue | Pas d'accès réseau au service de rendu | Sans conséquence : `common.viz.afficher` bascule en rendu texte |
| Pas de traces dans Langfuse | Clés absentes, ou projet créé en région US | Clés d'un projet EU, et `LANGFUSE_HOST=https://cloud.langfuse.com` dans `.env` |
| Docker refuse de démarrer | Licence ou démon inactif | Sans conséquence : Docker est optionnel (démo du jour 2) |
