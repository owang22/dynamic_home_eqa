"""Why the survival models win at long ages: the four-case split.

A question whose last sighting is a day or more old falls into one of
four cases, by whether the object has MOVED since that sighting and by
whether a later room visit EXCLUDED the last-seen receptacle (found it
without the object). The base class's exclusion rule
(:mod:`baselines.beliefs.base`) is hard and permanent until the next
sighting, so every classical model is structurally unable to answer an
excluded receptacle even after the object has come back to it. The
Perpetua models bypass that rule (negative evidence enters their filters
as ``y = 0`` and the emergence filter re-admits the receptacle after the
expected absence), which is where their long-age gain comes from.

This module replays LastObs and MostFreq per question on every bank --
cheap, a few seconds per bank -- to get each question's case and those
two answers, joins the Perpetua models' correctness from
``absence_signal.csv.gz`` on question id, and writes ``perpetua_cases.md``
(per-home tables, one block per age range) and
``perpetua_cases_by_home.png`` next to the household analysis. Homes are
never pooled; seeds of one home are.

Usage:
  python -m baselines.perpetua_cases                  # all homes, 5 seeds
  python -m baselines.perpetua_cases --workers 60 --in-dir reports/baselines/household_analysis
"""
from __future__ import annotations

import argparse
import collections
import concurrent.futures
import csv
import gzip
import json
import logging
import pathlib
import random
from typing import Any, Dict, List, Optional, Sequence, Tuple

from baselines.bank import JsonlBank
from baselines.household_analysis import (FINE_AGE_EDGES_H, SEEDS, bank_path,
                                          household_meta)
from baselines.passive_eval import PassiveProtocolConfig, question_ages
from baselines.registry import build_registered_belief

logger = logging.getLogger(__name__)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_IN = REPO_ROOT / "reports" / "baselines" / "household_analysis"
MIN_N = 30
"""Fewest questions a cell needs to be quoted (household_report.MIN_N)."""

LONG_AGES = ("[24h,48h)", "[48h,72h)", "[72h,inf)")
AGE_BLOCKS: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("last sighting 1 day old or older", LONG_AGES),
    ("last sighting 12-24 h old", ("[12h,24h)",)),
)
CASES = (("stayed, not excluded", False, False),
         ("stayed, EXCLUDED", False, True),
         ("moved, not excluded", True, False),
         ("moved, EXCLUDED", True, True))
CASE_COLORS = ("#2a78d6", "#00838f", "#eda100", "#e34948")
COMPARATORS: Tuple[Tuple[str, Dict[str, Any]], ...] = (
    ("last_observation", {"name": "last_observation"}),
    ("most_frequent", {"name": "most_frequent", "half_life_h": 24}))


