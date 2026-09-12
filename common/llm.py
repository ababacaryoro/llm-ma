"""Fabrique de modeles LLM, agnostique du fournisseur.

Tout le code de la formation passe par `get_llm()`. On change de fournisseur
en editant UNE variable dans `.env` :

    LLM_PROVIDER=mistral  # tier gratuit "Experiment" (par defaut, limite en debit)
    LLM_PROVIDER=openai   # si une cle est fournie par le formateur
    LLM_PROVIDER=ollama   # local, hors ligne (qualite tool-calling limitee)

Garde-fous budget integres : modele leger par defaut, max_tokens borne,
temperature 0. Ne pas les retirer pendant la formation.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

# Modele par defaut de chaque fournisseur (surchargable via LLM_MODEL dans .env)
DEFAULT_MODELS = {
    "mistral": "mistralai:mistral-small-latest",
    "openai": "openai:gpt-5-mini",
    "ollama": "ollama:qwen3:4b",
}

REQUIRED_KEY = {
    "mistral": "MISTRAL_API_KEY",
    "openai": "OPENAI_API_KEY",
    "ollama": None,  # pas de cle, mais le serveur Ollama doit tourner
}


def get_provider() -> str:
    provider = os.getenv("LLM_PROVIDER", "mistral").strip().lower()
    if provider not in DEFAULT_MODELS:
        raise ValueError(
            f"LLM_PROVIDER={provider!r} inconnu. Valeurs possibles : {sorted(DEFAULT_MODELS)}"
        )
    key = REQUIRED_KEY[provider]
    if key and not os.getenv(key):
        raise OSError(
            f"LLM_PROVIDER={provider} mais {key} est absent de votre .env. "
            f"Copiez env.example vers .env et renseignez la cle."
        )
    return provider


def get_llm(
    *,
    max_tokens: int | None = None,
    temperature: float = 0.0,
    tags: list[str] | None = None,
    **kwargs,
):
    """Retourne un chat model LangChain pret a l'emploi.

    max_tokens : borne dure par reponse (garde-fou budget, defaut LLM_MAX_TOKENS ou 1024).
    tags       : etiquettes visibles dans les traces Langfuse (ex. ["tp2", "superviseur"]).
    """
    provider = get_provider()
    model = os.getenv("LLM_MODEL") or DEFAULT_MODELS[provider]
    max_tokens = max_tokens or int(os.getenv("LLM_MAX_TOKENS", "1024"))
    return init_chat_model(
        model,
        temperature=temperature,
        max_tokens=max_tokens,
        tags=tags or [],
        **kwargs,
    )


def invoquer(llm, entree, tentatives: int = 4, **kwargs):
    """`llm.invoke` avec attente et nouvel essai sur erreur 429 (limite de debit).

    Le tier gratuit Mistral accepte environ une requete par seconde : dans un
    notebook, une boucle de 3 questions suffit a le depasser.
    """
    import time

    for i in range(tentatives):
        try:
            return llm.invoke(entree, **kwargs)
        except Exception as e:
            if "429" not in str(e) or i == tentatives - 1:
                raise
            time.sleep(2 * (i + 1))


if __name__ == "__main__":
    llm = get_llm(max_tokens=50)
    print(f"Fournisseur actif : {get_provider()}")
    print(llm.invoke("Reponds en un mot : quelle est la capitale de la France ?").content)
