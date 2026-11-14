"""Pick S0 + 3 alternatives (Dev A).

Plan:
1. S0 = farmer's current rotation.
2. Candidates = templates in data/rotations.yaml for the field's region (north if lat > 43.5, else south —
   put the threshold in fields.yaml or a small regions.yaml).
3. Score every candidate: water, soil, profit, resilience as 0–100 (min–max across candidates + S0).
4. overall = weighted sum with the farmer's priority sliders (normalised to sum 1).
5. Pick: S1 "Best for your priorities" (highest overall), then two specialists
   ("Water saver", "Soil builder", "Profit", "Climate-proof") from the objectives with the highest
   weights, skipping duplicates of S0/S1.
6. delta_vs_s0 for every metric.
"""
from __future__ import annotations

from .schema import Priorities


def pick_strategies(scored: list[dict], priorities: Priorities) -> list[dict]:
    raise NotImplementedError("Dev A: implement strategy selection")
