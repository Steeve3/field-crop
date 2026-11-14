"""SAMPLE strategies so the UI can be built before the engine exists.

!!! Every score and metric here is a PLACEHOLDER, not a result. Delete this file when
engine/api.py uses the real model. The UI shows a "SAMPLE DATA" badge while it is used.
"""
from __future__ import annotations

from . import calendars, config
from .schema import AnalysisResult, CropYear, Field, Irrigation, Strategy, WhatIf

SAMPLE_SOURCE = "SAMPLE placeholder — not a model result"
_PICKS = [("S1", "Best for your priorities"), ("S2", "Water saver"), ("S3", "Soil builder")]


def _metric(value: float, unit: str) -> dict:
    return {"value": value, "unit": unit, "source": SAMPLE_SOURCE, "note": ""}


def _strategy(sid: str, label: str, template_id: str, rotation: list[CropYear],
              irrigation: Irrigation, k: int) -> Strategy:
    metrics = {
        "irrigation_mm": _metric(300 - 60 * k, "mm/yr"),
        "margin_eur_ha": _metric(600 + 20 * k, "€/ha/yr"),
        "margin_p10_eur_ha": _metric(300 + 40 * k, "€/ha/yr"),
        "soil_score": _metric(40 + 12 * k, "score 0-100"),
    }
    return {
        "id": sid,
        "label": label,
        "template_id": template_id,
        "rotation": rotation,
        "irrigation": irrigation,
        "scores": {"water": 40 + 15 * k, "soil": 40 + 12 * k, "profit": 60 - 5 * k,
                   "resilience": 45 + 10 * k, "overall": 50 + 5 * k},
        "metrics": metrics,
        "delta_vs_s0": {},
        "evidence_card": {
            "why": "SAMPLE text — the real reason will come from the engine.",
            "evidence": [{"claim": "SAMPLE evidence item", "metric": "irrigation_mm",
                          "source": SAMPLE_SOURCE, "confidence": "low"}],
            "benefits": ["SAMPLE benefit"],
            "risks": ["SAMPLE risk"],
            "information_gaps": ["No on-farm soil test", "Weather is ~50 km NASA POWER grid, not a field station"],
            "needs_local_review": ["Variety choice", "Water availability and rights", "Buyers and contracts"],
            "confidence": "low",
        },
        "calendars": {
            "bare_months": calendars.bare_months(rotation),  # real: computed from crops.yaml
            "vulnerability": {cy["crop"]: ["low"] * 12 for cy in rotation},
        },
    }


def sample_result(field: Field, climate: dict, current_rotation: list[CropYear],
                  current_irrigation: Irrigation, whatif: WhatIf, status: str) -> AnalysisResult:
    region = "north" if field["lat"] > 43.5 else "south"
    templates = [t for t in config.rotations() if region in t["regions"]][:3]
    strategies = [_strategy("S0", "Your current rotation", "current", current_rotation, current_irrigation, 0)]
    for k, ((sid, label), t) in enumerate(zip(_PICKS, templates), start=1):
        rot = [{"year": i + 1, "crop": c, "cover": cov} for i, (c, cov) in enumerate(zip(t["years"], t["cover"]))]
        strategies.append(_strategy(sid, label, t["id"], rot, t["irrigation"], k))
    s0 = strategies[0]["metrics"]
    for s in strategies:
        s["delta_vs_s0"] = {key: m["value"] - s0[key]["value"] for key, m in s["metrics"].items()}
    return {
        "field": field,
        "climate": climate,
        "strategies": strategies,
        "data_status": "sample",
        "whatif": whatif,
        "notes": [f"Climate facts are real NASA POWER data ({status}). Strategies are SAMPLE placeholders."],
    }
