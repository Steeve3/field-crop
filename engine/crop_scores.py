"""Crop ranking per farmer, read from the farmer's CSV in data/ (see sample.FARMERS).

Each CSV is the output of the terrain notebook for that area: FAO GAEZ v5 climate suitability,
then terrain bonuses/penalties from NASADEM + HLS.
"""
from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path

from . import sample

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SOURCE = "FAO GAEZ v5 crop suitability (terrain notebook output)"

# The notebook writes its notes in Italian; the UI is in English.
NOTES_EN = {
    "adattabilità climatica standard": "standard climate suitability",
    "standard climatic adaptability": "standard climate suitability",
    "penalizzata per rischio erosione su pendio": "penalised for erosion risk on slopes",
    "favorita per protezione del suolo": "favoured because it protects the soil",
    "penalizzata per rischio ristagno/asfissia radicale": "penalised for waterlogging risk",
    "penalizzata per elevato fabbisogno idrico": "penalised for high water need",
    "favorita per resistenza alla siccità": "favoured for drought tolerance",
}


def _note_en(note: str) -> str:
    parts = [p.strip() for p in note.split(";") if p.strip()]
    text = "; ".join(NOTES_EN.get(p.lower(), p) for p in parts)
    return text[:1].upper() + text[1:]


@lru_cache
def crop_ranking(farmer_id: str) -> dict:
    """All crops for the farmer's area, best first. Scores are percentages (0-100)."""
    farmer = sample.FARMER[farmer_id]
    with (DATA_DIR / farmer["crops_csv"]).open(encoding="utf-8", newline="") as f:
        sep = ";" if ";" in f.readline() else ","   # the notebook export may use either
        f.seek(0)
        crops = [{
            "rank": int(r["posizione"]),
            "code": r["crop_code"],
            "name": r["crop_name"],
            "category": r["category"].strip(),
            "climate_pct": float(r["adattabilita_pct"]),   # FAO GAEZ climate suitability
            "score_pct": float(r["punteggio_finale"]),     # after terrain bonuses/penalties
            "note": _note_en(r["note_agronomiche"]),
        } for r in csv.DictReader(f, delimiter=sep)]
    crops.sort(key=lambda c: c["rank"])
    return {
        "bbox": farmer["bbox"],
        "source": SOURCE,
        "terrain_adjusted": any(c["score_pct"] != c["climate_pct"] for c in crops),
        "crops": crops,
    }
