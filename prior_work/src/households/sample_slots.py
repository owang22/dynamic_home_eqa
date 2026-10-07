#!/usr/bin/env python3
"""Enumerate cells (archetype x optional overlay), 3 variants each ->
profiles/households/control.yaml + slot_summary.md.

The cell list is grid.ARCHETYPES x grid.OVERLAYS — whole-unit
households, no attribute mixing, no population-proportion matching:
every cell gets equal weight (3 variants) regardless of how common it
is; survey data only makes each household's own timings believable.

A variant keeps the archetype and schedule fixed and re-draws: the
timing tuples (fresh ATUS respondent-days for the matching group),
point ages inside each resident's band, and the generation seed. The
occupation CATEGORY is part of the cell; the LLM later picks the
specific job title inside it.

Deterministic under --seed (byte-identical reruns). Consistency is
grid.violations(); tags and the >=3-with-only-that-quirk rule are
checked in code and reported in the summary.
"""
from __future__ import annotations

import argparse
import collections
import datetime
import json
import pathlib
import random

import yaml

from . import grid

ATUS_JSON = grid.DATA_DIR / "grounding" / "atus_group_stats.json"
VARIANTS_PER_CELL = 3


class AtusSampler:
    """Whole-tuple draws from atus_group_stats.json with age-band and
    daytype fallbacks, every fallback logged.

    Each draw is seeded INDEPENDENTLY from its own key (household,
    resident, field), never from a shared sequential stream: adding or
    tightening a rejection filter must only change the draws it rejects,
    not cascade new tuples onto every household after it — the built
    households' declared ground truth has to survive sampler fixes."""

    def __init__(self, path: pathlib.Path, seed: int) -> None:
        data = json.loads(path.read_text())
        self.groups = data["groups"]
        self.seed = seed
        self.fallbacks: list[str] = []

    def _find(self, emp: str, sched: str, band: str, daytype: str):
        bands = [band] + [b for _l, _h, b in grid.AGE_BANDS if b != band]
        for e in (emp, "full_time"):
            for b in bands:
                for d in (daytype, "weekday", "weekend"):
                    key = f"{e}|{sched}|{b}|{d}"
                    if key in self.groups:
                        if key != f"{emp}|{sched}|{band}|{daytype}":
                            self.fallbacks.append(
                                f"{emp}|{sched}|{band}|{daytype} -> {key}")
                        return key
        return None

    def draw(self, draw_key: str, emp: str, sched: str, band: str,
             daytype: str, workday: bool = False, typical: bool = False):
        """A requirement baked into a prompt should be a typical day,
        not the group's oddest diary. workday=True keeps days with at
        least 4h work and at most 10h sleep; for daytime schedules a
        contiguous 4-11h block with an observable wake; for night and
        evening schedules a shift that STARTS in the evening (16:00-
        02:00 for night, 14:00-21:00 for evening) — ATUS diaries run
        04:00-04:00, so a night worker's window can open MID-SHIFT and
        leave only the shift's tail (a "night shift" starting 04:00),
        which is a truncation artifact, not a schedule. typical=True
        (non-working days) keeps 5-11h of sleep and an observable wake.
        """
        key = self._find(emp, sched, band, daytype)
        if key is None:
            return None
        days = self.groups[key]["days"]
        rng = random.Random(f"{self.seed}:{draw_key}:{key}")
        for _ in range(60):
            day = dict(rng.choice(days))
            if workday:
                ok = (day.get("work_min", 0) >= 240
                      and (day.get("sleep_min") or 0) <= 600)
                ws = day.get("work_start")
                if ok and sched == "daytime":
                    we = day.get("work_end")
                    ok = (day.get("wake") is not None
                          and ws is not None and we is not None
                          and ws < we and 240 <= we - ws <= 660)
                elif ok and sched == "night":
                    ok = ws is not None and (ws >= 16 * 60 or ws <= 120)
                elif ok and sched == "evening":
                    ok = ws is not None and 14 * 60 <= ws <= 21 * 60
            elif typical:
                ok = (300 <= (day.get("sleep_min") or 0) <= 660
                      and day.get("wake") is not None)
            else:
                ok = True
            if ok:
                break
        day["atus_group"] = key
        if workday and sched == "night":
            # the 04:00 window boundary splits a night worker's recovery
            # sleep, so this window's wake and sleep total are
            # systematically biased — they must not become constraints.
            # The story prompt still requires daily sleep; only the
            # shift block is trustworthy here.
            day["wake"] = None
            day["sleep_min"] = None
        return day


