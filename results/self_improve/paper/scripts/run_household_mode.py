#!/usr/bin/env python3
"""Run the mode memory in the loop, exactly as LastSeen runs, and check the loop first.

NOTHING HERE IS TRUSTED UNTIL THE REPLAY MATCHES. This driver rebuilds the environment the runner
builds - the same household, the same `TheHouseAsSeen`, the same question schedule, the same
budget, the same seeds - and then reruns LastSeen through the runner's own `run_one_search`. If
every field of every row does not equal the recorded cell, the environment is not the one the
results came from and the new arm's numbers would be measuring the difference.

    PYTHONPATH=src python3 results/self_improve/paper/scripts/run_household_mode.py --check
    PYTHONPATH=src python3 results/self_improve/paper/scripts/run_household_mode.py --run
"""
import argparse
import json
import pathlib
import random
import sys
import tempfile

sys.path.insert(0, "src")
from self_improve import search_driven as sd                           # noqa: E402
from self_improve.frozen_household import FrozenHousehold              # noqa: E402
from self_improve.household_mode import HouseholdModes                 # noqa: E402
from self_improve.looking import LookTarget, TheHouseAsSeen            # noqa: E402
from self_improve.memory_notes import Notes                            # noqa: E402
from self_improve.who_lives_here import names_by_resident_id           # noqa: E402

RUNS = {"ten homes, 8 a day":
        ("results/self_improve/overnight_wave", "ten_homes", 31, 8,
         ["hh_s2_t03", "hh_s19_t03", "hh_s20_t03", "hh_s32_t03", "hh_s48_t03",
          "hh_s63_t03", "hh_s93_t03", "hh_s109_t03", "hh_s123_t03", "hh_s151_t03"]),
        "three homes, 50 days, 24 a day":
        ("results/self_improve/wave_the_second_illness", "all_generated_v2_twice", 49, 24,
         ["hh_s2_t03", "hh_s32_t03", "hh_s48_t03"]),
        "five wider homes, 24 a day":
        ("results/self_improve/wave_wider_five", "headline_five", 31, 24,
         ["hh_s32_t03", "hh_s48_t03", "hh_s63_t03", "hh_s93_t03", "hh_s151_t03"]),
        "five wider homes, 8 a day":
        ("results/self_improve/wave_the_budget_sweep_q8", "headline_five", 31, 8,
         ["hh_s32_t03", "hh_s48_t03", "hh_s63_t03", "hh_s93_t03", "hh_s151_t03"]),
        "five wider homes, 4 a day":
        ("results/self_improve/wave_the_budget_sweep_q4", "headline_five", 31, 4,
         ["hh_s32_t03", "hh_s48_t03", "hh_s63_t03", "hh_s93_t03", "hh_s151_t03"])}
COMPARE = ("question_id", "object_id", "day", "rooms_opened", "n_rooms_opened", "found_it",
           "found_at_step", "answer_place", "answer_room", "correct_place", "correct_room",
           "true_place", "true_room", "is_a_mover")


def build(banks, home, out_dir):
    household = FrozenHousehold(pathlib.Path(
        f"results/self_improve/varied_homes/{banks}/banks/{home}.jsonl"))
    eyes = TheHouseAsSeen(household, out_dir / "looks.jsonl", "room",
                          names=names_by_resident_id(str(household.bank_path)))
    rotation = list(household.rooms)
    random.Random(f"{household.name}/rotation/0").shuffle(rotation)
    return household, eyes, rotation


def replay_last_seen(banks, home, last_day, qpd, out_dir):
    household, eyes, rotation = build(banks, home, out_dir)
    notes = Notes(out_dir / "notes.json", household.name, "replay", "incremental edits")
    rng = random.Random(f"{household.name}/{sd.LAST_SEEN}/incremental edits/0")
    movers, seen_before, trail = sd.the_movers(household), {}, {}
    rows = []
    for day in range(last_day + 1):
        for question in sd.questions_spread_across_the_day(
                sd.answerable_questions_on_day(household, day), qpd):
            rows.append(sd.run_one_search(
                eyes, household, notes, question, sd.LAST_SEEN, None, 3, rotation, [0], rng,
                movers, seen_before, set(household.places), True, trail))
    return [{k: getattr(r, k) for k in COMPARE} for r in rows]


