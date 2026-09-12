"""Banc d'essai du TP « Ameliorer l'utilisation d'un LLM ».

Une meme tache, un meme jeu de questions, et une mesure identique a chaque etape
(prompt brut, prompt travaille, memoire, RAG). Les chiffres remplacent l'impression.

    from src.evaluation import Banc, FORMAT_FICHE
    banc = Banc(questions_test("loi-repost"))
    banc.mesurer("0 - prompt brut", lambda q: llm.invoke(q))
    banc.tableau()
"""

from __future__ import annotations

import re
import time
import unicodedata

from rich.console import Console
from rich.table import Table

console = Console()

# Format de reponse impose a partir de l'etape 1. Quatre champs, dans cet ordre.
FORMAT_FICHE = """REPONSE : <une phrase, 40 mots maximum>
DETAILS : <2 ou 3 puces commencant par "- ">
SOURCE : <reference du passage utilise, ou "non trouvee">
CONFIANCE : <haute | moyenne | basse>"""

_CHAMPS = ["REPONSE", "DETAILS", "SOURCE", "CONFIANCE"]
_RE_CONFIANCE = re.compile(r"confiance\s*:\s*(haute|moyenne|basse)")
_RE_SOURCE = re.compile(r"source\s*:\s*(.+)")
_RE_AVEU = re.compile(
    r"je ne (sais|peux|dispose|connais|suis pas en mesure)|pas (d'|de )?information"
    r"|aucune information|non trouvee|ne figure pas|impossible de repondre"
)


def normaliser(texte: str) -> str:
    """Minuscules, sans accents ni mise en forme markdown, apostrophes et espaces unifies."""
    texte = unicodedata.normalize("NFKD", texte)
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    texte = texte.replace("’", "'").replace("‘", "'")
    texte = re.sub(r"[*_`]+", "", texte)  # **REPONSE** vaut REPONSE
    return re.sub(r"\s+", " ", texte).lower().strip()


def format_ok(reponse: str) -> bool:
    """Les 4 champs sont presents, dans l'ordre, et CONFIANCE a une valeur autorisee."""
    txt = normaliser(reponse)
    positions = [txt.find(f"{champ.lower()} :") for champ in _CHAMPS]
    if any(p < 0 for p in positions) or positions != sorted(positions):
        return False
    return bool(_RE_CONFIANCE.search(txt))


def faits_trouves(reponse: str, faits_attendus: list) -> list:
    """Un fait est une chaine, ou une liste de variantes dont une seule doit apparaitre."""
    txt = normaliser(reponse)
    trouves = []
    for fait in faits_attendus:
        variantes = [fait] if isinstance(fait, str) else fait
        if any(normaliser(v) in txt for v in variantes):
            trouves.append(fait)
    return trouves


def champ_source(reponse: str) -> str:
    """Contenu du champ SOURCE, normalise. Chaine vide s'il est absent."""
    m = _RE_SOURCE.search(normaliser(reponse))
    return m.group(1).strip() if m else ""


def source_juste(reponse: str, source_attendue: list[str]) -> bool:
    """Le champ SOURCE pointe vers le bon passage du corpus (et pas vers une reference
    plausible mais inventee)."""
    src = champ_source(reponse)
    return bool(src) and any(normaliser(s) in src for s in source_attendue)


def source_donnee(reponse: str) -> bool:
    src = champ_source(reponse)
    return bool(src) and "non trouvee" not in src and len(src) > 3


def aveu_ignorance(reponse: str) -> bool:
    return bool(_RE_AVEU.search(normaliser(reponse)))


def evaluer(reponse, question: dict) -> dict:
    """Mesure une reponse a une question de test (dict issu de questions.json).

    `reponse` : un AIMessage (avec usage_metadata) ou une simple chaine.
    """
    texte = getattr(reponse, "content", reponse)
    usage = getattr(reponse, "usage_metadata", None) or {}
    attendus = question["faits_attendus"]
    trouves = faits_trouves(texte, attendus)
    juste = source_juste(texte, question.get("source_attendue", []))
    donnee = source_donnee(texte)
    return {
        "format_ok": format_ok(texte),
        "mots": len(texte.split()),
        "faits": f"{len(trouves)}/{len(attendus)}",
        "nb_faits": len(trouves),
        "nb_attendus": len(attendus),
        "source_juste": juste,
        "source": "juste" if juste else ("inventee" if donnee else "absente"),
        "aveu": aveu_ignorance(texte),
        "tokens_entree": usage.get("input_tokens", 0),
        "tokens_sortie": usage.get("output_tokens", 0),
        "texte": texte,
    }


def resume_mesure(m: dict) -> str:
    return (
        f"format {'OK' if m['format_ok'] else 'KO'} · {m['mots']} mots · faits {m['faits']} · "
        f"source {m['source']} · tokens {m['tokens_entree']}→{m['tokens_sortie']}"
    )


class Banc:
    """Passe les questions de test a une fonction `repondre(question) -> AIMessage`
    et conserve les mesures, etape par etape."""

    def __init__(self, questions: list[dict], pause: float = 1.0):
        self.questions = questions
        self.pause = pause  # secondes entre deux appels : tier gratuit Mistral
        self.resultats: dict[str, list[dict]] = {}

    def mesurer(self, etape: str, repondre, afficher: bool = True) -> list[dict]:
        lignes = []
        for q in self.questions:
            reponse = repondre(q["question"])
            mesure = evaluer(reponse, q)
            mesure["question"] = q["question"]
            lignes.append(mesure)
            if afficher:
                console.rule(f"[bold]{etape}[/bold] — {q['question'][:70]}…")
                console.print(mesure["texte"], markup=False, highlight=False)
                console.print(f"[dim]{resume_mesure(mesure)}[/dim]", highlight=False)
            time.sleep(self.pause)
        self.resultats[etape] = lignes
        return lignes

    def enregistrer(self, etape: str, mesures: list[dict]) -> None:
        """Enregistre des mesures produites hors de `mesurer` (ex. conversation multi-tours)."""
        self.resultats[etape] = mesures

    def tableau(self) -> None:
        """Une ligne par etape : ce que chaque technique a corrige, et ce qu'elle a coute."""
        t = Table(title="Une tache, quatre facons de l'aborder")
        for col in ["Etape", "Format OK", "Mots", "Faits justes", "Source juste", "Tokens entree"]:
            t.add_column(col, justify="right" if col != "Etape" else "left")
        for etape, lignes in self.resultats.items():
            n = len(lignes)
            t.add_row(
                etape,
                f"{sum(m['format_ok'] for m in lignes)}/{n}",
                f"{sum(m['mots'] for m in lignes) // n}",
                f"{sum(m['nb_faits'] for m in lignes)}/{sum(m['nb_attendus'] for m in lignes)}",
                f"{sum(m['source_juste'] for m in lignes)}/{n}",
                f"{sum(m['tokens_entree'] for m in lignes) // n}",
            )
        console.print(t)
