"""Bare-field and vulnerability calendars (Dev A)."""
from __future__ import annotations

import pandas as pd

from . import config
from .schema import CropYear, Risk


def bare_months(rotation: list[CropYear]) -> list[float]:
    """Share of rotation years in which each month (Jan..Dec) has no living crop or cover crop."""
    crops = config.crops()
    cover_kc = crops["cover_crop"]["kc_by_month"]
    bare = [0.0] * 12
    for cy in rotation:
        kc = crops[cy["crop"]]["kc_by_month"]
        for m in range(12):
            covered = kc[m] > 0 or (cy["cover"] and cover_kc[m] > 0)
            bare[m] += 0 if covered else 1
    return [round(b / len(rotation), 2) for b in bare]


def vulnerability(daily: pd.DataFrame, rotation: list[CropYear]) -> dict[str, list[Risk]]:
    """Crop id -> 12 monthly risk levels, only for months the crop is in the field.

    Use POWER daily data: heat days above heat_threshold_c in heat_months, frost days in
    frost_months, and water deficit (ET0 − rain) in growing months. Thresholds in YAML.
    """
    raise NotImplementedError("Dev A: implement the vulnerability calendar")
