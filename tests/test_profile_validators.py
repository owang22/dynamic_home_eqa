"""One deliberately-broken profile per validator check (V1-V5 structural,
V6a-V6e anchor), plus transform-purity and generator->ReplayWorld round-trip.

Fixtures are built by loading a VERIFIED-shaped base profile dict and mutating
exactly one thing, so each test isolates the check it targets. V6 tests use the
committed envelope.yaml (BDDL/Housekeep compile to OK from the cloned repos;
the rest degrade to NEEDS_DATA and are asserted as such).
"""
from __future__ import annotations

import copy
import pathlib

import pytest

from dynbelief.profiles.schema import (
    profile_from_dict, load_profile, validate_structural, has_fail,
)
from dynbelief.profiles import transforms
from dynbelief.profiles.generator import simulate, write_episode

REPO = pathlib.Path(__file__).resolve().parents[1]
MANUAL = REPO / "profiles" / "manual"
SINGLE = MANUAL / "single_adult_typ_v1.yaml"


def _findings(check, findings):
    return [f for f in findings if f.check == check]


def _fails(check, findings):
    return [f for f in _findings(check, findings) if f.severity == "FAIL"]


# ── base fixture (raw dict) ──────────────────────────────────────────────────

@pytest.fixture
def base_raw():
    import yaml
    return yaml.safe_load(SINGLE.read_text())


# ── V1: object required in two receptacles at the same instant ───────────────

def test_v1_double_placement_fires(base_raw):
    raw = copy.deepcopy(base_raw)
    # add a second resident whose concurrent activity puts `mug` somewhere else
    raw["residents"].append({
        "id": "R2", "description": "conflicting",
        "schedule": [{"activity": "breakfast", "days": ["Mo", "Tu", "We", "Th", "Fr"],
                      "start": "07:20", "end": "07:45"}],
    })
    # a NEW activity, concurrent with breakfast, that puts mug at a DIFFERENT receptacle
    raw["activities"]["breakfast_conflict"] = {
        "jitter_min": 0, "objects": ["mug"],
        "during": {"mug": "sofa_l1"},        # breakfast puts mug at counter_k1
    }
    raw["residents"][1]["schedule"][0]["activity"] = "breakfast_conflict"
    ch = profile_from_dict(raw)
    fs = validate_structural(ch)
    assert _fails("V1", fs), "expected V1 FAIL for concurrent conflicting during"


def test_v1_clean_base_has_no_fail(base_raw):
    ch = profile_from_dict(base_raw)
    assert not has_fail(validate_structural(ch))


# ── V2: reference to an undeclared receptacle ────────────────────────────────

def test_v2_undeclared_receptacle_fires(base_raw):
    raw = copy.deepcopy(base_raw)
    raw["placements"]["mug"]["home"] = "counter_NONEXISTENT"
    ch = profile_from_dict(raw)
    assert _fails("V2", validate_structural(ch))


def test_v2_missing_placement_for_activity_object(base_raw):
    raw = copy.deepcopy(base_raw)
    del raw["placements"]["mug"]           # mug still used by breakfast
    ch = profile_from_dict(raw)
    assert _fails("V2", validate_structural(ch))


# ── V3: two DIFFERENT activities overlap nominally ───────────────────────────

def test_v3_nominal_overlap_fires(base_raw):
    raw = copy.deepcopy(base_raw)
    # make dinner start before cook_dinner ends (different activities overlap)
    for b in raw["residents"][0]["schedule"]:
        if b["activity"] == "dinner" and b["days"] == ["Mo", "Tu", "We", "Th", "Fr"]:
            b["start"] = "18:30"           # cook_dinner is 18:15-19:00
    ch = profile_from_dict(raw)
    assert _fails("V3", validate_structural(ch))


# ── V4: probability out of range ─────────────────────────────────────────────

def test_v4_bad_probability_fires(base_raw):
    raw = copy.deepcopy(base_raw)
    raw["activities"]["breakfast"]["after"]["mug"]["p"] = 1.4
    ch = profile_from_dict(raw)
    assert _fails("V4", validate_structural(ch))


def test_v4_p_misplace_without_set_fires(base_raw):
    raw = copy.deepcopy(base_raw)
    raw["placements"]["laptop"]["p_misplace"] = 0.2   # no misplace_set
    ch = profile_from_dict(raw)
    assert _fails("V4", validate_structural(ch))


# ── V5: alias collides with a canonical receptacle id ────────────────────────

def test_v5_alias_collision_fires(base_raw):
    raw = copy.deepcopy(base_raw)
    # make sink_k1 claim an alias that is another receptacle's canonical id
    for r in raw["receptacles"]:
        if r["id"] == "sink_k1":
            r["aliases"] = ["counter_k1"]
    findings = []
    profile_from_dict(raw, findings)
    assert _fails("V5", findings), "alias colliding with a canonical id must FAIL"


