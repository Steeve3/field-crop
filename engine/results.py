"""Static results of the optimisation model, copied by hand from its printed output. Nothing is computed here.

Scores are the model's own 0-1 values:
  water    water pressure, LOWER is better (evapotranspiration + water deficit, see data/readme.pdf)
  revenue  relative gross revenue, higher is better
  soil     rotation quality (diversity, legumes before cereals, other families, cover crops), higher is better
model_score is the model's score under each strategy's own weighting (the current rotation: under the balanced one).

RESULTS holds one set per area. Areas without their own set use DEFAULT, whose area was not stated.
Replace this file with the real per-area output when it exists.
"""
from __future__ import annotations

SOURCE = "Optimisation model output (static results)"

# The current rotation, as given with the Val di Chiana results. The other areas report the same two
# rule violations, so the same sequence is shown for them. ASSUMPTION until confirmed per area.
CURRENT_CROPS = ["Silage maize", "Silage maize", "Silage maize", "Wheat", "Wheat"]

DEFAULT_STRATEGIES = [
    {"id": "balanced", "label": "Balanced",
     "crops": ["Rapeseed", "Phaseolus bean", "Rye", "Phaseolus bean", "Buckwheat"],
     "water": 0.203, "revenue": 0.285, "soil": 0.912, "model_score": 0.853},
    {"id": "water_saving", "label": "Water saving",
     "crops": ["Dry pea", "Phaseolus bean", "Rapeseed", "Buckwheat", "Buckwheat"],
     "water": 0.187, "revenue": 0.198, "soil": 0.512, "model_score": 1.0},
    {"id": "economic_return", "label": "Economic return",
     "crops": ["Alfalfa", "Phaseolus bean", "Phaseolus bean", "Pasture grasses", "Phaseolus bean"],
     "water": 0.354, "revenue": 0.391, "soil": 0.275, "model_score": 1.0},
    {"id": "soil_health", "label": "Soil health",
     "crops": ["Wheat", "Phaseolus bean", "Rye", "Buckwheat", "Pasture grasses"],
     "water": 0.304, "revenue": 0.210, "soil": 1.0, "model_score": 1.0},
]

# percentile = share of the rotations tested that score below it.
DEFAULT_CURRENT = {
    "id": "current", "label": "Your current rotation", "crops": CURRENT_CROPS,
    "water": 0.3246, "revenue": 0.0752, "soil": 0.1875, "model_score": 0.1797, "percentile": 0.0102,
    "violations": ["Only 2 main crops (minimum 3)", "Silage maize: 2 consecutive repeats (maximum 1)"],
}

DEFAULT = {"strategies": DEFAULT_STRATEGIES, "current": DEFAULT_CURRENT}

_VIOLATIONS = ["Only 2 main crops (minimum 3)", "Silage maize: 2 consecutive repeats (maximum 1)"]

RESULTS = {
    "val_di_chiana": {
        "strategies": [
            {"id": "balanced", "label": "Balanced",
             "crops": ["Phaseolus bean", "Buckwheat", "Phaseolus bean", "Foxtail millet", "Tomato"],
             "water": 0.172, "revenue": 0.158, "soil": 0.912, "model_score": 0.809},
            {"id": "water_saving", "label": "Water saving",
             "crops": ["Buckwheat", "Phaseolus bean", "Foxtail millet", "Cabbage", "Carrot"],
             "water": 0.143, "revenue": 0.109, "soil": 1.0, "model_score": 0.859},
            {"id": "economic_return", "label": "Economic return",
             "crops": ["Phaseolus bean", "Wheat", "Phaseolus bean", "Tomato", "Phaseolus bean"],
             "water": 0.180, "revenue": 0.187, "soil": 0.675, "model_score": 0.853},
            {"id": "soil_health", "label": "Soil health",
             "crops": ["Phaseolus bean", "Wheat", "Buckwheat", "Tomato", "Cabbage"],
             "water": 0.164, "revenue": 0.126, "soil": 1.0, "model_score": 0.909},
        ],
        "current": {"id": "current", "label": "Your current rotation", "crops": CURRENT_CROPS,
                    "water": 0.2372, "revenue": 0.0396, "soil": 0.1875, "model_score": 0.1727,
                    "percentile": 0.000167, "violations": _VIOLATIONS},
    },
}