def _timing_for(res: dict, atus: AtusSampler, draw_key: str
                ) -> dict | None:
    if res["role"] == "child":
        return None
    emp = {"full_time": "full_time", "part_time": "part_time",
           "retired": "retired", "student": "nonworking_adult",
           "nonworking_adult": "nonworking_adult"}[res["employment"]]
    band = grid.age_band(res["age"])
    sched = res["schedule_type"]
    timing: dict = {}
    if sched == "none":
        timing["typical_day"] = atus.draw(
            f"{draw_key}:typical", emp, "non_workday", band, "weekday",
            typical=True)
    elif sched == "rotating_shift":
        for phase in ("daytime", "evening", "night"):
            timing[f"workday_{phase}"] = atus.draw(
                f"{draw_key}:{phase}", emp, phase, band, "weekday",
                workday=True)
    else:
        for component in grid.ATUS_SCHEDULE_FOR[sched]:
            day = atus.draw(f"{draw_key}:workday", emp, component, band,
                            "weekday", workday=True)
            if day:
                timing["workday"] = day
                break
    timing["dayoff"] = atus.draw(f"{draw_key}:dayoff", emp,
                                 "non_workday", band, "weekend",
                                 typical=True)
    return timing


SCHOOL_BLOCK = {"start": 8 * 60, "end": 15 * 60,
                "note": "NCES-conventional school day; under ATUS floor"}


def build_variant(cell: tuple, variant: int, rng: random.Random,
                  atus: AtusSampler) -> dict:
    archetype, overlay = cell
    spec = [dict(s) for s in grid.ARCHETYPES[archetype]]
    if overlay:
        grid.apply_overlay(spec, overlay,
                           grid.OVERLAYS[overlay][archetype])
    residents = []
    for s in spec:
        r = {"role": s["role"], "age": rng.randint(*s["age_range"]),
             "employment": s["employment"],
             "schedule_type": s["schedule_type"],
             "occupation_category": s["occupation_category"],
             "wfh": s["wfh"]}
        if s["role"] == "child":
            r["school_block"] = (dict(SCHOOL_BLOCK)
                                 if s["employment"] == "school_child"
                                 else None)
        r["timing"] = _timing_for(
            r, atus, f"{cell_name(archetype, overlay)}:v{variant}"
                     f":r{len(residents) + 1}")
        residents.append(r)
    rec = {
        "archetype": archetype, "overlay": overlay, "variant": variant,
        "residents_detail": residents,
        "residents": len(residents),
        "bedrooms": grid.BEDROOMS[archetype],
        "generation_seed": rng.randrange(2 ** 31),
    }
    rec["tags"] = grid.tags_for(rec)
    probs = grid.violations(rec)
    if probs:
        raise RuntimeError(f"built invalid record {cell} v{variant}: "
                           f"{probs}")
    return rec


def cell_name(archetype: str, overlay: str | None) -> str:
    return f"{archetype}__{overlay}" if overlay else archetype


def cells() -> list[tuple]:
    out = [(a, None) for a in grid.ARCHETYPES]
    for overlay, targets in grid.OVERLAYS.items():
        out += [(a, overlay) for a in targets]
    return out



