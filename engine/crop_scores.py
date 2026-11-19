"""Crop ranking per farmer, read from the farmer's CSV in data/ (see sample.FARMERS).

Each CSV is the output of the terrain notebook for that area: FAO GAEZ v5 climate suitability,
then terrain bonuses/penalties from NASADEM + HLS. Columns used: Rank, Crop code, Crop name,
Category, Climate suitability (%), Final score, Agronomic notes. Separator ";" or ",".
"""
from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path

from . import sample

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SOURCE = "FAO GAEZ v5 crop suitability (terrain notebook output)"


@lru_cache
def crop_ranking(farmer_id: str) -> dict:
    """All crops for the farmer's area, best first. Scores are percentages (0-100)."""
    farmer = sample.FARMER[farmer_id]
    with (DATA_DIR / farmer["crops_csv"]).open(encoding="utf-8-sig", newline="") as f:
        sep = ";" if ";" in f.readline() else ","   # the notebook export may use either
        f.seek(0)
        crops = [{
            "rank": int(r["Rank"]),
            "code": r["Crop code"],
            "name": r["Crop name"],
            "category": r["Category"].strip(),
            "climate_pct": float(r["Climate suitability (%)"]),   # FAO GAEZ climate suitability
            "score_pct": float(r["Final score"]),                  # after terrain bonuses/penalties
            "note": r["Agronomic notes"].strip(),
        } for r in csv.DictReader(f, delimiter=sep)]
    crops.sort(key=lambda c: c["rank"])
    return {
        "bbox": farmer["bbox"],
        "source": SOURCE,
        "terrain_adjusted": any(c["score_pct"] != c["climate_pct"] for c in crops),
        "crops": crops,
    }