def test_v5_alias_normalizes_at_load(base_raw):
    raw = copy.deepcopy(base_raw)
    # reference an alias (couch) instead of the canonical id (sofa_l1)
    raw["activities"]["tv_evening"]["during"]["remote_control"] = "couch"
    ch = profile_from_dict(raw)
    assert ch.activities["tv_evening"].during["remote_control"] == "sofa_l1"


# ── transforms: pure, params recorded, atypicality provenance ────────────────

def test_phase_shift_records_params_and_preserves_placements():
    ch = load_profile(SINGLE)
    t = transforms.phase_shift(ch, hours=10)
    assert t.derived_from == "single_adult_typ_v1"
    assert t.transformation == {"type": "phase_shift", "params": {"hours": 10}}
    # placements/affinities inherited untouched (only timing changes)
    assert {o: p.home for o, p in t.placements.items()} == \
           {o: p.home for o, p in ch.placements.items()}
    # source profile object is not mutated (purity)
    assert ch.transformation is None
    assert not has_fail(validate_structural(t))


def test_block_permutation_swaps_days():
    ch = load_profile(SINGLE)
    t = transforms.block_permutation(ch, swap=[["Sa", "Su"], ["Mo", "Tu"]])
    assert t.transformation["type"] == "block_permutation"
    assert not has_fail(validate_structural(t))


def test_unregistered_transform_raises():
    ch = load_profile(SINGLE)
    with pytest.raises(ValueError):
        transforms.apply_transform(ch, "not_a_transform")


# ── W3: addendum-v2 transform registry (T1/T2) ──────────────────────────────

FAMILY = MANUAL / "family4_typ_v1.yaml"

_REPORTABLE_TRANSFORMS = [
    ("night_shift_reversion", SINGLE, {}),
    ("workday_pattern", SINGLE, {"pattern": "three_twelves"}),
    ("workday_pattern", FAMILY, {"pattern": "weekend_worker"}),
]


@pytest.mark.parametrize("kind,base_path,params", _REPORTABLE_TRANSFORMS)
def test_transform_bindings_identical_and_valid(kind, base_path, params):
    """W3(i) bindings+placements byte-identical, (ii) V1-V5 pass, (iii) dist>0."""
    base = load_profile(base_path)
    t = transforms.apply_transform(base, kind, **params)
    assert base.raw["activities"] == t.raw["activities"]      # (i)
    assert base.raw["placements"] == t.raw["placements"]
    assert not has_fail(validate_structural(t))               # (ii)
    assert transforms.atypicality_distance(base, t) > 0       # (iii)
    assert base.transformation is None                        # purity: base untouched


def test_t1_offdays_byte_identical_to_base():
    """W3(iv): T1 reversion leaves a pure off-day (Sunday) unchanged."""
    base = load_profile(SINGLE)
    t = transforms.night_shift_reversion(base)

    def sunday(ch):
        return sorted((b.activity, b.start_min, b.end_min)
                      for b in ch.residents[0].schedule if "Su" in b.days and "Sa" not in b.days
                      or b.days == ["Su"])
    # any block that includes Su but not the transition Sat is reversion
    base_su = sorted((b.activity, b.start_min, b.end_min)
                     for b in base.residents[0].schedule if "Su" in b.days)
    t_su = sorted((b.activity, b.start_min, b.end_min)
                  for b in t.residents[0].schedule if "Su" in b.days)
    assert base_su == t_su


def test_atypicality_distance_zero_for_identity():
    base = load_profile(SINGLE)
    assert transforms.atypicality_distance(base, base) == 0.0


def test_t4_rotating_flagged_non_reportable():
    base = load_profile(SINGLE)
    t4 = transforms.rotating_shift(base)
    assert t4.raw.get("reportable") is False


def test_anchor_field_defaults_and_validates():
    import yaml
    raw = yaml.safe_load(SINGLE.read_text())
    ch = profile_from_dict(raw)
    # annotated weekday blocks carry non-clock anchors; others default to clock
    anchors = {b.activity: b.anchor for b in ch.residents[0].schedule}
    assert anchors["morning_prep"] == "wake"
    assert anchors["leave_work"] == "shift_start"
    assert anchors.get("sleep", "clock") == "clock"


# ── generator -> ReplayWorld round-trip ──────────────────────────────────────

