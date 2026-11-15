"""Crop ranking for one fixed region, read from data/score_colture.csv.

The table is the output of the terrain notebook (FAO GAEZ v5 climate suitability, then terrain
bonuses/penalties from NASADEM + HLS). It was computed once for REGION_BBOX and does not follow
the field drawn on the map yet.
"""
from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "score_colture.csv"
REGION_BBOX = (7.32, 46.20, 7.52, 46.27)  # lon_min, lat_min, lon_max, lat_max the table was computed for
SOURCE = "FAO GAEZ v5 crop suitability (terrain notebook output, data/score_colture.csv)"

# The notebook writes its notes in Italian; the UI is in English.
NOTES_EN = {
    "adattabilità climatica standard": "Climate suitability only",
    "penalizzata per rischio erosione su pendio": "Penalised: erosion risk on slopes",
    "favorita per protezione del suolo": "Favoured: protects the soil",
    "penalizzata per rischio ristagno/asfissia radicale": "Penalised: waterlogging risk",
    "penalizzata per elevato fabbisogno idrico": "Penalised: high water need",
    "favorita per resistenza alla siccità": "Favoured: drought tolerant",
}


def _note_en(note: str) -> str:
    parts = [p.strip() for p in note.split(";") if p.strip()]
    return "; ".join(NOTES_EN.get(p.lower(), p) for p in parts)


@lru_cache
def crop_ranking() -> dict:
    """All crops for the fixed region, best first. Scores are percentages (0-100)."""
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        crops = [{
            "rank": int(r["posizione"]),
            "code": r["crop_code"],
            "name": r["crop_name"],
            "category": r["category"].strip(),
            "climate_pct": float(r["adattabilita_pct"]),   # FAO GAEZ climate suitability
            "score_pct": float(r["punteggio_finale"]),     # after terrain bonuses/penalties
            "note": _note_en(r["note_agronomiche"]),
        } for r in csv.DictReader(f)]
    crops.sort(key=lambda c: c["rank"])
    return {
        "bbox": REGION_BBOX,
        "source": SOURCE,
        "terrain_adjusted": any(c["score_pct"] != c["climate_pct"] for c in crops),
        "crops": crops,
    }
