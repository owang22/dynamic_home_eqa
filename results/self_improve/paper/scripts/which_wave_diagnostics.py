#!/usr/bin/env python3
"""Which 24-a-day wave each implementation diagnostic belongs to, measured per cell.

The draft quotes three diagnostics without naming a wave, and both `overnight_wave_24_questions`
and `wave_reasons_first` hold ACE-as-published and MemGPT-as-published cells on the same banks.
This prints, per cell: the MemGPT block size and refusal days, the ACE merge counts and whether
the 4-item merge cap could have bound, and ACE's credit concentration.

    python3 results/self_improve/paper/scripts/which_wave_diagnostics.py
"""
import glob
import json


def memgpt(path):
    d = json.load(open(path))
    nights = [n for n in (d.get("nightly") or []) if n.get("day", 0) > 0]
    refused = [n["day"] for n in nights if n.get("refused_because_the_block_was_full")]
    biggest = max((n.get("characters_in_the_block") or 0) for n in nights)
    last = nights[-1]
    runs = []
    for day in refused:
        if runs and day == runs[-1][-1] + 1:
            runs[-1].append(day)
        else:
            runs.append([day])
    return (f"block reaches {biggest}, ends at {last.get('characters_in_the_block')}"
            f" ({last.get('share_of_the_block_used')}), archive holds "
            f"{last.get('n_passages_in_the_archive')} passages, "
            f"refused on {len(refused)} nights"
            + (f", longest run days {runs[-1][0]}-{runs[-1][-1]}" if runs else ""))


def ace(path):
    d = json.load(open(path))
    nights = [n for n in (d.get("nightly") or []) if n.get("day", 0) > 0]
    proposed = sum((n.get("how_it_merged") or {}).get("n_pairs_proposed", 0) for n in nights)
    merged = sum((n.get("how_it_merged") or {}).get("n_merged", 0) for n in nights)
    most = max([(n.get("how_it_merged") or {}).get("n_merged", 0) for n in nights] or [0])
    at_four = sum(1 for n in nights
                  if (n.get("how_it_merged") or {}).get("n_merged", 0) == 4
                  and (n.get("how_it_merged") or {}).get("n_pairs_proposed", 0) > 4)
    # credit concentration over the claims the run ended with
    claims = d.get("claims") or []
    helped = sorted((c.get("times_it_helped", 0) for c in claims), reverse=True)
    total = sum(helped)
    live = [c for c in claims if c.get("standing") == "still standing"] or claims
    share = ""
    if total:
        for frac in (0.11, 0.20):
            k = max(1, int(round(frac * len(live))))
            share += f" top {frac:.0%} of live claims hold {sum(helped[:k])/total:.0%};"
    return (f"{merged} merges from {proposed} proposed, most in one night {most}, "
            f"nights that merged exactly 4 with more proposed: {at_four}."
            f"{share} {len(claims)} claims, {len(live)} live")


def main() -> int:
    for wave in ("overnight_wave_24_questions", "wave_reasons_first", "wave_the_second_illness",
                 "wave_wider_five", "overnight_wave"):
        for arm, fn in (("MemGPT_as_published", memgpt), ("ACE_as_published", ace),
                        ("claim_store_told_if_it_was_right", ace)):
            for path in sorted(glob.glob(
                    f"results/self_improve/{wave}/cells/{arm}/*/cell.json")):
                home = path.split("/")[-2]
                try:
                    print(f"{wave:28s} {arm:32s} {home:12s} {fn(path)}")
                except Exception as why:                       # noqa: BLE001
                    print(f"{wave:28s} {arm:32s} {home:12s} could not read: {why}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
