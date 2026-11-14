"""Checks on the YAML data files and the POWER parser (no network)."""
from engine import config, power


def test_crops_have_12_month_kc():
    for cid, c in config.crops().items():
        assert len(c["kc_by_month"]) == 12, cid
        assert all(0 <= k <= 1.3 for k in c["kc_by_month"]), cid


def test_rotations_and_fields_use_known_crops():
    known = set(config.crops())
    for r in config.rotations():
        assert len(r["years"]) == len(r["cover"]) == 4, r["id"]
        assert set(r["years"]) <= known, r["id"]
        assert r["irrigation"] in {"rainfed", "deficit", "full"}
    for fid, f in config.fields().items():
        assert set(f["current_rotation"]) <= known, fid


def test_power_parse_replaces_fill_values():
    raw = {"properties": {"parameter": {
        "T2M": {"20240101": 5.0, "20240102": -999.0},
        "PRECTOTCORR": {"20240101": 1.2, "20240102": 0.0},
    }}}
    df = power.parse(raw)
    assert list(df.columns) == ["tmean_c", "rain_mm"]
    assert df["tmean_c"].isna().sum() == 1
