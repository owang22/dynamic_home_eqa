"""Re-run the STRICT leak rule over every model-written span quoted into any prompt of every LLM arm on disk, and
report English-word hits (cause/causes/reason — everyday words the model wrote itself) separately from structural
ones (snake_case event/field names, resident ids, "whim"). The prose rule in leak_check.py was narrowed on
2026-09-22 to structural ids only; this audit is the reviewer's evidence that nothing structural ever got
through and that the narrowing only ever affected the English words. Expected: some English, ZERO structural.

    python3 -m baselines.patrol.leak_audit [glob ...]
"""
from __future__ import annotations

import collections
import glob
import json
import os
import sys

from baselines.patrol.leak_check import find_leaks

ENGLISH = {"cause", "causes", "reason"}
DEFAULT = ["/home/oliver/robot/dynamic_home_eqa_fm/results/fm_memory/run1/*",
           "/home/oliver/robot/dynamic_home_eqa_fm/results/fm_memory/run2_told/*",
           "/home/oliver/robot/dynamic_home_eqa_fm/results/fm_memory/run3_toldret/*",
           "/home/oliver/robot/dynamic_home_eqa_fm/results/fm_memory/partial/*",
           "/home/oliver/robot/dynamic_home_eqa_fm/results/fm_memory/partial_told/*",
           os.path.join(os.path.dirname(__file__), "../../../results/confidence_shift_2026-09-20/uq/llm_strategies/chain_person/*/*")]


def main(argv=None) -> int:
    pats = argv[1:] if argv and len(argv) > 1 else DEFAULT
    tot: collections.Counter = collections.Counter()
    per_arm = {}
    n_arms = n_fin = n_rows = 0
    for pat in pats:
        for d in sorted(glob.glob(pat)):
            cp = os.path.join(d, "calls.jsonl")
            if not os.path.isdir(d) or not os.path.exists(cp):
                continue
            n_arms += 1
            n_fin += os.path.exists(os.path.join(d, "run_log.jsonl"))
            c: collections.Counter = collections.Counter()
            for l in open(cp):
                try:
                    r = json.loads(l)
                except ValueError:
                    continue
                n_rows += 1
                for span in r.get("llm_authored") or []:
                    for hit in find_leaks(span, prose=False):
                        c[("english:" if hit in ENGLISH else "structural:") + hit] += 1
            if c:
                per_arm[d] = dict(c)
            tot.update(c)
    structural = sum(v for k, v in tot.items() if k.startswith("structural:"))
    english = sum(v for k, v in tot.items() if k.startswith("english:"))
    print(f"arms scanned: {n_arms} ({n_fin} finished), prompt rows: {n_rows}")
    print(f"strict rule inside model-written spans: ENGLISH {english}, STRUCTURAL {structural}")
    for k, v in sorted(tot.items(), key=lambda kv: -kv[1]):
        print(f"  {k}: {v}")
    for a, c in per_arm.items():
        print(f"  {a}: {c}")
    return 0 if structural == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