def test_generator_roundtrips_through_replayworld(tmp_path):
    from dynbelief.replay.world import ReplayWorld
    ch = load_profile(SINGLE)
    write_episode(ch, tmp_path / "ep", n_days=10, seed=0)
    w = ReplayWorld(tmp_path / "ep")
    assert w.n_days == 10
    assert len(w.objects()) == len(ch.placements)
    # keys are away during work hours, home in the evening (dynamics sanity)
    kid = next(i for i, l in w.obj_label.items() if l == "keys")
    from dynbelief import ELSEWHERE_LABEL
    assert w.recep_label[w.true_parent(kid, 12 * 60)] == ELSEWHERE_LABEL
    assert w.recep_label[w.true_parent(kid, 20 * 60)] != ELSEWHERE_LABEL


def test_generator_is_deterministic():
    ch = load_profile(SINGLE)
    a = simulate(ch, n_days=10, seed=0)[0]
    b = simulate(ch, n_days=10, seed=0)[0]
    assert a == b
    c = simulate(ch, n_days=10, seed=1)[0]
    assert a != c


# ── V6 anchor checks (need the committed envelope) ───────────────────────────

envelope_present = (REPO / "src" / "dynbelief" / "anchors" / "envelope.yaml").exists()


@pytest.mark.skipif(not envelope_present, reason="envelope.yaml not compiled")
def test_v6d_flags_unmodeled_behav_object(tmp_path):
    from dynbelief.anchors import validate_profile as vc
    import yaml
    raw = yaml.safe_load(SINGLE.read_text())
    # inject a clearly-unmodeled [BEHAV] object into breakfast
    p = tmp_path / "broken_v6d.yaml"
    text = SINGLE.read_text().replace(
        "objects: [mug, bowl, spoon]",
        "objects: [mug, bowl, spoon, moon_rock]  # [BEHAV]")
    # also give it a placement so V2 stays clean
    text = text.replace("  glasses:        {home: nightstand_r1}",
                        "  glasses:        {home: nightstand_r1}\n"
                        "  moon_rock:      {home: nightstand_r1}")
    p.write_text(text)
    checks, ch = vc.validate(p)
    v6d = next(c for c in checks if c.check == "V6d")
    assert v6d.status in ("WARN", "FAIL")
    assert "moon_rock" in v6d.detail


@pytest.mark.skipif(not envelope_present, reason="envelope.yaml not compiled")
def test_v6e_flags_implausible_placement(tmp_path):
    from dynbelief.anchors import validate_profile as vc
    p = tmp_path / "broken_v6e.yaml"
    # put the toaster's [HKEEP]... actually keys has no HKEEP home; use mug home
    # send `mug` to the bathtub via an [HKEEP] tag -> implausible per Housekeep
    text = SINGLE.read_text().replace(
        "  mug:            {home: cupboard_k1}",
        "  mug:            {home: bathroom_c1}  # [HKEEP] implausible")
    p.write_text(text)
    checks, ch = vc.validate(p)
    v6e = next(c for c in checks if c.check == "V6e")
    assert v6e.status in ("WARN", "FAIL")


@pytest.mark.skipif(not envelope_present, reason="envelope.yaml not compiled")
def test_v6a_v6b_needs_data_without_atus_homer():
    from dynbelief.anchors import validate_profile as vc
    checks, ch = vc.validate(SINGLE)
    v6a = next(c for c in checks if c.check == "V6a")
    v6b = next(c for c in checks if c.check == "V6b")
    # ATUS unreachable + HOMER jitter unparsed -> non-gating NEEDS_DATA
    assert v6a.status in ("NEEDS_DATA", "SKIP")
    assert v6b.status in ("NEEDS_DATA", "SKIP")


@pytest.mark.skipif(not envelope_present, reason="envelope.yaml not compiled")
def test_v6c_computes_emergent_rates():
    from dynbelief.anchors import validate_profile as vc
    checks, ch = vc.validate(SINGLE)
    v6c = next(c for c in checks if c.check == "V6c")
    # emergent hazard rates always compute (band may be NEEDS_DATA)
    assert "phone=" in v6c.detail


# ── bank builder (A2-A4) ─────────────────────────────────────────────────────

def _tiny_bank(tmp_path, name="typ_v1", days=6, targets=12):
    from dynbelief.profiles import bank
    specs = bank.default_bank_specs()
    spec = specs[name]
    spec.n_days = days
    spec.n_targets = targets
    return bank.build_bank(spec, MANUAL, tmp_path, allow_draft=True)


def test_bank_builds_reportable_from_verified(tmp_path):
    m = _tiny_bank(tmp_path)
    # profiles are VERIFIED with no anchor FAIL -> reportable even under --allow-draft
    assert m["non_reportable"] is False
    assert all(h["status"] == "VERIFIED" for h in m["households"])
    assert len(m["households"]) == 3
    assert m["envelope_hash"]                    # envelope pinned


