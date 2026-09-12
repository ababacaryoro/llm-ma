"""Mini-RAG a cout nul : Qdrant en memoire + embeddings locaux fastembed.

Reutilise tel quel par le RAG reflexif.
Aucun service externe, aucune cle API, aucun Docker.

Le corpus se choisit par son nom de dossier dans `data/corpus/` :

    from common.rag import indexer_corpus, rechercher
    indexer_corpus("loi-repost")          # ou RAG_CORPUS dans .env
    rechercher("Quelle est la peine encourue pour ... ?", k=4)

Chaque dossier de corpus contient ses documents (.md ou .txt) et un fichier
`questions.json` (questions de test et faits attendus) utilise par les grilles
d'evaluation des TP.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

load_dotenv()

RACINE = Path(__file__).resolve().parent.parent
CORPUS_DIR = RACINE / "data" / "corpus"
CORPUS_DEFAUT = os.getenv("RAG_CORPUS", "loi-repost")

# Recherche hybride : un modele dense multilingue leger (~220 Mo) pour le sens, et BM25
# (~10 Mo) pour les termes exacts (numeros d'article, montants, noms propres). Les deux
# sont telecharges une fois par `uv run check-env`. Le modele dense par defaut de
# fastembed est anglophone : mauvais sur un corpus francais.
MODELE_EMBEDDINGS = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
MODELE_BM25 = "Qdrant/bm25"
TAILLE_CHUNK = 1000  # caracteres, ~250 tokens

_client: QdrantClient | None = None
# Frontieres de decoupage : « Article 12 » (texte de loi) ou titre markdown (## ...)
_RE_SECTION = re.compile(
    r"^(?:Article (?P<article>\d+[a-z]*)|#{1,3} (?P<titre>.+))\s*$", re.MULTILINE
)


def get_client() -> QdrantClient:
    """Client Qdrant en memoire (singleton). Remplacer par une URL pour la demo Docker."""
    global _client
    if _client is None:
        _client = QdrantClient(":memory:")
    return _client


def _dense(texte: str) -> models.Document:
    """Texte a vectoriser localement par fastembed (dense) a l'upsert ou a la requete."""
    return models.Document(text=texte, model=MODELE_EMBEDDINGS)


def _sparse(texte: str) -> models.Document:
    """Idem, vecteur creux BM25 (avec racinisation francaise)."""
    return models.Document(text=texte, model=MODELE_BM25, options={"language": "french"})


def charger_embeddings() -> None:
    """Force le telechargement des modeles d'embeddings (appele par check-env)."""
    from fastembed import SparseTextEmbedding, TextEmbedding

    TextEmbedding(model_name=MODELE_EMBEDDINGS)
    SparseTextEmbedding(model_name=MODELE_BM25, language="french")


def chemin_corpus(nom: str | None = None) -> Path:
    nom = nom or CORPUS_DEFAUT
    dossier = CORPUS_DIR / nom
    if not dossier.is_dir():
        disponibles = sorted(p.name for p in CORPUS_DIR.iterdir() if p.is_dir())
        raise FileNotFoundError(f"Corpus {nom!r} introuvable. Disponibles : {disponibles}")
    return dossier


def questions_test(nom: str | None = None) -> list[dict]:
    """Questions de test du corpus : [{question, faits_attendus: [str, ...]}]."""
    return json.loads((chemin_corpus(nom) / "questions.json").read_text(encoding="utf-8"))


def _alineas(texte: str) -> list[str]:
    """Reconstitue les alineas : une ligne qui ne se termine pas par une ponctuation
    forte est la suite de la precedente (texte replie a 80 ou 100 colonnes)."""
    alineas: list[str] = []
    for ligne in texte.splitlines():
        ligne = ligne.strip()
        if not ligne:
            continue
        if alineas and not alineas[-1].endswith((".", ";", ":", "»", "|")):
            alineas[-1] += " " + ligne
        else:
            alineas.append(ligne)
    return alineas


