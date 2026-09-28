#!/usr/bin/env python3
"""Where each told-arm count comes from: which wave, which cells, and did they read the log.

The matcher is deliberate. An earlier version tested the whole claim record with `"ill " in blob`
and reported that every claim mentions being unwell - because `"still standing"` ends in `"ill "`.
So this matches word boundaries, and only in the fields the model wrote: the statement and the
condition, never the bookkeeping.

    python3 results/self_improve/paper/scripts/told_arm_counts.py
"""
import glob
import json
import re

UNWELL = re.compile(r"\b(unwell|ill|illness|ills|sick|sickness|poorly|not well|"
                    r"under the weather|resting|recovering|recovery)\b", re.I)


def says_unwell(text):
    return bool(UNWELL.search(text or ""))


def claim_words(c):
    return " ".join([c.get("statement") or "", c.get("holds_under") or ""])


def main() -> int:
    print("=== claims written on the first changed day (14) that name being unwell, and whether "
          "the wording survived three nights")
    for p in sorted(glob.glob("results/self_improve/*/cells/ours_told*/*/notes.json")
                    + glob.glob("results/self_improve/*/cells/ours_a_profile*/*/notes.json")):
        parts = p.split("/")
        wave, arm, home = parts[2], parts[4], parts[5]
        claims = json.load(open(p)).get("claims", [])
        born14 = [c for c in claims if c.get("first_written_day") == 14 and says_unwell(claim_words(c))]
        still = 0
        for c in born14:
            # what it said by night 17: the last revision on or before day 17, else as written
            later = [r for r in (c.get("revision_history") or []) if (r.get("day") or 0) <= 17]
            text = (later[-1].get("statement") if later else None) or c.get("statement")
            still += says_unwell(text)
        if born14:
            print(f"{wave:30s} {arm:32s} {home:12s} {len(born14)} claims named it on day 14, "
                  f"{still} still said so by night 17")
    print("\n=== room choices on day 14 whose reason names being unwell")
    for f in sorted(glob.glob("results/self_improve/*/cells/ours_told*/*/searches.jsonl")
                    + glob.glob("results/self_improve/*/cells/ours_a_profile*/*/searches.jsonl")):
        parts = f.split("/")
        wave, arm, home = parts[2], parts[4], parts[5]
        rows = [json.loads(l) for l in open(f)]
        d14 = [r for r in rows if r.get("kind") == "search" and r.get("day") == 14]
        hit = sum(1 for r in d14 if any(says_unwell(w) for w in (r.get("why_each_room") or [])))
        first = sum(1 for r in d14 if says_unwell((r.get("why_each_room") or [""])[0]))
        if d14:
            print(f"{wave:30s} {arm:32s} {home:12s} {hit} of {len(d14)} questions mention it in "
                  f"any reason, {first} in the first room's reason")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
