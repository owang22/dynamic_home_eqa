"""Loader integrity: the canonical traces must match the Phase-0 inventory.

Silent row loss through joins is the failure mode that has bitten this
project before, so the counts asserted here come from a DIFFERENT code
path (the inventory, computed during the raw parse) than the reload being
tested. The receptacle counts are additionally pinned as a regression
against the parent-resolution bug this loader already had once: choosing
parents by lowest id resolved every object to its room and collapsed
26-29 receptacles to 5.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from homer.loader import read_traces

TRACES = pathlib.Path("data/homer_traces")
PINNED_RECEPTACLES = {"A": 26, "B": 29, "C": 25}


@pytest.fixture(scope="module")
def inventory() -> dict:
    path = TRACES / "inventory.json"
    if not path.exists():
        pytest.skip("traces not built; run homer.loader.write_traces")
    return json.loads(path.read_text())


@pytest.mark.parametrize("household", ["A", "B", "C"])
def test_row_counts_match_inventory(household: str, inventory: dict) -> None:
    inv = inventory[household]
    rows = read_traces(TRACES, household)
    train = [r for r in rows if r.split == "train"]
    test = [r for r in rows if r.split == "test"]
    assert len(train) == inv["rows_train"]
    assert len(test) == inv["rows_test"]
    assert len({r.object_id for r in rows}) == inv["n_objects"]
    assert len({r.receptacle_id for r in rows}) == inv["n_receptacles"]
    assert inv["n_receptacles"] == PINNED_RECEPTACLES[household]
    assert len({r.day_index for r in train}) == inv["days_train"] == 65
    assert len({r.day_index for r in test}) == inv["days_test"] == 10


@pytest.mark.parametrize("household", ["A", "B", "C"])
def test_every_day_has_an_initial_state(household: str, inventory: dict) -> None:
    rows = read_traces(TRACES, household)
    # Every (split, day) must open with a full-population snapshot: the
    # piecewise-constant lookup is only sound if day-initial state exists.
    for split in ("train", "test"):
        sub = [r for r in rows if r.split == split]
        for day in {r.day_index for r in sub}:
            day_rows = [r for r in sub if r.day_index == day]
            t0 = min(r.timestamp for r in day_rows)
            n_initial = len({r.object_id for r in day_rows
                             if r.timestamp == t0})
            assert n_initial >= inventory[household]["n_objects"] * 0.9