def _decouper_paragraphes(texte: str, taille: int = TAILLE_CHUNK) -> list[str]:
    """Regroupe les alineas jusqu'a `taille` caracteres."""
    chunks, courant = [], ""
    for alinea in _alineas(texte):
        if courant and len(courant) + len(alinea) > taille:
            chunks.append(courant)
            courant = ""
        courant = f"{courant}\n{alinea}" if courant else alinea
    if courant:
        chunks.append(courant)
    return [c for c in chunks if len(c) >= 80]


def decouper(texte: str, source: str) -> list[tuple[str, dict]]:
    """Decoupe un document en chunks, par section (article de loi ou titre markdown).

    Retourne [(texte_du_chunk, metadata)]. Une section longue est redecoupee par
    groupes d'alineas, chaque morceau gardant le nom de sa section en metadata.
    """
    positions = list(_RE_SECTION.finditer(texte))
    if not positions:
        return [(c, {"source": source}) for c in _decouper_paragraphes(texte)]

    resultat = []
    # En-tete (avant la premiere section) : un seul chunk, ex. titre et date d'une loi
    en_tete = " ".join(l.strip() for l in texte[: positions[0].start()].splitlines() if l.strip())
    if len(en_tete) >= 80:
        resultat.append((en_tete, {"source": source, "article": "en-tete"}))
    for i, m in enumerate(positions):
        fin = positions[i + 1].start() if i + 1 < len(positions) else len(texte)
        if m.group("article"):
            meta = {"source": source, "article": m.group("article")}
            entete = f"Article {m.group('article')}"
        else:
            meta = {"source": source, "section": m.group("titre").strip()}
            entete = m.group("titre").strip()
        for c in _decouper_paragraphes(texte[m.end() : fin]):
            resultat.append((f"{entete}\n{c}", meta))
    return resultat


def indexer_corpus(nom: str | None = None) -> int:
    """Indexe tous les .md et .txt du corpus `nom`. Retourne le nombre de chunks."""
    dossier = chemin_corpus(nom)
    client = get_client()
    collection = dossier.name
    if client.collection_exists(collection):
        client.delete_collection(collection)
    client.create_collection(
        collection,
        vectors_config={
            "dense": models.VectorParams(
                size=client.get_embedding_size(MODELE_EMBEDDINGS), distance=models.Distance.COSINE
            )
        },
        sparse_vectors_config={"bm25": models.SparseVectorParams(modifier=models.Modifier.IDF)},
    )

    points = []
    for fichier in sorted(dossier.glob("*")):
        if fichier.suffix not in {".md", ".txt"} or fichier.name.upper() == "README.MD":
            continue
        for texte, meta in decouper(fichier.read_text(encoding="utf-8"), fichier.name):
            points.append(
                models.PointStruct(
                    id=len(points),
                    vector={"dense": _dense(texte), "bm25": _sparse(texte)},
                    payload={"texte": texte, **meta},
                )
            )
    client.upsert(collection, points=points)
    return len(points)


def rechercher(question: str, k: int = 4, nom: str | None = None) -> list[dict]:
    """Retourne les k passages les plus proches : [{texte, source, article, section, score}].

    Recherche hybride : les meilleurs candidats dense et BM25 sont fusionnes par RRF
    (Reciprocal Rank Fusion). Le score retourne est celui de la fusion.
    """
    collection = chemin_corpus(nom).name
    hits = (
        get_client()
        .query_points(
            collection,
            prefetch=[
                models.Prefetch(query=_dense(question), using="dense", limit=3 * k),
                models.Prefetch(query=_sparse(question), using="bm25", limit=3 * k),
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=k,
        )
        .points
    )
    return [
        {
            "texte": h.payload["texte"],
            "source": h.payload.get("source"),
            "article": h.payload.get("article"),
            "section": h.payload.get("section"),
            "score": round(h.score, 3),
        }
        for h in hits
    ]


def formater_contexte(passages: list[dict]) -> str:
    """Met en forme les passages pour injection dans un prompt, avec leur reference."""
    blocs = []
    for i, p in enumerate(passages, 1):
        ref = p["source"]
        if p.get("article"):
            ref += f", article {p['article']}"
        elif p.get("section"):
            ref += f", {p['section']}"
        blocs.append(f"[{i}] ({ref})\n{p['texte']}")
    return "\n\n".join(blocs)
