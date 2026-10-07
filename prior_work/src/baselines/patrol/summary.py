"""Pool patrol run logs into the report tables.

    python3 -m baselines.patrol.summary --logs results/overnight/classical/*.jsonl --out report_dir

Scores: right location +1, wrong -1, ABSTAIN 0. An agent abstains when its
top probability is under the threshold (classical agents and the LLM
confidence route) or when it answered ABSTAIN outright (the LLM direct
route, ``answer == "ABSTAIN"``). Reported per day (with shift days
marked), per truth type (in-house spot, ON_PERSON, OUT_OF_HOUSE), per
shift / non-shift day, per patrol density, and look on / off.
"""
from __future__ import annotations

import argparse
import glob
import json
import pathlib
import sys
from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Sequence

from baselines.types import ON_PERSON, OUT_OF_HOUSE

THRESHOLDS = (None, 0.4, 0.5, 0.6)
"""None = only outright ABSTAIN answers count (the LLM direct route; classical agents never abstain there)."""
DAY_SHORT = {"Monday": "Mon", "Tuesday": "Tue", "Wednesday": "Wed", "Thursday": "Thu",
             "Friday": "Fri", "Saturday": "Sat", "Sunday": "Sun"}


def truth_kind(rec: str) -> str:
    return "on_person" if rec == ON_PERSON else "out_of_house" if rec == OUT_OF_HOUSE else "spot"


def load_logs(paths: Iterable[str]) -> List[dict]:
    rows = []
    for p in sorted(paths):
        with open(p) as f:
            rows += [json.loads(l) for l in f if l.strip()]
    return rows


class Cell:
    """Counts for one group of questions at one abstain threshold."""

    def __init__(self) -> None:
        self.n = 0; self.answered = 0; self.right = 0; self.abstained = 0; self.direct_abstain = 0

    def add(self, r: dict, threshold: Optional[float]) -> None:
        self.n += 1
        direct = r["answer"] == "ABSTAIN"
        abstain = direct or (threshold is not None and r.get("top_prob", 1.0) < threshold)
        if abstain:
            self.abstained += 1
            self.direct_abstain += int(direct)
        else:
            self.answered += 1
            self.right += int(r["correct"])

    @property
    def acc_all(self) -> float:      # accuracy over every question (abstain counts as wrong)
        return self.right / self.n if self.n else float("nan")

    @property
    def acc_answered(self) -> float:
        return self.right / self.answered if self.answered else float("nan")

    @property
    def abstain_rate(self) -> float:
        return self.abstained / self.n if self.n else float("nan")

    @property
    def mean_score(self) -> float:
        wrong = self.answered - self.right
        return (self.right - wrong) / self.n if self.n else float("nan")

    def as_dict(self) -> dict:
        return {"n": self.n, "answered": self.answered, "right": self.right, "abstained": self.abstained,
                "direct_abstain": self.direct_abstain, "acc_all": round(self.acc_all, 4),
                "acc_answered": round(self.acc_answered, 4), "abstain_rate": round(self.abstain_rate, 4),
                "mean_score": round(self.mean_score, 4)}


def group(rows: Sequence[dict], keys: Sequence[str], threshold: Optional[float]) -> Dict[tuple, Cell]:
    cells: Dict[tuple, Cell] = defaultdict(Cell)
    for r in rows:
        cells[tuple(r.get(k) for k in keys)].add(r, threshold)
    return cells


def fmt(x: float, pct: bool = True) -> str:
    if x != x:
        return "-"
    return f"{100 * x:.0f}%" if pct else f"{x:+.2f}"


def agent_name(r: dict) -> str:
    return r.get("agent") or r["belief"]


