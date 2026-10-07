"""Post-leak-fix report (phase2_fixes.md, group B): what the LLM was
shown, what happened to the objects the tour missed, what the new-class
triggers did, and how many revision operations touched several leaves.

Usage:
  python -m baselines.llm_hypotheses.leak_report --study-dir results/llm_hypotheses/runs/main
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
import pathlib
from typing import Any, Dict, List

from baselines.bank import JsonlBank
from baselines.household_analysis import bank_path
from baselines.types import DAY_SECONDS


def first_sightings(episode) -> Dict[str, int]:
    first: Dict[str, int] = {}
    for obs in episode.initial_observations:
        first.setdefault(obs.object_id, obs.t)
    for e in episode.evidence_stream():
        for o in ([e.object_id] if hasattr(e, "object_id") else e.contents):
            first.setdefault(o, e.t)
    return first


def covered_by(body: Dict[str, Any], obj: str, cls: str) -> Dict[str, bool]:
    """Does one leaf body give ``obj`` a rest entry or a move, directly
    or through its class?"""
    rest = body.get("rest") or {}
    keys = set(rest) if isinstance(rest, dict) else {e.get("target") for e in rest}
    rest_hit = obj in keys or f"class:{cls}" in keys
    move_hit = any(m.get("target") in (obj, f"class:{cls}")
                   for a in body.get("activities", []) for m in a.get("moves", []))
    return {"rest": rest_hit, "move": move_hit}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--study-dir", type=pathlib.Path, required=True)
    ap.add_argument("--household", default="hh_001")
    ap.add_argument("--bank-dir", type=pathlib.Path,
                    default=pathlib.Path("banks/baselines/tour_start_day0/tl0"))
    ap.add_argument("--hyp-subdir", default="tl0_bank0_clean")
    args = ap.parse_args()
    episode = next(JsonlBank(bank_path(args.household, 0, args.bank_dir)).episodes())
    first = first_sightings(episode)
    tour_seen = {o.object_id for o in episode.initial_observations}
    absent = sorted(set(episode.object_classes) - tour_seen)
    lines = [f"# Leak report — {args.household}, {args.study_dir.name}", ""]

    lines += ["## Elicitation table vs full inventory", "", "| condition | objects shown | inventory | classes shown | classes in inventory |", "|---|---|---|---|---|"]
    for cond in ("tour_named", "tour_anonymized", "graph_named", "graph_anonymized"):
        f = pathlib.Path("results/llm_hypotheses/hypotheses") / cond / args.hyp_subdir / f"{args.household}.json"
        if not f.exists():
            continue
        d = json.load(open(f)); vocab = d.get("vocabulary") or {}
        lines.append(f"| {cond} | {len(vocab)} | {len(episode.object_classes)} | {len(set(vocab.values()))} | {len(set(episode.object_classes.values()))} |")

    lines += ["", f"## Tour-absent objects ({len(absent)}): first sighting, and whether a revision ever gave them a rest or a move", ""]
    arms = sorted(str(p.parent) for p in (args.study_dir / f"{args.household}__bank0/arms").rglob("diagnostics.json")
                  if ("graph" in p.parent.name or "llm" in p.parent.name)
                  and "incomplete" not in p.parts and not p.parent.name.startswith("_"))
    header = "| object | class | first sighted (day) | " + " | ".join(pathlib.Path(a).name.replace("__", " · ") for a in arms) + " |"
    lines += [header, "|" + "---|" * (3 + len(arms))]
    finals = {}
    for a in arms:
        d = json.load(open(pathlib.Path(a) / "diagnostics.json"))
        finals[a] = d.get("final_hypotheses") or []
    for obj in absent:
        cls = episode.object_classes[obj]
        cells = []
        for a in arms:
            hits = [covered_by(b, obj, cls) for b in finals[a]]
            r = sum(h["rest"] for h in hits); m = sum(h["move"] for h in hits)
            cells.append(f"rest {r}/{len(hits)}, move {m}/{len(hits)}" if hits else "-")
        day = first.get(obj)
        lines.append(f"| {obj} | {cls} | {day / DAY_SECONDS:.1f} | " + " | ".join(cells) + " |" if day is not None
                     else f"| {obj} | {cls} | never | " + " | ".join(cells) + " |")

    lines += ["", "## New-class / uncovered-bank triggers and other re-ask events", "", "| arm | events (day: trigger → changed, leaves after) | bank contents at each uncovered fire |", "|---|---|---|"]
    for a in arms:
        d = json.load(open(pathlib.Path(a) / "diagnostics.json"))
        ev = (d.get("reask") or {}).get("events") or []
        if not ev:
            continue
        summary = "; ".join(f"d{e['day']}: {e['trigger']} → {'revised' if e['changed'] else 'kept'}, {e['n_hypotheses_after']}" for e in ev)
        banks = "; ".join(f"d{e['day']}: " + ", ".join(f"{b['object']} ({b['class']})" for b in (e.get('before') or {}).get('uncovered_bank') or [])
                          for e in ev if e["trigger"] == "uncovered") or "-"
        lines.append(f"| {pathlib.Path(a).name.replace('__', ' · ')} | {summary} | {banks} |")

    lines += ["", "## Per revision call: operations touching more than one leaf", "", "| arm | day | call type | ops | leaves touched | activities added to >1 leaf | rejected |", "|---|---|---|---|---|---|---|"]
    for a in arms:
        for f in sorted(glob.glob(str(pathlib.Path(a) / "revisions" / "*.json"))):
            r = json.load(open(f))
            ops = r.get("operations") or []
            leaves = {o.get("leaf_id") for o in ops if o.get("leaf_id")}
            names = collections.Counter(str((o.get("activity") or {}).get("name")) for o in ops if o.get("op") == "add_activity")
            multi = [n for n, c in names.items() if c > 1]
            lines.append(f"| {pathlib.Path(a).name.replace('__', ' · ')} | {r['day']} | {r.get('call_type')} | {len(ops)} | {len(leaves)} | {multi or '-'} | {len(r.get('rejected') or [])} |")
    out = args.study_dir / f"{args.household}__bank0" / "figures" / "leak_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
