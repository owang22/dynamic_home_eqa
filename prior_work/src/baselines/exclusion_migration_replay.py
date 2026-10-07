"""Paired replay: the negative-evidence migration's evidence.

Ran the frozen panel plus PerpetuaStar under NeverSense and
SequentialSearch, at the bank budget, over the 20 seed-0 fleet banks,
TWICE: with the pre-migration semantics (a hard, permanent veto on every
looked-at receptacle, uniform redistribution, no floor; reproduced at
the time by a replay-only ``legacy_exclusion_veto`` flag on the belief
base class) and with the migrated pipeline (floor mix plus decaying soft
suppression, :mod:`baselines.beliefs.base`). Same banks, same seeds,
same policies: the only difference was the belief's treatment of an
empty look.

HISTORICAL RECORD. The flag and the old code path were deleted in the
migration's cleanup phase (commit history: "Beliefs: soft negative
evidence over the full location space" added them, the cleanup commit
removed them), so the ``old`` arm can no longer be reproduced from the
current tree; :func:`run_task` refuses it loudly rather than silently
running the new semantics under the old label. The committed report
under ``reports/baselines/exclusion_migration/`` is the permanent
record of the comparison. ``--render-only`` (rebuild ``README.md`` from
the committed csvs) still works; the module is kept so the exact
procedure that produced the report stays readable.

Every split is computed from bank DATA, never from the veto:

* age bin: hours since the object's newest ambient positive sighting at
  or before the query (the tour counts; never sighted = oldest bin);
* regime: ``truly_out`` = truth is the unsensable location at t_query;
  ``came_back`` = truth EQUALS the object's last-seen receptacle AND an
  ambient visit observed that receptacle without the object after the
  last sighting; ``stale_in_house`` = everything else.

Outputs under ``reports/baselines/exclusion_migration/``: ``headline.csv``
(accuracy per belief x policy, old vs new), ``by_age.csv``,
``by_regime.csv``, ``out_of_house.csv`` (OUT_OF_HOUSE answers fired /
correct, old vs new, per age bin), ``README.md`` (generated, with the
expected signature and which parts held) and ``provenance.json``.

Usage:
  PYTHONPATH=src python -m baselines.exclusion_migration_replay --workers 40

One-off, kept for provenance; the flag it depends on is deleted after
the migration and this module goes with it or stays as a record.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import dataclasses
import datetime
import json
import logging
import pathlib
from collections import defaultdict
from typing import Any, Dict, List, Optional, Sequence, Tuple

from baselines.bank import JsonlBank
from baselines.cli import build_agent, git_state
from baselines.conformal.calibration import (DEFAULT_AGE_EDGES_H,
                                             age_bin_index, age_bin_labels)
from baselines.harness import run_episode
from baselines.healthcheck import BELIEF_PANEL
from baselines.types import Episode, SenseResult

logger = logging.getLogger(__name__)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_BANK_GLOB = "banks/baselines/fleet/*__hh_0??_bank.jsonl"
DEFAULT_OUT = REPO_ROOT / "reports" / "baselines" / "exclusion_migration"

BELIEFS: Tuple[Tuple[str, Dict[str, Any]], ...] = (
    *((str(spec["name"]), dict(spec)) for spec in BELIEF_PANEL),
    ("perpetua_star", {"name": "perpetua_star"}),
)
POLICIES = ("never_sense", "sequential_search")
SEMANTICS = ("old", "new")
REGIMES = ("truly_out", "came_back", "stale_in_house")
AGE_LABELS = age_bin_labels(DEFAULT_AGE_EDGES_H)
SEED = 0


# ------------------------------------------------------------- facts

@dataclasses.dataclass(frozen=True)
class QuestionFacts:
    question_id: str
    object_id: str
    t_query: int
    truth: str
    last_seen: Optional[str]
    age_bin: str
    regime: str


def question_facts(episode: Episode) -> Dict[str, QuestionFacts]:
    """Per question: truth, last ambient sighting, age bin and regime,
    from the bank alone."""
    unsensable = set(episode.unsensable_receptacle_ids)
    sightings: Dict[str, List[Tuple[int, str]]] = defaultdict(list)
    for obs in (*episode.initial_observations, *episode.scripted_observations):
        sightings[obs.object_id].append((obs.t, obs.receptacle_id))
    for seq in sightings.values():
        seq.sort()
    looks = [e for e in episode.evidence_stream() if isinstance(e, SenseResult)]
    facts: Dict[str, QuestionFacts] = {}
    for day in episode.questions_by_day:
        for q in day:
            truth = episode.true_location(q.object_id, q.t_query)
            past = [(t, r) for t, r in sightings.get(q.object_id, [])
                    if t <= q.t_query]
            if past:
                t_last, last_seen = past[-1]
                age_h: Optional[float] = (q.t_query - t_last) / 3600.0
            else:
                t_last, last_seen, age_h = -1, None, None
            if truth in unsensable:
                regime = "truly_out"
            elif last_seen is not None and truth == last_seen and any(
                    e.receptacle_id == last_seen and t_last < e.t <= q.t_query
                    and q.object_id not in e.contents for e in looks):
                regime = "came_back"
            else:
                regime = "stale_in_house"
            facts[q.question_id] = QuestionFacts(
                question_id=q.question_id, object_id=q.object_id,
                t_query=q.t_query, truth=truth, last_seen=last_seen,
                age_bin=AGE_LABELS[age_bin_index(age_h, DEFAULT_AGE_EDGES_H)],
                regime=regime)
    return facts


# ------------------------------------------------------------- tasks

def run_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """One (bank, belief, policy, semantics) replay; returns compact
    per-question outcomes plus the bank's question facts.

    The ``old`` arm is refused: the flag it needed is gone (module
    docstring). Running it silently under the new pipeline would file
    new-semantics numbers under the old label.
    """
    if task["semantics"] == "old":
        raise RuntimeError(
            "the old-semantics arm needs the legacy_exclusion_veto flag, "
            "deleted in the migration's cleanup phase; the committed report "
            "under reports/baselines/exclusion_migration/ is the record, and "
            "--render-only rebuilds it from the csvs")
    episode = next(iter(JsonlBank(path=pathlib.Path(task["bank"])).episodes()))
    facts = question_facts(episode)
    spec = dict(task["belief_spec"])
    agent = build_agent(spec, {"name": task["policy"]}, SEED,
                        episode.episode_id)
    unsensable = set(episode.unsensable_receptacle_ids)
    rows = []
    for record in run_episode(agent, episode):
        f = facts[record.question_id]
        rows.append({
            "household": episode.household_id, "question_id": record.question_id,
            "age_bin": f.age_bin, "regime": f.regime,
            "correct": int(record.correct), "spent": record.budget_spent,
            "answered_out": int(record.answer_receptacle in unsensable),
            "truth_out": int(f.truth in unsensable)})
    return {"belief_key": task["belief_key"], "belief": agent.belief.name,
            "policy": agent.policy.name, "semantics": task["semantics"],
            "household": episode.household_id, "rows": rows}


# ------------------------------------------------------------- aggregate

Key = Tuple[str, str, str]      # (belief, policy, semantics)


def _acc(rows: Sequence[Dict[str, Any]]) -> Tuple[int, int]:
    return sum(int(r["correct"]) for r in rows), len(rows)


def aggregate(results: Sequence[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    by_key: Dict[Key, List[Dict[str, Any]]] = defaultdict(list)
    for res in results:
        by_key[(res["belief"], res["policy"], res["semantics"])].extend(res["rows"])
    beliefs = list(dict.fromkeys(k[0] for k in by_key))
    policies = list(dict.fromkeys(k[1] for k in by_key))

    def paired(split_name: str, split_values: Sequence[str],
               select: Any) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for b in beliefs:
            for p in policies:
                for v in split_values:
                    cells = {}
                    for s in SEMANTICS:
                        rows = [r for r in by_key[(b, p, s)] if select(r, v)]
                        cells[s] = _acc(rows)
                    n = cells["new"][1]
                    row: Dict[str, Any] = {"belief": b, "policy": p,
                                           split_name: v, "n": n}
                    for s in SEMANTICS:
                        k, m = cells[s]
                        row[f"acc_{s}"] = round(k / m, 4) if m else ""
                    row["delta"] = (round(cells["new"][0] / n
                                          - cells["old"][0] / n, 4)
                                    if n else "")
                    out.append(row)
        return out

    headline = paired("split", ("all",), lambda r, v: True)
    by_age = paired("age_bin", AGE_LABELS, lambda r, v: r["age_bin"] == v)
    by_regime = paired("regime", REGIMES, lambda r, v: r["regime"] == v)

    out_rows: List[Dict[str, Any]] = []
    for b in beliefs:
        for p in policies:
            for label in (*AGE_LABELS, "all"):
                row: Dict[str, Any] = {"belief": b, "policy": p,
                                       "age_bin": label}
                for s in SEMANTICS:
                    rows = [r for r in by_key[(b, p, s)]
                            if label == "all" or r["age_bin"] == label]
                    fired = sum(int(r["answered_out"]) for r in rows)
                    right = sum(int(r["answered_out"]) * int(r["correct"])
                                for r in rows)
                    truth = sum(int(r["truth_out"]) for r in rows)
                    row["n"] = len(rows)
                    row["truth_out"] = truth
                    row[f"fired_{s}"] = fired
                    row[f"correct_{s}"] = right
                    row[f"fired_over_truth_{s}"] = (
                        round(fired / truth, 3) if truth else "")
                out_rows.append(row)
    return {"headline": headline, "by_age": by_age, "by_regime": by_regime,
            "out_of_house": out_rows}


# ------------------------------------------------------------- report

def _table(rows: Sequence[Dict[str, Any]], fields: Sequence[str]) -> List[str]:
    lines = ["| " + " | ".join(fields) + " |",
             "|" + "|".join("---" for _ in fields) + "|"]
    for r in rows:
        lines.append("| " + " | ".join(str(r.get(f, "")) for f in fields) + " |")
    return lines


def _short(name: str) -> str:
    return name.split("(", 1)[0]


def render_readme(tables: Dict[str, List[Dict[str, Any]]],
                  provenance: Dict[str, Any]) -> str:
    head = tables["headline"]
    age = tables["by_age"]
    reg = tables["by_regime"]
    out = tables["out_of_house"]
    never = "NeverSense"
    search = "SequentialSearch"
    beliefs = list(dict.fromkeys(r["belief"] for r in head))
    graded = [b for b in beliefs if not b.startswith("LastObservation")]
    long_bins = ("24-72h", "72h+")

    def find(rows: Sequence[Dict[str, Any]], **where: Any) -> Dict[str, Any]:
        for r in rows:
            if all(r.get(k) == v for k, v in where.items()):
                return r
        return {}

    lines = [
        "# Exclusion-veto migration: paired replay",
        "",
        f"Generated {provenance['generated']} at commit "
        f"`{provenance['git_commit'][:12]}`"
        f"{' (dirty tree)' if provenance['git_dirty'] else ''} by "
        "`python -m baselines.exclusion_migration_replay`. "
        f"{provenance['n_banks']} seed-0 fleet banks, bank budget, seed "
        f"{SEED}; beliefs: the frozen panel and PerpetuaStar; policies: "
        "NeverSense and SequentialSearch. `old` = the pre-migration hard "
        "permanent veto (uniform redistribution, no floor; the "
        "`legacy_exclusion_veto` flag); `new` = the floor-mix plus "
        "decaying-suppression pipeline. Age bins and regimes come from "
        "the bank data (module docstring), never from either rule.",
        "",
        "## Headline accuracy",
        "",
        *_table(head, ("belief", "policy", "n", "acc_old", "acc_new", "delta")),
        "",
        "## By age of the last ambient sighting",
        "",
        *_table(age, ("belief", "policy", "age_bin", "n", "acc_old",
                      "acc_new", "delta")),
        "",
        "## By regime (from data)",
        "",
        "truly_out = truth OUT_OF_HOUSE at t_query; came_back = truth equals "
        "the last-seen receptacle and an ambient visit saw that receptacle "
        "empty of the object after the last sighting; stale_in_house = the "
        "rest.",
        "",
        *_table(reg, ("belief", "policy", "regime", "n", "acc_old",
                      "acc_new", "delta")),
        "",
        "## OUT_OF_HOUSE answers: fired / correct",
        "",
        *_table(out, ("belief", "policy", "age_bin", "n", "truth_out",
                      "fired_old", "correct_old", "fired_over_truth_old",
                      "fired_new", "correct_new", "fired_over_truth_new")),
        "",
        "## Expected signature, and what held",
        "",
    ]
    verdicts: List[str] = []
    # Beliefs whose numbers never move consume negatives natively (the
    # pipeline skips its suppression step for them): identical by
    # construction, reported as the control.
    unchanged = {b for b in beliefs if all(
        r["acc_old"] == r["acc_new"] for r in head if r["belief"] == b)}
    for b in unchanged:
        verdicts.append(f"- {_short(b)}: identical under both semantics by "
                        f"construction (negatives enter its own filters; the "
                        f"base rule never applied to it). Serves as the control.")
    # (a) OUT_OF_HOUSE over-firing at long ages shrinks toward the truth rate.
    for b in beliefs:
        if b in unchanged:
            continue
        fired = {s: 0 for s in SEMANTICS}
        truth = 0
        for label in long_bins:
            r = find(out, belief=b, policy=never, age_bin=label)
            if not r:
                continue
            truth += int(r["truth_out"])
            for s in SEMANTICS:
                fired[s] += int(r[f"fired_{s}"])
        if truth == 0:
            continue
        ratio = {s: fired[s] / truth for s in SEMANTICS}
        held = abs(ratio["new"] - 1.0) < abs(ratio["old"] - 1.0)
        verdicts.append(
            f"- OUT_OF_HOUSE over-firing shrinks toward the truth rate at "
            f"ages of a day and more, {_short(b)} passive: fired/truth "
            f"{ratio['old']:.2f} old -> {ratio['new']:.2f} new "
            f"({fired['old']} -> {fired['new']} answers against {truth} "
            f"true): **{'held' if held else 'did not hold'}**"
            + ("" if held or ratio["new"] >= 1.0 else
               " (it shrank past the truth rate: passive OUT_OF_HOUSE "
               "answers all but vanish; see the pushback recorded in "
               "STATUS)."))
    # (b) came_back accuracy rises for every graded model.
    for b in graded:
        if b in unchanged:
            continue
        r = find(reg, belief=b, policy=never, regime="came_back")
        if not r or r["delta"] == "":
            continue
        held = float(r["delta"]) > 0
        verdicts.append(
            f"- came_back accuracy rises for graded models, {_short(b)} "
            f"passive: {r['acc_old']} -> {r['acc_new']} (n={r['n']}): "
            f"**{'held' if held else 'did not hold'}**")
    # (c) truly_out passive accuracy may dip.
    for b in beliefs:
        if b in unchanged:
            continue
        r = find(reg, belief=b, policy=never, regime="truly_out")
        if not r or r["delta"] == "":
            continue
        verdicts.append(
            f"- truly_out passive accuracy may dip where the veto was "
            f"subsidizing it, {_short(b)}: {r['acc_old']} -> {r['acc_new']} "
            f"(n={r['n']}): {'dipped' if float(r['delta']) < 0 else 'did not dip'}")
    # (d) search-policy accuracy holds or rises.
    for b in beliefs:
        if b in unchanged:
            continue
        r = find(head, belief=b, policy=search)
        if not r or r["delta"] == "":
            continue
        held = float(r["delta"]) >= -0.005
        verdicts.append(
            f"- search-policy accuracy holds or rises, {_short(b)} + "
            f"SequentialSearch: {r['acc_old']} -> {r['acc_new']}: "
            f"**{'held' if held else 'did not hold'}**")
    lines += verdicts
    lines += ["", "Bank hashes and settings: `provenance.json`.", ""]
    return "\n".join(lines)


# ------------------------------------------------------------- driver

def _typed(value: str) -> Any:
    if value == "":
        return ""
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def load_tables(out: pathlib.Path) -> Dict[str, List[Dict[str, Any]]]:
    """The four csvs back into the aggregate's shape (``--render-only``)."""
    tables: Dict[str, List[Dict[str, Any]]] = {}
    for name in ("headline", "by_age", "by_regime", "out_of_house"):
        with open(out / f"{name}.csv") as fh:
            tables[name] = [{k: _typed(v) for k, v in row.items()}
                            for row in csv.DictReader(fh)]
    return tables


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--banks", nargs="*", type=pathlib.Path, default=None,
                        help=f"bank files (default: {DEFAULT_BANK_GLOB})")
    parser.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--render-only", action="store_true",
                        help="rebuild README.md from the csvs under --out")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    if args.render_only:
        provenance = json.loads((args.out / "provenance.json").read_text())
        (args.out / "README.md").write_text(
            render_readme(load_tables(args.out), provenance))
        print(f"re-rendered {args.out / 'README.md'}")
        return 0
    banks = (sorted(args.banks) if args.banks
             else sorted(REPO_ROOT.glob(DEFAULT_BANK_GLOB)))
    if not banks:
        raise SystemExit("no banks found")
    tasks = [{"bank": str(bank), "belief_key": key, "belief_spec": spec,
              "policy": policy, "semantics": semantics}
             for bank in banks for key, spec in BELIEFS
             for policy in POLICIES for semantics in SEMANTICS]
    logger.info("%d banks x %d beliefs x %d policies x 2 semantics = %d runs",
                len(banks), len(BELIEFS), len(POLICIES), len(tasks))
    results: List[Dict[str, Any]] = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_task, t) for t in tasks]
        for i, fut in enumerate(futures, start=1):
            results.append(fut.result())
            if i % 20 == 0 or i == len(futures):
                logger.info("%d/%d runs done", i, len(futures))
    tables = aggregate(results)
    args.out.mkdir(parents=True, exist_ok=True)
    for name, rows in tables.items():
        with open(args.out / f"{name}.csv", "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    commit, dirty = git_state(REPO_ROOT / "src" / "baselines")
    provenance = {
        "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        "git_commit": commit, "git_dirty": dirty, "seed": SEED,
        "n_banks": len(banks),
        "banks": [{"path": (str(p.relative_to(REPO_ROOT))
                            if p.is_relative_to(REPO_ROOT) else str(p)),
                   "sha256": JsonlBank(path=p).manifest_hash}
                  for p in banks],
        "beliefs": [spec for _, spec in BELIEFS], "policies": list(POLICIES),
        "age_edges_h": list(DEFAULT_AGE_EDGES_H)}
    (args.out / "provenance.json").write_text(json.dumps(provenance, indent=2))
    (args.out / "README.md").write_text(render_readme(tables, provenance))
    for row in tables["headline"]:
        print(f"{row['belief']:<45} {row['policy']:<18} old {row['acc_old']} "
              f"new {row['acc_new']} delta {row['delta']}")
    print(f"report -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