def _incoherent_night_tuple(rec: dict) -> list[str]:
    """Which residents of this record carry a night-shift constraint the
    04:00 diary boundary corrupted: a 'night shift' starting in the
    daytime band (the window opened mid-shift and kept only the tail),
    or a sub-5h declared sleep next to a wake (recovery sleep split by
    the boundary). These constraints are impossible or wrong; a
    household built against them must be rebuilt."""
    bad = []
    for i, r in enumerate(rec.get("residents_detail") or [], 1):
        phases = []
        t = r.get("timing") or {}
        if r.get("schedule_type") == "fixed_night_shift":
            phases = [t.get("workday")]
        elif r.get("schedule_type") == "rotating_shift":
            phases = [t.get("workday_night")]
        for wd in phases:
            if not wd:
                continue
            ws = wd.get("work_start")
            if ws is not None and 120 < ws < 960:
                bad.append(f"resident_{i}: night shift starting "
                           f"{ws // 60:02d}:{ws % 60:02d} (truncation "
                           f"artifact)")
            elif (wd.get("sleep_min") is not None
                    and wd["sleep_min"] < 300 and wd.get("wake")):
                bad.append(f"resident_{i}: declared "
                           f"{wd['sleep_min']}min sleep with a wake "
                           f"(boundary-split recovery sleep)")
    return bad


def carry_forward_built(records: list[dict], out_dir: pathlib.Path
                        ) -> tuple[list[str], list[str]]:
    """Built households keep their as-built record VERBATIM: their
    control entry is the ground truth their timelines were generated
    and validated against, and a sampler improvement must not rewrite
    history under them. The one exception: a built record whose
    constraints _incoherent_night_tuple() rejects is replaced by the
    freshly sampled (repaired) one and must be REBUILT."""
    prev_path = out_dir / "control.yaml"
    generated_root = out_dir / "generated"
    if not prev_path.exists():
        return [], []
    prev = {r["household_id"]: r
            for r in yaml.safe_load(prev_path.read_text())["households"]}
    built = ({d.name for m in generated_root.iterdir()
              for d in m.glob("hh_*")
              if (d / "program.yaml").exists()}
             if generated_root.is_dir() else set())
    carried, invalidated = [], []
    order = {"pilot": 0, "hard5": 1, "wave1": 2, "wave2": 3}
    recs = sorted(records, key=lambda r: (order[r["wave"]],
                                          r["archetype"],
                                          r["overlay"] or "",
                                          r["variant"]))
    for i, new_rec in enumerate(recs, 1):
        hid = f"hh_{i:03d}"
        old_rec = prev.get(hid)
        if old_rec is None or hid not in built:
            continue
        reasons = _incoherent_night_tuple(old_rec)
        if reasons:
            invalidated.append(f"{hid}: " + "; ".join(reasons))
            continue
        idx = records.index(new_rec)
        keep = dict(old_rec)
        keep["wave"] = new_rec["wave"]      # waves stay sampler-owned
        records[idx] = keep
        carried.append(hid)
    return carried, invalidated

# ---------------------------------------------------------------- waves --

def assign_waves(records: list[dict]) -> None:
    """pilot 1 -> hard5 5 -> wave1 (to 20 cumulative) -> wave2. The
    pilot is the plan's night-shift working couple. hard5 covers the
    1-resident home, the 5-resident home, rotating shift, gig, and
    opposite schedules — the schedule extremes, since manipulated
    households are out of scope."""
    def pick(archetype, overlay, variant=1):
        return next(r for r in records
                    if r["archetype"] == archetype
                    and r["overlay"] == overlay
                    and r["variant"] == variant)

    for r in records:
        r["wave"] = "wave2"
    # pilot: one working adult, normal daytime shift — the easiest
    # household to read and check by hand
    pick("working_professional_solo", None)["wave"] = "pilot"
    for a, o in (("multigenerational_family", None),
                 ("single_parent_teens", "rotating_shift"),
                 ("working_couple_no_children", "night_shift"),
                 ("working_professional_solo", "irregular_gig"),
                 ("working_couple_no_children", "opposite_schedules")):
        pick(a, o)["wave"] = "hard5"
    # wave1: variant 1 of every remaining cell (12), plus variant 2 of
    # the pilot cell and of the plain working couple — two same-cell
    # pairs land early so the variant-similarity check has data before
    # wave 2
    for r in records:
        if r["variant"] == 1 and r["wave"] == "wave2":
            r["wave"] = "wave1"
    pick("working_professional_solo", None, 2)["wave"] = "wave1"
    pick("working_couple_no_children", None, 2)["wave"] = "wave1"


