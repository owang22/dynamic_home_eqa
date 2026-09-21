"""Targeted reset from the affected list, applied after the fact to a logged belief.

    python3 -m baselines.patrol.mixture_reset --log live.jsonl --bank hh_s10_p2.jsonl --lists lists.jsonl --out out.jsonl [--strength 1.0]

For a belief whose per-question distributions were logged (a hypothesis
mixture arm's ``live.jsonl``, or ``patrol.bocpd --variant none``), the
message-day reset from the affected list is applied post hoc:

* at the first question of a message day every object on that day's list
  gets a doubt ``lambda = strength``;
* a question about such an object at time ``t`` answers from
  ``(1 - lambda) * p + lambda * uniform(spots)`` with
  ``lambda = strength * 0.5 ** k``, ``k`` = the number of patrol sightings
  of that object since the reset (the counter's count reset recovers the
  same way: each new sighting outweighs the discounted past a little more);
* objects not on the list are untouched.

The answer is the argmax of the blended distribution and the confidence
its probability, so this reset can lower confidence and, by reverting to
flat, change the answer only when the belief was nearly flat already.
Rows come out in the classical log format plus ``lambda`` and ``listed``.
"""
from __future__ import annotations

import argparse
import bisect
import json
import pathlib
import sys
from collections import defaultdict
from typing import Dict, List

from baselines.patrol.run import spots_only
from baselines.types import ON_PERSON, OUT_OF_HOUSE


def sightings_from_bank(rows: List[dict]) -> Dict[str, List[int]]:
    seen: Dict[str, set] = defaultdict(set)
    for r in rows:
        if r["kind"] == "room_visit":
            for rec, objs in r["contents"].items():
                for o in objs:
                    seen[o].add(int(r["t"]))
    return {o: sorted(ts) for o, ts in seen.items()}


def apply(log_rows: List[dict], bank_rows: List[dict], lists: Dict[int, set], strength: float, tag: dict) -> List[dict]:
    header = bank_rows[0]
    spots = [r for r in header["receptacle_ids"] if r not in (ON_PERSON, OUT_OF_HOUSE)]
    n = len(spots)
    sight = sightings_from_bank(bank_rows)
    rows = sorted(log_rows, key=lambda r: (int(r["t_query"]), r["question_id"]))
    reset_t: Dict[int, int] = {}
    out = []
    for r in rows:
        day = int(r.get("day_index", r.get("day")))
        t = int(r["t_query"])
        if day in lists and day not in reset_t:
            reset_t[day] = t
        o = r["object_id"]
        dist, dropped = spots_only({k: float(v) for k, v in r["dist"].items()})
        lam = 0.0
        listed = False
        for d, t0 in reset_t.items():
            if o in lists[d] and t0 <= t:
                ts = sight.get(o, [])
                k = bisect.bisect_right(ts, t) - bisect.bisect_right(ts, t0)
                lam = max(lam, strength * 0.5 ** k)
                listed = True
        if lam > 0:
            dist = {s: (1 - lam) * dist.get(s, 0.0) + lam / n for s in spots}
        answer = max(dist, key=lambda s: (dist[s], s)) if dist else r.get("argmax")
        truth = r["truth"]
        out.append({**tag, "day_index": day, "question_id": r["question_id"], "object_id": o, "t_query": t,
                    "answer": answer, "top_prob": round(dist.get(answer, 0.0), 4), "truth": truth, "correct": answer == truth,
                    "p_outside": round(dropped, 4), "lambda": round(lam, 4), "listed": listed,
                    "dist": {s: round(p, 5) for s, p in sorted(dist.items()) if p >= 1e-4}})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", type=pathlib.Path, required=True)
    ap.add_argument("--bank", type=pathlib.Path, required=True)
    ap.add_argument("--lists", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--strength", type=float, default=1.0)
    ap.add_argument("--belief", default="mixture")
    a = ap.parse_args(argv)
    bank_rows = [json.loads(l) for l in a.bank.open()]
    hh = bank_rows[0]["household_id"]
    lists = {int(r["day_index"]): set(r["objects"]) for r in (json.loads(l) for l in a.lists.open()) if r["household"] == hh}
    log_rows = [json.loads(l) for l in a.log.open() if l.strip()]
    log_rows = [r for r in log_rows if "dist" in r]
    tag = {"household": hh, "belief": a.belief, "variant": "listed_posthoc", "strength": a.strength}
    out = apply(log_rows, bank_rows, lists, a.strength, tag)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open("w") as f:
        for r in out:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    n_ok = sum(r["correct"] for r in out)
    print(f"{hh} {a.belief} listed-posthoc {n_ok}/{len(out)} reset days {sorted(lists)} "
          f"listed questions {sum(r['listed'] for r in out)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
