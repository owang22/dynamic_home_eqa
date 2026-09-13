"""Ground truth against the hypotheses, and where predictions come from.

Two instruments, both built from what is already on disk (no LLM):

**Side-by-side.** The bank's program records the true activity schedule
(per-day blocks with start/end), what every object does DURING each
activity (carried, or placed somewhere) and where it lands AFTER, and
each object's home. Printed in the hypothesis layout — activity table,
then a per-object table with the truth in the first column and each
hypothesis beside it — plus a scorecard where the join is exact:
stated rest vs true home; hypothesis moves vs true destinations;
objects the truth carries out of the house vs objects the hypothesis
sends there; weekday-only activities.

**Provenance heatmap.** Objects on one axis, days on the other, each
cell coloured by what produced that hypothesis's prediction
(:meth:`HypothesisProgramBelief.explain`): an activity rule, the stated
rest, the tour default, the statistical fallback, or nothing. One panel
per hypothesis plus one for the particle holding the mixture's weight.
Sampled on a fixed grid (four hours a day, every object), so coverage
does not depend on which objects were queried. For a re-asking arm the
recorded revisions are replayed at their recorded days.

Usage:
  python -m baselines.llm_hypotheses.truth_vs_hypotheses \
      --household hh_001 --condition tour_named [--arm passive__llm__tour_named]
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import random
import statistics
from typing import Any, Dict, List, Optional, Sequence, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

from baselines.bank import JsonlBank
from baselines.beliefs.hypothesis_program import (ORDINAL_CENTERS,
                                                   HypothesisProgramBelief,
                                                   parse_hypothesis)
from baselines.beliefs.llm_hypothesis_mixture import (LLMHypothesisMixture,
                                                      ReaskConfig)
from baselines.household_analysis import REPO_ROOT, bank_path
from baselines.llm_hypotheses.elicit import (DEFAULT_OUT_DIR, extract_json,
                                             validate_hypotheses)
from baselines.llm_hypotheses.prompt import (build_anonymization_maps,
                                             deanonymize_hypothesis)
from baselines.llm_hypotheses.run_tour_start import STUDY_DIR
from baselines.types import DAY_SECONDS

PROFILE_ROOT = REPO_ROOT / "profiles" / "households" / "generated" / "gpt-5.6-terra"
GRID_HOURS = (8, 12, 17, 21)
PROV_ORDER = ("rule", "rest", "tour", "fallback", "cold")
PROV_COLOR = {"rule": "#2a78d6", "rest": "#eb6834", "tour": "#eda100",
              "fallback": "#b5b5b5", "cold": "#ecebe7"}
PROV_LABEL = {"rule": "activity rule", "rest": "stated rest", "tour": "tour only",
              "fallback": "statistical fallback", "cold": "never sighted"}
HYP = lambda hid: "hyp" + str(hid)[1:] if str(hid).startswith("h") and str(hid)[1:].isdigit() else str(hid)


# ------------------------------------------------------------------ truth

def load_truth(household: str) -> Dict[str, Any]:
    p = PROFILE_ROOT / household
    prog = yaml.safe_load((p / "program.yaml").read_text())
    motions = yaml.safe_load((p / "expanded_motions.yaml").read_text())
    blocks: Dict[str, List[Tuple[int, float, float]]] = collections.defaultdict(list)
    for ev in prog["arc_events"]:
        for b in ev["patch"].get("add", []):
            h = lambda s: int(s[:2]) + int(s[3:]) / 60
            blocks[b["activity"]].append((ev["day"], h(b["start"]), h(b["end"])))
    activities = {}
    for name, rows in blocks.items():
        days = sorted({d for d, _, _ in rows})
        wd = sum(1 for d in days if d % 7 < 5); we = len(days) - wd
        kind = "weekday" if we == 0 else "weekend" if wd == 0 else "both"
        starts = [s for _, s, _ in rows]; durs = [max(0.0, e - s) for _, s, e in rows]
        activities[name] = {"days": kind, "n_days": len(days), "weekday_days": wd, "weekend_days": we,
                            "per_week": round(7 * len(days) / prog["days"], 1),
                            "start": statistics.median(starts), "duration_h": statistics.median(durs),
                            "at": motions["object_motions"].get(name, {}).get("at")}
    during: Dict[str, List[Tuple[str, str]]] = collections.defaultdict(list)   # obj -> [(activity, dest)]
    after: Dict[str, List[Tuple[str, str, float]]] = collections.defaultdict(list)  # obj -> [(activity, dest, p)]
    for name, m in motions["object_motions"].items():
        if name not in activities:
            continue
        for obj, d in (m.get("during") or {}).items():
            if isinstance(d, dict):     # v3 departure leg {dest, p[, only_from]}
                d = d["dest"]
            dest = "OUT_OF_HOUSE" if (isinstance(d, str) and d.startswith("person") and m.get("at") == "ELSEWHERE") \
                else "ON_PERSON" if isinstance(d, str) and d.startswith("person") else d
            during[obj].append((name, dest))
        for obj, d in (m.get("after") or {}).items():
            if isinstance(d, dict) and d.get("dist"):
                dest, p = max(d["dist"].items(), key=lambda kv: kv[1])
                after[obj].append((name, dest, p * (1 - d.get("noop_p", 0))))
    homes = {o: v["home"] for o, v in motions["placements"].items()}
    return {"activities": activities, "during": during, "after": after, "homes": homes,
            "household_type": prog.get("household_type")}


def _chance_word(p: float) -> str:
    return min(ORDINAL_CENTERS, key=lambda k: abs(ORDINAL_CENTERS[k] - p))


# ------------------------------------------------------------- hypotheses

def load_hypothesis_sets(household: str, condition: str,
                         arm: Optional[str]) -> List[Tuple[str, List[dict]]]:
    """(label, hypotheses) for day 0 and, with ``arm``, each recorded
    revision — real ids, validated."""
    episode = next(JsonlBank(bank_path(household, 0)).episodes())
    sets = [("day 0", json.loads((DEFAULT_OUT_DIR / "hypotheses" / condition / f"{household}.json").read_text())["hypotheses"])]
    if arm:
        rev_dir = STUDY_DIR / household / arm / "revisions"
        anonymized = "anonymized" in condition
        omap, rmap, cmap = build_anonymization_maps(episode) if anonymized else ({}, {}, {})
        for path in sorted(rev_dir.glob(f"{household}_revision_*.json")):
            L = json.loads(path.read_text())
            if L.get("outcome") != "revised":
                continue
            hyps = None
            for r in L["rounds"]:
                if r["kind"] in ("revision", "salvage", "repair") and r.get("payload"):
                    try:
                        cand = extract_json(r["payload"]).get("hypotheses", [])
                    except Exception:
                        continue
                    if anonymized:
                        cand = [deanonymize_hypothesis(h, omap, rmap, cmap) for h in cand]
                    valid, _ = validate_hypotheses(cand, episode.object_classes, episode.receptacle_ids)
                    if len(valid) == L.get("n_valid", len(valid)):
                        hyps = valid
            if hyps:
                sets.append((f"day {L['day']} revision", hyps))
    return sets


# ------------------------------------------------------------ side by side

def side_by_side(household: str, truth: Dict[str, Any], label: str,
                 hyps: List[dict], episode) -> str:
    parsed = [parse_hypothesis(h, episode.object_classes, episode.receptacle_ids) for h in hyps]
    ids = [HYP(p.hypothesis_id) for p in parsed]
    L = [f"## {label}", ""]
    # -- activity tables
    L += ["### Activity schedule — truth", "", "| activity | days | ~start | ~length | where | objects carried / placed during | landed after |", "|---|---|---|---|---|---|---|"]
    acts = sorted(truth["activities"].items(), key=lambda kv: kv[1]["start"])
    for name, a in acts:
        dur = [f"{o}→{d}" for o, lst in truth["during"].items() for n, d in lst if n == name]
        aft = [f"{o}→{d}" for o, lst in truth["after"].items() for n, d, _ in lst if n == name]
        L.append(f"| {name} | {a['days']} ({a['weekday_days']}wd/{a['weekend_days']}we, {a['per_week']}×/wk) | {a['start']:.1f}h | {a['duration_h']:.1f}h | {a['at']} | {', '.join(dur[:6])}{' …' if len(dur) > 6 else ''} | {', '.join(aft[:5])}{' …' if len(aft) > 5 else ''} |")
    L.append("")
    for hid, hp in zip(ids, parsed):
        L += [f"### Activity schedule — {hid}: {hyps[ids.index(hid)].get('rationale', '')[:120]}", "",
              "| activity | days | start | length | moves |", "|---|---|---|---|---|"]
        for a in sorted(hp.activities, key=lambda x: x.start_hour):
            mv = [f"{m.raw_target}→{m.to} ({m.chance}, {m.after})" for m in a.moves]
            L.append(f"| {a.name} | {a.days} ({a.frequency_per_week:g}×/wk) | {a.start_hour:.1f}h | {a.duration_h:.1f}h | {'; '.join(mv[:5])}{' …' if len(mv) > 5 else ''} |")
        L.append("")
    # -- per-object table
    L += ["### Per object — truth in the first column, each hypothesis beside it", "",
          "| object | TRUTH | " + " | ".join(ids) + " |", "|---|---|" + "---|" * len(ids)]
    for obj in sorted(episode.object_classes):
        cell = [f"home **{truth['homes'].get(obj, '?')}**"]
        d = truth["during"].get(obj, []); a = truth["after"].get(obj, [])
        if d: cell.append("during: " + ", ".join(f"{n}→{x}" for n, x in d[:4]) + (" …" if len(d) > 4 else ""))
        if a: cell.append("after: " + ", ".join(f"{n}→{x}({p:.1f})" for n, x, p in a[:3]) + (" …" if len(a) > 3 else ""))
        row = [obj, "<br>".join(cell)]
        for hp in parsed:
            parts = []
            if obj in hp.rest: parts.append(f"rest {hp.rest[obj]}")
            for act in hp.activities:
                for m in act.moves:
                    if obj in m.targets: parts.append(f"{act.name}→{m.to} ({m.chance[:4]},{m.after[:3]})")
            row.append("<br>".join(parts) if parts else "— *(fallback)*")
        L.append("| " + " | ".join(row) + " |")
    L.append("")
    # -- scorecard
    truth_out = {o for o, lst in truth["during"].items() if any(x == "OUT_OF_HOUSE" for _, x in lst)}
    truth_dest = collections.defaultdict(set)
    for o, lst in truth["during"].items():
        for _, x in lst: truth_dest[o].add(x)
    for o, lst in truth["after"].items():
        for _, x, _ in lst: truth_dest[o].add(x)
    wd_only = {n for n, a in truth["activities"].items() if a["days"] == "weekday" and a["n_days"] >= 5}
    L += ["### Scorecard (exact joins only)", "",
          "| hypothesis | objects mentioned | stated rest = true home | moves whose destination the truth ever uses | true carry-out objects it sends OUT_OF_HOUSE | objects it sends OUT that never leave | weekday-only activities |",
          "|---|---|---|---|---|---|---|"]
    for hid, hp in zip(ids, parsed):
        rest_ok = sum(1 for o, r in hp.rest.items() if truth["homes"].get(o) == r)
        moves = [(o, m.to) for act in hp.activities for m in act.moves for o in m.targets]
        mv_ok = sum(1 for o, to in moves if to in truth_dest.get(o, set()) or to == truth["homes"].get(o))
        hyp_out = {o for o, to in moves if to == "OUT_OF_HOUSE"}
        wd_acts = sum(1 for a in hp.activities if a.days == "weekday")
        L.append(f"| {hid} | {len(hp.covered_objects())}/{len(episode.object_classes)} | {rest_ok}/{len(hp.rest)} | {mv_ok}/{len(moves)} | {len(hyp_out & truth_out)}/{len(truth_out)} | {len(hyp_out - truth_out)} | {wd_acts}/{len(hp.activities)} (truth: {len(wd_only)}) |")
    L += ["", f"Truth: {len(truth_out)} objects leave the house during weekday work ({', '.join(sorted(truth_out))}).", ""]
    return "\n".join(L)


# --------------------------------------------------------------- heatmap

class _ScriptedElicitor:
    """Replays recorded revisions at their recorded days."""

    def __init__(self, sets: Sequence[Tuple[str, List[dict]]]) -> None:
        self._queue = [s for lab, s in sets[1:]]

    def __call__(self, report, previous, context):
        return self._queue.pop(0) if self._queue else previous


def provenance_grid(household: str, condition: str, sets, reask: bool):
    episode = next(JsonlBank(bank_path(household, 0)).episodes())
    m = LLMHypothesisMixture(random.Random(0), DEFAULT_OUT_DIR / "hypotheses" / condition,
                             reask=ReaskConfig(window=10 ** 6, scheduled_days=(3, 7), max_calls=len(sets) - 1) if reask else None,
                             elicitor=_ScriptedElicitor(sets) if reask else None)
    m.reset(episode.agent_view())
    for o in episode.initial_observations:
        m.update(o)
    objects = sorted(episode.object_classes); n_days = episode.n_days
    labels = [HYP(h.get("hypothesis_id")) for h in sets[0][1]]
    grids = {lab: np.full((len(objects), n_days), -1) for lab in labels + ["mixture leader"]}
    stream = list(episode.evidence_stream()); cursor = 0
    for day in range(n_days):
        for hour in GRID_HOURS:
            t = day * DAY_SECONDS + hour * 3600
            while cursor < len(stream) and stream[cursor].t <= t:
                m.update(stream[cursor]); cursor += 1
            parts = [p for p in m.particles if isinstance(p, HypothesisProgramBelief)]
            leader = max(range(len(m.particles)), key=lambda i: m.weights[i])
            for oi, obj in enumerate(objects):
                for p in parts:
                    lab = HYP(p.hypothesis.hypothesis_id)
                    if lab in grids:
                        v = PROV_ORDER.index(p.explain(obj, t))
                        grids[lab][oi, day] = v if grids[lab][oi, day] < 0 else grids[lab][oi, day]  # first sample of the day
                lp = m.particles[leader]
                v = PROV_ORDER.index(lp.explain(obj, t)) if isinstance(lp, HypothesisProgramBelief) else PROV_ORDER.index("fallback")
                if grids["mixture leader"][oi, day] < 0: grids["mixture leader"][oi, day] = v
    # mode over the day's four samples would be better than first; recompute with counts
    return objects, grids


def provenance_heatmap(household: str, condition: str, sets, reask: bool, out: pathlib.Path) -> Dict[str, Any]:
    objects, grids = provenance_grid(household, condition, sets, reask)
    labels = list(grids)
    cmap = ListedColormap([PROV_COLOR[k] for k in PROV_ORDER])
    fig, axes = plt.subplots(1, len(labels), figsize=(3.1 * len(labels) + 2.2, 0.22 * len(objects) + 1.9), sharey=True)
    shares = {}
    for ax, lab in zip(axes, labels):
        g = grids[lab]; ax.imshow(g, cmap=cmap, vmin=0, vmax=len(PROV_ORDER) - 1, aspect="auto", interpolation="nearest")
        counts = collections.Counter(int(v) for v in g.flatten() if v >= 0); tot = sum(counts.values())
        shares[lab] = {PROV_ORDER[k]: round(v / tot, 3) for k, v in counts.items()}
        top = max(shares[lab], key=shares[lab].get)
        ax.set_title(f"{lab}\n{PROV_LABEL[top]} {shares[lab][top]:.0%}", fontsize=9, loc="left")
        ax.set_xticks([0, 7, 14, 21, 27]); ax.set_xlabel("day")
        for d in (3, 7):
            if reask: ax.axvline(d - 0.5, color="#0b0b0b", lw=0.8, ls=(0, (2, 2)))
    axes[0].set_yticks(range(len(objects))); axes[0].set_yticklabels(objects, fontsize=7)
    fig.legend(handles=[Patch(color=PROV_COLOR[k], label=PROV_LABEL[k]) for k in PROV_ORDER], loc="lower center", ncol=5, frameon=False, fontsize=9, bbox_to_anchor=(0.5, -0.005))
    fig.suptitle(f"What produced each prediction — {household} · {condition}{' · re-asking (dotted = revision)' if reask else ' · fixed set'} — sampled at 08/12/17/21h, first sample of the day shown",
                 x=0.01, ha="left", fontsize=11, fontweight="bold")
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))
    name = f"provenance__{condition}{'__reask' if reask else '__fixed'}.png"
    fig.savefig(out / name, dpi=140); plt.close(fig)
    return {"file": name, "shares": shares}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--household", default="hh_001")
    ap.add_argument("--condition", default="tour_named")
    ap.add_argument("--arm", default=None, help="re-asking arm dir name, to include its revisions")
    args = ap.parse_args()
    episode = next(JsonlBank(bank_path(args.household, 0)).episodes())
    truth = load_truth(args.household)
    sets = load_hypothesis_sets(args.household, args.condition, args.arm)
    out = STUDY_DIR / args.household / "figures"; out.mkdir(parents=True, exist_ok=True)
    md = [f"# Ground truth vs hypotheses — {args.household} ({truth['household_type']}) · {args.condition}", "",
          "Truth from the bank's program: activity blocks per day, what each object does during and after each activity, and its home. Hypotheses in the same layout. Objects are the join key; activity names differ by construction.", ""]
    for label, hyps in sets:
        md.append(side_by_side(args.household, truth, label, hyps, episode))
    heat = [provenance_heatmap(args.household, args.condition, sets[:1], False, out)]
    if len(sets) > 1:
        heat.append(provenance_heatmap(args.household, args.condition, sets, True, out))
    md += ["## Prediction provenance (share of object-days)", "", "| set | panel | " + " | ".join(PROV_LABEL[k] for k in PROV_ORDER) + " |", "|---|---|" + "---|" * len(PROV_ORDER)]
    for h, tag in zip(heat, ("fixed", "re-asking")):
        for lab, sh in h["shares"].items():
            md.append(f"| {tag} | {lab} | " + " | ".join(f"{sh.get(k, 0):.0%}" for k in PROV_ORDER) + " |")
    md += ["", "Figures: " + ", ".join(h["file"] for h in heat), ""]
    path = out / f"truth_vs_hypotheses__{args.condition}.md"
    path.write_text("\n".join(md)); print(f"wrote {path}")
    for h in heat: print("  ", h["file"], {k: v for k, v in h["shares"].items()})


if __name__ == "__main__":
    main()