# --------------------------------------------------------------- checks --

def only_quirk_counts(records: list[dict]) -> dict:
    """tag -> households where that tag is the ONLY unusual thing.
    For unusual tags: no other unusual tag present. For ordinary tags:
    no unusual tag present at all."""
    out: dict = {}
    all_tags = sorted({t for r in records for t in r["tags"]})
    for tag in all_tags:
        n = 0
        for r in records:
            if tag not in r["tags"]:
                continue
            unusual = set(r["tags"]) & set(grid.UNUSUAL_TAGS)
            if tag in grid.UNUSUAL_TAGS:
                if unusual == {tag}:
                    n += 1
            elif not unusual:
                n += 1
        out[tag] = n
    return out


# -------------------------------------------------------------- output --

OBJECT_VOCABULARY = [
    "mug", "bowl", "plate", "laptop", "phone", "tablet", "keys", "wallet",
    "book", "water_bottle", "remote", "charger", "backpack", "jacket",
    "headphones", "glasses", "notebook", "pen", "medication_bottle",
    "toy", "blanket", "towel", "gaming_controller", "dog_leash",
    "lunchbox", "umbrella", "laundry_basket", "vacuum_cleaner", "pot",
    "pan", "suitcase", "hairbrush", "makeup_kit", "watering_can",
    "yoga_mat",
]   # owned copy of the revamp_v2 vocabulary (35 objects), unchanged

OVERLAY_REASONS = {
    ("working_professional_solo", "night_shift"):
        "the merged old night_shift_worker_solo; cleanest solo night "
        "signal",
    ("working_couple_no_children", "night_shift"):
        "one partner on nights, desync without children",
    ("working_couple_no_children", "opposite_schedules"):
        "the classic two-earner deliberate desync",
    ("single_parent_teens", "rotating_shift"):
        "rotating healthcare parent with self-managing teens: high "
        "routine variance plus dependents",
    ("working_professional_solo", "irregular_gig"):
        "solo gig worker: the most irregular single-resident signal",
    ("college_roommates", "irregular_gig"):
        "students with gig shifts: multi-resident irregularity",
}


def _wd(rec):
    t0 = next((r["timing"] for r in rec["residents_detail"]
               if r.get("timing")), {}) or {}
    return (t0.get("workday") or t0.get("typical_day")
            or t0.get("workday_daytime") or {})


def summary_md(records: list[dict], fallbacks: list[str],
               seed: int) -> str:
    L = [f"# Slot summary — {len(records)} households = "
         f"{len(cells())} cells x {VARIANTS_PER_CELL} variants "
         f"(seed {seed}, {datetime.date.today().isoformat()})", ""]
    L += ["## Merge notes", ""] + [f"- {m}" for m in grid.MERGE_NOTES]
    L += ["", "## Proposed archetype additions (from the structural "
          "audit of the storyfirst 10)", "",
          "- single_senior_solo: the base list has no single-senior "
          "home.",
          "- multigenerational_family: the base list has no "
          "three-generation home.",
          "", "## Overlay cells and why", ""]
    for (a, o), reason in OVERLAY_REASONS.items():
        L.append(f"- {cell_name(a, o)}: {reason}")
    L += ["", "## Ruled-out archetype x overlay pairs", ""]
    for pair, reason in grid.RULED_OUT:
        L.append(f"- {pair}: {reason}")

    L += ["", "## Households", "",
          "| id | wave | cell | v | res | ages | r1 wake | r1 work | "
          "gen seed |", "|---|---|---|---|---|---|---|---|---|"]
    for r in records:
        wd = _wd(r)
        ages = ",".join(str(x["age"]) for x in r["residents_detail"])
        L.append(
            f"| {r['household_id']} | {r['wave']} "
            f"| {cell_name(r['archetype'], r['overlay'])} "
            f"| {r['variant']} | {r['residents']} | {ages} "
            f"| {wd.get('wake')} "
            f"| {wd.get('work_start')}-{wd.get('work_end')} "
            f"| {r['generation_seed']} |")

    L += ["", "## What differs inside a cell", "",
          "Across a cell's 3 variants only these change: the timing "
          "tuples (fresh ATUS draws), point ages within each band, the "
          "generation seed, and (at generation time) names and the "
          "specific job title inside the fixed occupation category.", ""]

    counts = only_quirk_counts(records)
    L += ["## Group tags: households where the tag is the only unusual "
          "thing", ""]
    for tag, n in counts.items():
        flag = "  ** BELOW 3 **" if n < 3 else ""
        L.append(f"- {tag}: {n}{flag}")

    all_tags = sorted({t for r in records for t in r["tags"]})
    L += ["", "## Tag overlap (households carrying both)", "",
          "| | " + " | ".join(all_tags) + " |",
          "|" + "---|" * (len(all_tags) + 1)]
    for t1 in all_tags:
        row = [t1]
        for t2 in all_tags:
            n = sum(1 for r in records
                    if t1 in r["tags"] and t2 in r["tags"])
            row.append(str(n) if t2 != t1 else f"({n})")
        L.append("| " + " | ".join(row) + " |")

    if fallbacks:
        L += ["", "## ATUS group fallbacks (thin groups borrowed a "
              "neighbor)", ""] + [
            f"- {f}" for f in sorted(set(fallbacks))]
    return "\n".join(L) + "\n"


