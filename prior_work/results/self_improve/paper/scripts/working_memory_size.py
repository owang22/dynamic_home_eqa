#!/usr/bin/env python3
"""What working-memory limit each MemGPT-shaped cell actually ran under.

`memory_notes.WORKING_MEMORY_CHARACTERS` is 20,000 today (src/self_improve/memory_notes.py:194)
and was 1,200 before 2026-09-26 (the constant kept as A_DELIBERATELY_TIGHT_WORKING_MEMORY,
line 200, whose comment says a run at that size "is labelled the tight variant and never as
MemGPT"). The nightly record stores both the characters used and the share of the limit, so the
limit the cell ran under is recoverable: characters / share.

    python3 results/self_improve/paper/scripts/working_memory_size.py
"""
import glob
import json


def main() -> int:
    for f in sorted(glob.glob("results/self_improve/**/cells/*/*/cell.json", recursive=True)):
        d = json.load(open(f))
        caps = set()
        for night in d.get("nightly") or []:
            used = night.get("characters_in_working_memory")
            share = night.get("share_of_working_memory_used")
            if used and share:
                caps.add(round(used / share))
            used = night.get("characters_in_the_block")
            share = night.get("share_of_the_block_used")
            if used and share:
                caps.add(round(used / share))
        if caps:
            print(f"{f.split('results/self_improve/')[1]:96s} limit(s) seen: {sorted(caps)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
