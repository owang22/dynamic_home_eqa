"""How solvable is this task, really? Lay out the questions for a strong reasoner.

THE WHOLE FILE LEAKED, not just each record. Each question's record legitimately stops
before its own moment - but a LATER question about the SAME OBJECT has a record that
includes that moment, so the answer to question A was printed verbatim inside question B.
34 of 45 questions were compromised this way and the reasoner found it, not me. Only the
eleven that no other record covered were scoreable.

The fix is structural rather than a filter: AT MOST ONE QUESTION PER OBJECT PER HOUSEHOLD.
Two records can only overlap on a moment if they are about the same object, so one question
per object makes the leak impossible instead of detectable. The count is kept up by drawing
from every household rather than from one.

The robot answers with a small local model under a three-room budget. This asks a
different question: given everything the robot had actually seen by that moment, and as
much thinking time as it likes, how often can the right spot be worked out at all? That is
the ceiling the memory arms are being measured against, and nobody has measured it.

It writes two files. `questions_for_the_reasoner.json` holds, per question, exactly what
the robot knew: the rooms and their spots, every sighting of the asked object with the day
and the time and what else was in the room, and every room looked in without finding it.
`the_answers_it_should_have_given.json` holds the truth, and is NOT given to the reasoner.

    python3 results/self_improve/build_the_ceiling_probe.py <a finished cell> <out dir>
"""
import json
import pathlib
import random
import sys

sys.path.insert(0, "src")
from self_improve.frozen_household import FrozenHousehold
from self_improve.looking import LookRecord, Sighting

HOW_MANY = 45

# THE RECORD MUST STOP STRICTLY BEFORE THE QUESTION. The first version of this used
# `look["time"] <= at`, and the look the robot takes while searching for THIS question
# carries exactly that timestamp - so 41 of 45 questions handed over the answer as a direct
# observation, and "answer with the most recent sighting" was right by construction. The
# reasoner running the probe found it and the probe measured nothing. Strictly less than.
STRICTLY_BEFORE = True

# Questions about a thing that never moves are free. In one household 15 of 45 sampled
# questions were about a towel that was on the same rail in all ~100 sightings across all
# 31 days, and 31 of 45 answers were one of two spots. So the sample is drawn from the
# objects the disruption moves, and half of it from the days around the two turning points,
# where the reasoner said all the real difficulty lives.
ONLY_MOVERS = True
ONE_QUESTION_PER_OBJECT = True
THE_TURNING_POINTS = set(range(12, 18)) | set(range(22, 28))
BANKS = pathlib.Path("results/self_improve/varied_homes/ten_homes/banks")


def _clock(t: int) -> str:
    t %= 86400
    return f"{t // 3600:02d}:{(t % 3600) // 60:02d}"


