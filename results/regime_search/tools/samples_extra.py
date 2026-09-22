#!/usr/bin/env python3
"""Put the sampling run into the panel library, in the shape the library's chart builder already reads.

    python3 tools/samples_extra.py            (from results/regime_search)

Writes ONE key, ``samples_live``, through extra_store so it cannot tread on another extractor's keys.

The library draws a line from cells of the form ``cells[household][split][day] = [n, ok, sum_conf]`` and plots
either ``ok/n`` or ``sum_conf/n`` as a percentage. Nothing here reshapes that. Two lines come out:

  accuracy    [n, correct, sum of the stated confidence]  - the arm's own accuracy, and under the page's
              confidence toggle the number the model says out loud
  agreement   [n, sum of agreement, sum of agreement]     - how often the ten samples land on the same place.
              The same value sits in both slots on purpose, so the line reads as agreement under BOTH toggle
              positions: it is neither an accuracy nor a stated confidence, and flipping the toggle must not
              silently turn it into a different quantity. It is a genuine percentage, so it belongs on the
              library's 0-100 axis beside the others.

The day rule is the one the conformal figure needed: a day is emitted only once EVERY household has finished
it. While the arms run at different speeds an unfinished day is just whichever household is fastest, and the
pooled line then shows that household's shape wearing a three-household error bar. A day is counted finished
for a household when that household has rows on a LATER day, which costs the run's final day and errs the safe
way round.
"""
import collections
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extra_store import write_keys                                    # noqa: E402

SAMPLES = os.path.join(os.path.dirname(ROOT), "confidence_shift_2026-09-20",
                       "uq", "llm_strategies", "samples20")
DAYS = 31


def main():
    rows = []
    for f in sorted(glob.glob(os.path.join(SAMPLES, "hh_s*", "hh_s*.jsonl"))):
        for l in open(f):
            if not l.strip():
                continue
            try:
                rows.append(json.loads(l))
            except ValueError:
                continue
    if not rows:
        print("no sampling rows yet; nothing written")
        return 0

    hhs = sorted({r["household"] for r in rows})
    last = {h: max(r["day_index"] for r in rows if r["household"] == h) for h in hhs}
    # a day is finished for a household only if that household has moved past it
    done = {d for d in range(1, DAYS + 1) if all(last[h] > d for h in hhs)}
    reached = {d for d in range(1, DAYS + 1) if all(last[h] >= d for h in hhs)}

    by = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        by[r["household"]][r["day_index"]].append(r)

    def cells(pick):
        out = {}
        for h in hhs:
            arr = [None] * (DAYS + 1)
            for d, g in by[h].items():
                if d not in done or d > DAYS:
                    continue
                arr[d] = pick(g)
            out[h] = {"all": arr}
        return out

    acc = cells(lambda g: [len(g),
                           sum(1 for r in g if r.get("correct")),
                           sum(float(r.get("verbalized") or 0.0) for r in g)])
    agr = cells(lambda g: [len(g),
                           sum(float(r.get("agreement") or 0.0) for r in g),
                           sum(float(r.get("agreement") or 0.0) for r in g)])

    k = rows[0].get("k")
    live = 0
    try:
        import subprocess
        live = int(subprocess.run(["bash", "-c", "ps -eo cmd | grep -c '[u]q_llm_samples'"],
                                  capture_output=True, text=True).stdout.strip() or 0)
    except Exception:
        pass

    payload = {
        "n_days": DAYS + 1,
        "k": k,
        "n_hh": len(hhs),
        "n_rows": len(rows),
        "running": live,
        "last_day": max(reached) if reached else 0,
        "complete_day": max(done) if done else 0,   # the last day the panel can actually draw
        "per_hh_last": {h: last[h] for h in hhs},
        "lines": {"accuracy": acc, "agreement": agr},
    }
    print(write_keys("samples_extra", {"samples_live": payload}))
    print(f"  {len(rows)} rows, {len(hhs)} households, days through {max(done) if done else 0} complete, "
          f"{live} arm(s) running")
    return 0


if __name__ == "__main__":
    sys.exit(main())
