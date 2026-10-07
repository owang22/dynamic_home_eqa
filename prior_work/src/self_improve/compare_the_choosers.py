"""Three looking arms, and an ablation that says which repair mattered.

The looking factor is three arms, not two:

  the fixed fair rotation   the control: one room a day, seeded rota, no choosing.
  the naive chooser         "look where your own notes disagree", taken literally.
                            KEPT AS AN ARM, not discarded. It is the honest
                            consequence of the hypothesis and it fails for a real
                            reason: a room the robot holds no claim about can never
                            be the site of a disagreement, so the policy can only
                            send it back where it has already been - which is never
                            where an unnoticed change is.
  the repaired chooser      the same policy with two changes of DIFFERENT KINDS,
                            which the write-up must keep distinct:
                              - it is told how long since it looked in each room.
                                That RESTORES INFORMATION a real robot has about its
                                own history; withholding it handicaps the policy
                                rather than testing it.
                              - the two competing claims must be about the SAME
                                thing. That CORRECTS THE SPECIFICATION: two claims
                                about two unrelated objects are not a disagreement
                                about the world, and we wrote the looser version by
                                accident.

Leaving each out in turn says which one did the work. All four variants start from
the same notes and see the same house, so nothing but the policy differs.

    python -m self_improve.compare_the_choosers --household hh_s3_t03 --days 10
"""
from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any, Dict, List, Optional

from baselines.patrol.llm import LLMClient
from self_improve.choose_where_to_look import choose_and_look
from self_improve.frozen_household import FROZEN_BANKS, FrozenHousehold
from self_improve.look_diagnosticity_check import check_a_log
from self_improve.looking import (FixedLookSchedule, TheHouseAsSeen, clock_to_seconds)
from self_improve.memory_notes import Notes
from self_improve.study_settings import LOCKED
from self_improve.write_the_notes import write_the_notes

VARIANTS = {
    "the fixed fair rotation": None,
    "the naive chooser": (False, False),
    "the naive chooser, plus its own look history": (True, False),
    "the naive chooser, plus one-thing disagreements": (False, True),
    "the repaired chooser, both changes": (True, True),
}


def build_starting_notes(household: FrozenHousehold, client: LLMClient,
                         out_dir: pathlib.Path, through_day: int) -> Notes:
    """Notes every chooser variant starts from, built by the fixed schedule so no
    variant's own choices are baked into them."""
    out_dir.mkdir(parents=True, exist_ok=True)
    eyes = TheHouseAsSeen(household, out_dir / "looks.jsonl", LOCKED.granularity)
    schedule = FixedLookSchedule(household, LOCKED.granularity, LOCKED.fixed_schedule_kind,
                                 LOCKED.budget_per_look, LOCKED.visit_times,
                                 LOCKED.rotation_seed)
    notes = Notes(out_dir / "notes.json", household.name,
                  "the shared starting notes", "incremental edits")
    if LOCKED.shared_warm_start:
        eyes.shared_warm_start()
    for day in range(through_day + 1):
        looks = [eyes.look(schedule.targets_for(day, i), day, clock_to_seconds(when),
                           "the fixed schedule")
                 for i, when in enumerate(LOCKED.visit_times)]
        if day == 0 and LOCKED.shared_warm_start:
            looks = [eyes.looks[0]] + looks
        write_the_notes(notes, household, day, day * 86400 + 23 * 3600, looks, client,
                        LOCKED.read_budget_lines)
        notes.save()
    eyes.close()
    return notes


