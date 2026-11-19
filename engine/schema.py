"""The shared data shape between engine/ and app.py. Agree with your teammate before changing it."""
from __future__ import annotations

from typing import Literal, NotRequired, TypedDict


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


class Year(TypedDict):
    name: str
    role: str               # cereal | legume | cover | other (card colour)


class Option(TypedDict):
    id: str
    name: str
    current: bool           # True for the farmer's existing rotation
    years: list[Year] | None  # 5-year sequence; None when not provided
    water: float            # 0-1, higher is better: 1 - the model's water pressure
    revenue: float          # higher is better
    soil: float             # higher is better
    model_score: float      # the model's own score under its weighting
    percentile: NotRequired[float]       # current rotation only
    violations: NotRequired[list[str]]   # current rotation only: rules it breaks


class AnalysisResult(TypedDict):
    data_status: Literal["sample", "live", "cached"]
    source: str
    climate: Climate
    options: list[Option]   # the four strategies, then the current rotation
    selected: str           # id of the strategy matching the farmer's preference


class CropScore(TypedDict):
    rank: int
    code: str
    name: str
    category: str
    climate_pct: float      # FAO GAEZ climate suitability, 0-100
    score_pct: float        # after terrain bonuses/penalties, 0-100
    note: str


class CropRanking(TypedDict):
    bbox: tuple[float, float, float, float]   # lon_min, lat_min, lon_max, lat_max the table was computed for
    source: str
    terrain_adjusted: bool  # False when every score equals the climate suitability
    crops: list[CropScore]  # best first
