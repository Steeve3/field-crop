"""Checks on the climate helper and on the static rotation results."""
from engine import analyze, model, sample


def test_et0_is_plausible_for_every_farmer():
    for f in sample.FARMERS:
        et0 = model.climate_for(f["climate"])["ET0"]
        assert 700 < sum(et0) < 1200 and et0[6] == max(et0), f["id"]  # peak in July


def test_options_are_complete():
    for f in sample.FARMERS:
        options = analyze(f["id"])["options"]
        assert [o["id"] for o in options] == ["balanced", "water_saving", "economic_return", "soil_health", "current"]
        assert all(len(o["years"]) == 5 for o in options) and options[4]["current"]
        assert [y["name"] for y in options[4]["years"]] == ["Silage maize"] * 3 + ["Wheat"] * 2
        assert all(0 <= o[k] <= 1 for o in options for k in ("water", "revenue", "soil"))


def test_each_preference_selects_its_strategy():
    expected = {"balanced": "balanced", "water": "water_saving", "revenue": "economic_return", "soil": "soil_health"}
    for preference, strategy in expected.items():
        assert analyze("mugello", preference)["selected"] == strategy


def test_val_di_chiana_has_its_own_results():
    own = {o["id"]: o for o in analyze("val_di_chiana")["options"]}
    other = {o["id"]: o for o in analyze("asciano")["options"]}
    assert own["balanced"]["years"][0]["name"] == "Phaseolus bean" and own["current"]["water"] == 0.7628
    assert own["balanced"]["water"] != other["balanced"]["water"]