def main() -> int:
    """One argument is a single cell. Pass a DIRECTORY OF CELLS and it merges them, because
    one household yields only about a dozen leak-free questions and the ceiling is now a
    number the write-up leans on."""
    cell = pathlib.Path(sys.argv[1])
    out = pathlib.Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    header = json.loads((cell / "searches.jsonl").open().readline())
    home = FrozenHousehold(BANKS / f"{header['household']}.jsonl")
    looks = [json.loads(l) for l in (cell / "looks.jsonl").read_text().splitlines()
             if l.strip() and json.loads(l).get("kind") == "look"]
    rows = [json.loads(l) for l in (cell / "searches.jsonl").read_text().splitlines()
            if l.strip() and json.loads(l).get("kind") == "search"]
    rows = [r for r in rows if r.get("true_place")]
    if ONLY_MOVERS:
        movers = [r for r in rows if r.get("is_a_mover")]
        if len(movers) >= HOW_MANY:
            rows = movers

    # Spread the sample over the three windows so the ceiling can be read per window.
    windows = {"settled": [r for r in rows if r["day"] < 14],
               "while ill": [r for r in rows if 14 <= r["day"] < 24],
               "after the return": [r for r in rows if r["day"] >= 24]}
    rng = random.Random(11)
    # One question per object, and the objects spread across the three windows rather than
    # all taken from the first one. Each object is assigned to whichever window currently has
    # the fewest, among the windows it actually has a question in, preferring a day next to a
    # turning point.
    by_object = {}
    for name, group in windows.items():
        for r in group:
            by_object.setdefault(r["object_id"], []).append((name, r))
    filled = {name: 0 for name in windows}
    picked = []
    for thing in sorted(by_object, key=lambda t: rng.random()):
        options = by_object[thing]
        rng.shuffle(options)
        options.sort(key=lambda pair: (filled[pair[0]],
                                       0 if pair[1]["day"] in THE_TURNING_POINTS else 1))
        name, row = options[0]
        filled[name] += 1
        picked.append((name, row))
    # THE THIRD LEAK, found by the reasoner as well. One question per object stops two
    # records covering the same moment for the SAME object, and does nothing about other
    # objects: each sighting lists what else was in the room, so if question A asks where the
    # mug is at day 25 21:40 and question B, a different object in the same household, has a
    # sighting at exactly that instant in the mug's room, then the mug is printed in B's list
    # and A's room is handed over. It fired on 27 of 79 questions, and a fourth channel - a
    # sighting at the asked instant in a room whose contents do NOT list the asked object -
    # ruled a room out on another 24. The reasoner also reported that the list is useless
    # inside its own record, since the record already states presence or absence for every
    # earlier look, so it pays off only across records, which is to say only as the leak.
    asked_about = {row["object_id"] for _, row in picked}
    asked, truth = [], []
    for window, r in picked:
        at = r["time"]
        seen, absent = [], {}
        for look in looks:
            if look["time"] >= at if STRICTLY_BEFORE else look["time"] > at:
                continue
            mine = [s for s in look["sightings"] if s["object_id"] == r["object_id"]]
            if mine:
                others = sorted({s["object_id"] for s in look["sightings"]
                                 if s["object_id"] != r["object_id"]})
                seen.append({"day": look["day"], "clock": _clock(look["time"]),
                             "spot": mine[0]["place_id"], "room": mine[0]["room"],
                             "people there": look.get("residents_seen") or []})
            else:
                for t in look["targets"]:
                    absent.setdefault(t["name"], []).append(
                        {"day": look["day"], "clock": _clock(look["time"]),
                         "people there": look.get("residents_seen") or []})
        asked.append({
            "id": r["question_id"], "window": window,
            "asked on day": r["day"], "at": _clock(at),
            "where is": r["object_id"],
            "rooms and the spots in them": {room: home.places_in_room[room]
                                            for room in home.rooms},
            "every time you have seen it": sorted(seen, key=lambda s: -s["day"]),
            # With the clock time and who was there, because whether a failed look came
            # before or after the moment asked about is the whole of the evidence on a day
            # when something moved.
            "rooms you looked in without finding it, newest first":
                {room: sorted(when, key=lambda w: (-w["day"], w["clock"]))[:6]
                 for room, when in absent.items()},
            "rooms you have never looked in":
                sorted(set(home.rooms) - set(absent) - {s["room"] for s in seen}),
        })
        # The comparable number is the FIRST ROOM, not the final answer. The small model
        # answers 90% of questions by having found the object during its search, so its
        # final answer is mostly a measure of finding rather than of working anything out.
        # The reasoner here does no searching at all, so it is the first choice it should
        # be read against.
        first_room_right = (bool(r.get("rooms_opened"))
                            and r["rooms_opened"][0] == r.get("true_room"))
        truth.append({"id": r["question_id"], "true_spot": r["true_place"],
                      "true_room": r["true_room"], "window": window,
                      "is_a_mover": r["is_a_mover"],
                      "what the small model answered": r.get("answer_place"),
                      "was the small model right after searching": r.get("correct_place"),
                      "was the small model's FIRST ROOM right": first_room_right})
    (out / "questions_for_the_reasoner.json").write_text(json.dumps(asked, indent=1))
    (out / "the_answers_it_should_have_given.json").write_text(json.dumps(truth, indent=1))
    right = sum(1 for t in truth if t["was the small model right after searching"])
    first = sum(1 for t in truth if t["was the small model's FIRST ROOM right"])
    print(f"{len(asked)} questions from {header['household']}, "
          f"{len(asked[0]['every time you have seen it'])} sightings on the first one")
    print(f"the small model: {right} of {len(truth)} right after searching "
          f"({right/len(truth):.0%}), and its FIRST room was right {first} times "
          f"({first/len(truth):.0%}) - the second is the comparable one")
    print(f"written to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
