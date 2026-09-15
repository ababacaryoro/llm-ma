"""Banc d'essai des agents.

Chaque approche (boucle a la main, create_agent, graphe explicite) est une fonction
`lancer(question) -> list[messages]`. Le banc lit la liste de messages produite et en
tire : nombre d'appels au modele, nombre d'appels d'outils, tokens, reponse finale,
faits attendus presents, limite de recursion atteinte.

    banc = BancAgent(questions_test("loi-repost", "questions_agent.json"))
    banc.mesurer("1 - ReAct a la main", react_a_la_main)
    banc.tableau()
"""

from __future__ import annotations

import time

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langgraph.errors import GraphRecursionError
from rich.console import Console
from rich.table import Table

from common.evaluation import faits_trouves

console = Console()


def mesurer_messages(messages: list[BaseMessage], question: dict) -> dict:
    """Mesures tirees d'une liste de messages (HumanMessage, AIMessage, ToolMessage...)."""
    ia = [m for m in messages if isinstance(m, AIMessage)]
    outils = [m for m in messages if isinstance(m, ToolMessage)]
    appels_outils = [ap["name"] for m in ia for ap in (m.tool_calls or [])]
    reponse = ia[-1].content if ia and not ia[-1].tool_calls else ""
    if isinstance(reponse, list):  # certains fournisseurs renvoient des blocs
        reponse = " ".join(b.get("text", "") for b in reponse if isinstance(b, dict))
    trouves = faits_trouves(reponse, question["faits_attendus"])
    attendus = question.get("outils_attendus", [])
    return {
        "appels_llm": len(ia),
        "appels_outils": len(outils),
        "outils": appels_outils,
        "outils_ok": all(o in appels_outils for o in attendus),
        "tokens": sum((m.usage_metadata or {}).get("total_tokens", 0) for m in ia),
        "faits": f"{len(trouves)}/{len(question['faits_attendus'])}",
        "nb_faits": len(trouves),
        "nb_attendus": len(question["faits_attendus"]),
        "reponse": reponse,
        "limite_atteinte": False,
    }


def afficher_trace(messages: list[BaseMessage], largeur: int = 110) -> None:
    """La conversation complete, un message par ligne : ce que le modele a vu et decide."""
    for m in messages:
        role = type(m).__name__.replace("Message", "")
        if isinstance(m, AIMessage) and m.tool_calls:
            for ap in m.tool_calls:
                console.print(f"[bold cyan]{role:>6}[/] → {ap['name']}({ap['args']})", highlight=False)
        else:
            contenu = m.content if isinstance(m.content, str) else str(m.content)
            contenu = contenu.replace("\n", " ")
            if len(contenu) > largeur:
                contenu = contenu[:largeur] + "…"
            couleur = {"Human": "green", "AI": "cyan", "Tool": "yellow", "System": "dim"}.get(role, "")
            console.print(f"[bold {couleur}]{role:>6}[/] {contenu}", markup=True, highlight=False)


class BancAgent:
    """Passe les questions de test a `lancer(question) -> list[messages]` et conserve
    les mesures, approche par approche."""

    def __init__(self, questions: list[dict], pause: float = 1.0):
        self.questions = questions
        self.pause = pause  # secondes entre deux questions : tier gratuit Mistral
        self.resultats: dict[str, list[dict]] = {}
        self.traces: dict[str, list[list[BaseMessage]]] = {}

    def mesurer(self, etape: str, lancer, afficher: bool = True) -> list[dict]:
        lignes, traces = [], []
        for q in self.questions:
            debut = time.time()
            try:
                messages = lancer(q["question"])
                mesure = mesurer_messages(messages, q)
            except GraphRecursionError:
                messages = []
                mesure = mesurer_messages([], q) | {"limite_atteinte": True}
            mesure["duree"] = round(time.time() - debut, 1)
            mesure["question"] = q["question"]
            lignes.append(mesure)
            traces.append(messages)
            if afficher:
                console.rule(f"[bold]{etape}[/bold] — {q['question'][:70]}…")
                if mesure["limite_atteinte"]:
                    console.print("[red]Limite de recursion atteinte : pas de reponse.[/red]")
                else:
                    console.print(mesure["reponse"], markup=False, highlight=False)
                console.print(
                    f"[dim]{mesure['appels_llm']} appels LLM · outils {mesure['outils']} · "
                    f"{mesure['tokens']} tokens · faits {mesure['faits']} · "
                    f"{mesure['duree']} s[/dim]",
                    highlight=False,
                )
            time.sleep(self.pause)
        self.resultats[etape] = lignes
        self.traces[etape] = traces
        return lignes

    def tableau(self) -> None:
        """Une ligne par approche : meme boucle, memes chiffres, ou pas."""
        t = Table(title="Un agent, trois ecritures")
        for col in ["Approche", "Appels LLM", "Appels outils", "Outils attendus", "Tokens", "Faits justes", "Limite"]:
            t.add_column(col, justify="right" if col != "Approche" else "left")
        for etape, lignes in self.resultats.items():
            n = len(lignes)
            t.add_row(
                etape,
                f"{sum(m['appels_llm'] for m in lignes) / n:.1f}",
                f"{sum(m['appels_outils'] for m in lignes) / n:.1f}",
                f"{sum(m['outils_ok'] for m in lignes)}/{n}",
                f"{sum(m['tokens'] for m in lignes) // n}",
                f"{sum(m['nb_faits'] for m in lignes)}/{sum(m['nb_attendus'] for m in lignes)}",
                f"{sum(m['limite_atteinte'] for m in lignes)}/{n}",
            )
        console.print(t)