def test_bank_non_reportable_when_draft(tmp_path):
    """A DRAFT profile under --allow-draft must stamp the manifest
    non_reportable (the reportability gate, independent of the current
    VERIFIED bases)."""
    import yaml
    from dynbelief.profiles import bank
    draft_dir = tmp_path / "manual"
    draft_dir.mkdir()
    raw = yaml.safe_load(SINGLE.read_text())
    raw["household"] = "draft_probe"
    raw["status"] = "DRAFT"
    (draft_dir / "draft_probe.yaml").write_text(yaml.safe_dump(raw))
    spec = bank.BankSpec("typ_v1", [bank.HouseholdSpec("draft_probe")],
                         n_days=4, n_targets=8)
    m = bank.build_bank(spec, draft_dir, tmp_path / "b", allow_draft=True)
    assert m["non_reportable"] is True


def test_bank_held_out_is_class_disjoint(tmp_path):
    import json
    from dynbelief.profiles.schema import default_class
    _tiny_bank(tmp_path)
    for hh in (tmp_path / "typ_v1").iterdir():
        tj = hh / "targets.json"
        if not tj.exists():
            continue
        t = json.loads(tj.read_text())
        obs_c = {default_class(o) for o in t["observed"]}
        held_c = {default_class(o) for o in t["held_out"]}
        assert held_c.isdisjoint(obs_c), f"{hh.name}: held-out classes leak into observed"
        assert len(t["held_out"]) == 5


def test_bank_ground_truth_matches_replay(tmp_path):
    import json
    from dynbelief.replay.world import ReplayWorld
    _tiny_bank(tmp_path)
    hh = tmp_path / "typ_v1" / "single_adult_typ_v1"
    w = ReplayWorld(hh)
    for r in [json.loads(l) for l in (hh / "ground_truth.jsonl").open()]:
        oid = next(i for i, l in w.obj_label.items() if l == r["object"])
        assert w.recep_label[w.true_parent(oid, r["t_query"])] == r["true_receptacle"]


def test_bank_terciles_balanced(tmp_path):
    m = _tiny_bank(tmp_path)
    for h in m["households"]:
        counts = h["tercile_counts"]
        assert max(counts.values()) - min(counts.values()) <= 1


def test_b25_betabayes_calibrated(tmp_path):
    """B2.5 tracks a static object confidently, expresses MORE uncertainty than
    B2 when stale, and yields valid distributions."""
    import numpy as np
    from dynbelief.replay.world import ReplayWorld
    from dynbelief.beliefs.factory import make_belief, BELIEF_TIERS
    from dynbelief.profiles.bank import build_bank, default_bank_specs
    spec = default_bank_specs()["typ_v1"]
    spec.n_days, spec.n_targets = 6, 12
    build_bank(spec, MANUAL, tmp_path, allow_draft=True)
    assert "b25_betabayes" in BELIEF_TIERS
    w = ReplayWorld(tmp_path / "typ_v1" / "single_adult_typ_v1")
    objs, receps = w.objects(), w.receptacles(include_elsewhere=True)

    def train(tier):
        b = make_belief(tier, w, train_horizon_min=4 * 1440)
        b.reset(objs, receps, 0)
        for d in range(4):
            for h in range(7, 23, 2):
                t = d * 1440 + h * 60
                b.observe(t, {o: (w.true_parent(o, t), {}) for o in objs})
        return b

    b25, b2 = train("b25_betabayes"), train("b2_classdecay")
    tq = 4 * 1440 + 12 * 60          # stale
    p25, p2 = b25.predict(tq), b2.predict(tq)
    assert all(abs(p25[o].sum() - 1) < 1e-6 for o in objs)   # valid distributions
    to = next(i for i, l in w.obj_label.items() if l == "toaster")
    # static object: correct argmax, but B2.5 less overconfident than B2's flat 1.0
    assert w.recep_label[p25[to].argmax()] == w.recep_label[w.true_parent(to, tq)]
    assert p25[to].max() <= p2[to].max()


def test_bank_is_deterministic(tmp_path):
    import json
    m1 = _tiny_bank(tmp_path / "a")
    m2 = _tiny_bank(tmp_path / "b")
    h1 = m1["households"][0]["file_hashes"] if "file_hashes" in m1["households"][0] else None
    # compare the queries file hash across two builds (same seed => identical)
    fa = json.loads((tmp_path / "a" / "typ_v1" / "manifest.json").read_text())["file_hashes"]
    fb = json.loads((tmp_path / "b" / "typ_v1" / "manifest.json").read_text())["file_hashes"]
    assert fa == fb
