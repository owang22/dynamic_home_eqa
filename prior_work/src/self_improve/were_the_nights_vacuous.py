"""Did a night's writing record any fact the memory did not already hold?

Byte-identical repetition is a brittle way to show that the wholesale-rewrite arm is
inert: a reviewer will fairly say near-verbatim rewording slips past it. So this asks
the semantic question instead, in the same vocabulary for both arms:

  a night is VACUOUS if the set of (thing, place) pairs it asserts contains nothing
  the memory had not already asserted on an earlier night.

Both arms are measured with the same extractor,
`write_the_notes.facts_a_statement_asserts`, which was built for the claim store and
is reused here rather than replaced by a fresh regex.

Two notes on the extractor, because a weaker version of it gives a badly wrong answer:

  it matches a place by its bare words ("kitchen cupboard"), not by the article-
  prefixed form `plain_place_name` produces ("the cupboard"). The summaries write
  prose, so matching the article-prefixed form recovered pairs on 8 nights of 29; the
  bare form recovers 24 of 29.

  it pairs each thing with the NEAREST place mentioned in the same line. Pairing every
  thing with every place emits a cross-product - one line about three nightstands and
  three books would assert nine pairs, most of them false - and a slight rewording
  would reshuffle them and count as new information.

    python -m self_improve.were_the_nights_vacuous
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import statistics
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from self_improve.frozen_household import FROZEN_BANKS, FrozenHousehold
from self_improve.memory_notes import summary_lines
from self_improve.write_the_notes import facts_a_statement_asserts

Pair = Tuple[str, str]


def pairs_in(lines: Sequence[str], household: FrozenHousehold) -> Set[Pair]:
    found: Set[Pair] = set()
    for line in lines:
        found |= facts_a_statement_asserts(line, household.asked_objects,
                                           household.places, household.place_room)
    return found


def nights_of(notes: Dict[str, Any], household: FrozenHousehold
              ) -> List[Tuple[int, Set[Pair]]]:
    """(day, the pairs the memory asserts that night), for either arm."""
    if notes.get("nightly_summaries"):
        return [(row["day"], pairs_in(summary_lines(row["summary"]), household))
                for row in notes["nightly_summaries"]]
    claims = notes.get("claims") or []
    if not claims:
        return []
    last = max(c.get("last_revised_day", 0) for c in claims)
    out = []
    for day in range(last + 1):
        statements = [statement_as_of(c, day) for c in claims
                      if c.get("first_written_day", 0) <= day]
        out.append((day, pairs_in([x for x in statements if x], household)))
    return out


def statement_as_of(claim: Dict[str, Any], day: int) -> Optional[str]:
    """What a claim SAID at the end of this night, not what it says now.

    Reconstructing the claim store from `first_written_day` alone and the current
    wording would miss every revision: a claim that moved an object from the desk to
    the coffee table on night 16 would look, on every night, as though it had always
    said the coffee table - or never said it. That asymmetry matters here because the
    rewrite arm's per-night text is exact and recorded, so getting the claim store
    wrong would bias the comparison in one direction.

    `revision_history` stores a `was` snapshot at each revision, so the wording in
    force on a given night is the `was` of the earliest revision made AFTER it, and the
    current wording when no later revision exists.
    """
    if claim.get("first_written_day", 0) > day:
        return None
    later = sorted((r for r in (claim.get("revision_history") or [])
                    if r.get("day", 0) > day),
                   key=lambda r: r.get("day", 0))
    if later:
        return (later[0].get("was") or {}).get("statement") or claim["statement"]
    return claim["statement"]


def informative_nights(looks_file: pathlib.Path, asked: Sequence[str]) -> Set[int]:
    """Nights whose look actually saw something the robot is asked about. A night that
    saw nothing relevant cannot be blamed for recording nothing."""
    seen: Set[int] = set()
    if looks_file.exists():
        wanted = set(asked)
        for line in looks_file.open():
            row = json.loads(line)
            if row.get("kind") != "look":
                continue
            if any(s["object_id"] in wanted for s in row.get("sightings", [])):
                seen.add(row["day"])
    return seen


def measure_one_cell(cell_dir: pathlib.Path, household: FrozenHousehold) -> Optional[Dict[str, Any]]:
    notes_file = cell_dir / "notes.json"
    if not notes_file.exists():
        return None
    notes = json.loads(notes_file.read_text())
    nights = nights_of(notes, household)
    if not nights:
        return None
    relevant = informative_nights(cell_dir / "looks.jsonl", household.asked_objects)

    already: Set[Pair] = set()
    vacuous_days, new_days = [], []
    for day, pairs in nights:
        if day == nights[0][0]:
            already |= pairs
            continue
        (new_days if (pairs - already) else vacuous_days).append(day)
        already |= pairs

    judged = [d for d, _ in nights[1:]]
    judged_informative = [d for d in judged if d in relevant]
    vacuous_informative = [d for d in vacuous_days if d in relevant]
    return {
        "cell": cell_dir.name,
        "how_memory_is_written": notes.get("how_memory_is_written"),
        "n_nights_judged": len(judged),
        "n_vacuous": len(vacuous_days),
        "share_vacuous": len(vacuous_days) / len(judged) if judged else None,
        "n_informative_nights_judged": len(judged_informative),
        "n_vacuous_on_informative_nights": len(vacuous_informative),
        "share_vacuous_on_informative_nights":
            (len(vacuous_informative) / len(judged_informative))
            if judged_informative else None,
        "vacuous_days": vacuous_days,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sweeps", type=pathlib.Path, nargs="+",
                        default=[pathlib.Path("results/self_improve/memory_factor_v1")])
    parser.add_argument("--banks", type=pathlib.Path, default=FROZEN_BANKS)
    parser.add_argument("--out", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/nights_vacuous.json"))
    args = parser.parse_args(argv)

    households: Dict[str, FrozenHousehold] = {}
    by_household: Dict[str, Dict[str, Dict[str, Any]]] = collections.defaultdict(dict)
    for root in args.sweeps:
        for household_dir in sorted(root.glob("hh_s*")):
            name = household_dir.name
            if name not in households:
                households[name] = FrozenHousehold(args.banks / f"{name}.jsonl")
            for cell_dir in sorted(d for d in household_dir.iterdir() if d.is_dir()):
                row = measure_one_cell(cell_dir, households[name])
                if row:
                    by_household[name][row["how_memory_is_written"] or cell_dir.name] = row

    for field, label in (("share_vacuous", "all nights"),
                         ("share_vacuous_on_informative_nights",
                          "nights that saw something asked about")):
        print(f"=== nights recording no fact the memory did not already hold - {label}")
        paired = {}
        for name, arms in sorted(by_household.items()):
            a = arms.get("wholesale rewrite", {}).get(field)
            b = arms.get("incremental edits", {}).get(field)
            bits = []
            for arm, value in (("wholesale rewrite", a), ("incremental edits", b)):
                bits.append(f"{arm} {'n/a' if value is None else format(100*value, '.0f')+'%'}")
            print(f"  {name}: " + ", ".join(bits))
            if a is not None and b is not None:
                paired[name] = 100 * (a - b)
        if len(paired) > 1:
            values = list(paired.values())
            se = statistics.stdev(values) / len(values) ** 0.5
            mean = statistics.fmean(values)
            print(f"  paired, wholesale minus incremental: {mean:+.1f} points, "
                  f"standard error {se:.1f}, n={len(values)} households -> "
                  + ("detected" if abs(mean) > 2 * se else "not detected"))
            print(f"  same direction in {sum(1 for v in values if v > 0)} of {len(values)}")
        print()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(by_household, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
