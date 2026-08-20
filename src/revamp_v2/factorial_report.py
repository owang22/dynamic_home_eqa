#!/usr/bin/env python3
"""The 2x2 factorial table: one markdown table over the four generation
arms (rule_based / freeform / story_driven / story_rules), per household
and model where built, plus the casas/aruba comparator row (real ADL
activity stream, INVENTED object layer — see the legend; it is a timing-
scatter comparator, not ground truth for move volume or which objects
move).
Numbers and a fixed legend only — no prose generation, no re-running.

Columns are the realism panel's statistics (non-carry basis) plus
`carry_frac`, `dead_days`, `unbound_story_activities` and
`fallback_days` (both "-" where the arm has no story stage).

Usage:
  python src/revamp_v2/factorial_report.py \
      [--seed 0] [--out reports/revamp_v2/factorial.md]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import realism_panel  # noqa: E402

REPO = HERE.parent.parent
ARMS = ["rule_based", "freeform", "story_driven", "story_rules"]

COLS = ["arm", "model", "household", "n_events", "events_per_day",
        "moves_per_object_day", "hour_entropy", "daily_fano", "fano_all",
        "carry_frac", "top2", "dead_days", "unbound_story_activities",
        "fallback_days"]

LEGEND = """\
Legend (all event statistics on the NON-CARRY basis — departure-carry
pickups/putdowns excluded; `carry_frac` is their share of all events and
`fano_all` the all-events Fano, so the basis is visible):
- n_events / events_per_day / moves_per_object_day: non-carry move counts.
- hour_entropy: hour-of-day entropy of move times, normalized by log 24.
- daily_fano: var/mean of daily non-carry move counts.
- top2: share of non-carry events owed to the two most-moved objects.
- dead_days: days with < 3 non-carry events while a resident was home
  awake >= 6 h.
- unbound_story_activities: story activities no object rule or reset_all
  names ("-" for arms with no story stage).
- fallback_days: days the story stage failed to author ("-" likewise).
  A household with > 30% fallback days is marked NOT story-driven.
- casas_aruba (casas/aruba/timeline_21d): its ACTIVITY stream is real
  CASAS free-living data; its OBJECT layer (inventory + activity->object
  binding) is INVENTED, with the per-bout probabilities that set move
  volume "tuned by feel" (casas/README.md). Treat it as a comparator for
  TIMING SCATTER only — hour_entropy and daily_fano inherit their
  character from the real intervals (that README's deterministic-rules
  run reproduces them: 0.74/1.92 -> 0.76/2.03). Its volume columns
  (n_events, events_per_day, moves_per_object_day) and object-identity
  columns (top2, twin_pairs, never_move) come from the invented layer and
  are NOT ground truth: read that row as one authored household, not a
  target.\
"""


def _row(arm: str, model: str, hh: str, tl: pathlib.Path) -> dict:
    s = realism_panel.timeline_stats(tl)
    meta = json.loads((tl / "meta.json").read_text())
    has_story = arm in ("story_driven", "story_rules")
    hh_label = hh + (" (NOT story-driven)"
                     if s.get("not_story_driven") else "")
    return {
        "arm": arm, "model": model, "household": hh_label,
        "n_events": s["n_events"], "events_per_day": s["events_per_day"],
        "moves_per_object_day": s["moves_per_object_day"],
        "hour_entropy": s["hour_entropy"], "daily_fano": s["daily_fano"],
        "fano_all": s["fano_all"], "carry_frac": s["carry_frac"],
        "top2": s["top2"], "dead_days": s["dead_days"],
        "unbound_story_activities":
            (meta.get("n_unbound_story_activities", "-")
             if has_story else "-"),
        "fallback_days": (s["fallback_days"] if has_story else "-"),
    }


def collect(seed: int) -> list[dict]:
    rows: list[dict] = []
    root = REPO / "profiles" / "revamp_v2"
    for arm in ARMS:
        arm_dir = root / arm
        if not arm_dir.is_dir():
            continue
        for model_dir in sorted(p for p in arm_dir.iterdir() if p.is_dir()):
            for hh in sorted(model_dir.glob("hh*"),
                             key=lambda p: (len(p.name), p.name)):
                tl = hh / f"timeline_seed{seed}"
                if (tl / "meta.json").exists():
                    rows.append(_row(arm, model_dir.name, hh.name, tl))
    return rows


def render(rows: list[dict], reference: dict | None) -> str:
    lines = ["| " + " | ".join(COLS) + " |", "|" + "---|" * len(COLS)]
    for r in rows:
        lines.append("| " + " | ".join(str(r[c]) for c in COLS) + " |")
    if reference:
        ref = {c: "-" for c in COLS}
        ref.update({"arm": "comparator", "model": "-",
                    "household": "casas_aruba (real ADLs, invented objects)"})
        for c in ("n_events", "events_per_day", "moves_per_object_day",
                  "hour_entropy", "daily_fano", "fano_all", "carry_frac",
                  "top2", "dead_days"):
            ref[c] = reference[c]
        lines.append("| " + " | ".join(str(ref[c]) for c in COLS) + " |")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=pathlib.Path,
                    default=REPO / "reports" / "revamp_v2" / "factorial.md")
    args = ap.parse_args()
    rows = collect(args.seed)
    if not rows:
        raise SystemExit("no built timelines under profiles/revamp_v2/")
    ref_dir = REPO / "casas" / "aruba" / "timeline_21d"
    ref = (realism_panel.timeline_stats(ref_dir) if ref_dir.exists()
           else None)
    text = ("# revamp_v2 factorial report (2x2: calendar x movement)\n\n"
            + render(rows, ref) + "\n\n" + LEGEND + "\n")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text)
    print(text)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
