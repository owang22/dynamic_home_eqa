"""Is the wholesale arm's verbatim repetition a fact about wholesale rewriting, or
about the word "again" in our prompt?

    python -m self_improve.rewrite_wording_variants --household hh_s0_t03 \
        --wording "as it stands"

Runs the WHOLESALE REWRITE ARM ONLY, unchanged in every respect except the
instruction text, which comes from `write_the_notes.REWRITE_WORDINGS`. The loop is
a copy of `compare_the_two_memory_formats.run_one_format` restricted to one arm, so
that adding a keyword to that shared function was not necessary while four other
jobs are running against it.

Because it is a copy, the thing that could silently go wrong is that this loop
builds a DIFFERENT look stream from the one the existing numbers were measured on -
and then any difference between wordings would be confounded by different
observations. So the run asserts its `looks.jsonl` is byte-identical to the
already-measured wholesale cell's, when one exists, and records the hash either
way. The fixed rota does not depend on what the robot remembers, so they must match.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from typing import Any, Dict, List, Sequence

from baselines.patrol.llm import LLMClient
from self_improve.frozen_household import FROZEN_BANKS, FrozenHousehold, period_of_day
from self_improve.frozen_memory_test import FREEZE_POINTS
from self_improve.looking import FixedLookSchedule, TheHouseAsSeen, clock_to_seconds
from self_improve.memory_notes import Notes
from self_improve.study_settings import LOCKED
from self_improve.write_the_notes import AS_IT_STANDS, REWRITE_WORDINGS, write_the_notes

LOOK_AT_THE_END_OF_DAY = 23 * 3600 + 30 * 60

# The same days compare_the_two_memory_formats snapshots, taken from the freeze
# points themselves so the two cannot drift apart. frozen_memory_test raises if a
# snapshot's written_up_to_day is not the exact day its freeze point needs.
PEEK_DAYS = tuple(sorted({plan["notes_through_day"] for plan in FREEZE_POINTS.values()}))

WHERE_THE_MEASURED_ARM_LIVES = pathlib.Path("results/self_improve/memory_factor_v1")


def slug(text: str) -> str:
    return text.replace(" ", "_").replace("'", "")


def run_one_wording(household: FrozenHousehold, wording: str, client: LLMClient,
                    out_dir: pathlib.Path, last_day: int = 28, settings=LOCKED,
                    peek_days: Sequence[int] = PEEK_DAYS,
                    compare_looks_with: pathlib.Path = None) -> Dict[str, Any]:
    if wording not in REWRITE_WORDINGS:
        raise ValueError(f"unknown wording {wording!r}; known: {sorted(REWRITE_WORDINGS)}")
    how = "wholesale rewrite"
    arm = f"the fixed schedule with {how}, wording: {wording}"
    out_dir.mkdir(parents=True, exist_ok=True)
    eyes = TheHouseAsSeen(household, out_dir / "looks.jsonl", settings.granularity)
    schedule = FixedLookSchedule(household, settings.granularity,
                                 settings.fixed_schedule_kind, settings.budget_per_look,
                                 settings.visit_times, settings.rotation_seed)
    notes = Notes(out_dir / "notes.json", household.name, arm, how)
    nightly: List[Dict[str, Any]] = []

    warm_start = None
    if settings.shared_warm_start:
        record = eyes.shared_warm_start()
        warm_start = {"n_things_seen": len(record.sightings),
                      "n_asked_objects_seen": len(record.asked_objects_seen),
                      "of_how_many": len(household.asked_objects)}
    peeks: Dict[int, Dict[str, Any]] = {}

    for day in range(last_day + 1):
        looks_today = [eyes.look(schedule.targets_for(day, i), day,
                                 clock_to_seconds(when), "the fixed schedule")
                       for i, when in enumerate(settings.visit_times)]
        if day == 0 and warm_start is not None:
            looks_today = [eyes.looks[0]] + looks_today
        report = write_the_notes(notes, household, day,
                                day * 86400 + LOOK_AT_THE_END_OF_DAY,
                                looks_today, client, settings.read_budget_lines,
                                settings.tell_the_model_everything_it_saw,
                                # KEYWORD, not positional: write_the_notes is shared
                                # code and gained a parameter next to this one while
                                # this experiment was running. A positional argument
                                # here would silently bind to whatever is added next.
                                wording=wording)
        report["period"] = period_of_day(day)
        report["rooms_looked_in"] = [t["name"] for look in looks_today for t in look.targets]
        nightly.append(report)
        notes.save()
        # the notes as they read at the end of each night, so a measure never has to
        # reconstruct a summary it can simply be handed
        with (out_dir / "notes_by_night.jsonl").open("a") as history:
            history.write(json.dumps({"day": day,
                                      "text": notes.newest_summary() or ""}) + "\n")
        (out_dir / "nightly.json").write_text(json.dumps(nightly, indent=1))
        if day in peek_days:
            can_read = notes.what_the_robot_can_read(settings.read_budget_lines)
            peeks[day] = {
                "period": period_of_day(day),
                "n_claims": len(notes.claims),
                "what_the_robot_can_read": can_read.text,
                "n_lines_available": can_read.n_lines_available,
                "the_read_budget_bit": can_read.budget_bit,
                "everything_written_down": notes.newest_summary() or "",
            }
            notes.snapshot_to(out_dir / f"notes_frozen_at_day_{day}.json")
    eyes.close()

    looks_bytes = (out_dir / "looks.jsonl").read_bytes()
    look_hash = hashlib.sha256(looks_bytes).hexdigest()
    same_looks = None
    if compare_looks_with is not None and compare_looks_with.exists():
        same_looks = hashlib.sha256(compare_looks_with.read_bytes()).hexdigest() == look_hash

    result = {"household": household.name, "wording": wording,
              "how_memory_is_written": how, "arm": arm,
              "instruction_text": "\n".join(REWRITE_WORDINGS[wording]),
              "schedule": schedule.describe(), "warm_start": warm_start,
              "read_budget_lines": settings.read_budget_lines,
              "tell_the_model_everything_it_saw": settings.tell_the_model_everything_it_saw,
              "last_day": last_day, "peek_days": list(peek_days),
              "nightly": nightly, "peeks": peeks,
              "n_looks": len(eyes.looks),
              "n_sightings": len(eyes.sightings_so_far()),
              "n_absences_recorded": len(eyes.absences_so_far()),
              "look_stream_sha256": look_hash, "look_stream_bytes": len(looks_bytes),
              "looks_match_the_already_measured_cell": same_looks,
              "n_nights_the_model_call_failed": sum(1 for n in nightly
                                                    if n.get("model_call_failed")),
              "model": {**client.stats, "model": client.model}}
    (out_dir / "run.json").write_text(json.dumps(result, indent=1))
    if same_looks is False:
        raise SystemExit(
            f"{household.name} / {wording}: the look stream does NOT match the "
            f"already-measured wholesale cell, so this cell is confounded by "
            f"different observations and is void. Hash {look_hash}.")
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--household", required=True)
    parser.add_argument("--wording", required=True, choices=sorted(REWRITE_WORDINGS))
    parser.add_argument("--banks", type=pathlib.Path, default=FROZEN_BANKS)
    parser.add_argument("--last-day", type=int, default=28)
    parser.add_argument("--root", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/rewrite_wording/runs"))
    parser.add_argument("--cache", type=pathlib.Path,
                        default=pathlib.Path("llm_prior_cache/rewrite_wording"))
    args = parser.parse_args(argv)

    household = FrozenHousehold(args.banks / f"{args.household}.jsonl")
    client = LLMClient(args.cache)
    out_dir = args.root / args.household / slug(args.wording)
    measured = (WHERE_THE_MEASURED_ARM_LIVES / args.household /
                "wholesale_rewrite" / "looks.jsonl")
    result = run_one_wording(household, args.wording, client, out_dir,
                             last_day=args.last_day, compare_looks_with=measured)
    repeats = sum(1 for n in result["nightly"] if n.get("identical_to_last_night"))
    print(f"{args.household} | {args.wording}: {result['n_looks']} looks, "
          f"{repeats}/{len(result['nightly'])} nights identical to the night before, "
          f"looks match the measured cell: {result['looks_match_the_already_measured_cell']}, "
          f"{result['model'].get('lost', 0)} lost calls, "
          f"{result['model']['calls']} calls / {result['model']['cached']} cache hits",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
