# Mise en place de l'environnement de travail

À faire **avant la formation**. Compter 20 à 30 minutes, dont une bonne partie de téléchargement. En cas de blocage, voir [DEPANNAGE.md](DEPANNAGE.md), puis prévenir le formateur.

Deux parcours :

- **Parcours A, installation locale** (sections 1 à 9) : VS Code, Git, uv, puis le dépôt.
- **Parcours B, GitHub Codespaces** (section 10) : rien à installer, tout tourne dans le navigateur. Solution de repli si le poste est verrouillé ou si le parcours A échoue.

Dans les deux cas, la section 0 (comptes) est nécessaire.

---

## 0. Comptes à créer

| Compte | Obligatoire | Rôle | Lien |
|---|---|---|---|
| Mistral AI | **Oui** | Fournisseur LLM des TP (tier gratuit) | <https://console.mistral.ai> |
| Langfuse (région **EU**) | Recommandé | Visualiser les traces des agents (jour 2) | <https://cloud.langfuse.com> |
| GitHub | Optionnel | Codespaces (parcours B), clone avec `git` | <https://github.com> |
| Hugging Face | Optionnel | Explorer des modèles open-weight | <https://huggingface.co> |

**Mistral** : après inscription, activer le plan *Experiment* (gratuit, sans carte bancaire ; une vérification par numéro de téléphone est demandée), puis *Clés API → Créer une nouvelle clé*. Copier la clé immédiatement, elle n'est plus affichée ensuite. Sans plan activé, toute requête est refusée avec une erreur 429.

**Langfuse** : créer une *organisation* puis un *projet* « formation ». Dans *Settings → API Keys*, noter la clé publique (`pk-lf-…`) et la clé secrète (`sk-lf-…`).

---

## 1. Installer Visual Studio Code

Télécharger depuis <https://code.visualstudio.com>.

Sous Windows, cocher pendant l'installation **« Ajouter à PATH »** et **« Ouvrir avec Code »**.

PyCharm convient aussi, à condition que l'édition installée inclue le support Jupyter. Les instructions ci-dessous sont données pour VS Code.

## 2. Installer les extensions VS Code

Panneau **Extensions** (`Ctrl+Shift+X`, `Cmd+Shift+X` sur macOS). Coller l'identifiant dans la barre de recherche pour tomber directement sur la bonne extension.

| Extension | Identifiant | Rôle |
|---|---|---|
| Python | `ms-python.python` | Support du langage, sélection de l'interpréteur |
| Pylance | `ms-python.vscode-pylance` | Autocomplétion et analyse de code |
| Jupyter | `ms-toolsai.jupyter` | Exécution des notebooks `.ipynb` dans VS Code |
| Ruff *(optionnel)* | `charliermarsh.ruff` | Formatage et qualité du code |

À l'ouverture du dépôt, VS Code propose lui-même ces extensions (fichier `.vscode/extensions.json`).

## 3. Installer Git

Vérifier d'abord, dans un terminal :

```bash
git --version
```

Si la commande échoue : <https://git-scm.com/downloads> (sous Windows, conserver les options par défaut).

Git n'est pas indispensable : le dépôt peut aussi être téléchargé en zip (section 5).

## 4. Installer uv

`uv` remplace `pip`, `venv` et `conda` en un seul outil. Il installe aussi Python : **inutile d'installer Python séparément**.

**Windows**, dans PowerShell :

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS / Linux**, dans un terminal :

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Fermer puis rouvrir le terminal**, et vérifier :

```bash
uv --version
```

Si la commande n'est pas reconnue, le dossier d'installation n'est pas dans le `PATH`. Correctif :

- **Windows** (PowerShell, à taper tel quel, sans rien remplacer) :

  ```powershell
  $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
  ```

  Cette ligne ne vaut que pour la session en cours. Pour la rendre permanente : *Paramètres → Système → Informations système → Paramètres système avancés → Variables d'environnement*, ajouter `%USERPROFILE%\.local\bin` à la variable `Path` de l'utilisateur, puis rouvrir le terminal.

