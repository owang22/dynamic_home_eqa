"""Print the three prompts of the arm that reads its own record, exactly as the model sees
them, on a real household with a real day of looks. No model is called.

    python3 results/self_improve/show_me_the_prompts.py [output_directory]
"""
import json
import pathlib
import sys
import tempfile

sys.path.insert(0, "src")
from self_improve import search_driven as sd
from self_improve import write_the_notes as writing
from self_improve import what_the_robot_is_told as told
from self_improve.frozen_household import FrozenHousehold
from self_improve.looking import TheHouseAsSeen
from self_improve.memory_notes import Notes, THE_LOG_AND_THE_ROUTINE
from self_improve.the_log_the_robot_reads import the_log_block

BANK = pathlib.Path("results/self_improve/varied_homes/ten_homes/banks/hh_s109_t03.jsonl")


def build():
    sd.use_the_search_day_renderer()
    home = FrozenHousehold(BANK)
    work = pathlib.Path(tempfile.mkdtemp())
    eyes = TheHouseAsSeen(home, work / "looks.jsonl", "room")
    eyes.shared_warm_start(day=0)
    targets = eyes.available_targets()
    for day in range(1, 17):
        for room in home.rooms[:4]:
            eyes.look([t for t in targets if t.name == room], day,
                      13 * 3600 + day * 300, "this listing")
    notes = Notes(work / "notes.json", home.name, "memory-guided search",
                  THE_LOG_AND_THE_ROUTINE)
    notes.add_claim(
        "One of them has been at home all day since about day 14, and spends the "
        "afternoon in the office rather than going out",
        "since day 14", 15, 10, ["sighting_0102"])
    notes.add_claim(
        "Look in the room that person is in first for anything of theirs. Their mug and "
        "charger follow them about the house",
        "while that person is at home all day", 16, 10, ["sighting_0111"])
    notes.add_claim(
        "If I stop seeing their things in the office in the afternoon, this has stopped "
        "being true", "a note about the note above", 16, 10, ["sighting_0111"])
    obj = home.asked_objects[0]
    day = 16
    at_time = day * 86400 + 15 * 3600 + 1800
    question = {"object_id": obj, "day_index": day, "t_query": 15 * 3600 + 1800,
                "question_id": "q1"}
    record = the_log_block(eyes, obj, at_time)

    choose = sd.choice_prompt(
        home, notes, question, list(home.rooms), [], [],
        eyes.days_since_each_room_was_looked_in(day), 1, 3,
        show_it_the_notes=True, the_record_to_read=record,
        ask_what_the_people_are_doing=True)

    answer = sd.answer_prompt(
        home, question, notes.what_the_robot_can_read(None, about_object=obj).text,
        ["bathroom", "kitchen", "living"], the_record_to_read=record)

    looks_today = [l for l in eyes.looks if l.day == day]
    current = "\n".join(c.as_plain_words() for c in notes.claims_in_reading_order())
    from self_improve.write_the_notes_about_the_routine import (
        the_day_this_arm_sees)
    night = told.the_nightly_prompt(
        THE_LOG_AND_THE_ROUTINE, home, day,
        the_day_this_arm_sees(looks_today, home.asked_objects, True), current, 240,
        name_the_things_it_is_asked_about=False)

    # The two calls the ACE arm makes every night, rendered from the same code the run
    # uses, so this page cannot drift from what the model is sent.
    class Row:
        def __init__(self, obj, rooms, found_at, true_place, true_room, answer):
            self.object_id, self.rooms_opened = obj, rooms
            self.found_it, self.found_at_step = found_at is not None, found_at
            self.true_place, self.true_room, self.answer_place = true_place, true_room, answer
    from self_improve.write_the_notes_told_if_right import (
        the_day_in_results, JUDGING_SYSTEM)
    ace_notes = Notes(work / "ace.json", home.name, "memory-guided search",
                      "claim store told if it was right")
    ace_notes.add_claim(f"{obj} is on the nightstand in the bedroom_2", "current",
                        14, 10, ["sighting_0102"])
    ace_notes.add_claim("mug_felix is on the desk in the office", "current",
                        15, 10, ["sighting_0111"])
    rows = [Row(obj, ["bedroom_2"], 1, "nightstand_b2", "bedroom_2", None),
            Row("mug_felix", ["office", "kitchen", "living"], None, None, None,
                "desk_o1")]
    judging = (
        told.the_people_who_live_here(home.asked_objects, home.resident_ids)
        + ["", f"It is the end of day {day}. Here is what you were asked today, what you "
               f"did, and whether it worked.", "",
           *the_day_in_results(ace_notes, rows), "",
           "Say which of your notes helped you and which sent you the wrong way, and what "
           "you want changed tonight.", "",
           "A note helped if it sent you into the right room first. A note sent you the "
           "wrong way if you went where it pointed and the thing was not there. Only "
           "judge the notes listed above, by their number.", "",
           "A note can be wrong now because the home has changed, or it can have been "
           "wrong all along. It may help to say which of the two you think it is, because "
           "they call for different things: one needs correcting, and one may be worth "
           "keeping beside a new note.", "",
           told.how_much_you_may_write(200)])
    ace_night = told.the_nightly_prompt(
        "claim store told if it was right", home, day,
        writing._what_happened_today(looks_today, home.asked_objects, True),
        "\n".join(c.as_plain_words() for c in ace_notes.claims_in_reading_order()), 240,
        extra_before_the_instruction=[
            "HOW YOUR NOTES DID TODAY, from your own reading of it:",
            f"- [claim_0001] helped on {obj}: it sent me straight to the right room",
            "- [claim_0002] sent me the wrong way on mug_felix: it is not on the office "
            "desk any more, so this is out of date rather than wrong when written",
            "",
            "What you said you wanted changed tonight:",
            "- record that mug_felix has moved and keep the old note beside it",
            "",
            "You are carrying 2 note(s). You may carry up to 30.",
            ""])

    return {
        "ACE, step one: judging the day": "\n".join(judging),
        "ACE, step one, the system line": JUDGING_SYSTEM,
        "ACE, step two: changing the notes": "\n".join(ace_night),
        "the home it was built on": home.name,
        "when it is asked": f"day {day} at 15:30",
        "what it is asked about": obj,
        "choosing a room": choose[-1]["content"],
        "choosing a room, the system line": choose[0]["content"],
        "answering the question": answer[-1]["content"],
        "answering, the system line": answer[0]["content"],
        "writing its notes at the end of the day": "\n".join(night),
        "writing, the system line": told.WRITING_SYSTEM,
    }


def main() -> int:
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
    built = build()
    (out / "the_three_prompts.json").write_text(json.dumps(built, indent=1))
    for key in ("choosing a room", "answering the question",
                "writing its notes at the end of the day"):
        print("=" * 78)
        print(key.upper())
        print("=" * 78)
        print(built[key])
        print()
    print(f"written to {out / 'the_three_prompts.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
