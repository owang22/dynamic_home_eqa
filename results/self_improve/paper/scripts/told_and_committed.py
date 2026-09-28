#!/usr/bin/env python3
"""The arm that was told AND made to write down what would change, on all eight homes.

What it commits to on the night it is told, whether the commitment survives, and whether the
rooms it named are where the ill resident's things actually went the next day.

"Predicted rooms" are the rooms named in the claims that arm wrote on the night the sentence
arrived, read out of the claim text - the model writes prose, not room ids, so the match is the
room name as a word. The comparator is the same wave's untold `log and notes` arm: same banks,
same homes, same chooser, same questions.

    PYTHONPATH=src python3 results/self_improve/paper/scripts/told_and_committed.py
"""
import json
import pathlib
import re
import statistics
import sys

sys.path.insert(0, "src")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from self_improve.frozen_household import FrozenHousehold  # noqa: E402
from self_improve.three_prompts import the_unwell_spells  # noqa: E402
import paper_data as D  # noqa: E402

TOLD = "ours_told_and_asked_what_changes"
UNTOLD = "the_log_and_notes_about_the_routine"
UNWELL = re.compile(r"\b(unwell|ill|illness|sick|poorly|not well|under the weather|resting|"
                    r"in bed|recovering)\w*", re.I)
CELLS = [("results/self_improve/wave_the_family_reads_the_log",
          "results/self_improve/varied_homes/ten_homes/banks",
          ["hh_s2_t03", "hh_s32_t03", "hh_s48_t03"]),
         ("results/self_improve/wave_told_on_the_wider_homes",
          "results/self_improve/varied_homes/headline_five/banks",
          ["hh_s32_t03", "hh_s48_t03", "hh_s63_t03", "hh_s93_t03", "hh_s151_t03"])]


def condition_on_night(claim, night):
    for r in sorted(claim.get("revision_history") or [], key=lambda r: (r.get("day") or 0)):
        if (r.get("day") or 0) > night:
            was = r.get("was")
            return was.get("holds_under") if isinstance(was, dict) else None
    return claim.get("holds_under")


def text_on_night(claim, night):
    """What this claim said at the END of `night`, or None if it did not exist yet.

    THE HISTORY STORES THE OLD TEXT, NOT THE NEW ONE. Each entry in `revision_history` carries
    `was` - the wording that revision replaced - and `statement` holds only the CURRENT wording.
    So the text on a given night is the `was` of the earliest revision made after it, and only a
    claim never revised since keeps its current statement. Reading `statement` directly reports
    what the arm believed on night 31: that is how this script first showed three homes
    "predicting", on the night they were told someone would fall ill tomorrow, that the resident
    was back to normal as of day 23 - sentences written ten nights later.

    Checked rather than assumed: `night_13_mentions_a_later_day` below re-reads every
    reconstructed night-13 note for a day number above 13, and finds none.
    """
    if (claim.get("first_written_day") or 0) > night:
        return None
    for r in sorted(claim.get("revision_history") or [], key=lambda r: (r.get("day") or 0)):
        if (r.get("day") or 0) > night:
            # `was` is the whole prior state - statement, condition, status, standing - not a
            # string. Taking it as text is the second way this reconstruction went wrong.
            was = r.get("was")
            return was.get("statement") if isinstance(was, dict) else was
    return claim.get("statement")


def night_13_mentions_a_later_day(text, night):
    """A note written on night N cannot cite a day after N. Returns the offending days."""
    return [int(d) for d in re.findall(r"[Dd]ay (\d+)", text or "") if int(d) > night]


def claims_written_on(notes, day):
    """Claims first written that night, WITH THE WORDS THEY HAD THAT NIGHT.

    `claim["statement"]` is the CURRENT text after every later revision, so reading it to see what
    the arm committed to on night 13 shows what it believed on night 31. That is how this script
    first reported three homes predicting the resident was "back to his usual routine as of Day 23"
    on the night it was told he was falling ill - those sentences were written ten nights later.
    """
    out = []
    for c in notes.get("claims", []):
        if c.get("first_written_day") == day:
            out.append({**c, "statement": text_on_night(c, day),
                        "holds_under": condition_on_night(c, day),
                        "as_it_stands": c.get("statement")})
    return out


def rooms_named(text, rooms):
    out = set()
    low = (text or "").lower().replace("_", " ")
    for room in rooms:
        if re.search(rf"\b{re.escape(room.lower().replace('_', ' '))}\b", low):
            out.add(room)
    return out