- **macOS** (le shell par défaut est zsh) :

  ```bash
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
  source ~/.zshrc
  ```

- **Linux** (bash) :

  ```bash
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
  source ~/.bashrc
  ```

## 5. Récupérer le dépôt de la formation

Dépôt : <https://github.com/ababacaryoro/llm-ma>

**Avec Git**, depuis le dossier de son choix :

```bash
git clone https://github.com/ababacaryoro/llm-ma.git
cd llm-ma
```

**Sans Git** : sur la page GitHub, bouton *Code → Download ZIP*, dézipper dans le dossier de son choix.

Puis ouvrir le dossier `llm-ma` dans VS Code (*Fichier → Ouvrir le dossier*, ou `code .` depuis un terminal placé dans le dossier).

## 6. Créer l'environnement et installer les dépendances

Le dépôt contient `pyproject.toml` (liste des dépendances) et `uv.lock` (versions exactes). Une seule commande, dans le terminal intégré de VS Code (*Terminal → Nouveau terminal*) :

```bash
uv sync
```

Cette commande :

- installe Python 3.12 s'il est absent ;
- crée l'environnement virtuel dans `.venv/` à la racine du projet ;
- installe toutes les bibliothèques de la formation (LangChain, LangGraph, Qdrant, Langfuse, Jupyter…) aux versions exactes du `uv.lock`.

Compter quelques centaines de Mo et 3 à 10 minutes selon la connexion. Tout le monde obtient exactement le même environnement, ce qui évite les écarts de comportement d'un poste à l'autre.

## 7. Connecter VS Code à cet environnement

Deux réglages distincts, tous les deux nécessaires.

**L'interpréteur Python** (pour les fichiers `.py` et le terminal) :

1. Palette de commandes : `Ctrl+Shift+P` (`Cmd+Shift+P` sur macOS).
2. Taper **Python: Select Interpreter**.
3. Choisir l'interpréteur situé dans `.venv` du projet (proposé en tête de liste, mention *Recommended*).

**Le noyau Jupyter** (pour les notebooks `.ipynb`) :

1. Ouvrir n'importe quel notebook du dépôt.
2. En haut à droite, cliquer sur **Select Kernel** (ou sur le nom du noyau courant).
3. Choisir *Python Environments…* puis `.venv`.

Ce choix est mémorisé pour les notebooks suivants.

## 8. Variables d'environnement

1. À la racine du projet, copier le fichier `env.example` et nommer la copie `.env` (avec le point devant).
2. Ouvrir `.env` et renseigner :

```
LLM_PROVIDER=mistral
MISTRAL_API_KEY=<la clé créée en section 0>
```

3. Si un compte Langfuse a été créé, renseigner aussi `LANGFUSE_PUBLIC_KEY` et `LANGFUSE_SECRET_KEY`. Sinon, laisser ces lignes vides : tout fonctionne sans traces.

Le fichier `.env` contient des secrets : il est ignoré par Git et ne doit jamais être partagé.

## 9. Vérifier l'installation

```bash
uv run check-env
```

Le script vérifie Python, les dépendances, le fichier `.env`, fait un appel réel au LLM et télécharge les modèles d'embeddings (~230 Mo, une seule fois). Résultat attendu :

```
  OK         Python 3.12 — 3.12.x
  OK         module langchain
  ...
  OK         fichier .env
  OK         fournisseur LLM — LLM_PROVIDER=mistral
  OK         appel LLM — reponse: 'pong'
  OK         embeddings locaux (fastembed) — modeles charges
  ATTENTION  cles Langfuse — traces desactivees
  ATTENTION  docker — absent — sans impact sur les TP
─────────────────────────────────────────────
Environnement pret (2 avertissement(s) non bloquant(s))
```

Les lignes `ATTENTION` ne bloquent pas. Une ligne `ERREUR` doit être corrigée : voir [DEPANNAGE.md](DEPANNAGE.md).

**Checklist finale**

