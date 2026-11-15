"""Checks on the crop ranking of every farmer (one CSV per area in data/)."""
from engine import crop_ranking, sample


def test_every_farmer_has_a_complete_ordered_ranking():
    for f in sample.FARMERS:
        r = crop_ranking(f["id"])
        scores = [c["score_pct"] for c in r["crops"]]
        assert len(scores) > 0 and len({c["code"] for c in r["crops"]}) == len(scores), f["id"]
        assert scores == sorted(scores, reverse=True) and all(0 <= s <= 100 for s in scores), f["id"]
        assert r["bbox"] == f["bbox"]


def test_tables_differ_and_notes_are_english():
    tops = [tuple(c["code"] for c in crop_ranking(f["id"])["crops"][:5]) for f in sample.FARMERS]
    assert len(set(tops)) == len(tops)
    for f in sample.FARMERS:
        notes = {c["note"] for c in crop_ranking(f["id"])["crops"]}
        assert len(notes) > 1, f["id"]
        assert not any(w in n.lower() for n in notes for w in ("favorita", "penalizzata", "adattabilit")), f["id"]
