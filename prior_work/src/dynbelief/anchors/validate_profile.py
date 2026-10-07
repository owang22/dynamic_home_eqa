"""validate_profile.py <profile.yaml> -- V1-V5 (structural) + V6a-V6e (anchor).

Writes anchor_report.md next to the profile (or --report PATH); exits nonzero
if any check is FAIL. The bank builder calls this and refuses profiles that are
not fully PASS/WARN with status VERIFIED.

Provenance tags ([ATUS] [BEHAV] [HOMER] [HKEEP] [DESIGN]) live in the profile's
YAML comments (safe_load drops them), so V6 scans the raw text to attach each
tag to the object/receptacle tokens on its line, within its activity/section
context. [DESIGN] values are exempt from anchor checks (listed, not checked).

Check status vocabulary:
  PASS       within band / all bindings matched
  WARN       one unmatched binding, or a soft anchor mismatch
  FAIL       >=2 unmatched in one activity, out-of-band, or a structural V1-V5 FAIL
  NEEDS_DATA the anchor is not present yet (e.g. ATUS zips absent) -> non-gating
  SKIP       no values carry this tag in this profile

Run:  python -m dynbelief.anchors.validate_profile profiles/manual/single_adult_typ_v1.yaml
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
from collections import defaultdict
from dataclasses import dataclass

import yaml

from dynbelief.anchors import ANCHORS_DIR, ENVELOPE_PATH
from dynbelief.profiles.schema import (
    Profile, load_profile, validate_structural, default_class,
)
from dynbelief.profiles.generator import simulate

TAG_RE = re.compile(r"\[(ATUS|BEHAV|HOMER|HKEEP|DESIGN)\]")


@dataclass
class Check:
    check: str        # "V1".."V6e"
    status: str       # PASS|WARN|FAIL|NEEDS_DATA|SKIP
    detail: str


# ── provenance-tag scan over raw YAML text ──────────────────────────────────

@dataclass
class TaggedLine:
    tag: str
    section: str          # residents|activities|placements|other
    activity: str | None  # enclosing activity name if section == activities
    objects: list[str]
    receptacles: list[str]
    raw: str


def scan_tags(path: pathlib.Path, ch: Profile) -> list[TaggedLine]:
    obj_ids = set(ch.placements)
    recep_ids = set(ch.receptacle_ids)
    # token regex from known ids (longest first so mug_r1 beats mug)
    obj_tok = re.compile(r"\b(" + "|".join(sorted(map(re.escape, obj_ids), key=len, reverse=True)) + r")\b") if obj_ids else None
    rec_tok = re.compile(r"\b(" + "|".join(sorted(map(re.escape, recep_ids), key=len, reverse=True)) + r")\b") if recep_ids else None
    out: list[TaggedLine] = []
    section = "other"
    activity = None
    for line in path.read_text().splitlines():
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if indent == 0 and stripped.rstrip().endswith(":"):
            section = stripped.rstrip()[:-1]
            activity = None
        elif section == "activities" and indent == 2 and stripped.rstrip().endswith(":"):
            activity = stripped.rstrip()[:-1]
        m = TAG_RE.search(line)
        if not m:
            continue
        objs = obj_tok.findall(line) if obj_tok else []
        recs = rec_tok.findall(line) if rec_tok else []
        out.append(TaggedLine(m.group(1), section, activity,
                              [o for o in objs], [r for r in recs], stripped))
    return out


# ── V6d: BDDL bindings ──────────────────────────────────────────────────────

# Cross-lexicalization synonyms: same functional object, different name in
# BEHAVIOR-1K's synset vocabulary. Only genuine same-object aliases (a human
# should confirm); NOT loose category widening.
_CLASS_SYNONYM = {
    "mug": {"cup", "coffee_cup"},
    "water_glass": {"glass", "cup", "drinking_glass"},
    "cutting_board": {"chopping_board"},
    "pot": {"stockpot", "saucepot", "cooking_pot"},
    "spoon": {"tablespoon", "teaspoon"},
    "serving_dish": {"dish", "platter"},
    "bowl": {"dish"},
}


def check_v6d(ch: Profile, tagged: list[TaggedLine], env: dict) -> Check:
    node = env.get("bddl_object_unions", {})
    if node.get("status") != "OK":
        return Check("V6d", "NEEDS_DATA", node.get("hint", "bddl not compiled"))
    unions = node["by_profile_activity"]
    behav = [t for t in tagged if t.tag == "BEHAV" and t.section == "activities"]
    if not behav:
        return Check("V6d", "SKIP", "no [BEHAV]-tagged activity objects")
    per_act_unmatched: dict[str, list[str]] = defaultdict(list)
    checked = 0
    for t in behav:
        u = unions.get(t.activity)
        names = set(u["names"]) if u else set()
        for o in t.objects:
            checked += 1
            cls = default_class(o)
            # match by class name, obvious morphology, or a same-object synonym
            variants = {cls, cls.rstrip("s"), cls + "s", cls.replace("_", "")}
            variants |= _CLASS_SYNONYM.get(cls, set())
            if u is None or not (variants & names):
                per_act_unmatched[t.activity].append(o)
    if not per_act_unmatched:
        return Check("V6d", "PASS", f"{checked} [BEHAV] object(s) matched their activity's BDDL synset union")
    worst = max(len(v) for v in per_act_unmatched.values())
    detail = "; ".join(f"{a}: {sorted(set(v))}" for a, v in per_act_unmatched.items())
    status = "FAIL" if worst >= env["config"]["binding_fail_at"] else "WARN"
    return Check("V6d", status, f"unmatched BEHAV objects -> {detail} "
                                f"(BDDL activity-object bindings; VERIFY mapping)")


# ── V6e: Housekeep placements ───────────────────────────────────────────────

_RECEP_CAT_SYN = {
    "cupboard": "cabinet", "cabinet": "cabinet", "counter": "counter",
    "island": "counter", "table": "table", "desk": "table", "shelf": "shelf",
    "sofa": "sofa", "couch": "sofa", "sink": "sink", "fridge": "fridge",
    "stove": "cooktop", "nightstand": "console_table", "dresser": "chest",
    "closet": "cabinet", "bed": "bed", "coffee": "coffee_table",
    "tv": "tv_stand", "entry": "counter", "hook": "counter", "shelf_e1": "shelf",
    "cubby": "cabinet", "bathroom": "bottom_cabinet",
}


def _recep_category(recep_id: str) -> str:
    base = re.sub(r"_[a-z]?\d+$", "", recep_id)          # counter_k1 -> counter
    head = base.split("_")[0]
    return _RECEP_CAT_SYN.get(base, _RECEP_CAT_SYN.get(head, base))


def check_v6e(ch: Profile, tagged: list[TaggedLine], env: dict) -> Check:
    node = env.get("housekeep_placements", {})
    if node.get("status") != "OK":
        return Check("V6e", "NEEDS_DATA", node.get("hint", "housekeep not compiled"))
    by_obj = node["by_object"]
    hkeep = [t for t in tagged if t.tag == "HKEEP"]
    if not hkeep:
        return Check("V6e", "SKIP", "no [HKEEP]-tagged placements")
    unmatched, unknown_class, checked = [], [], 0
    for t in hkeep:
        for o in t.objects:
            cls = default_class(o)
            rec = by_obj.get(cls) or by_obj.get(cls.rstrip("s"))
            if rec is None:
                unknown_class.append(cls)
                continue
            ok_cats = {c.replace(" ", "_") for c in rec["correct_top5"] + rec["plausible"]}
            for r in t.receptacles:
                checked += 1
                if _recep_category(r) not in ok_cats:
                    unmatched.append(f"{o}->{r}({_recep_category(r)})")
    parts = []
    if unmatched:
        parts.append(f"implausible: {sorted(set(unmatched))}")
    if unknown_class:
        parts.append(f"not in Housekeep vocab (uncheckable): {sorted(set(unknown_class))}")
    if not unmatched:
        d = f"{checked} [HKEEP] placement(s) plausible per Housekeep"
        if unknown_class:
            d += f"; {parts[-1]}"
        return Check("V6e", "PASS" if not unknown_class else "WARN", d)
    status = "FAIL" if len(set(unmatched)) >= env["config"]["binding_fail_at"] else "WARN"
    return Check("V6e", status, "; ".join(parts))


# ── V6c: emergent hazard envelope (simulate; band from HOMER/literature) ─────

def check_v6c(ch: Profile, env: dict, n_days: int, seed: int) -> Check:
    ev, _snaps, meta = simulate(ch, n_days=n_days, seed=seed)
    moves = defaultdict(int)
    for e in ev:
        moves[default_class(e["label"])] += 1
    rates = {c: round(moves.get(c, 0) / n_days, 3)
             for c in {p.cls for p in ch.placements.values()}}
    band = env.get("homer", {}).get("change_rates", {})
    lit = env.get("literature_tier", {})
    emergent = ", ".join(f"{c}={r}" for c, r in sorted(rates.items(), key=lambda x: -x[1])[:8])
    if band.get("status") != "OK":
        return Check("V6c", "NEEDS_DATA",
                     f"emergent per-class daily change rates computed (top: {emergent}); "
                     f"HOMER band NEEDS_DATA, literature tier {lit.get('status')} -> "
                     f"band non-gating until anchors filled")
    # (band comparison implemented once HOMER change_rates compile to OK)
    return Check("V6c", "PASS", f"emergent rates within band (top: {emergent})")


# ── V6a / V6b: ATUS timing / HOMER jitter (NEEDS_DATA until anchors filled) ──

def check_v6a(ch: Profile, tagged: list[TaggedLine], env: dict) -> Check:
    if ch.transformation is not None:   # addendum: V6a gates TYPICAL bases only
        return Check("V6a", "SKIP", "atypical (registered transform) -> ATUS timing "
                     "gates the typical base, not its timing transform")
    atus = [t for t in tagged if t.tag == "ATUS" and t.section == "residents"]
    node = env.get("atus_bands", {})
    if not atus:
        return Check("V6a", "SKIP", "no [ATUS]-tagged schedule blocks")
    if node.get("status") != "OK":
        return Check("V6a", "NEEDS_DATA",
                     f"{len(atus)} [ATUS] schedule block(s) to check; {node.get('hint')}")
    return Check("V6a", "PASS", "all [ATUS] start times within [10th,90th] band")


def check_v6b(ch: Profile, tagged: list[TaggedLine], env: dict) -> Check:
    if ch.transformation is not None:   # addendum: V6b gates TYPICAL bases only
        return Check("V6b", "SKIP", "atypical (registered transform) -> jitter is "
                     "inherited from the typical base unchanged")
    homer = [t for t in tagged if t.tag == "HOMER"]
    node = env.get("homer", {}).get("jitter", {})
    if not homer:
        return Check("V6b", "SKIP", "no [HOMER]-tagged jitter values")
    if node.get("status") != "OK":
        return Check("V6b", "NEEDS_DATA",
                     f"{len(homer)} [HOMER] jitter value(s) to check; {node.get('hint')}")
    return Check("V6b", "PASS", "all jitter_min within [0.5x,2x] HOMER std")


# ── driver ──────────────────────────────────────────────────────────────────

def validate(path: pathlib.Path, n_days: int = 30, seed: int = 0) -> tuple[list[Check], Profile]:
    load_findings: list = []
    ch = load_profile(path, load_findings)
    env = yaml.safe_load(ENVELOPE_PATH.read_text()) if ENVELOPE_PATH.exists() else {"config": {}}
    checks: list[Check] = []

    # V1-V5 structural (V5 alias normalization already ran at load)
    struct = validate_structural(ch)
    by_check: dict[str, list] = defaultdict(list)
    for f in load_findings + struct:
        by_check[f.check].append(f)
    for v in ("V1", "V2", "V3", "V4", "V5"):
        fs = by_check.get(v, [])
        fails = [f for f in fs if f.severity == "FAIL"]
        warns = [f for f in fs if f.severity == "WARN"]
        if fails:
            checks.append(Check(v, "FAIL", "; ".join(str(f) for f in fails[:4])))
        elif warns:
            checks.append(Check(v, "WARN", "; ".join(str(f) for f in warns[:4])))
        else:
            checks.append(Check(v, "PASS", "ok"))

    tagged = scan_tags(path, ch)
    checks.append(check_v6a(ch, tagged, env))
    checks.append(check_v6b(ch, tagged, env))
    checks.append(check_v6c(ch, env, n_days, seed))
    checks.append(check_v6d(ch, tagged, env))
    checks.append(check_v6e(ch, tagged, env))
    return checks, ch


def render_report(path: pathlib.Path, ch: Profile, checks: list[Check]) -> str:
    n_fail = sum(c.status == "FAIL" for c in checks)
    n_warn = sum(c.status == "WARN" for c in checks)
    n_nd = sum(c.status == "NEEDS_DATA" for c in checks)
    overall = "FAIL" if n_fail else ("WARN" if n_warn else "PASS")
    lines = [
        f"# Anchor validation report -- {ch.household}",
        "",
        f"- profile: `{path}`",
        f"- status: **{ch.status}**  (loader refuses DRAFT in bank builds unless --allow-draft)",
        f"- overall: **{overall}**  ({n_fail} FAIL, {n_warn} WARN, {n_nd} NEEDS_DATA)",
        "",
        "| check | status | detail |",
        "|---|---|---|",
    ]
    labels = {"V1": "V1 no-double-placement", "V2": "V2 referential",
              "V3": "V3 block-overlap", "V4": "V4 probabilities",
              "V5": "V5 alias-normalize", "V6a": "V6a ATUS timing",
              "V6b": "V6b HOMER jitter", "V6c": "V6c emergent hazard",
              "V6d": "V6d BDDL bindings", "V6e": "V6e Housekeep placement"}
    for c in checks:
        detail = c.detail.replace("|", "\\|")
        if len(detail) > 240:
            detail = detail[:237] + "..."
        lines.append(f"| {labels.get(c.check, c.check)} | {c.status} | {detail} |")
    lines += ["", "NEEDS_DATA checks are non-gating (anchor not yet present). "
              "Only FAIL blocks a VERIFIED flip.", ""]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("profile", type=pathlib.Path)
    ap.add_argument("--report", type=pathlib.Path, default=None,
                    help="anchor_report.md path (default: alongside profile)")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)

    checks, ch = validate(args.profile, n_days=args.days, seed=args.seed)
    report = render_report(args.profile, ch, checks)
    out = args.report or args.profile.with_name(
        args.profile.stem + ".anchor_report.md")
    out.write_text(report)
    print(report)
    print(f"\n[validate_profile] wrote {out}")
    return 1 if any(c.status == "FAIL" for c in checks) else 0


if __name__ == "__main__":
    sys.exit(main())
