"""The one function the app calls."""
from __future__ import annotations

from . import power, sample
from .schema import AnalysisResult, CropYear, Field, Irrigation, Priorities, WhatIf


def analyze(
    field: Field,
    current_rotation: list[CropYear],
    current_irrigation: Irrigation,
    priorities: Priorities,
    whatif: WhatIf | None = None,
) -> AnalysisResult:
    """Field + current rotation + priorities (+ what-if) -> S0 and 3 alternatives.

    Until the engine is finished this returns real NASA POWER climate facts plus
    SAMPLE strategies (clearly labelled). Dev A: replace the sample call with:
        daily -> model.simulate_rotation for S0 and every template -> strategies.pick_strategies
        -> calendars + explain.evidence_card for each pick.
    """
    whatif = whatif or {}
    daily, status = power.get_daily(field["lat"], field["lon"])
    climate = power.climate_summary(daily)
    return sample.sample_result(field, climate, current_rotation, current_irrigation, whatif, status)