def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--days", type=int, default=28)
    ap.add_argument("--out", type=pathlib.Path, default=grid.DATA_DIR)
    args = ap.parse_args()

    rng = random.Random(f"households-v3:{args.seed}")
    atus = AtusSampler(ATUS_JSON, args.seed)
    records = [build_variant(cell, v, rng, atus)
               for cell in cells()
               for v in range(1, VARIANTS_PER_CELL + 1)]
    assign_waves(records)
    carried, invalidated = carry_forward_built(records, args.out)
    order = {"pilot": 0, "hard5": 1, "wave1": 2, "wave2": 3}
    records.sort(key=lambda r: (order[r["wave"]], r["archetype"],
                                r["overlay"] or "", r["variant"]))
    for i, r in enumerate(records, 1):
        r["household_id"] = f"hh_{i:03d}"
        r["household_type"] = cell_name(r["archetype"], r["overlay"])

    counts = only_quirk_counts(records)
    thin = {t: n for t, n in counts.items() if n < 3}
    control = {
        "version": "households-v3", "sampler_seed": args.seed,
        "days": args.days, "day0": "Monday",
        "atus_stats": "grounding/atus_group_stats.json",
        "object_vocabulary": OBJECT_VOCABULARY,
        "households": records,
    }
    header = (
        "# GENERATED by python -m households.sample_slots --seed "
        f"{args.seed} on {datetime.date.today().isoformat()} — edit the\n"
        "# sampler or the grid, not this file.\n"
        "# Archetype x overlay cells, 3 variants each. No population\n"
        "# matching: every cell gets equal weight; ATUS tuples only\n"
        "# make each household's own timings believable. Timing values\n"
        "# are minutes from midnight; wake can be null for night\n"
        "# workers (asleep-at-4am is mid-shift in their diaries).\n")
    (args.out / "control.yaml").write_text(
        header + yaml.safe_dump(control, sort_keys=False, width=78,
                                allow_unicode=True))
    (args.out / "slot_summary.md").write_text(
        summary_md(records, atus.fallbacks, args.seed))
    print(f"{len(records)} households ({len(cells())} cells x "
          f"{VARIANTS_PER_CELL}) -> {args.out}/control.yaml")
    if carried:
        print(f"  carried forward as-built: {len(carried)}")
    for line in invalidated:
        print(f"  INVALIDATED (rebuild required): {line}")
    for t, n in counts.items():
        mark = "  ** BELOW 3 **" if n < 3 else ""
        print(f"  only-quirk {t}: {n}{mark}")
    if thin:
        print("NOTE: tags below 3 exist — see summary")


if __name__ == "__main__":
    _main()
