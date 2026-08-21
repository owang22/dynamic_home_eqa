#!/usr/bin/env python3
"""Realism panel — REPORTING ONLY, never a build gate: the event-timing
sporadicity statistics from casas/README.md ("Where the sporadicity comes
from") for each revamp_v2 timeline, against the casas/aruba comparator
(casas/aruba/timeline_21d).

What that comparator is, exactly (casas/README.md): its ACTIVITY stream is
real CASAS free-living data, but its OBJECT layer — the inventory and the
activity->object binding — is invented, and the per-bout probabilities that
set move VOLUME were "tuned by feel and worth calibrating". So it is a
reference for TIMING SCATTER only: the same README's deterministic-rules
experiment shows hour-entropy/Fano barely move when the binding's coin
flips are removed (0.74/1.92 -> 0.76/2.03), i.e. that character comes from
the real intervals. Its VOLUME columns (n_events, events_per_day,
moves_per_object_day) and its object-identity columns (top2, twin_pairs,
never_move) are properties of the invented layer and are NOT ground truth
— read them as one authored household among others, never as a target.

Per timeline, on a NON-CARRY basis (departure-carry pickups/putdowns are
mechanism bookkeeping, excluded from the sporadicity numbers; `fano_all`
keeps the all-events figure and `carry_frac` the carry share so the basis
is visible): events/day, moves/object/day, hour-of-day entropy of move
times (normalized by log 24), Fano factor (var/mean) of daily move counts,
`top2` (share of events owed to the two most-moved objects) and
`dead_days` (days with < 3 non-carry events while a resident was home
awake >= 6 h). Acceptance expectations (checked by the caller, reported
here): non-carry daily Fano in [1, 6] for >= 8 of 10 households,
hour-entropy >= 0.75, top2 <= 0.40 for the story_calendar arm.

Usage:
  python src/revamp_v2/realism_panel.py profiles/revamp_v2/<slug>/hh*/timeline_seed0 \
      [--reference casas/aruba/timeline_21d] [--out report.md]
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import pathlib


def timeline_stats(timeline: pathlib.Path) -> dict:
    events = [json.loads(line) for line in
              (timeline / "events.jsonl").read_text().splitlines()]
    with open(timeline / "hourly.csv") as f:
        reader = csv.reader(f)
        header = next(reader)
        columns = {name: [] for name in header}
        for row in reader:
            for name, v in zip(header, row):
                columns[name].append(v)
    objects = [c for c in header if c not in ("t", "stamp")]
    n_objects = len(objects)
    # Sporadicity statistics run on NON-CARRY events: the departure-carry
    # mechanism is bookkeeping (the same items ride along on every trip),
    # and counting it let carry storms dominate the burstiness numbers.
    # `fano_all` keeps the old all-events figure and `carry_frac` the carry
    # share, so the basis change is visible, never silent. Events without
    # a `kind` (older timelines, the real reference, the freeform/story
    # movement arms) are all non-carry by construction.
    non_carry = [e for e in events
                 if e.get("kind") not in ("carry_pickup", "carry_putdown")]
    # Trajectory duplication: how much of the household moves in lockstep
    # (or sits forever). phone_2 and wallet_2 sharing one timeline for 21
    # days is the fingerprint of copy-pasted rules; a home of statues is
    # the fingerprint of rules that never fire. Both are invisible in the
    # count/entropy stats, which is why they are counted here.
    traj = {o: tuple(columns[o]) for o in objects}
    seen: dict = {}
    dup_pairs = 0
    for o in objects:
        dup_pairs += len(seen.setdefault(traj[o], []))
        seen[traj[o]].append(o)
    never = sum(1 for o in objects if len(set(traj[o])) == 1)
    meta = json.loads((timeline / "meta.json").read_text())
    days = int(meta["days"])

    def _per_day_fano(evts):
        per_day = [0] * days
        for e in evts:
            if e["t"] < days * 1440:
                per_day[e["t"] // 1440] += 1
        mean = sum(per_day) / days
        var = sum((c - mean) ** 2 for c in per_day) / days
        return per_day, (var / mean if mean else float("nan"))

    per_day, fano = _per_day_fano(non_carry)
    _, fano_all = _per_day_fano(events)
    per_hour = [0] * 24
    for e in non_carry:
        if e["t"] < days * 1440:
            per_hour[(e["t"] // 60) % 24] += 1
    n = sum(per_hour)
    entropy = 0.0
    if n:
        for c in per_hour:
            if c:
                p = c / n
                entropy -= p * math.log(p)
        entropy /= math.log(24)
    mean = sum(per_day) / days
    # Protagonist bias: the share of (non-carry) events owed to the two
    # most-moved objects. A pair of objects carrying the household's whole
    # story is the LLM-movement failure the rules engine should not have.
    by_obj: dict = {}
    for e in non_carry:
        by_obj[e["object"]] = by_obj.get(e["object"], 0) + 1
    top2 = (sum(sorted(by_obj.values(), reverse=True)[:2]) / len(non_carry)
            if non_carry else 0.0)
    # Dead days: a day with < 3 non-carry events while somebody was home
    # and awake >= 6 h — the at-home rule-coverage gap made visible.
    dead = 0
    res_path = timeline / "residents.jsonl"
    if res_path.exists() and res_path.stat().st_size:
        rows = [json.loads(line) for line in
                res_path.read_text().splitlines()]
        for d in range(days):
            lo, hi = d * 1440, (d + 1) * 1440
            home_awake: dict = {}
            for r in rows:
                if (r.get("at") == "ELSEWHERE"
                        or any(s in r["activity"] for s in ("sleep", "nap"))):
                    continue
                span = min(r["t1"], hi) - max(r["t0"], lo)
                if span > 0:
                    home_awake[r["resident"]] = \
                        home_awake.get(r["resident"], 0) + span
            if any(v >= 6 * 60 for v in home_awake.values()) \
                    and per_day[d] < 3:
                dead += 1
    n_fallback = int(meta.get("n_fallback_days", meta.get("n_failed_days", 0))
                     or 0)
    return {
        "timeline": str(timeline), "household": meta.get("household", "?"),
        "n_events": len(non_carry), "days": days,
        "twin_pairs": dup_pairs,
        "never_move": f"{never}/{n_objects}",
        "events_per_day": round(mean, 2),
        "moves_per_object_day": round(len(non_carry) / n_objects / days, 2),
        "hour_entropy": round(entropy, 3),
        "daily_fano": round(fano, 2),
        "fano_all": round(fano_all, 2),
        "carry_frac": round(1 - len(non_carry) / len(events), 3) if events
                      else 0.0,
        "top2": round(top2, 3),
        "dead_days": dead,
        "fallback_days": n_fallback,
        "not_story_driven": bool(meta.get("not_story_driven")),
    }


def render(rows: list[dict], reference: dict | None) -> str:
    cols = ["household", "n_events", "events_per_day",
            "moves_per_object_day", "hour_entropy", "daily_fano",
            "fano_all", "carry_frac", "top2", "dead_days",
            "twin_pairs", "never_move"]
    # Fallback days only exist for the story arms; the column appears only
    # when some row carries one, so the rule_based table stays compact.
    if any(r.get("fallback_days") for r in rows):
        cols = cols + ["fallback_days"]
    lines = ["| " + " | ".join(cols) + " |",
             "|" + "---|" * len(cols)]

    def _cell(r, c):
        v = r.get(c, "")
        if c == "household" and r.get("not_story_driven"):
            return f"{v} (NOT story-driven)"
        return str(v)

    for r in rows:
        lines.append("| " + " | ".join(_cell(r, c) for c in cols) + " |")
    if reference:
        reference = dict(reference,
                         household="casas_aruba (real ADLs, invented objects)")
        lines.append("| " + " | ".join(_cell(reference, c) for c in cols)
                     + " |")
    n_fano = sum(1 for r in rows if 1.0 <= r["daily_fano"] <= 6.0)
    n_ent = sum(1 for r in rows if r["hour_entropy"] >= 0.75)
    lines.append("")
    lines.append(f"Fano in [1, 6]: {n_fano}/{len(rows)} households "
                 f"(expect >= 8/10); hour-entropy >= 0.75: "
                 f"{n_ent}/{len(rows)}.")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("timelines", nargs="+", type=pathlib.Path)
    ap.add_argument("--reference", type=pathlib.Path,
                    default=pathlib.Path(__file__).resolve().parent.parent
                    .parent / "casas" / "aruba" / "timeline_21d")
    ap.add_argument("--out", type=pathlib.Path, default=None)
    args = ap.parse_args()
    rows = [timeline_stats(t) for t in args.timelines]
    ref = timeline_stats(args.reference) if args.reference.exists() else None
    text = render(rows, ref)
    print(text)
    if args.out:
        args.out.write_text("# revamp_v2 realism panel\n\n" + text + "\n")
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
