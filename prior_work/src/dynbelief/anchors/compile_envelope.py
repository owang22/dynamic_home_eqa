"""compile_envelope.py -- raw anchors -> envelope.yaml (committed, cited).

Deterministic. Parses whatever anchor data is present under third_party/ and
data/anchors/ and writes envelope.yaml with:

  config:             band multipliers (editable; tighten later)
  bddl_object_unions: per profile-activity synset union       (Anchor 3, V6d)
  housekeep_placements: per object-class correct/misplaced receptacle
                        categories                            (Anchor 4, V6e)
  homer_jitter_std:   per HOMER activity, std of daily start  (Anchor 2, V6b)
  homer_change_rates: per mapped class, min/max daily change  (Anchor 2, V6c)
  atus_bands:         per activity/day-type start percentiles (Anchor 1, V6a)
  literature_tier:    secondary V6c band                      (Anchor 5)

Anchors with no data present are written as {status: NEEDS_DATA, ...} so
validate_profile degrades that check rather than failing the run. No numeric
value is invented: every number here is parsed from a shipped dataset or left
as NEEDS_DATA / TODO for human transcription.

Run:  python -m dynbelief.anchors.compile_envelope
"""
from __future__ import annotations

import json
import pathlib
import re
import statistics
from collections import defaultdict

import yaml

from dynamic_home_eqa.paths import REPO_ROOT
from dynbelief.anchors import ANCHORS_DIR, ENVELOPE_PATH

THIRD_PARTY = REPO_ROOT / "third_party"
DATA_ANCHORS = REPO_ROOT / "data" / "anchors"

# ── band multiplier config (defaults; edit here, re-run) ─────────────────────
CONFIG = {
    "jitter_band": [0.5, 2.0],       # V6b: profile jitter_min within [0.5x, 2x] HOMER std
    "hazard_band": [0.5, 2.0],       # V6c: emergent class rate within [0.5x min, 2x max]
    "atus_percentiles": [10, 50, 90],  # V6a band = [10th, 90th]
    "binding_warn_at": 1,            # V6d/V6e: 1 unmatched = WARN
    "binding_fail_at": 2,            # 2+ unmatched in one activity = FAIL
}


def _load_map(name: str) -> dict:
    return yaml.safe_load((ANCHORS_DIR / name).read_text())


# ── Anchor 3: BDDL object synset unions (V6d) ────────────────────────────────

_OBJ_LINE = re.compile(r"-\s+([a-zA-Z_][\w]*\.n\.\d+)")


def parse_bddl_synsets(activity_dir: pathlib.Path) -> set[str]:
    """Union of object synsets across an activity's problem*.bddl :objects."""
    synsets: set[str] = set()
    for prob in activity_dir.glob("problem*.bddl"):
        text = prob.read_text()
        m = re.search(r"\(:objects(.*?)\)\s*\(:init", text, re.S)
        block = m.group(1) if m else text
        for line in block.splitlines():
            typ = _OBJ_LINE.search(line)
            if typ:
                synsets.add(typ.group(1))
    return synsets


def compile_bddl() -> dict:
    root = THIRD_PARTY / "bddl" / "bddl" / "activity_definitions"
    if not root.exists():
        return {"status": "NEEDS_DATA", "hint": "run fetch_all (bddl clone missing)"}
    amap = _load_map("bddl_activity_map.yaml")["map"]
    per_bddl = {}
    out = {"status": "OK", "by_profile_activity": {}}
    for profile_act, spec in amap.items():
        union: set[str] = set()
        for bddl_act in spec["bddl"]:
            d = root / bddl_act
            if bddl_act not in per_bddl:
                per_bddl[bddl_act] = parse_bddl_synsets(d) if d.exists() else set()
            union |= per_bddl[bddl_act]
        out["by_profile_activity"][profile_act] = {
            "bddl": spec["bddl"], "confidence": spec.get("confidence"),
            "synsets": sorted(union),
            # bare object names (strip .n.NN) for name-level matching in V6d
            "names": sorted({s.split(".")[0] for s in union}),
        }
    return out


# ── Anchor 4: Housekeep placement rankings (V6e) ─────────────────────────────

def compile_housekeep() -> dict:
    base = THIRD_PARTY / "housekeep" / "cos_eor" / "scripts" / "orm" / "amt_data"
    npy = base / "data.npy"
    if not npy.exists():
        return {"status": "NEEDS_DATA", "hint": "run fetch_all (housekeep clone missing)"}
    try:
        import numpy as np
        data = np.load(npy, allow_pickle=True).item()
        ranks = np.asarray(data["ranks"])           # [room_recep, object, annot]
        objects = list(data["objects"])
        room_receps = list(data["room_receptacles"])
    except Exception as e:  # tolerant: degrade rather than crash the whole run
        return {"status": "NEEDS_DATA", "hint": f"data.npy unreadable: {e}"}

    recep_cat = [rr.split("|", 1)[1].strip() if "|" in rr else rr for rr in room_receps]
    out = {"status": "OK", "by_object": {}}
    for oi, obj in enumerate(objects):
        col = ranks[:, oi, :]                         # [room_recep, annot]
        # mean over annotations; >0 => "correct/after", <0 => "before", 0 => implausible
        mean_rank = col.mean(axis=1)
        pos_frac = (col > 0).mean(axis=1)
        nonzero = (col != 0).any(axis=1)
        scored = []
        for ri in range(len(room_receps)):
            scored.append((float(mean_rank[ri]), float(pos_frac[ri]),
                           bool(nonzero[ri]), recep_cat[ri]))
        correct = sorted([s for s in scored if s[0] > 0], key=lambda s: -s[0])
        plausible = [s for s in scored if s[2]]        # annotated at all
        # top-5 correct receptacle categories (dedup, preserve order)
        top5, seen = [], set()
        for _, _, _, cat in correct:
            if cat not in seen:
                seen.add(cat); top5.append(cat)
            if len(top5) >= 5:
                break
        out["by_object"][str(obj)] = {
            "correct_top5": top5,
            "plausible": sorted({s[3] for s in plausible}),
        }
    out["receptacle_categories"] = sorted(set(recep_cat))
    return out


