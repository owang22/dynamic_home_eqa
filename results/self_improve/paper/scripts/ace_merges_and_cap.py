#!/usr/bin/env python3
"""Which ACE cells ran under the 4-item merge cap, and what the merges joined.

THE CAP BINDS ON THE PROPOSAL, NOT THE MERGE. `MERGE_SCHEMA`'s `maxItems` limits how many pairs
the model may propose in a night (src/self_improve/write_the_notes_told_if_right.py:513-518, where
the comment records it was 4 and now is 12). So a cell that ran under the old cap shows nights
with exactly 4 pairs proposed and never more; a cell under the new one can go past 4.

For every merge that was applied, this also asks whether the two claims name any object in
common, reading the claim texts from the cell's own notes.json and matching the household's
asked-about object ids.

    python3 results/self_improve/paper/scripts/ace_merges_and_cap.py
"""
import collections
import glob
import json
import pathlib
import re
import sys

sys.path.insert(0, "src")


def objects_named(text, ids):
    return {o for o in ids if o in text}


def main() -> int:
    for path in sorted(glob.glob("results/self_improve/*/cells/ACE_as_published/*/cell.json")):
        cell = pathlib.Path(path).parent
        wave, home = path.split("/")[2], cell.name
        d = json.load(open(path))
        nights = [n for n in (d.get("nightly") or []) if n.get("day", 0) > 0]
        proposed = [(n.get("how_it_merged") or {}).get("n_pairs_proposed", 0) for n in nights]
        at4 = sum(1 for p in proposed if p == 4)
        biggest = max(proposed) if proposed else 0
        notes = json.load(open(cell / "notes.json"))
        claims = {c["claim_id"]: c for c in notes.get("claims", [])}
        ids = {o for o in re.findall(r"[a-z_]+_[a-z0-9]+", " ".join(
            c.get("statement", "") for c in claims.values()))}
        # the asked-object ids for this home, from the claims' own words: anything that looks like
        # an object id and appears in the movers list of the cell manifest is certainly one
        ids |= set(d.get("movers") or [])
        merged = [(n["day"], p) for n in nights
                  for p in (n.get("how_it_merged") or {}).get("pairs", []) if p.get("merged")]
        no_common = []
        for day, p in merged:
            a = claims.get(p.get("keep"), {}).get("statement", "")
            b = claims.get(p.get("fold_in"), {}).get("statement", "")
            if not a or not b:
                continue
            if not (objects_named(a, ids) & objects_named(b, ids)):
                no_common.append((day, p.get("keep"), p.get("fold_in")))
        readable = sum(1 for _, p in merged
                       if claims.get(p.get("keep"), {}).get("statement")
                       and claims.get(p.get("fold_in"), {}).get("statement"))
        print(f"{wave:28s} {home:12s} nights {len(nights):2d} | pairs proposed: most in a night "
              f"{biggest}, nights at exactly 4: {at4} | merges applied {len(merged)}, readable "
              f"{readable}, with no object in common {len(no_common)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
