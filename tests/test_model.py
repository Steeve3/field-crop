"""Sanity checks on the monthly model, run on the SAMPLE data."""
from engine import analyze, model, sample

ARGS = (sample.CROPS, sample.SOILS["loam"], sample.SLOPES["flat"], sample.ACCESS["limited"])


def test_more_rain_never_increases_water_gap():
    for rot in sample.ROTATIONS:
        dry = model.evaluate(sample.CLIMATE, rot, *ARGS, rain_pct=-30)
        base = model.evaluate(sample.CLIMATE, rot, *ARGS)
        wet = model.evaluate(sample.CLIMATE, rot, *ARGS, rain_pct=20)
        assert dry["water_gap_mm"] >= base["water_gap_mm"] >= wet["water_gap_mm"], rot["id"]


def test_scores_stay_in_range():
    for rot in sample.ROTATIONS:
        r = model.evaluate(sample.CLIMATE, rot, *ARGS, rain_pct=-40, d_temp=4)
        assert all(0 <= v <= 100 for v in r["scores"].values()), rot["id"]


def test_cover_crop_leaves_fewer_bare_months():
    by_id = {r["id"]: model.evaluate(sample.CLIMATE, r, *ARGS) for r in sample.ROTATIONS}
    assert by_id["r2"]["bare_months"] < by_id["r1"]["bare_months"] < by_id["r0"]["bare_months"]
    assert by_id["r0"]["bare_months"] == 6  # maize occupies April-September


def test_et0_is_plausible_for_po_valley():
    et0 = model.climate_for(sample.CLIMATE)["ET0"]
    assert 700 < sum(et0) < 1100 and et0[6] == max(et0)  # peak in July


def test_analyze_ranks_all_options():
    res = analyze()
    scores = [o["score"] for o in res["options"]]
    assert scores == sorted(scores, reverse=True) and len(scores) == len(sample.ROTATIONS)
    assert sum(o["current"] for o in res["options"]) == 1
    assert res["data_status"] == "sample"
