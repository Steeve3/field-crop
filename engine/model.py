"""Agronomic model (Dev A). Kept simple on purpose — document every formula in the Data & Methods expander.

Plan:
1. Monthly weather per year from POWER daily data (apply what-if: rain × (1 + rain_pct/100), temps + temp_delta_c).
2. ET0 per month: Hargreaves  ET0 = 0.0023 · Ra · (Tmean + 17.8) · sqrt(Tmax − Tmin)   (mm/day, Ra in mm/day)
   SOURCE: FAO-56 eq. 52. Ra (extraterrestrial radiation) from latitude + day of year, FAO-56 eq. 21.
3. ETc = kc_by_month · ET0.   Water need = ETc − effective rain (simple monthly bucket is fine).
4. Irrigation policy: full = cover all need; deficit = cover a share (put the share in YAML);
   rainfed = none. Respect irrigation_cap_mm.
5. Yield: 1 − Ya/Ym = ky · (1 − ETa/ETc)   SOURCE: FAO-33.
6. Margin = yield · price − cost − irrigation_mm · irrigation_cost_eur_per_mm.
7. Repeat for all 20 years → mean margin, P10 margin, failure probability (yield < 50 % Ym).
8. Soil score 0–100: legumes, cover crops, deep roots, crop diversity, fewer bare months (weights in YAML).
"""
from __future__ import annotations

import pandas as pd

from .schema import CropYear, Irrigation, Metric, WhatIf


def simulate_rotation(
    daily: pd.DataFrame,
    lat: float,
    rotation: list[CropYear],
    irrigation: Irrigation,
    whatif: WhatIf,
) -> dict[str, Metric]:
    """Run the rotation over all weather years. Return metrics:
    irrigation_mm, water_need_mm, margin_eur_ha, margin_p10_eur_ha, fail_prob_pct, yield_<crop>_t_ha ...
    """
    raise NotImplementedError("Dev A: implement the water balance + yield + margin")


def soil_score(rotation: list[CropYear]) -> Metric:
    """0–100 heuristic. Never present as measured."""
    raise NotImplementedError("Dev A: implement the soil score")
