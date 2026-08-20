#!/usr/bin/env python3
"""Realism panel — REPORTING ONLY, never a build gate: the event-timing
sporadicity statistics from casas/README.md ("Where the sporadicity comes
from") for each revamp_v2 timeline, against the real-ADL reference
(casas/aruba/timeline_21d).

Per timeline: events/day, moves/object/day, hour-of-day entropy of move
times (normalized by log 24), Fano factor (var/mean) of daily move counts.
Acceptance expectations (checked by the caller, reported here): daily-count
Fano in [1, 6] for >= 8 of 10 households, hour-entropy >= 0.75.

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
    times = [e["t"] for e in events]
    per_day = [0] * days
    per_hour = [0] * 24
    for t in times:
        if t < days * 1440:
            per_day[t // 1440] += 1
            per_hour[(t // 60) % 24] += 1
    n = sum(per_hour)
    entropy = 0.0
    if n:
        for c in per_hour:
            if c:
                p = c / n
                entropy -= p * math.log(p)
        entropy /= math.log(24)
    mean = sum(per_day) / days
    var = sum((c - mean) ** 2 for c in per_day) / days
    fano = var / mean if mean else float("nan")
    return {
        "timeline": str(timeline), "household": meta.get("household", "?"),
        "n_events": len(events), "days": days,
        "twin_pairs": dup_pairs,
        "never_move": f"{never}/{n_objects}",
        "events_per_day": round(mean, 2),
        "moves_per_object_day": round(len(events) / n_objects / days, 2),
        "hour_entropy": round(entropy, 3),
        "daily_fano": round(fano, 2),
    }


def render(rows: list[dict], reference: dict | None) -> str:
    cols = ["household", "n_events", "events_per_day",
            "moves_per_object_day", "hour_entropy", "daily_fano",
            "twin_pairs", "never_move"]
    lines = ["| " + " | ".join(cols) + " |",
             "|" + "---|" * len(cols)]
    for r in rows:
        lines.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    if reference:
        reference = dict(reference, household="casas_aruba (REAL, ref)")
        lines.append("| " + " | ".join(str(reference[c]) for c in cols)
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
