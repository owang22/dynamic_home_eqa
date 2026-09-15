"""Phase 3 report for the tree arms: node count and depth per day,
add_child versus add_root with their triggers, what happened to the
tour-absent objects, whether each revision's new nodes gained weight
over the following five days, prunes, rejections, label recovery.

Usage:
  python -m baselines.llm_hypotheses.tree_report --study-dir results/llm_hypotheses/runs/main
Writes ``<study>/<household>__bank0/figures/tree_report.md`` and
``tree_nodes_depth.png``.
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
from typing import Any, Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from baselines.bank import JsonlBank
from baselines.household_analysis import bank_path
from baselines.llm_hypotheses.hypothesis_tree import HypothesisTree
from baselines.llm_hypotheses.leak_report import covered_by, first_sightings
from baselines.types import DAY_SECONDS

GAIN_HORIZON_DAYS = 5


def tree_arms(run_dir: pathlib.Path) -> Dict[str, Dict[str, Any]]:
    out = {}
    for p in sorted((run_dir / "arms").rglob("diagnostics.json")):
        if "incomplete" in p.parts or p.parent.name.startswith("_"):
            continue
        d = json.load(open(p))
        if d.get("tree", {}).get("is_tree"):
            out[p.parent.name] = d
    return out


def node_gains(diag: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Per node a revision created: its weight share and subtree share
    the day it was created and GAIN_HORIZON_DAYS later (None when the
    node was pruned or the episode ended first)."""
    trace = diag["tree"]["tree_trace"]
    rows = []
    for op in diag["tree"]["edit_log"]:
        day, nid = op["day"], op["node_id"]
        at = trace.get(str(day), {}).get("nodes", {}).get(nid)
        later = trace.get(str(day + GAIN_HORIZON_DAYS), {}).get("nodes", {}).get(nid)
        rows.append({"day": day, "trigger": op["trigger"], "op": op["op"],
                     "node_id": nid, "labels": op.get("labels"),
                     "weight_day0": at["weight"] if at else None,
                     "subtree_day0": at["subtree"] if at else None,
                     "weight_day5": later["weight"] if later else None,
                     "subtree_day5": later["subtree"] if later else None,
                     "gained": (later["weight"] > at["weight"]) if (at and later) else None})
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--study-dir", type=pathlib.Path, required=True)
    ap.add_argument("--household", default="hh_001")
    ap.add_argument("--bank-dir", type=pathlib.Path,
                    default=pathlib.Path("banks/baselines/tour_start_day0/tl0"))
    args = ap.parse_args()
    run_dir = args.study_dir / f"{args.household}__bank0"
    arms = tree_arms(run_dir)
    out_dir = run_dir / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    episode = next(JsonlBank(bank_path(args.household, 0, args.bank_dir)).episodes())
    first = first_sightings(episode)
    absent = sorted(set(episode.object_classes) - {o.object_id for o in episode.initial_observations})
    lines = [f"# Tree arms — {args.household}, {args.study_dir.name}", "",
             "Every number is from one episode (one household, one bank seed); a change over a few nodes is anecdote, and the tables say which."]
    if not arms:
        lines.append("\n(no tree arms found)")
        (out_dir / "tree_report.md").write_text("\n".join(lines) + "\n")
        print("\n".join(lines)); return

    # 1. node count / depth per day
    lines += ["", "## Node count and depth per day", ""]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.2))
    for name, d in arms.items():
        trace = d["tree"]["tree_trace"]
        days = sorted(int(k) for k in trace)
        axes[0].plot(days, [trace[str(k)]["n_nodes"] for k in days], label=name.replace("__", " · "))
        axes[1].plot(days, [trace[str(k)]["max_depth"] for k in days], label=name.replace("__", " · "))
        lines.append(f"- {name.replace('__', ' · ')}: nodes by day " + " ".join(f"d{k}:{trace[str(k)]['n_nodes']}" for k in days if k % 3 == 0 or k == days[-1])
                     + f"; max depth reached {max(trace[str(k)]['max_depth'] for k in days)}")
    axes[0].set_title("live nodes"); axes[1].set_title("max depth"); axes[0].set_xlabel("day"); axes[1].set_xlabel("day")
    axes[1].legend(fontsize=6, frameon=False); fig.tight_layout(); fig.savefig(out_dir / "tree_nodes_depth.png", dpi=150); plt.close(fig)

    # 2. operations by kind and trigger
    lines += ["", "## Revisions: add_child versus add_root, by trigger", "", "| arm | call (day, trigger) | ops returned | add_child applied | add_root applied | rejected | outcome |", "|---|---|---|---|---|---|---|"]
    for name, d in arms.items():
        events = (d.get("reask") or {}).get("events") or []
        edits = d["tree"]["edit_log"]
        for e in events:
            mine = [op for op in edits if op["call_index"] == e["call_index"]]
            lines.append(f"| {name.replace('__', ' · ')} | d{e['day']}, {e['trigger']} | {e.get('operations', 0)} | "
                         f"{sum(1 for op in mine if op['op'] == 'add_child')} | {sum(1 for op in mine if op['op'] == 'add_root')} | "
                         f"{e.get('rejected', 0)} | {'revised' if e['changed'] else 'kept'} |")
        if not events:
            lines.append(f"| {name.replace('__', ' · ')} | (no revision calls) | | | | | |")

    # 3. tour-absent objects
    lines += ["", f"## Tour-absent objects ({len(absent)}): first sighting, and whether the FINAL tree gives them a rest or a move", ""]
    header = "| object | class | first sighted (day) | " + " | ".join(n.replace("__", " · ") for n in arms) + " |"
    lines += [header, "|" + "---|" * (3 + len(arms))]
    finals = {}
    for name, d in arms.items():
        tree = HypothesisTree.from_json(d["tree"]["final_tree"] or {"nodes": []})
        finals[name] = tree.bodies()
    for obj in absent:
        cls = episode.object_classes[obj]
        cells = []
        for name in arms:
            hits = [covered_by(b, obj, cls) for b in finals[name]]
            r = sum(h["rest"] for h in hits); m = sum(h["move"] for h in hits)
            cells.append(f"rest {r}/{len(hits)}, move {m}/{len(hits)}" if hits else "-")
        day = first.get(obj)
        when = f"{day / DAY_SECONDS:.1f}" if day is not None else "never"
        lines.append(f"| {obj} | {cls} | {when} | " + " | ".join(cells) + " |")

    # 4. did new nodes gain weight
    lines += ["", f"## Per revision: did the new node gain weight over the next {GAIN_HORIZON_DAYS} days?", "", "| arm | day | trigger | op | node | labels | weight at creation → +5 d | subtree at creation → +5 d | gained |", "|---|---|---|---|---|---|---|---|---|"]
    for name, d in arms.items():
        for r in node_gains(d):
            f = lambda x: "-" if x is None else f"{x:.3f}"
            lines.append(f"| {name.replace('__', ' · ')} | {r['day']} | {r['trigger']} | {r['op']} | {r['node_id']} | {', '.join(r['labels'] or [])} | "
                         f"{f(r['weight_day0'])} → {f(r['weight_day5'])} | {f(r['subtree_day0'])} → {f(r['subtree_day5'])} | "
                         f"{'yes' if r['gained'] else 'no' if r['gained'] is False else 'pruned/ended'} |")

    # 5. prunes and rejections
    lines += ["", "## Prunes and rejected responses", "", "| arm | node prunes | subtree prunes | re-parented children | rejected ops (whole-response rejections) | reasons |", "|---|---|---|---|---|---|"]
    for name, d in arms.items():
        t = d["tree"]
        kinds = collections.Counter(r.get("kind") for r in t["prune_log"])
        reasons = collections.Counter(r["reason"].split(":")[1].strip()[:60] if ":" in r["reason"] else r["reason"][:60] for r in t["rejected_ops"])
        lines.append(f"| {name.replace('__', ' · ')} | {kinds.get('node', 0)} | {kinds.get('subtree', 0)} | {len(t['reparent_log'])} | {len(t['rejected_ops'])} | "
                     + "; ".join(f"{k} ×{v}" for k, v in reasons.most_common(3)) + " |")

    # 6. label recovery and settled labels
    lines += ["", "## Labels: final weights, settled, and name-matched recovery of the bank's premises", ""]
    for name, d in arms.items():
        lw = d["tree"]["label_weights"]
        top = ", ".join(f"{l} {w:.2f}" for l, w in sorted(lw.items(), key=lambda kv: -kv[1])[:8])
        rec = d.get("label_recovery") or {}
        rec_text = "; ".join(f"{p}={v['label']} ({v['weight']:.2f})" if v else f"{p}: no match" for p, v in rec.items())
        lines.append(f"- {name.replace('__', ' · ')}: {top}. Settled: {', '.join(d['tree']['settled_labels']) or 'none'}. Recovery ({d.get('premises')}): {rec_text}")

    text = "\n".join(lines) + "\n"
    (out_dir / "tree_report.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