def main() -> int:
    summary = []
    for wave_dir, banks_dir, homes in CELLS:
        wave, banks = pathlib.Path(wave_dir), pathlib.Path(banks_dir)
        for home in homes:
            hh = FrozenHousehold(banks / f"{home}.jsonl")
            who, first_bad, _ = the_unwell_spells(hh)[0]
            told_night = first_bad - 1
            notes = json.load(open(wave / "cells" / TOLD / home / "notes.json"))
            committed = claims_written_on(notes, told_night)
            predicted = set()
            for c in committed:
                predicted |= rooms_named(c.get("statement"), hh.rooms)
            movers = D.spell_1_movers(home, banks)
            theirs = sorted(o for o in movers if o.endswith("_" + who.split("_")[-1])
                            or o.rsplit("_", 1)[-1] in (who, ""))
            # the ill resident's own things: object ids end in the resident's NAME
            name = next((p["name"] for p in hh.header["protocol"]["residents"]
                         if p["resident_id"] == who), "")
            theirs = sorted(o for o in movers if o.lower().endswith("_" + name.lower()))
            print(f"\n{'='*94}\n{home}  ({wave.name})   {name} is unwell from day {first_bad}; "
                  f"told on night {told_night}")
            print(f"  it wrote {len(committed)} notes that night; rooms named: "
                  f"{', '.join(sorted(predicted)) or 'NONE'}")
            for c in committed:
                print(f"    [{c['claim_id']}] {c.get('statement')}")
                late = night_13_mentions_a_later_day(c.get("statement"), told_night)
                if late:
                    print(f"        !! cites day {late} - the reconstruction is wrong")

            # --- where the ill resident's movers actually were on the first changed day
            rows_told = {r["question_id"]: r for r in D.rows(wave / "cells", TOLD, home)
                         if r["day"] == first_bad and r["object_id"] in theirs}
            rows_untold = {r["question_id"]: r for r in D.rows(wave / "cells", UNTOLD, home)
                           if r["day"] == first_bad and r["object_id"] in theirs}
            true_rooms = [r["true_room"] for r in rows_told.values()]
            in_predicted = sum(1 for room in true_rooms if room in predicted)
            a = D.share(list(rows_told.values()), "first")
            b = D.share(list(rows_untold.values()), "first")
            print(f"  day {first_bad}: {len(rows_told)} questions about {name}'s moved objects "
                  f"({', '.join(theirs)})")
            print(f"    actually in a predicted room: {in_predicted} of {len(true_rooms)}")
            print(f"    first room right - told and committed {a:.0f}%  |  untold {b:.0f}%")
            if a is not None and b is not None and len(rows_told) >= 4:
                summary.append((home, wave.name, a - b, len(rows_told)))

            # --- did the commitment survive
            for night in (first_bad + 1, first_bad + 2, first_bad + 3):
                kept, gone = [], []
                for c in committed:
                    now = text_on_night(c, night)
                    (kept if rooms_named(now, hh.rooms) & predicted
                     else gone).append((c["claim_id"], now))
                print(f"    night {night}: {len(kept)} of {len(committed)} still name a predicted "
                      f"room")
                for cid, now in gone:
                    print(f"        [{cid}] became: {now}")

            # --- day-14 room choices that name the illness
            choices = [r for r in D.rows(wave / "cells", TOLD, home) if r["day"] == first_bad]
            named = [r for r in choices
                     if any(UNWELL.search(w or "") for w in (r.get("why_each_room") or []))]
            to_predicted = 0
            for r in named:
                for i, why in enumerate(r.get("why_each_room") or []):
                    if UNWELL.search(why or ""):
                        to_predicted += r["rooms_opened"][i] in predicted
                        break
            print(f"    day {first_bad} room choices naming the illness: {len(named)} of "
                  f"{len(choices)}; of those, {to_predicted} opened a predicted room")

    print(f"\n\n{'='*94}\nSUMMARY: first room right on the ill resident's moved objects, day 14, "
          f"told-and-committed minus untold")
    d = [x[2] for x in summary]
    for home, wave, diff, n in summary:
        print(f"  {home:12s} {wave:32s} {diff:+6.1f}  ({n} questions)")
    tse = 2 * statistics.stdev(d) / len(d) ** 0.5
    print(f"  mean {statistics.mean(d):+.1f}, 2 SE {tse:.1f}, "
          f"same sign in {sum(1 for v in d if v > 0)} of {len(d)} homes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
