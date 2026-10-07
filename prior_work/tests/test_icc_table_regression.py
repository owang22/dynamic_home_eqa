"""Pin the committed ICC table.

Any change to a loader, the crosswalk, or the estimator that MOVES an ICC
must be a deliberate, reviewed diff — not a silent drift discovered later in
a figure. Rebuilding the table needs ~3 minutes and 3.8 M activity records,
which is too slow for the default suite, so this guards it two cheaper ways:

1. the committed table's headline values are pinned here, so an accidental
   edit to the CSV fails;
2. the committed provenance must carry the CURRENT crosswalk hash, so
   editing the crosswalk without rebuilding fails.

Regenerate deliberately with:  PYTHONPATH=src python -m icc.cli build
"""

from __future__ import annotations

import csv
import json
import pathlib

import pytest

from icc import crosswalk

TABLE = pathlib.Path("reports/icc/icc_table.csv")
PROVENANCE = pathlib.Path("reports/icc/provenance.json")

# (activity, measure) -> (status, icc or None when not applicable)
PINNED = {
    ("wake", "start_min"): ("OK", 0.558),
    ("wake", "participation"): ("OK", 0.698),
    ("sleep", "start_min"): ("OK", 0.531),
    ("sleep", "log_duration"): ("FLAGGED_NEGATIVE", -1.723),
    ("sleep", "participation"): ("DEGENERATE_NO_VARIANCE", None),
    ("meal_prep", "start_min"): ("OK", 0.817),
    ("meal_prep", "log_duration"): ("OK", 0.463),
    ("meal_prep", "participation"): ("OK", 0.976),
    ("eating", "start_min"): ("OK", 0.585),
    ("eating", "log_duration"): ("OK", 0.007),
    ("eating", "participation"): ("FLAGGED_NEGATIVE", -0.946),
    ("dishes", "participation"): ("OK", 0.320),
    ("housekeeping", "participation"): ("OK", 0.569),
    ("leisure", "log_duration"): ("OK", 0.168),
    ("leisure", "participation"): ("OK", 0.829),
    ("work_home", "start_min"): ("OK", 0.579),
    ("work_home", "log_duration"): ("OK", 0.426),
    ("work_home", "participation"): ("FLAGGED_NEGATIVE", -0.036),
    ("leave_home", "start_min"): ("OK", 0.463),
    ("leave_home", "participation"): ("OK", 0.282),
    ("hygiene", "participation"): ("OK", 0.986),
}


@pytest.fixture(scope="module")
def table() -> dict:
    if not TABLE.exists():
        pytest.skip(f"{TABLE} not built; run `python -m icc.cli build`")
    with open(TABLE, newline="") as f:
        return {(r["activity"], r["measure"]): r for r in csv.DictReader(f)}


def test_pinned_iccs_have_not_drifted(table: dict) -> None:
    for key, (status, icc) in PINNED.items():
        assert key in table, f"{key} missing from the committed table"
        row = table[key]
        assert row["status"] == status, f"{key}: status moved"
        if icc is None:
            continue
        assert float(row["icc"]) == pytest.approx(icc, abs=0.02), (
            f"{key}: ICC moved from the pinned {icc} to {row['icc']} — if "
            f"intended, update PINNED in the same commit")


def test_every_row_carries_a_recognized_status(table: dict) -> None:
    allowed = {"OK", "FLAGGED_NEGATIVE", "DEGENERATE_NO_VARIANCE",
               "INSUFFICIENT_DATA"}
    for key, row in table.items():
        assert row["status"] in allowed, key


def test_negative_iccs_are_not_silently_usable(table: dict) -> None:
    # The automated path consumes OK rows only; a negative ICC must never
    # arrive labelled OK.
    for key, row in table.items():
        if row["status"] == "OK" and row["icc"]:
            assert float(row["icc"]) >= 0, f"{key}: negative ICC marked OK"


def test_provenance_pins_the_current_crosswalk(table: dict) -> None:
    if not PROVENANCE.exists():
        pytest.skip("provenance.json not built")
    prov = json.loads(PROVENANCE.read_text())
    assert prov["crosswalk_sha256"] == crosswalk.content_hash(), (
        "the crosswalk changed since the ICC table was built — rebuild with "
        "`python -m icc.cli build` and review the diff")
    assert prov["crosswalk_version"] == crosswalk.version()
