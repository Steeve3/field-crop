"""The shared data shape between engine/ and app.py. Agree with your teammate before changing it."""
from __future__ import annotations

from typing import Literal, TypedDict


class Climate(TypedDict):
    T: list[float]          # 12 monthly values, index 0 = January (°C)
    Tx: list[float]
    Tn: list[float]
    P: list[float]          # rain, mm/month
    ET0: list[float]        # reference water demand, mm/month
    rain_mm: float
    et0_mm: float
    short: list[bool]       # months when demand exceeds rain
    deficit_mm: float
    frost: list[bool]
    heat: list[bool]


class Flag(TypedDict):
    type: Literal["frost", "heat"]
    crop: str
    months: list[int]       # 0 = January


class Option(TypedDict):
    id: str
    name: str
    current: bool           # True for the farmer's existing rotation
    years: int
    why: str
    benefits: list[str]
    gaps: list[str]         # information gaps
    risks: list[str]        # needs local review
    cal: list[dict | None]  # one cell per month: None = bare, else {id, crop, j, len, seg}
    score: float            # 0-100 with the farmer's weights
    lo: float               # score in a dry / wet year
    hi: float
    scores: dict[str, float]  # water, soil, fert, pest, income, forage, climate
    water_gap_mm: float
    gap_dry_mm: float
    bare_months: float
    bare_by_month: list[float]
    exposed_frac: float
    syn_n_kg: float
    residue_t: float
    heat_frost_months: float
    flags: list[Flag]


class AnalysisResult(TypedDict):
    data_status: Literal["sample", "live", "cached"]
    source: str
    climate: Climate
    options: list[Option]   # best first
