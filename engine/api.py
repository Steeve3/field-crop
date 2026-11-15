"""The one function the app calls. Runs on SAMPLE data for now (engine/sample.py); no dataset is read."""
from __future__ import annotations

from . import model, sample
from .schema import AnalysisResult


def analyze(farmer_id: str, soil: str = "loam", slope: str = "flat", access: str = "limited",
            weights: dict | None = None, rain_pct: float = 0.0, temp_delta_c: float = 0.0) -> AnalysisResult:
    """Farmer + field settings + priorities + what-if -> climate read and ranked rotations (current one included)."""
    base = sample.FARMER[farmer_id]["climate"]
    weights = weights or sample.PRESETS["balanced"]["w"]
    options = model.rank(base, sample.ROTATIONS, sample.CROPS, sample.SOILS[soil], sample.SLOPES[slope],
                         sample.ACCESS[access], weights, rain_pct, temp_delta_c)
    c = model.climate_for(base, rain_pct, temp_delta_c)
    short = [e > p for e, p in zip(c["ET0"], c["P"])]
    climate = {
        **c,
        "rain_mm": sum(c["P"]),
        "et0_mm": sum(c["ET0"]),
        "short": short,                                    # months when demand exceeds rain
        "deficit_mm": sum(e - p for e, p, s in zip(c["ET0"], c["P"], short) if s),
        "frost": [t < 1 for t in c["Tn"]],                 # ASSUMPTION: night low below 1 °C = frost-prone
        "heat": [t > 32 for t in c["Tx"]],                 # ASSUMPTION: daily high above 32 °C = heat
    }
    return {"data_status": "sample", "source": sample.SOURCE, "climate": climate, "options": options}
