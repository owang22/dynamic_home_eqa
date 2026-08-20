#!/usr/bin/env python3
"""Assemble the revamp_v2 acceptance report from build artifacts alone —
no re-running, no LLM: attempt counts, leak predictions, timeline and bank
stats, and the realism panel table.

Usage:
  python src/revamp_v2/acceptance_report.py --slug qwen3-32b \
      [--out reports/revamp_v2/acceptance.md]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import yaml

HERE = pathlib.Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import realism_panel  # noqa: E402

REPO = HERE.parent.parent


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--slug", default="qwen3-32b")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=pathlib.Path,
                    default=REPO / "reports" / "revamp_v2" / "acceptance.md")
    args = ap.parse_args()
    root = REPO / "profiles" / "revamp_v2" / args.slug
    # A household mid-generation has no build_log yet; report what exists
    # rather than crashing on a partially built set.
    hh_dirs = sorted((d for d in root.glob("hh*")
                      if d.is_dir() and (d / "build_log.json").exists()),
                     key=lambda p: int(p.name[2:]))
    if not hh_dirs:
        raise SystemExit(f"no built households under {root}")

    build_rows, timelines = [], []
    for d in hh_dirs:
        log = json.loads((d / "build_log.json").read_text())
        ok = log["accepted_attempt"] is not None
        leak = (log["attempts"][-1].get("leak_prediction") or {}) if ok else {}
        program = (yaml.safe_load((d / "routine_program.yaml").read_text())
                   if ok else {})
        build_rows.append({
            "hh": d.name, "type": log["household_type"],
            "persona_tries": len(log.get("persona_attempts") or []),
            "leaks": bool(log.get("leak_unresolved")),
            "status": "OK" if ok else "FAILED",
            "attempts": log["n_attempts"],
            "blocks": len(program.get("weekly_blocks", [])),
            "arcs": len(program.get("arc_events", [])),
            "objects": len(program.get("object_rules", [])),
            "rules": sum(len(e.get("rules") or [])
                         for e in program.get("object_rules") or []),
        })
        tl = d / f"timeline_seed{args.seed}"
        if tl.exists():
            timelines.append(tl)

    lines = ["# revamp_v2 acceptance report", "",
             f"Model slug: `{args.slug}`; seed {args.seed}.", "",
             "## Build (generation + the four gates)", "",
             "| hh | type | status | program tries | persona tries | "
             "blocks | arcs | objects | rules | ids leak type |",
             "|" + "---|" * 10]
    for r in build_rows:
        lines.append(
            f"| {r['hh']} | {r['type']} | {r['status']} | {r['attempts']} | "
            f"{r['persona_tries']} | {r['blocks']} | {r['arcs']} | "
            f"{r['objects']} | {r['rules']} | "
            f"{'YES' if r['leaks'] else 'no'} |")
    n_ok = sum(1 for r in build_rows if r["status"] == "OK")
    n_leak = sum(1 for r in build_rows if r["leaks"])
    lines += ["",
              f"{n_ok}/{len(build_rows)} households passed every check "
              f"within 5 program attempts. Leak audit (chance = 1/"
              f"{len(build_rows)}): {n_leak} household(s) could not be "
              f"resampled into an inventory that hides their type — see "
              f"the README on the closed object vocabulary.", ""]

    if timelines:
        rows = [realism_panel.timeline_stats(t) for t in timelines]
        ref_dir = REPO / "casas" / "aruba" / "timeline_21d"
        ref = (realism_panel.timeline_stats(ref_dir) if ref_dir.exists()
               else None)
        lines += ["## Realism panel (reporting only, never a gate)", "",
                  realism_panel.render(rows, ref), ""]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