# ── Anchor 2: HOMER jitter std + change rates (V6b, V6c) ─────────────────────

def compile_homer() -> dict:
    root = THIRD_PARTY / "HOMER_PLUS"
    if not root.exists():
        return {"jitter": {"status": "NEEDS_DATA"}, "change_rates": {"status": "NEEDS_DATA"}}
    common = root / "common_data.json"
    activities = []
    if common.exists():
        try:
            activities = json.loads(common.read_text()).get("activities", [])
        except Exception:
            pass
    # Per-activity daily start-time std across routine days. The routine JSONs
    # carry per-timestep `times` + activity labels; the exact per-activity
    # start extraction depends on HOMER's node-graph schema. We attempt the
    # documented `activities`/`times` alignment; if the schema does not expose
    # a clean per-activity start, the check degrades to NEEDS_DATA (numbers are
    # never guessed).
    starts: dict[str, list[float]] = defaultdict(list)
    n_routines = 0
    for hh in ("HouseholdA", "HouseholdB", "HouseholdC"):
        for rj in sorted((root / hh / "routines_train").glob("*.json")) if (root / hh / "routines_train").exists() else []:
            try:
                r = json.loads(rj.read_text())
            except Exception:
                continue
            n_routines += 1
            acts = r.get("activities") or r.get("activity") or []
            times = r.get("times") or []
            if acts and times and len(acts) == len(times):
                seen_today = set()
                for a, t in zip(acts, times):
                    if a not in seen_today:            # first occurrence = start
                        seen_today.add(a)
                        starts[str(a)].append(float(t))
    jitter = {}
    if starts:
        jitter["status"] = "OK"
        jitter["activity_start_std_min"] = {
            a: round(statistics.pstdev(v), 2) for a, v in starts.items() if len(v) >= 3}
        jitter["n_routines"] = n_routines
    else:
        jitter = {"status": "NEEDS_DATA",
                  "hint": f"parsed {n_routines} routines but no clean per-activity "
                          f"start alignment; HOMER routine schema needs a bespoke parser",
                  "homer_activities": activities}
    change = {"status": "NEEDS_DATA",
              "hint": "per-class receptacle-change-rate distribution requires the HOMER "
                      "object-node timeline parse; movable props are sparse -> V6c relies "
                      "on the emergent-sim + literature tier"}
    return {"jitter": jitter, "change_rates": change}


# ── Anchor 1: ATUS bands (V6a) ───────────────────────────────────────────────

def compile_atus() -> dict:
    raw = DATA_ANCHORS / "atus" / "raw"
    zips = list(raw.glob("*.zip")) if raw.exists() else []
    if not zips:
        return {"status": "NEEDS_DATA",
                "hint": "place ATUS zips in data/anchors/atus/raw (bls.gov unreachable); "
                        "then compile percentile bands per atus_code_map.yaml"}
    # ATUS microdata parse (fixed CSV per data dictionary) is implemented once
    # the zips are present; deliberately left as NEEDS_DATA-until-present so no
    # band numbers are fabricated.
    return {"status": "NEEDS_DATA",
            "hint": f"{len(zips)} zip(s) present; ATUS CSV parser not yet run "
                    f"(implement per data dictionary before flipping to OK)"}


def compile_literature() -> dict:
    lit = yaml.safe_load((ANCHORS_DIR / "literature_constants.yaml").read_text())
    return {"status": lit.get("status", "NEEDS_HUMAN_TRANSCRIPTION"),
            "source": "literature_constants.yaml"}


def main() -> int:
    envelope = {
        "_generated_by": "dynbelief.anchors.compile_envelope",
        "_note": "Deterministic compile of shipped anchor data. NEEDS_DATA sections "
                 "degrade their check; no numeric value is invented.",
        "config": CONFIG,
        "bddl_object_unions": compile_bddl(),
        "housekeep_placements": compile_housekeep(),
        "homer": compile_homer(),
        "atus_bands": compile_atus(),
        "literature_tier": compile_literature(),
    }
    ENVELOPE_PATH.write_text(
        "# AUTO-GENERATED by dynbelief.anchors.compile_envelope -- do not hand-edit\n"
        "# (edit CONFIG in compile_envelope.py or the mapping tables, then re-run).\n"
        "# Committed: small, reviewable, cited. Raw anchor data stays gitignored.\n"
        + yaml.safe_dump(envelope, sort_keys=False, width=100))
    # status summary
    def st(x):
        return x.get("status", "?") if isinstance(x, dict) else "?"
    print(f"[compile_envelope] wrote {ENVELOPE_PATH.relative_to(REPO_ROOT)}")
    print(f"  bddl_object_unions : {st(envelope['bddl_object_unions'])}")
    print(f"  housekeep_placements: {st(envelope['housekeep_placements'])}")
    print(f"  homer.jitter        : {st(envelope['homer']['jitter'])}")
    print(f"  homer.change_rates  : {st(envelope['homer']['change_rates'])}")
    print(f"  atus_bands          : {st(envelope['atus_bands'])}")
    print(f"  literature_tier     : {st(envelope['literature_tier'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
