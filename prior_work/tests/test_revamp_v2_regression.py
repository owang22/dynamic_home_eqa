"""The regression anchor: the hand-translated hh1 routine program, with no
skip_p/fragment anywhere, reproduces revamp_v1 hh1's timeline byte-for-byte
through the v2 expander + extended simulator.

Two comparisons:
  * against a fresh run of the UNMODIFIED v1 simulator on the original
    authored files (full byte equality of events/hourly/residents);
  * against the committed timeline_seed0/events.jsonl on disk, comparing
    the simulator-native fields only (that file was enriched in place by
    visualization/spatialize.py with room/pos fields, which re-running
    spatialize would add again).
"""
from __future__ import annotations

import json
import pathlib

import yaml

from revamp_v2_helpers import REPO  # noqa: F401  (sys.path side effect)

import simulate as sim

HH1 = REPO / "profiles" / "revamp_v1" / "claude-fable-5" / "hh1"
FIXTURE = (REPO / "tests" / "fixtures" /
           "revamp_v2_hh1_translated_program.yaml")
SIM_KEYS = ("t", "stamp", "object", "from", "to", "by")


def _run_both(tmp_path: pathlib.Path):
    sa = sim.load_v1()
    acts, motions = sa.load(HH1)
    sa.validate(acts, motions)
    days = int(acts["days"])
    out_v1 = tmp_path / "v1"
    log, hourly, blocks, stats = sa.simulate(acts, motions, days, 0)
    sa.write_outputs(out_v1, motions, log, hourly, blocks, stats, days, 0,
                     HH1)

    program = yaml.safe_load(FIXTURE.read_text())
    assert not any(b.get("skip_p") for b in program["weekly_blocks"])
    assert not any(a.get("fragment") for a in program["activities"])
    # The anchor is "v1 reproduced with the NEW mechanisms off" — skip and
    # fragmentation are absent from the fixture itself; carry-on-departure
    # is a realization parameter, so it is turned off here the same way.
    params = dict(sim.load_params(), carry_on_departure={"enabled": False})
    log2, hourly2, blocks2, stats2, _, motions2 = sim.simulate_program(
        program, days, 0, sa=sa, params=params)
    out_v2 = tmp_path / "v2"
    sa.write_outputs(out_v2, motions2, log2, hourly2, blocks2, stats2, days,
                     0, FIXTURE)
    return out_v1, out_v2


def test_translated_hh1_reproduces_v1_byte_for_byte(tmp_path):
    out_v1, out_v2 = _run_both(tmp_path)
    for name in ("events.jsonl", "hourly.csv", "residents.jsonl"):
        assert (out_v1 / name).read_bytes() == (out_v2 / name).read_bytes(), \
            f"{name} differs from the v1 simulator's own output"


def test_translated_hh1_matches_committed_events(tmp_path):
    _, out_v2 = _run_both(tmp_path)
    committed = (HH1 / "timeline_seed0" / "events.jsonl").read_text()
    ours = (out_v2 / "events.jsonl").read_text()
    a = [{k: e[k] for k in SIM_KEYS}
         for e in map(json.loads, committed.splitlines())]
    b = [{k: e[k] for k in SIM_KEYS}
         for e in map(json.loads, ours.splitlines())]
    assert a == b
