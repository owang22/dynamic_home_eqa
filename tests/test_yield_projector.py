"""
Unit tests for scripts/yield_projector.py's pure-logic pieces (StratumTally,
_label_categories). The full project()/hazard-count functions need real
generation_out data on disk and are exercised as a smoke test by actually
running the script (see the phase's own verification notes), not unit-tested
here with synthetic fixtures for every I/O path.
"""
from __future__ import annotations


def test_stratum_tally_starts_at_zero():
    import dynamic_home_eqa.scripts.yield_projector as yp
    tally = yp.StratumTally()
    assert tally.location_stable == tally.location_volatile == 0
    assert tally.state_stable == tally.state_volatile == 0


def test_stratum_tally_add_routes_to_correct_field():
    import dynamic_home_eqa.scripts.yield_projector as yp
    tally = yp.StratumTally()
    tally.add("location", "stable", 5, "scene_a")
    tally.add("location", "volatile", 3, "scene_a")
    tally.add("state", "stable", 2, "scene_a")
    tally.add("state", "volatile", 1, "scene_a")
    assert tally.location_stable == 5
    assert tally.location_volatile == 3
    assert tally.state_stable == 2
    assert tally.state_volatile == 1


def test_stratum_tally_add_accumulates_across_scenes():
    import dynamic_home_eqa.scripts.yield_projector as yp
    tally = yp.StratumTally()
    tally.add("location", "stable", 5, "scene_a")
    tally.add("location", "stable", 7, "scene_b")
    assert tally.location_stable == 12


def test_stratum_tally_tracks_distinct_contributing_scenes_as_n_clusters():
    import dynamic_home_eqa.scripts.yield_projector as yp
    tally = yp.StratumTally()
    tally.add("location", "stable", 5, "scene_a")
    tally.add("location", "stable", 7, "scene_b")
    tally.add("location", "stable", 2, "scene_a")  # same scene again -> not a new cluster
    assert tally.location_stable_scenes == {"scene_a", "scene_b"}
    assert len(tally.location_stable_scenes) == 2


def test_stratum_tally_zero_labels_does_not_count_as_a_cluster():
    import dynamic_home_eqa.scripts.yield_projector as yp
    tally = yp.StratumTally()
    tally.add("location", "stable", 0, "scene_a")
    assert tally.location_stable_scenes == set()


def test_label_categories_first_occurrence_wins():
    import dynamic_home_eqa.scripts.yield_projector as yp
    manifests = [
        {"changes": [{"label": "book_1", "object_category": "book"}]},
        {"changes": [{"label": "book_1", "object_category": "book"}]},  # same label, later day
    ]
    cats = yp._label_categories(manifests)
    assert cats == {"book_1": "book"}


def test_label_categories_merges_across_manifests():
    import dynamic_home_eqa.scripts.yield_projector as yp
    manifests = [
        {"changes": [{"label": "book_1", "object_category": "book"}]},
        {"changes": [{"label": "vase_1", "object_category": "vase"}]},
    ]
    cats = yp._label_categories(manifests)
    assert cats == {"book_1": "book", "vase_1": "vase"}


def test_state_folder_name_inserts_before_day_suffix():
    import dynamic_home_eqa.scripts.yield_projector as yp
    assert yp._state_folder_name("102343992_family_with_kids_day2") == "102343992_family_with_kids_state_day2"
    assert yp._state_folder_name("102343992_family_with_kids") == "102343992_family_with_kids_state"