def replay_bank(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Per question of one bank: age bin, whether the object moved since
    its last sighting, whether the last-seen receptacle is under an active
    exclusion, and the LastObs / MostFreq answers. Runs in a worker."""
    household, seed = task["household"], task["seed"]
    bank_dir = task.get("bank_dir")
    episode = next(iter(JsonlBank(path=bank_path(
        household, seed, pathlib.Path(bank_dir) if bank_dir else None)).episodes()))
    cfg = PassiveProtocolConfig(seed=0, recency_bin_edges_h=FINE_AGE_EDGES_H)
    ages = question_ages(episode)
    questions = sorted((q for day in episode.questions_by_day for q in day),
                       key=lambda q: q.t_query)
    events = list(episode.evidence_stream())
    beliefs = {name: build_registered_belief(dict(spec), random.Random(0))
               for name, spec in COMPARATORS}
    for belief in beliefs.values():
        belief.reset(episode.agent_view())
        for obs in episode.initial_observations:
            belief.update(obs)
    probe = beliefs["last_observation"]      # evidence bookkeeping is shared
    out = []
    i = 0
    for q in questions:
        while i < len(events) and events[i].t < q.t_query:
            for belief in beliefs.values():
                belief.update(events[i])
            i += 1
        history = probe._history.get(q.object_id, [])
        last_seen = history[-1][1] if history else None
        truth = episode.true_location(q.object_id, q.t_query)
        out.append({
            "household": household, "seed": seed, "qid": q.question_id,
            "age_bin": cfg.recency_bin(ages[q.question_id]),
            "moved": truth != last_seen,
            "excluded": last_seen in probe._active_exclusions(q.object_id),
            "truth": truth,
            "answers": {name: b.predict_readonly(q.object_id, q.t_query).argmax
                        for name, b in beliefs.items()}})
    return out


def perpetua_correctness(in_dir: pathlib.Path, bins: Sequence[str]
                         ) -> Dict[str, Dict[Tuple[str, int, str], int]]:
    """model display base -> (household, seed, qid) -> correct, from the
    absence side file, kept-current mode, restricted to ``bins``."""
    wanted = set(bins)
    out: Dict[str, Dict[Tuple[str, int, str], int]] = {}
    path = in_dir / "absence_signal.csv.gz"
    if not path.exists():
        return out
    with gzip.open(path, "rt") as fh:
        for r in csv.DictReader(fh):
            if r["mode"] != "continuous" or r["age_bin"] not in wanted:
                continue
            base = r["model"].split("(")[0]
            out.setdefault(base, {})[
                (r["household"], int(r["seed"]), r["question_id"])] = int(r["correct"])
    return out


def _case_of(r: Dict[str, Any]) -> str:
    for label, moved, excluded in CASES:
        if r["moved"] == moved and r["excluded"] == excluded:
            return label
    raise AssertionError("unreachable")


def tabulate(rows: Sequence[Dict[str, Any]],
             correct: Dict[str, Dict[Tuple[str, int, str], int]],
             meta: Dict[str, Dict[str, Any]], bins: Sequence[str]
             ) -> Tuple[List[str], Dict[str, Dict[str, Dict[str, int]]]]:
    """Per-home table lines for one age block and the counters behind
    them (home -> case -> counters)."""
    models = ["last_observation", "most_frequent"] + sorted(correct)
    short = {"last_observation": "LastObs", "most_frequent": "MostFreq",
             "Perpetua": "Perpetua", "PerpetuaStar": "PerpStar",
             "PerpetuaStarFlat": "PerpFlat"}
    cnt: Dict[str, Dict[str, Dict[str, int]]] = collections.defaultdict(
        lambda: collections.defaultdict(lambda: collections.defaultdict(int)))
    for r in rows:
        if r["age_bin"] not in bins:
            continue
        key = (r["household"], r["seed"], r["qid"])
        if any(key not in correct[m] for m in correct):
            continue
        c = cnt[r["household"]][_case_of(r)]
        c["n"] += 1
        for m in ("last_observation", "most_frequent"):
            c[m] += int(r["answers"][m] == r["truth"])
        for m in correct:
            c[m] += correct[m][key]
    head = ["home", "res", "n"] + [f"{label} share" for label, _, _ in CASES]
    for label, _, _ in CASES:
        head.append(f"{label}: " + " / ".join(short.get(m, m) for m in models))
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for hh in sorted(meta, key=lambda h: (meta[h]["resident_group"], h)):
        cases = cnt.get(hh)
        if not cases:
            continue
        total = sum(c["n"] for c in cases.values())
        cells = [hh, str(meta[hh]["residents"]), str(total)]
        cells += [f"{cases[label]['n'] / total:.2f}" if cases.get(label) else "0.00"
                  for label, _, _ in CASES]
        for label, _, _ in CASES:
            c = cases.get(label, {})
            if c.get("n", 0) < MIN_N:
                cells.append(f"n={c.get('n', 0)}<{MIN_N}")
            else:
                cells.append(" / ".join(f"{c[m] / c['n']:.2f}" for m in models))
        lines.append("| " + " | ".join(cells) + " |")
    return lines, cnt


def case_totals(cnt: Dict[str, Dict[str, Dict[str, int]]]
                ) -> Dict[str, Dict[str, int]]:
    """Counters summed over homes, per case (orientation only; the
    per-home table is the result)."""
    out: Dict[str, Dict[str, int]] = {}
    for cases in cnt.values():
        for label, c in cases.items():
            t = out.setdefault(label, collections.defaultdict(int))
            for k, v in c.items():
                t[k] += v
    return {k: dict(v) for k, v in out.items()}


def fig_cases_by_home(cnt: Dict[str, Dict[str, Dict[str, int]]],
                      meta: Dict[str, Dict[str, Any]], out: pathlib.Path,
                      title: str) -> None:
    """Stacked shares of the four cases per home (one bar per home)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    homes = [h for h in sorted(meta, key=lambda h: (meta[h]["resident_group"], h))
             if cnt.get(h)]
    if not homes:
        return
    fig, ax = plt.subplots(figsize=(8.5, 0.34 * len(homes) + 1.8),
                           facecolor="#fcfcfb")
    ax.set_facecolor("#fcfcfb")
    ys = list(range(len(homes)))[::-1]
    left = [0.0] * len(homes)
    for (label, _, _), color in zip(CASES, CASE_COLORS):
        shares = []
        for h in homes:
            total = sum(c["n"] for c in cnt[h].values())
            shares.append(cnt[h][label]["n"] / total if cnt[h].get(label) else 0.0)
        ax.barh(ys, shares, left=left, color=color, height=0.72, label=label,
                edgecolor="#fcfcfb", linewidth=1)
        left = [a + b for a, b in zip(left, shares)]
    ax.set_yticks(ys)
    ax.set_yticklabels([f"{h} · {meta[h]['residents']}r · n={sum(c['n'] for c in cnt[h].values())}"
                        for h in homes], fontsize=7)
    ax.set_xlim(0, 1)
    ax.set_xlabel("share of the home's questions in this age range", fontsize=8,
                  color="#52514e")
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#e8e7e2")
    ax.tick_params(colors="#52514e", labelsize=7, length=0)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=4,
              frameon=False, fontsize=7.5)
    fig.suptitle(title, fontsize=9.5, color="#0b0b0b", x=0.01, ha="left", y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(out, dpi=150, facecolor="#fcfcfb")
    plt.close(fig)


def build(in_dir: pathlib.Path, workers: int, seeds: Sequence[int],
          households: Sequence[str],
          bank_dir: Optional[pathlib.Path] = None) -> pathlib.Path:
    meta = {h: m for h, m in household_meta(bank_dir).items() if h in households}
    tasks = [{"household": h, "seed": s, "bank_dir": str(bank_dir) if bank_dir else None}
             for h in sorted(meta) for s in seeds if bank_path(h, s, bank_dir).exists()]
    rows: List[Dict[str, Any]] = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        for res in pool.map(replay_bank, tasks):
            rows.extend(res)
    logger.info("%d questions replayed over %d banks", len(rows), len(tasks))
    all_bins = tuple(b for _, bins in AGE_BLOCKS for b in bins)
    correct = perpetua_correctness(in_dir, all_bins)
    md = [
        "# Why the survival models win at long ages: the four-case split",
        "",
        "Each question is classed by whether the object MOVED since its last "
        "sighting and whether a later room visit EXCLUDED the last-seen "
        "receptacle (found it without the object). The base class's "
        "exclusion is hard and permanent until the next sighting, so LastObs "
        "and MostFreq can never re-answer an excluded receptacle; the "
        "Perpetua models feed the same negative evidence into their filters "
        "and the emergence filter re-admits the receptacle after the "
        "expected absence. Seeds of a home are pooled; homes are not. "
        f"Cells under {MIN_N} questions are not quoted.",
        "",
    ]
    for title, bins in AGE_BLOCKS:
        lines, cnt = tabulate(rows, correct, meta, bins)
        totals = case_totals(cnt)
        (in_dir / f"perpetua_cases_totals_{'long' if bins == LONG_AGES else 'mid'}.json"
         ).write_text(json.dumps(totals, indent=1))
        slug = "long" if bins == LONG_AGES else "mid"
        fig_path = in_dir / f"perpetua_cases_by_home_{slug}.png"
        fig_cases_by_home(cnt, meta, fig_path,
                          f"Case shares per home, {title} (belief kept current, seeds pooled)")
        md += [f"## {title}", "", f"![]({fig_path.name})", "",
               "Accuracy per case, LastObs / MostFreq / " +
               " / ".join(sorted(correct)) + ":", ""] + lines + [""]
    path = in_dir / "perpetua_cases.md"
    path.write_text("\n".join(md) + "\n")
    return path


def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in-dir", type=pathlib.Path, default=DEFAULT_IN)
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--seeds", type=int, nargs="*", default=list(SEEDS))
    ap.add_argument("--households", nargs="*", default=None)
    ap.add_argument("--bank-dir", type=pathlib.Path, default=None)
    args = ap.parse_args()
    households = args.households or sorted(household_meta(args.bank_dir))
    path = build(args.in_dir, args.workers, args.seeds, households,
                 args.bank_dir)
    print(f"-> {path}")


if __name__ == "__main__":
    main()
