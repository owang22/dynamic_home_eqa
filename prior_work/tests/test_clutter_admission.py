"""Unit tests for clutter admission (judge floor + catalog cap) — the gate
that stops census-starved scenes from seeding absurd start states (the
measured case: 18 bowls in one home, 6 of them on a bed)."""
from __future__ import annotations

from dynamic_home_eqa.generation.clutter.generate import admit_clutter

CATALOG = {"bowl": 2, "book": 3, "candle": 1}


def _p(cat, anchor):
    return {"object_category": cat, "target_relationship": "on", "target_anchor": anchor}


def test_floor_rejects_low_scored_placements():
    pool = [_p("bowl", "kitchen.table_1"), _p("bowl", "bedroom_1.bed_1")]
    kept, rejected, below, over = admit_clutter(pool, [0.7, 0.1], 0.3, CATALOG)
    assert [p["target_anchor"] for p in kept] == ["kitchen.table_1"]
    assert below == 1 and over == 0


def test_catalog_cap_keeps_highest_scored():
    # The 18-bowls case in miniature: 5 above-floor bowls, catalog says 2 —
    # keep the two highest-scored, count the rest as over-cap.
    pool = [_p("bowl", f"a{i}") for i in range(5)]
    scores = [0.4, 0.9, 0.5, 0.8, 0.35]
    kept, rejected, below, over = admit_clutter(pool, scores, 0.3, CATALOG)
    assert {p["target_anchor"] for p in kept} == {"a1", "a3"}
    assert below == 0 and over == 3


def test_cap_is_per_category_and_order_preserved():
    pool = [_p("book", "s1"), _p("bowl", "t1"), _p("book", "s2"),
            _p("candle", "t2"), _p("candle", "t3")]
    scores = [0.6, 0.6, 0.6, 0.5, 0.9]
    kept, rejected, below, over = admit_clutter(pool, scores, 0.3, CATALOG)
    # candle capped at 1 (highest wins: t3); books both fit (cap 3); bowl fits.
    assert [p["target_anchor"] for p in kept] == ["s1", "t1", "s2", "t3"]
    assert over == 1


def test_unknown_category_has_zero_cap():
    kept, rejected, below, over = admit_clutter([_p("gadget", "x")], [0.9], 0.3, CATALOG)
    assert kept == [] and over == 1


def test_score_ties_break_by_emission_order():
    pool = [_p("candle", "first"), _p("candle", "second")]
    kept, _, _, over = admit_clutter(pool, [0.5, 0.5], 0.3, CATALOG)
    assert [p["target_anchor"] for p in kept] == ["first"]
    assert over == 1