def report(rows: List[dict], shift_days: Dict[str, List[int]], day_names: Dict[int, str],
           title: str) -> str:
    for r in rows:
        r["agent"] = agent_name(r)
        r["shift"] = r["day_index"] in set(shift_days.get(r["household"], []))
        r["truth_kind"] = truth_kind(r["truth"])
    households = sorted({r["household"] for r in rows})
    agents = sorted({r["agent"] for r in rows})
    densities = sorted({r["patrol_hours"] for r in rows})
    looks = sorted({r["look"] for r in rows})
    days = sorted({r["day_index"] for r in rows})
    L = [f"# {title}", "",
         f"{len(households)} households ({', '.join(households)}), {len(agents)} agents, "
         f"patrol every {densities} h, look on/off = {looks}. "
         f"{len(rows)} agent-question records. Shift days per household: "
         + "; ".join(f"{h}: {shift_days.get(h, [])}" for h in households) + ".", ""]
    per_hh_counts = defaultdict(int)
    for r in rows:
        per_hh_counts[r["household"]] += 1
    L += ["Records per household: " + ", ".join(f"{h} {per_hh_counts[h]}" for h in households), ""]

    # 1. accuracy per day per agent (no abstain), one table per (density, look)
    L += ["## 1. Accuracy per day per agent (no abstaining; shift days marked *)", ""]
    n_shift_by_day = defaultdict(int)
    for h in households:
        for d in shift_days.get(h, []):
            n_shift_by_day[d] += 1
    for ph in densities:
        for lk in looks:
            sub = [r for r in rows if r["patrol_hours"] == ph and r["look"] == lk]
            if not sub:
                continue
            L += [f"### patrol every {ph} h, look {lk}", ""]
            head = "| agent | " + " | ".join(
                f"{DAY_SHORT.get(day_names.get(d, str(d)), d)}{'*' if n_shift_by_day[d] == len(households) else ('°' if n_shift_by_day[d] else '')}"
                for d in days) + " | all | shift | non-shift | spot | on_person | out |"
            L += [head, "|" + "---|" * (len(days) + 7)]
            byday = group(sub, ("agent", "day_index"), None)
            byshift = group(sub, ("agent", "shift"), None)
            bykind = group(sub, ("agent", "truth_kind"), None)
            byagent = group(sub, ("agent",), None)
            for a in agents:
                if (a,) not in byagent:
                    continue
                cells = [byday.get((a, d), Cell()) for d in days]
                L.append(f"| {a} | " + " | ".join(fmt(c.acc_all) for c in cells)
                         + f" | {fmt(byagent[(a,)].acc_all)} | {fmt(byshift.get((a, True), Cell()).acc_all)}"
                         f" | {fmt(byshift.get((a, False), Cell()).acc_all)}"
                         f" | {fmt(bykind.get((a, 'spot'), Cell()).acc_all)} | {fmt(bykind.get((a, 'on_person'), Cell()).acc_all)}"
                         f" | {fmt(bykind.get((a, 'out_of_house'), Cell()).acc_all)} |")
            moved = group([r for r in sub if r.get("moved_24h")], ("agent",), None)
            still = group([r for r in sub if not r.get("moved_24h")], ("agent",), None)
            L += ["", "Objects that moved in the 24 h before the question vs. objects that did not:", "",
                  "| agent | moved: n | moved: acc | still: n | still: acc |", "|---|---|---|---|---|"]
            for a in agents:
                if (a,) in moved or (a,) in still:
                    L.append(f"| {a} | {moved.get((a,), Cell()).n} | {fmt(moved.get((a,), Cell()).acc_all)} "
                             f"| {still.get((a,), Cell()).n} | {fmt(still.get((a,), Cell()).acc_all)} |")
            n_kind = group(sub, ("truth_kind",), None)
            L += ["", "Questions by truth type: " + ", ".join(
                f"{k} {n_kind[(k,)].n // max(1, len({r['agent'] for r in sub}))}" for k in sorted(k for (k,) in n_kind)),
                "(* every household shifts that day; ° some households do)", ""]

    # 2. accuracy vs patrol density
    L += ["## 2. Accuracy vs patrol density (all days, no abstaining)", ""]
    for lk in looks:
        sub = [r for r in rows if r["look"] == lk]
        L += [f"### look {lk}", "",
              "| agent | " + " | ".join(f"every {ph} h" for ph in densities) + " |", "|" + "---|" * (len(densities) + 1)]
        cells = group(sub, ("agent", "patrol_hours"), None)
        for a in agents:
            if not any((a, ph) in cells for ph in densities):
                continue
            L.append(f"| {a} | " + " | ".join(fmt(cells.get((a, ph), Cell()).acc_all) for ph in densities) + " |")
        L.append("")

    # 3. look on vs off
    L += ["## 3. What the free look is worth (all densities pooled)", "",
          "| agent | look off | look voi | look top | before-look answer (voi runs) | found by voi look | found by top look |",
          "|---|---|---|---|---|---|---|"]
    bylook = group(rows, ("agent", "look"), None)
    for a in agents:
        sub = [r for r in rows if r["look"] == "voi" and r["agent"] == a]
        sub_top = [r for r in rows if r["look"] == "top" and r["agent"] == a]
        before = sum(r.get("correct_before_look", r["correct"]) for r in sub) / len(sub) if sub else float("nan")
        found = sum(bool(r.get("found_in_look")) for r in sub) / len(sub) if sub else float("nan")
        found_top = sum(bool(r.get("found_in_look")) for r in sub_top) / len(sub_top) if sub_top else float("nan")
        L.append(f"| {a} | {fmt(bylook.get((a, 'off'), Cell()).acc_all)} | {fmt(bylook.get((a, 'voi'), Cell()).acc_all)} "
                 f"| {fmt(bylook.get((a, 'top'), Cell()).acc_all)} | {fmt(before)} | {fmt(found)} | {fmt(found_top)} |")
    L.append("")
    # look value by confidence bucket
    L += ["Look gain by confidence before the look (pooled over agents, look-on runs):", "",
          "| top prob before look | n | acc before look | acc after look |", "|---|---|---|---|"]
    buckets = [(0.0, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 0.95), (0.95, 1.01)]
    for lo, hi in buckets:
        sub = [r for r in rows if r["look"] != "off" and lo <= r.get("top_prob_before_look", 1.0) < hi]
        if not sub:
            continue
        L.append(f"| [{lo:.2f}, {hi:.2f}) | {len(sub)} | {fmt(sum(r.get('correct_before_look', r['correct']) for r in sub) / len(sub))} "
                 f"| {fmt(sum(r['correct'] for r in sub) / len(sub))} |")
    L.append("")

    # 4. abstain per day
    L += ["## 4. Abstain rate and answered-accuracy per day (look voi for classical agents, look on for LLM agents; all densities pooled)", ""]
    sub_all = [r for r in rows if r["look"] in ("voi", "llm")] or rows
    for thr in THRESHOLDS:
        L += [f"### {'outright ABSTAIN answers only (LLM direct route)' if thr is None else 'threshold ' + str(thr) + ' on the top probability / stated confidence, plus outright ABSTAIN answers'}", "",
              "| agent | " + " | ".join(f"{DAY_SHORT.get(day_names.get(d, str(d)), d)} abstain / acc" for d in days)
              + " | shift abstain / acc | non-shift abstain / acc | mean score |",
              "|" + "---|" * (len(days) + 4)]
        byday = group(sub_all, ("agent", "day_index"), thr)
        byshift = group(sub_all, ("agent", "shift"), thr)
        byagent = group(sub_all, ("agent",), thr)
        for a in agents:
            if (a,) not in byagent:
                continue
            cells = [byday.get((a, d), Cell()) for d in days]
            L.append(f"| {a} | " + " | ".join(f"{fmt(c.abstain_rate)} / {fmt(c.acc_answered)}" for c in cells)
                     + f" | {fmt(byshift.get((a, True), Cell()).abstain_rate)} / {fmt(byshift.get((a, True), Cell()).acc_answered)}"
                     f" | {fmt(byshift.get((a, False), Cell()).abstain_rate)} / {fmt(byshift.get((a, False), Cell()).acc_answered)}"
                     f" | {fmt(byagent[(a,)].mean_score, pct=False)} |")
        L.append("")
    # 5. told vs not told (LLM agents)
    told_agents = sorted({a for a in agents if "/told/" in a})
    if told_agents:
        L += ["## 5. Told vs not told, per day (LLM agents; hint message in the prompt from each shift day's first question on)", "",
              "| agent | " + " | ".join(f"{DAY_SHORT.get(day_names.get(d, str(d)), d)}{'*' if n_shift_by_day[d] == len(households) else ('°' if n_shift_by_day[d] else '')} told / not" for d in days)
              + " | all told / not | shift told / not | non-shift told / not |", "|" + "---|" * (len(days) + 4)]
        byday = group(rows, ("agent", "day_index"), None)
        byshift = group(rows, ("agent", "shift"), None)
        byagent = group(rows, ("agent",), None)
        for a in told_agents:
            b = a.replace("/told/", "/not_told/")
            L.append(f"| {a.replace('/told', '')} | " + " | ".join(
                f"{fmt(byday.get((a, d), Cell()).acc_all)} / {fmt(byday.get((b, d), Cell()).acc_all)}" for d in days)
                + f" | {fmt(byagent.get((a,), Cell()).acc_all)} / {fmt(byagent.get((b,), Cell()).acc_all)}"
                f" | {fmt(byshift.get((a, True), Cell()).acc_all)} / {fmt(byshift.get((b, True), Cell()).acc_all)}"
                f" | {fmt(byshift.get((a, False), Cell()).acc_all)} / {fmt(byshift.get((b, False), Cell()).acc_all)} |")
        L.append("")
        # fallback and look-request rates
        L += ["LLM parse fallbacks and look requests:", "", "| agent | n | fallback | asked for a look | look found it | direct ABSTAIN |", "|---|---|---|---|---|---|"]
        for a in agents:
            sub = [r for r in rows if r["agent"] == a and "fallback" in r]
            if not sub:
                continue
            L.append(f"| {a} | {len(sub)} | {fmt(sum(r['fallback'] for r in sub) / len(sub))} "
                     f"| {fmt(sum(r.get('look_room') is not None for r in sub) / len(sub))} "
                     f"| {fmt(sum(bool(r.get('found_in_look')) for r in sub) / len(sub))} "
                     f"| {fmt(sum(r.get('abstain_direct', False) for r in sub) / len(sub))} |")
        L.append("")
    # 6. paired by household: each household is its own control
    L += ["## 6. Shift effect paired by household", "",
          "For every household and agent: accuracy on the household's own shift days minus accuracy on its own "
          "non-shift days (`shift - non`), then the mean and the count of households where the difference is negative. "
          "Also aligned on each household's first major-event day (guests or illness, weekend days excluded): "
          "accuracy on the day before, the day, and the day after, mean over households that have such a day. "
          "Spot-only columns use in-house truths only, so the OUT_OF_HOUSE mix cannot drive the difference.", ""]
    major_first: Dict[str, Optional[int]] = {}
    for h in households:
        cands = [d for d in shift_days.get(h, []) if day_names.get(d) not in ("Saturday", "Sunday")]
        major_first[h] = min(cands) if cands else None
    for lk in looks:
        sub = [r for r in rows if r["look"] == lk]
        if not sub:
            continue
        L += [f"### look {lk}", "",
              "| agent | mean(shift - non) | households with a drop | mean(shift - non), spot only | drop, spot only | "
              "event day -1 / 0 / +1 | event day -1 / 0 / +1, spot only | households with an event day |",
              "|---|---|---|---|---|---|---|---|"]
        by = group(sub, ("agent", "household", "shift"), None)
        by_spot = group([r for r in sub if r["truth_kind"] == "spot"], ("agent", "household", "shift"), None)
        byday = group(sub, ("agent", "household", "day_index"), None)
        byday_spot = group([r for r in sub if r["truth_kind"] == "spot"], ("agent", "household", "day_index"), None)
        for a in sorted({r["agent"] for r in sub}):
            diffs, diffs_spot = [], []
            for h in households:
                c1, c0 = by.get((a, h, True)), by.get((a, h, False))
                if c1 and c0 and c1.n and c0.n:
                    diffs.append(c1.acc_all - c0.acc_all)
                s1, s0 = by_spot.get((a, h, True)), by_spot.get((a, h, False))
                if s1 and s0 and s1.n and s0.n:
                    diffs_spot.append(s1.acc_all - s0.acc_all)
            aligned = [[], [], []]; aligned_spot = [[], [], []]
            for h in households:
                d0 = major_first[h]
                if d0 is None:
                    continue
                for k, d in enumerate((d0 - 1, d0, d0 + 1)):
                    c = byday.get((a, h, d)); cs = byday_spot.get((a, h, d))
                    if c and c.n:
                        aligned[k].append(c.acc_all)
                    if cs and cs.n:
                        aligned_spot[k].append(cs.acc_all)
            mean = lambda v: (sum(v) / len(v)) if v else float("nan")
            pm = lambda v: ("-" if not v else f"{100 * mean(v):+.1f}")
            L.append(f"| {a} | {pm(diffs)} | {sum(d < 0 for d in diffs)}/{len(diffs)} | {pm(diffs_spot)} | "
                     f"{sum(d < 0 for d in diffs_spot)}/{len(diffs_spot)} | "
                     + " / ".join(fmt(mean(v)) for v in aligned) + " | " + " / ".join(fmt(mean(v)) for v in aligned_spot)
                     + f" | {len(aligned[1])} |")
        L.append("")
    # per-household day grid for one representative agent set
    L += ["### Per-household accuracy per day (look voi / llm; `*` = that household's shift day)", ""]
    sub = [r for r in rows if r["look"] in ("voi", "llm")] or rows
    byday = group(sub, ("household", "agent", "day_index"), None)
    for h in households:
        sd = set(shift_days.get(h, []))
        L += [f"**{h}** (shift days: {', '.join(day_names.get(d, str(d))[:3] for d in sorted(sd)) or 'none'})", "",
              "| agent | " + " | ".join(f"{DAY_SHORT.get(day_names.get(d, str(d)), d)}{'*' if d in sd else ''}" for d in days) + " |",
              "|" + "---|" * (len(days) + 1)]
        for a in sorted({r["agent"] for r in sub if r["household"] == h}):
            L.append(f"| {a} | " + " | ".join(fmt(byday.get((h, a, d), Cell()).acc_all) for d in days) + " |")
        L.append("")
    return "\n".join(L) + "\n"


