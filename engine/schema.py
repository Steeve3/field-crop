"""The shared data shape between engine/ and app.py.

Agree with your teammate before changing anything here.
Plain TypedDicts: easy to read, easy to turn into JSON (or Pydantic) later.
"""
from __future__ import annotations

from typing import Literal, TypedDict

Confidence = Literal["low", "medium", "high"]
Risk = Literal["low", "medium", "high"]
Irrigation = Literal["rainfed", "deficit", "full"]


class Metric(TypedDict):
    value: float
    unit: str            # "mm/yr", "€/ha/yr", "t/ha", "days/yr", "score 0-100"
    source: str          # "NASA POWER daily 2005-2024" or "engine (FAO-56 + crops.yaml)"
    note: str            # short, plain-language explanation; "" if none


class CropYear(TypedDict):
    year: int            # 1..4
    crop: str            # id from data/crops.yaml
    cover: bool          # winter cover crop before this crop


class EvidenceItem(TypedDict):
    claim: str           # "Uses 180 mm less irrigation water per year than your rotation"
    metric: str          # key in Strategy["metrics"] or AnalysisResult["climate"]
    source: str
    confidence: Confidence


class EvidenceCard(TypedDict):
    why: str                       # why suggested / "this is your current rotation"
    evidence: list[EvidenceItem]   # 3-5 items
    benefits: list[str]            # <= 3
    risks: list[str]               # <= 3
    information_gaps: list[str]    # what the model does not know
    needs_local_review: list[str]  # items for farmer / agronomist
    confidence: Confidence


class Calendars(TypedDict):
    bare_months: list[float]                 # 12 values, 0 = covered all 4 years, 1 = bare all 4 years
    vulnerability: dict[str, list[Risk]]     # crop id -> 12 monthly risk levels


class Strategy(TypedDict):
    id: str                        # "S0", "S1", ...
    label: str                     # "Your current rotation", "Best for your priorities", "Water saver"...
    template_id: str               # id in data/rotations.yaml, or "current"
    rotation: list[CropYear]
    irrigation: Irrigation
    scores: dict[str, float]       # water, soil, profit, resilience, overall — 0..100
    metrics: dict[str, Metric]     # irrigation_mm, margin_eur_ha, margin_p10_eur_ha, yield_*, bare_months...
    delta_vs_s0: dict[str, float]  # same keys as metrics, value minus S0 value
    evidence_card: EvidenceCard
    calendars: Calendars


class Field(TypedDict):
    id: str
    name: str
    lat: float
    lon: float


class WhatIf(TypedDict, total=False):
    rain_pct: float        # -40 .. +20
    temp_delta_c: float    # 0 .. +4
    irrigation_cap_mm: float | None


class Priorities(TypedDict):
    water: float           # 0..100 each; normalised inside the engine
    soil: float
    profit: float
    resilience: float


class AnalysisResult(TypedDict):
    field: Field
    climate: dict[str, Metric]     # rain_mm, et0_mm, tmean_c, heat_days, frost_days, dry_months...
    strategies: list[Strategy]     # S0 first, then 3 alternatives
    data_status: Literal["live", "cached", "sample"]
    whatif: WhatIf
    notes: list[str]               # data-quality notes shown in the UI
