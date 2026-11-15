"""Checks on the fixed-region crop ranking (data/score_colture.csv)."""
from engine import crop_ranking


def test_ranking_is_complete_and_ordered():
    r = crop_ranking()
    crops = r["crops"]
    assert len(crops) == 77 and len({c["code"] for c in crops}) == 77
    assert [c["rank"] for c in crops] == list(range(1, 78))
    scores = [c["score_pct"] for c in crops]
    assert scores == sorted(scores, reverse=True) and all(0 <= s <= 100 for s in scores)
    assert len(r["bbox"]) == 4


def test_notes_are_translated():
    assert all("Adattabilit" not in c["note"] for c in crop_ranking()["crops"])