def run_modes(banks, home, last_day, qpd, out_dir, alpha, stay):
    """The same loop, with the mode memory choosing the rooms."""
    household, eyes, rotation = build(banks, home, out_dir)
    rng = random.Random(f"{household.name}/household mode/0")
    movers = sd.the_movers(household)
    memory = HouseholdModes(household.rooms, alpha=alpha, stay=stay)
    trail, seen_before, rows = {}, {}, []
    spots = {}                       # object -> (time, place) of the most recent sighting
    for day in range(last_day + 1):
        memory.start_the_day()
        today = []
        for question in sd.questions_spread_across_the_day(
                sd.answerable_questions_on_day(household, day), qpd):
            at_time = question["t_query"]
            rooms_left, opened, found_here, step_found = list(household.rooms), [], None, None
            for step in range(1, 4):
                if not rooms_left:
                    break
                if memory.knows(question["object_id"]):
                    room = memory.rank(question["object_id"], rooms_left)[0]
                else:
                    room, _ = sd._the_next_room_it_was_seen_in(
                        question["object_id"], household, trail, rooms_left, rng)
                rooms_left.remove(room)
                opened.append(room)
                look = eyes.look([LookTarget(room, "room")], day, at_time % 86400,
                                 "a mode memory, no model")
                for s in look.sightings:
                    sd._remember_where_it_was_seen(trail, s["object_id"], s["time"],
                                                   s["place_id"], s["room"])
                    spots[s["object_id"]] = (s["time"], s["place_id"])
                    memory.saw(s["object_id"], s["room"])
                    today.append((s["object_id"], s["room"]))
                here = [s for s in look.sightings if s["object_id"] == question["object_id"]]
                if here:
                    found_here, step_found = here[0]["place_id"], step
                    break
            true_place = household.true_place_for_question(question)
            # answered from the search when it found it; otherwise the newest place on the trail,
            # which is exactly what LastSeen answers with
            place = found_here
            if place is None:
                mine = (trail.get(question["object_id"]) or (None,))[0]
                place = mine[1] if mine else None
            room_of = sd._room_of(household, place)
            rows.append({"question_id": question["question_id"],
                         "object_id": question["object_id"], "day": day,
                         "rooms_opened": opened, "n_rooms_opened": len(opened),
                         "found_it": found_here is not None, "found_at_step": step_found,
                         "answer_place": place, "answer_room": room_of,
                         "correct_place": None if place is None or true_place is None
                         else place == true_place,
                         "correct_room": None if place is None or true_place is None
                         else room_of == sd._room_of(household, true_place),
                         "true_place": true_place,
                         "true_room": sd._room_of(household, true_place),
                         "is_a_mover": question["object_id"] in movers})
        memory.close_the_day(day, today)
    return rows, memory


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--alpha", type=float, default=1.0)
    ap.add_argument("--stay", type=float, default=0.9)
    ap.add_argument("--out", default="results/self_improve/paper/household_mode")
    args = ap.parse_args(argv)
    scratch = pathlib.Path(tempfile.mkdtemp())

    if args.check:
        print("replaying LastSeen through the runner's own search, and comparing every field\n")
        ok = True
        for label, (wave, banks, last_day, qpd, homes) in RUNS.items():
            for home in homes:
                recorded = [{k: r.get(k) for k in COMPARE}
                            for r in (json.loads(l) for l in
                                      open(f"{wave}/cells/last_seen_no_model/{home}/"
                                           "searches.jsonl"))
                            if r.get("kind") == "search"]
                mine = replay_last_seen(banks, home, last_day, qpd, scratch / f"{label}{home}")
                same = mine == recorded
                ok &= same
                bad = sum(1 for a, b in zip(mine, recorded) if a != b)
                print(f"  {label:32s} {home:12s} {len(recorded):5d} rows  "
                      + ("identical" if same else f"DIFFER on {bad} rows"))
        print("\n" + ("every replayed row matches the recorded cell"
                      if ok else "THE REPLAY DOES NOT MATCH - do not trust the new arm"))
        return 0 if ok else 3

    if args.run:
        out = pathlib.Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        for label, (wave, banks, last_day, qpd, homes) in RUNS.items():
            for home in homes:
                rows, memory = run_modes(banks, home, last_day, qpd,
                                         scratch / f"m{label}{home}", args.alpha, args.stay)
                name = (f"{label.replace(' ', '_').replace(',', '')}~{home}"
                        f"~a{args.alpha}~s{args.stay}.json")
                (out / name).write_text(json.dumps(
                    {"run": label, "household": home, "alpha": args.alpha, "stay": args.stay,
                     "n_modes": len(memory.modes),
                     "day_to_mode": memory.history, "rows": rows}))
                print(f"  {label:32s} {home:12s} {len(rows):5d} questions, "
                      f"{len(memory.modes)} modes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
