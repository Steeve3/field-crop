"""The one function the app calls: static rotation results, with the strategy matching the farmer's preference."""
from __future__ import annotations

from . import model, results, sample
from .crop_scores import crop_ranking
from .schema import AnalysisResult

# Crop colour on the cards, from the category in the area's crop file. Other categories -> "other".
CATEGORY_ROLE = {"Cereals": "cereal", "Pulses": "legume", "Fodder crops": "cover"}


def analyze(farmer_id: str, preference: str = "balanced") -> AnalysisResult:
    """Farmer + preference -> climate read, all options (current rotation last) and the selected strategy id.

    The rotation results are static (engine/results.py). The only change: water is shown as
    1 - water pressure, so that higher is better for all three scores.
    """
    categories = {c["name"]: c["category"] for c in crop_ranking(farmer_id)["crops"]}
    found = results.RESULTS.get(farmer_id, results.DEFAULT)
    rows = [*found["strategies"], found["current"]]
    options = [{
        **r,
        "name": r["label"],
        "water": round(1 - r["water"], 4),   # the model gives water pressure (lower is better)
        "current": r["id"] == "current",
        "years": [{"name": n, "role": CATEGORY_ROLE.get(categories.get(n), "other")} for n in r["crops"]]
                 if r["crops"] else None,
    } for r in rows]

    c = model.climate_for(sample.FARMER[farmer_id]["climate"])
    short = [e > p for e, p in zip(c["ET0"], c["P"])]
    climate = {
        **c,
        "rain_mm": sum(c["P"]),
        "et0_mm": sum(c["ET0"]),
        "short": short,                                    # months when demand exceeds rain
        "deficit_mm": sum(e - p for e, p, s in zip(c["ET0"], c["P"], short) if s),
        "frost": [t < 1 for t in c["Tn"]],                 # ASSUMPTION: night low below 1 C = frost-prone
        "heat": [t > 32 for t in c["Tx"]],                 # ASSUMPTION: daily high above 32 C = heat
    }
    return {"data_status": "sample", "source": results.SOURCE, "climate": climate, "options": options,
            "selected": sample.PRESETS[preference]["strategy"]}