def run_one_variant(household: FrozenHousehold, name: str, switches,
                    starting_notes_path: pathlib.Path, client: LLMClient,
                    out_dir: pathlib.Path, first_day: int, days: int) -> Dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    notes = Notes.load(starting_notes_path)
    notes.path = out_dir / "notes.json"
    eyes = TheHouseAsSeen(household, out_dir / "looks.jsonl", LOCKED.granularity)
    schedule = FixedLookSchedule(household, LOCKED.granularity, LOCKED.fixed_schedule_kind,
                                 LOCKED.budget_per_look, LOCKED.visit_times,
                                 LOCKED.rotation_seed)
    when = LOCKED.visit_times[0]
    for day in range(first_day, first_day + days):
        if switches is None:
            eyes.look(schedule.targets_for(day, 0), day, clock_to_seconds(when),
                      "the fixed schedule")
        else:
            history, same_object = switches
            choose_and_look(eyes, household, notes, day, when, clock_to_seconds(when),
                            client, fall_back_to=schedule,
                            tell_it_days_since_each_room_was_looked_in=history,
                            require_the_two_claims_to_be_about_the_same_object=same_object)
    eyes.close()

    rooms = [look.targets[0]["name"] for look in eyes.looks]
    seen = sorted({o for look in eyes.looks for o in look.asked_objects_seen})
    where_the_change_is = rooms_the_change_moved_into(household, first_day, first_day + days)
    report = {
        "arm": name,
        "n_looks": len(eyes.looks),
        "n_distinct_rooms_visited": len(set(rooms)),
        "rooms_in_order": rooms,
        "n_asked_objects_seen": len(seen),
        "of_how_many_asked_objects": len(household.asked_objects),
        "reached_a_room_the_change_moved_into": bool(set(rooms) & where_the_change_is),
        "rooms_the_change_moved_into": sorted(where_the_change_is),
        "n_looks_where_the_model_did_not_answer":
            sum(1 for look in eyes.looks if look.model_call_failed),
    }
    diagnosticity = check_a_log(out_dir / "looks.jsonl")
    if diagnosticity.get("n_looks_the_model_chose"):
        report["share_that_settled_which_claim_held"] = diagnosticity[
            "share_that_actually_settled_which_claim_held"]
        report["share_whose_two_expectations_merely_differed"] = diagnosticity[
            "share_that_could_tell_their_two_claims_apart"]
        report["diagnosticity_concerns"] = diagnosticity["concerns"]
    return report


def rooms_the_change_moved_into(household: FrozenHousehold, first_day: int,
                                last_day: int) -> set:
    """Rooms that hold an asked-about object during these days but did not usually
    hold one in the settled fortnight. Harness-side only; no arm sees it."""
    def rooms_over(days):
        out = set()
        for day in days:
            for object_id in household.asked_objects:
                room = household.room_of_object(object_id, day * 86400 + 13 * 3600)
                if room != "beyond the reach of any look":
                    out.add(room)
        return out
    return rooms_over(range(max(first_day, 14), last_day)) - rooms_over(range(0, 14))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--household", default="hh_s3_t03")
    parser.add_argument("--banks", type=pathlib.Path, default=FROZEN_BANKS)
    parser.add_argument("--notes-through-day", type=int, default=7)
    parser.add_argument("--first-day", type=int, default=8)
    parser.add_argument("--days", type=int, default=10)
    parser.add_argument("--out", type=pathlib.Path,
                        default=pathlib.Path("results/self_improve/chooser_ablation"))
    parser.add_argument("--cache", type=pathlib.Path,
                        default=pathlib.Path("llm_prior_cache/self_improve"))
    args = parser.parse_args(argv)

    household = FrozenHousehold(args.banks / f"{args.household}.jsonl")
    client = LLMClient(args.cache)
    args.out.mkdir(parents=True, exist_ok=True)

    print(f"building the shared starting notes through day {args.notes_through_day} ...",
          flush=True)
    notes = build_starting_notes(household, client, args.out / "starting_notes",
                                 args.notes_through_day)
    print(f"  {len(notes.claims)} claims to start from", flush=True)

    reports = []
    for name, switches in VARIANTS.items():
        print(f"running {name} ...", flush=True)
        reports.append(run_one_variant(
            household, name, switches, args.out / "starting_notes" / "notes.json",
            client, args.out / name.replace(",", "").replace(" ", "_"),
            args.first_day, args.days))

    (args.out / "chooser_ablation.json").write_text(json.dumps(
        {"household": household.name, "days": f"{args.first_day}-{args.first_day + args.days - 1}",
         "n_starting_claims": len(notes.claims), "arms": reports,
         "llm": {**client.stats, "model": client.model}}, indent=1))
    print()
    for r in reports:
        line = (f"{r['arm']:52s} rooms {r['n_distinct_rooms_visited']:2d} | "
                f"objects seen {r['n_asked_objects_seen']:2d}/{r['of_how_many_asked_objects']} | "
                f"reached the change: {r['reached_a_room_the_change_moved_into']}")
        if "share_that_settled_which_claim_held" in r:
            line += (f" | settled {r['share_that_settled_which_claim_held']:.0%} "
                     f"(merely differed {r['share_whose_two_expectations_merely_differed']:.0%})")
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
