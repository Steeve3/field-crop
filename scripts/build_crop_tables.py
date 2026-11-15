"""Build one placeholder crop table per farmer, same columns as the terrain notebook output.

Climate suitability (adattabilita_pct) is real: the mean of the FAO GAEZ grid cells of
data/toscana_crop_suitability.csv that fall inside the farmer's bbox.
The final score (punteggio_finale) and the notes apply the terrain notebook's own rules, but
with the SAMPLE terrain shares in engine/sample.py instead of measured ones.
Replace data/score_<farmer>.csv with the real notebook output when it is available.

Run:  python scripts/build_crop_tables.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine import sample  # noqa: E402

DATA = ROOT / "data"

# Crop groups, thresholds and points: copied from classifica_colture_con_terreno() in the terrain notebook.
ERODING = {"MZE", "MZS", "SFL", "SUB", "SOY", "TOB", "WPO", "COT"}   # row crops that leave soil exposed
PROTECTING = {"ALF", "PST", "BRL", "WHE", "RYE", "OAT", "TRI"}       # dense roots hold the soil
WATERLOG_SENSITIVE = {"ALF", "CHK", "WPO", "OLV"}
THIRSTY = {"MZE", "MZS", "SOY", "SUB", "RCW"}
DROUGHT_TOLERANT = {"SRG", "CHK", "BRL", "OLV", "SFL"}
EROSION_MIN, WATERLOG_MIN, DROUGHT_MIN = 0.20, 0.15, 0.20


def adjust(code: str, score: float, terrain: dict) -> tuple[float, str]:
    notes = []
    if terrain["erosion"] > EROSION_MIN:
        if code in ERODING:
            score -= 25.0 * terrain["erosion"]
            notes.append("penalizzata per rischio erosione su pendio")
        elif code in PROTECTING:
            score += 10.0 * terrain["erosion"]
            notes.append("favorita per protezione del suolo")
    if terrain["waterlogging"] > WATERLOG_MIN and code in WATERLOG_SENSITIVE:
        score -= 30.0 * terrain["waterlogging"]
        notes.append("penalizzata per rischio ristagno/asfissia radicale")
    if terrain["drought"] > DROUGHT_MIN:
        if code in THIRSTY:
            score -= 20.0 * terrain["drought"]
            notes.append("penalizzata per elevato fabbisogno idrico")
        elif code in DROUGHT_TOLERANT:
            score += 10.0 * terrain["drought"]
            notes.append("favorita per resistenza alla siccità")
    note = "; ".join(notes).capitalize() if notes else "Adattabilità climatica standard"
    return round(min(100.0, max(0.0, score)), 1), note


def main() -> None:
    grid = pd.read_csv(DATA / "toscana_crop_suitability.csv")
    meta = pd.read_csv(DATA / "score_colture.csv").set_index("crop_code")  # names, categories, raster paths
    codes = [c for c in grid.columns if c not in ("cell_id", "latitude", "longitude")]
    for f in sample.FARMERS:
        lon0, lat0, lon1, lat1 = f["bbox"]
        cells = grid[grid.longitude.between(lon0, lon1) & grid.latitude.between(lat0, lat1)]
        rows = []
        for code in codes:
            climate = round(float(cells[code].mean()) * 100, 1)
            final, note = adjust(code, climate, f["terrain"])
            rows.append({"crop_code": code, "crop_name": meta.at[code, "crop_name"], "category": meta.at[code, "category"],
                         "raster_path": meta.at[code, "raster_path"], "raster_available": True,
                         "adattabilita_pct": climate, "punteggio_finale": final, "note_agronomiche": note})
        table = pd.DataFrame(rows).sort_values("punteggio_finale", ascending=False, kind="stable").reset_index(drop=True)
        table.insert(0, "posizione", table.index + 1)
        table.to_csv(DATA / f["crops_csv"], index=False, encoding="utf-8")
        print(f"{f['crops_csv']}: {len(cells)} grid cells, {len(table)} crops, top: "
              + ", ".join(f"{r.crop_name} {r.punteggio_finale}" for r in table.head(4).itertuples()))


if __name__ == "__main__":
    main()
