"""Mechanism table: where sensing pays, by age of evidence and regime.

For each belief of a sweep, one table with rows = age bin x regime
(regimes from bank data, as in
:mod:`baselines.exclusion_migration_replay`: ``truly_out``, ``came_back``,
``stale_in_house``) and columns:

* question share of the cell (test households);
* mean belief mass on OUT_OF_HOUSE at the passive (never-sense) answer,
  and the share of passive prediction sets that contain OUT_OF_HOUSE at
  the chosen alpha;
* first-sense hit rate under the chosen sensing policy (among questions
  it sensed at all, how often the FIRST sense returned the object);
* accuracy given the policy sensed at least once, and given it answered
  from memory (its own split, so the two are not a controlled
  comparison of sensing: the policy chose which questions to sense);
* passive accuracy (NeverSense) under the new semantics and, when an
  old-semantics sweep directory is given, under the old.

Outputs ``mechanism_by_age_case.csv`` and ``mechanism.md`` with the
three verdicts the brief asks for, computed from the numbers.

Usage:
  PYTHONPATH=src python -m baselines.conformal.mechanism \\
      --sweep results/conformal_sweep_v2/budget90 \\
      --old-sweep results/conformal_sweep_v1/alpha_to_0.5_budget90 \\
      --policy conformal_global_alpha0.3 --alpha 0.3 \\
      --bank banks/baselines/fleet/*__hh_0??_bank.jsonl \\
      --out results/conformal_sweep_v2
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import pathlib
from collections import defaultdict
from typing import Any, Dict, List, Optional, Sequence, Tuple

from baselines.bank import JsonlBank
from baselines.conformal.calibration import prediction_set
from baselines.exclusion_migration_replay import (AGE_LABELS, REGIMES,
                                                  QuestionFacts,
                                                  question_facts)

OUT = "OUT_OF_HOUSE"


def _read_dump(path: pathlib.Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with gzip.open(path, "rt") as fh:
        for line in fh:
            rows.append(json.loads(line))
    return rows


def _belief_keys(sweep: pathlib.Path) -> List[str]:
    keys = sorted({p.name.split("__", 1)[0]
                   for p in (sweep / "questions").glob("*__never_sense.jsonl.gz")})
    return keys


def _test_households(sweep: pathlib.Path) -> set[str]:
    calib = json.loads((sweep / "calibration.json").read_text())
    return {h for h, side in calib["split"].items() if side == "test"}


def _global_qhat(sweep: pathlib.Path, belief_name: str, alpha: float) -> float:
    calib = json.loads((sweep / "calibration.json").read_text())
    for t in calib["tables"]:
        if t["belief"] == belief_name and t["mode"] == "global" \
                and abs(float(t["alpha"]) - alpha) < 1e-9:
            return float(t["global_qhat"])
    raise KeyError(f"no global table for {belief_name} at alpha {alpha}")


def _cells(facts: Dict[Tuple[str, str], QuestionFacts],
           passive: Sequence[Dict[str, Any]],
           sensing: Sequence[Dict[str, Any]],
           old_passive: Sequence[Dict[str, Any]], qhat: float,
           receptacles: Dict[str, Sequence[str]]
           ) -> List[Dict[str, Any]]:
    def idx(r: Dict[str, Any]) -> Tuple[str, str]:
        return (str(r["episode_id"]), str(r["question_id"]))

    def acc(rs: Sequence[Dict[str, Any]]) -> Any:
        return (round(sum(int(r["correct"]) for r in rs) / len(rs), 4)
                if rs else "")

    groups: Dict[Tuple[str, str], Dict[str, List[Dict[str, Any]]]] = defaultdict(
        lambda: {"passive": [], "sensing": [], "old": []})
    for kind, rows in (("passive", passive), ("sensing", sensing),
                       ("old", old_passive)):
        for r in rows:
            f = facts.get(idx(r))
            if f is None:
                continue
            groups[(f.age_bin, f.regime)][kind].append(r)
    total = len(passive)
    out: List[Dict[str, Any]] = []
    for age in AGE_LABELS:
        for regime in REGIMES:
            g = groups.get((age, regime))
            if g is None:
                continue
            pas, sen, old = g["passive"], g["sensing"], g["old"]
            sensed = [r for r in sen if r["budget_spent"] > 0]
            memory = [r for r in sen if r["budget_spent"] == 0]
            first_hits = 0
            for r in sensed:
                first = next(a for a in r["actions"] if a["type"] == "sense")
                first_hits += int(r["object_id"] in first["contents"])
            sets_with_out = 0
            for r in pas:
                recs = receptacles[str(r["episode_id"])]
                sets_with_out += int(OUT in prediction_set(r["distribution"],
                                                           qhat, recs))
            out.append({
                "age_bin": age, "regime": regime, "n": len(pas),
                "share": round(len(pas) / total, 4) if total else "",
                "mean_out_mass": round(sum(float(r["distribution"].get(OUT, 0.0))
                                           for r in pas) / len(pas), 4) if pas else "",
                "set_contains_out": round(sets_with_out / len(pas), 4) if pas else "",
                "n_sensed": len(sensed),
                "sensed_share": round(len(sensed) / len(sen), 4) if sen else "",
                "first_sense_hit_rate": (round(first_hits / len(sensed), 4)
                                         if sensed else ""),
                "acc_given_sensed": acc(sensed),
                "acc_given_memory": acc(memory),
                "acc_passive_new": acc(pas),
                "acc_passive_old": acc(old),
                "n_old": len(old)})
    return out


def verdicts(belief: str, rows: Sequence[Dict[str, Any]]) -> List[str]:
    def pooled(regime: str, key_num: str, key_den: str = "n") -> Tuple[float, int]:
        num = den = 0.0
        for r in rows:
            if r["regime"] != regime or r[key_num] == "":
                continue
            weight = float(r[key_den])
            num += float(r[key_num]) * weight
            den += weight
        return (num / den if den else float("nan")), int(den)

    def fmt(x: float) -> str:
        return "n/a" if x != x else f"{x:.3f}"

    lines = [f"**{belief}**"]
    s_acc, s_n = pooled("stale_in_house", "acc_given_sensed", "n_sensed")
    m_acc, m_n = pooled("stale_in_house", "acc_given_memory", "n")
    lines.append(f"- sensing pays in stale_in_house: accuracy given sensed "
                 f"{fmt(s_acc)} (n={s_n}) vs answered from memory {fmt(m_acc)}: "
                 f"**{'held' if s_acc > m_acc else ('no questions' if s_n == 0 else 'did not hold')}** (the "
                 f"policy chose which questions to sense, so this is the "
                 f"policy's own split, not a controlled contrast)")
    c_new, c_n = pooled("came_back", "acc_passive_new")
    c_old, c_on = pooled("came_back", "acc_passive_old", "n_old")
    one_hot = belief.startswith("LastObservation")
    lines.append(f"- came_back addressable by graded beliefs, passive accuracy "
                 f"new {fmt(c_new)} (n={c_n})"
                 + (f" vs old {fmt(c_old)}" if c_on else "")
                 + (": one-hot belief, not expected to move" if one_hot else
                    f": **{'held' if (not c_on and c_new > 0) or (c_on and c_new > c_old) else 'did not hold'}**"))
    t_hit, t_n = pooled("truly_out", "first_sense_hit_rate", "n_sensed")
    t_new, t_nn = pooled("truly_out", "acc_passive_new")
    t_old, t_on = pooled("truly_out", "acc_passive_old", "n_old")
    lines.append(f"- truly_out near-worthless per single sense: first-sense hit "
                 f"rate {fmt(t_hit)} (n={t_n}): "
                 f"**{'no questions' if t_n == 0 else 'held' if t_hit < 0.05 else 'did not hold'}**; reachable "
                 f"by passive answering: memory accuracy new {fmt(t_new)} "
                 f"(n={t_nn})" + (f" vs old {fmt(t_old)}" if t_on else "")
                 + f": **{'no questions' if t_nn == 0 else 'held' if t_new > (t_old if t_on else 0.0) else 'did not hold'}**")
    return lines


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--sweep", type=pathlib.Path, required=True)
    parser.add_argument("--old-sweep", type=pathlib.Path, default=None)
    parser.add_argument("--policy", default="conformal_global_alpha0.3",
                        help="dump slug of the sensing policy to read")
    parser.add_argument("--alpha", type=float, default=0.3,
                        help="alpha whose global qhat defines the passive set")
    parser.add_argument("--bank", nargs="+", type=pathlib.Path, required=True)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    args = parser.parse_args(argv)

    facts: Dict[Tuple[str, str], QuestionFacts] = {}
    receptacles: Dict[str, Sequence[str]] = {}
    for bank in args.bank:
        for episode in JsonlBank(path=bank).episodes():
            receptacles[episode.episode_id] = episode.receptacle_ids
            for qid, f in question_facts(episode).items():
                facts[(episode.episode_id, qid)] = f
    test = _test_households(args.sweep)
    calib = json.loads((args.sweep / "calibration.json").read_text())
    names = {t["belief"] for t in calib["tables"]}
    all_rows: List[Dict[str, Any]] = []
    md = ["# Mechanism table: age of evidence x regime", "",
          f"Sweep `{args.sweep}`; sensing policy `{args.policy}`; passive "
          f"sets at alpha {args.alpha:g} (global). Regimes from bank data. "
          "Cells with fewer than 30 questions are listed but not quoted "
          "in the verdicts' pooled numbers beyond their weight.", ""]
    for key in _belief_keys(args.sweep):
        passive = [r for r in _read_dump(args.sweep / "questions" / f"{key}__never_sense.jsonl.gz")
                   if r["household_id"] in test]
        sensing = _read_dump(args.sweep / "questions" / f"{key}__{args.policy}.jsonl.gz")
        belief = str(passive[0]["belief"])
        old: List[Dict[str, Any]] = []
        if args.old_sweep is not None:
            old_path = args.old_sweep / "questions" / f"{key}__never_sense.jsonl.gz"
            if old_path.exists():
                old = [r for r in _read_dump(old_path) if r["household_id"] in test]
        qhat = _global_qhat(args.sweep, belief, args.alpha) if belief in names else 1.0
        rows = _cells(facts, passive, sensing, old, qhat, receptacles)
        for r in rows:
            all_rows.append({"belief": belief, **r})
        fields = list(rows[0]) if rows else []
        md += [f"## {belief}", "",
               "| " + " | ".join(fields) + " |",
               "|" + "|".join("---" for _ in fields) + "|"]
        md += ["| " + " | ".join(str(r[f]) for f in fields) + " |" for r in rows]
        md += ["", *verdicts(belief, rows), ""]
    args.out.mkdir(parents=True, exist_ok=True)
    with open(args.out / "mechanism_by_age_case.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(all_rows[0]))
        writer.writeheader()
        writer.writerows(all_rows)
    (args.out / "mechanism.md").write_text("\n".join(md) + "\n")
    print("\n".join(line for line in md if line.startswith("- ") or line.startswith("**")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