def shift_days_from_banks(bank_paths: Iterable[str]) -> tuple:
    """(household -> shift days, day index -> weekday, (household, question) -> moved in last 24 h)."""
    shift: Dict[str, List[int]] = {}
    names: Dict[int, str] = {}
    moved: Dict[tuple, bool] = {}
    for p in sorted(bank_paths):
        rows = [json.loads(l) for l in open(p) if l.strip()]
        h = rows[0]
        shift[h["household_id"]] = list(h["shift_days"])
        names.update({int(k): v for k, v in h["day_names"].items()})
        truth_t: Dict[str, List[int]] = defaultdict(list)
        for r in rows:
            if r["kind"] == "truth":
                truth_t[r["object_id"]].append(int(r["t"]))
        for r in rows:
            if r["kind"] == "question":
                ts = truth_t[r["object_id"]]
                moved[(h["household_id"], r["question_id"])] = any(
                    r["t_query"] - 86400 < t <= r["t_query"] for t in ts if t > 0)
    return shift, names, moved


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--logs", nargs="+", required=True)
    ap.add_argument("--banks", nargs="+", required=True, help="bank files (for shift days and day names)")
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--title", default="patrol evaluation")
    a = ap.parse_args(argv)
    logs = [p for pat in a.logs for p in glob.glob(pat)]
    banks = [p for pat in a.banks for p in glob.glob(pat)]
    rows = load_logs(logs)
    shift, names, moved = shift_days_from_banks(banks)
    for r in rows:
        r["moved_24h"] = moved.get((r["household"], r["question_id"]), False)
    text = report(rows, shift, names, a.title)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
