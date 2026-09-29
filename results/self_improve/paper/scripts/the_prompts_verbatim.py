#!/usr/bin/env python3
"""The two prompts the appendix quotes, rendered by the code that sends them.

Not copied out of the source by hand and not recovered from the model cache - the cache stores
only the reply, keyed by a hash of the request, so the prompt is not in it. This calls the same
builders the run calls, on the same household, with the same day's looks read back from the cell's
own looks.jsonl, and prints what came out.

NIGHT 1 is used for both, because night 1 is the one night whose inputs can be reproduced exactly:
the notes are empty, so nothing has to be rewound. A later night's prompt would need the notes as
they stood that evening, and the cells keep only the end state.

    PYTHONPATH=src python3 results/self_improve/paper/scripts/the_prompts_verbatim.py
"""
import json
import pathlib
import sys

sys.path.insert(0, "src")
from self_improve import choose_where_to_look as choosing         # noqa: E402
from self_improve import what_the_robot_is_told as told           # noqa: E402
from self_improve import write_the_notes as writing               # noqa: E402
from self_improve.frozen_household import FrozenHousehold         # noqa: E402
from self_improve.looking import LookRecord                       # noqa: E402
from self_improve.memory_notes import Notes                       # noqa: E402

HOUSEHOLD = "hh_s2_t03"
BANK = pathlib.Path(f"results/self_improve/varied_homes/ten_homes/banks/{HOUSEHOLD}.jsonl")
CELL = pathlib.Path(f"results/self_improve/overnight_wave/cells/incremental_edits/{HOUSEHOLD}")
DAY = 1


def looks_on(day):
    out = []
    for line in (CELL / "looks.jsonl").open():
        row = json.loads(line)
        if row.get("kind") != "look" or row["day"] != day:
            continue
        row.pop("kind")
        out.append(LookRecord(**row))
    return out


def rule(title):
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def main() -> int:
    h = FrozenHousehold(BANK)
    looks = looks_on(DAY)
    notes = Notes(pathlib.Path("/dev/null"), HOUSEHOLD, "appendix", "incremental edits")

    rule(f"NIGHTLY UPDATE - system prompt ({HOUSEHOLD}, night {DAY}, the claim store)")
    print(writing.SYSTEM)

    rule(f"NIGHTLY UPDATE - user prompt ({HOUSEHOLD}, night {DAY})")
    lines = told.the_nightly_prompt(
        "incremental edits", h, DAY,
        writing._what_happened_today(looks, h.asked_objects, False),
        "(nothing written yet)", 240,
        name_the_things_it_is_asked_about=False)
    print("\n".join(lines))

    allowance = writing.how_many_edits_a_night(h, notes, looks)
    rule(f"NIGHTLY UPDATE - output schema (the allowance this night was {allowance} edits)")
    print(json.dumps(writing.edits_schema(allowance), indent=2))

    rule(f"ROOM CHOICE - system prompt")
    print(choosing.SYSTEM)

    rule(f"ROOM CHOICE - user prompt ({HOUSEHOLD}, day {DAY}, empty notes)")
    messages = choosing.choice_prompt(h, notes, DAY, "09:00")
    print(messages[1]["content"])

    rule("ROOM CHOICE - output schema")
    print(json.dumps(choosing.choice_schema(h.rooms, h.asked_objects, False), indent=2))

    rule("HOW ONE EXISTING NOTE IS SHOWN BACK (from the landed claim store, day 31)")
    stored = json.loads((CELL / "notes.json").read_text())
    from self_improve.memory_notes import Claim
    fields = {f for f in Claim.__dataclass_fields__}
    for row in stored["claims"][:2]:
        print(Claim(**{k: v for k, v in row.items() if k in fields}).as_plain_words())
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
