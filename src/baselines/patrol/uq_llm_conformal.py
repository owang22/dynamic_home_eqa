"""KnowNo-style conformal prediction set on an LLM's own multiple-choice answer, built post-hoc from a uq_llm.py
log (no new LLM calls: every row already has ``letter_probs``, the model's probability over its 10 MCQ options,
and ``mcq_options`` / ``truth``). Same online-conformal machinery as the classical ocp agent
(``uq_agents.DecayingStepConformal``): score(option) = 1 - its probability; set = options with score <= q_t;
q_t adjusted after every question from whether the truth's own option was in the set (found-it feedback).

    python3 -m baselines.patrol.uq_llm_conformal --log uq/llm_channels/regime_sick10_all_hh_s0/hh_s0.jsonl

Reference: Ren et al., *Robots That Ask For Help: Uncertainty Alignment for Large Language Model Planners*
(KnowNo), CoRL 2023, arXiv:2307.01928.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import defaultdict

from baselines.patrol.uq_agents import DecayingStepConformal

LETTERS = "ABCDEFGHIJ"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", type=pathlib.Path, required=True)
    ap.add_argument("--alpha", type=float, default=0.1)
    a = ap.parse_args(argv)
    rows = [json.loads(l) for l in a.log.open() if l.strip()]
    conformal = DecayingStepConformal(alpha=a.alpha)
    out = []
    for r in rows:
        options = r["mcq_options"] + ["other"]           # "J" = other, matching letter_probs' "J" key
        lps = r.get("letter_probs") or {}
        scores = {opt: 1.0 - lps.get(LETTERS[i], 0.0) for i, opt in enumerate(options)}
        cset = conformal.set_of(scores)
        truth_opt = r["truth"] if r["truth"] in r["mcq_options"] else "other"
        covered = truth_opt in cset
        score_truth = scores.get(truth_opt, 1.0)
        conformal.update(not covered, score_truth)
        out.append({**r, "know_set_size": len(cset), "know_q_t": round(conformal.q, 4), "know_covered": covered})
    n = len(out)
    cov = sum(r["know_covered"] for r in out) / n if n else float("nan")
    size = sum(r["know_set_size"] for r in out) / n if n else float("nan")
    print(f"{a.log.name}: {n} questions, coverage {cov:.3f} (target {1 - a.alpha:.2f}), mean set size {size:.2f}/10 options", file=sys.stderr)
    by_day = defaultdict(list)
    for r in out:
        by_day[r["day_index"]].append(r)
    for d in sorted(by_day):
        rs = by_day[d]
        print(f"  day {d}: coverage {sum(x['know_covered'] for x in rs)/len(rs):.3f}  set {sum(x['know_set_size'] for x in rs)/len(rs):.2f}  "
              f"accuracy(mcq) {sum(x['mcq_correct'] for x in rs)/len(rs):.2f}", file=sys.stderr)
    out_path = a.log.with_name(a.log.stem + "_knowno.jsonl")
    with out_path.open("w") as f:
        for r in out:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
