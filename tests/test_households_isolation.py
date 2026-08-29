"""The src/households package must run with every revamp tree gone.

NOTE: this test renames repo directories for its duration — run the
suite sequentially (default); pytest-xdist would race other tests that
read old_profiles/.

The old pipeline loads executable Python out of profiles/revamp_v1 at
runtime; src/households vendored those modules. This test makes the
isolation claim real: it RENAMES profiles/revamp_v1, profiles/revamp_v2
and src/revamp_v2 away, then — in a fresh interpreter, so no module
already imported in this process can mask a hidden load — imports every
households module and realizes a real household (the copied hh_001
fixture) end to end, checking the event log against the golden hash the
vendoring diff established (identical to the old pipeline's output,
2026-08-28).

LLM stages are exercised separately once generate.py lands (stub client);
this test covers everything importable plus the full non-LLM realization.
"""
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
FIXTURE = REPO / "tests" / "fixtures" / "households" / "hh_001"

GOLDEN_EVENTS = 1148
GOLDEN_SHA = "40201c18938a1582248ae0b18c0b37e6d8f5f5a14f49525cfcc8e32da7d05c86"

# The old sets live in old_profiles/ (moved there 2026-08-28); the old
# code tree is src/revamp_v2. All of it goes away for the test's duration.
RENAME_AWAY = [REPO / "old_profiles",
               REPO / "src" / "revamp_v2"]

CHILD = r'''
import hashlib, json, sys, yaml
# every module in the package, imported fresh
import households
import households.expand_calendar
import households.normalize
import households.prompts
import households.schemas
import households.simulate as sim
import households.simulate_activities
import households.validate

fixture = sys.argv[1]
program = yaml.safe_load(open(fixture + "/program.yaml"))
log, hourly, blocks, stats, _a, _m = sim.simulate_program(
    program, int(program["days"]), 0)
sim.tag_event_kinds(log)
params = sim.load_params()
carry = params.get("carry_on_departure", {})
sim.suppress_carry_rehome(log, hourly,
                          float(carry.get("carry_rehome_min", 0)))
sha = hashlib.sha256(json.dumps(log, sort_keys=True).encode()).hexdigest()

# vendored normalizer, same fresh interpreter
from households import normalize
plog = []
persona = yaml.safe_load(open(fixture + "/persona.yaml"))
canonical = normalize.canonicalize(persona, plog, persona["household_id"])
problems = normalize.validate(normalize.strip_styles(canonical),
                              persona["household_id"])
print(json.dumps({"n_events": len(log), "sha": sha,
                  "persona_problems": problems}))
'''


def test_households_runs_with_revamp_trees_renamed_away(tmp_path):
    moved = []
    for d in RENAME_AWAY:
        if not d.is_dir():
            continue
        away = d.with_name(d.name + ".RENAMED-AWAY-BY-TEST")
        if away.exists():
            pytest.fail(f"stale {away} — a previous run died mid-test; "
                        f"restore it by hand before rerunning")
        d.rename(away)
        moved.append((d, away))
    try:
        proc = subprocess.run(
            [sys.executable, "-c", CHILD, str(FIXTURE)],
            capture_output=True, text=True, cwd=tmp_path, timeout=600)
        assert proc.returncode == 0, (
            f"households pipeline failed without the revamp trees:\n"
            f"{proc.stderr[-3000:]}")
        out = json.loads(proc.stdout.strip().splitlines()[-1])
    finally:
        for d, away in moved:
            away.rename(d)
    assert out["n_events"] == GOLDEN_EVENTS
    assert out["sha"] == GOLDEN_SHA, (
        "realization diverged from the vendoring-diff golden")
    assert out["persona_problems"] == []


def test_data_households_holds_no_code():
    """profiles/households is YAML and JSON only — a .py appearing there
    is the exact failure mode the vendoring removed."""
    data_dir = REPO / "profiles" / "households"
    if not data_dir.is_dir():
        pytest.skip("profiles/households not created yet")
    stray = [str(p.relative_to(REPO))
             for p in data_dir.rglob("*.py")]
    assert stray == [], f"executable code in the data tree: {stray}"