- [ ] `uv run check-env` se termine par `Environnement pret`
- [ ] Un notebook s'ouvre dans VS Code avec le noyau `.venv` sélectionné
- [ ] La clé Mistral est dans `.env`

---

## 10. Parcours B : GitHub Codespaces

Environnement complet dans le navigateur, sans rien installer sur le poste. Nécessite un compte GitHub (gratuit). Le quota mensuel gratuit d'un compte personnel couvre largement les deux jours.

1. Ouvrir <https://github.com/ababacaryoro/llm-ma>.
2. Bouton *Code → Codespaces → Create codespace on main*.
3. Attendre la fin de l'installation automatique (2 à 3 minutes, visible dans le terminal).
4. Copier `env.example` en `.env`, renseigner la clé Mistral (section 8).
5. Terminal : `uv run check-env`.

VS Code dans le navigateur se comporte comme la version locale (sélection du noyau, section 7). Penser à arrêter le codespace en fin de journée (*Codespaces → Stop*) pour préserver le quota.

---

## Docker (facultatif)

Aucun TP n'en dépend. Docker sert uniquement à une démonstration d'industrialisation si nécessaire.

> **Licence** : Docker Desktop n'est gratuit que pour l'usage personnel, l'éducation et les entreprises de moins de 250 salariés et 10 M$ de chiffre d'affaires. Dans un grand groupe, ne pas l'installer sur un poste professionnel sans licence. Alternatives gratuites : Codespaces (Docker inclus), Podman Desktop, Rancher Desktop, Docker Engine sous WSL2.

---

## Commandes uv utiles

| Commande | Effet |
|---|---|
| `uv sync` | Installe ou met à jour l'environnement depuis `pyproject.toml` et `uv.lock` |
| `uv add <paquet>` | Ajoute une dépendance et l'installe |
| `uv add --dev <paquet>` | Ajoute une dépendance de développement |
| `uv remove <paquet>` | Retire une dépendance |
| `uv run <commande>` | Exécute une commande dans l'environnement, sans l'activer |
| `uv run python script.py` | Exécute un script Python dans l'environnement |
| `uv lock` | Recalcule le fichier de verrouillage |
| `uv python list` | Liste les versions de Python disponibles et installées |
| `uv self update` | Met à jour uv |

Avec `uv run`, activer l'environnement n'est jamais nécessaire. Pour le faire malgré tout : `source .venv/bin/activate` (macOS/Linux) ou `.venv\Scripts\activate` (Windows).

`pyproject.toml` et `uv.lock` sont suivis par Git ; `.venv/` ne l'est jamais.

## Équivalences macOS / Windows

Toutes les commandes du cours passent par `uv run …`, identiques sur les trois OS. Les seules différences :

| Action | macOS / Linux | Windows (PowerShell) |
|---|---|---|
| Copier le fichier d'environnement | `cp env.example .env` | `Copy-Item env.example .env` |
| Chemin de l'interpréteur | `.venv/bin/python` | `.venv\Scripts\python.exe` |
| Ouvrir le terminal intégré | `` Ctrl+` `` (`Ctrl+ù` en AZERTY) | idem |

**Mac Intel ou Apple Silicon** : le dépôt s'installe sur les deux. Sur Apple Silicon (M1 à M4), si `uv sync` identifie la machine en `x86_64`, le terminal ou uv tourne sous Rosetta : comparer `uname -m` et `uv python list`, puis réinstaller uv depuis un terminal natif (arm64). Les embeddings locaux sont nettement plus rapides en natif.

---

## Annexe : démarrer un projet uv depuis zéro

Pour les travaux ultérieurs :

```bash
uv init mon-projet          # crée pyproject.toml, .python-version, .gitignore
cd mon-projet
uv python pin 3.12          # fige la version de Python
uv add langchain langgraph  # ajoute les dépendances (crée .venv au passage)
uv add --dev ipykernel      # nécessaire pour les notebooks dans VS Code
code .                      # ouvre le projet dans VS Code
```
