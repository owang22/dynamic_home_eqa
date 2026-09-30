#!/usr/bin/env python3
"""The told-cause pattern, on every run where the model was told the illness on night 13.

Four questions per run: did night 13 produce a prediction, did day 14 land where it said, on which
night was the illness condition dropped, and was a confirming sighting filed as a standing fact in
the same pass.

THE NIGHT CONVENTION, which is the whole of the arithmetic here. `revision_history` stores, under
`was`, the text a revision REPLACED. So the text a claim carried at the end of night N is the `was`
of its first revision dated after N, and the current `statement` if there is none. Reading
`statement` instead puts every quotation on the wrong night, which is the error this script was
written around.

    PYTHONPATH=src python3 results/self_improve/paper/scripts/the_told_cause_across_runs.py
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, "src")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import paper_data as D                                              # noqa: E402
from baselines.types import DAY_SECONDS, ON_PERSON, OUT_OF_HOUSE    # noqa: E402
from self_improve import search_driven as sd                        # noqa: E402
from self_improve.frozen_household import FrozenHousehold, plain_place_name  # noqa: E402
from self_improve.three_prompts import the_unwell_spells            # noqa: E402
from self_improve.who_lives_here import names_by_resident_id        # noqa: E402

TOLD = "ours_told_and_asked_what_changes"
TOLD_NIGHT = 13
UNWELL = re.compile(r"\b(unwell|ill|illness|sick|poorly|not well|under the weather|resting|"
                    r"in bed|recovering)\w*", re.I)
# A note can retire the hypothesis while still using the word - "the 'unwell' hypothesis from
# Day 13 is not supported" mentions illness and abandons it in the same sentence. So two dates are
# reported: the night the note stops CONDITIONING on the illness, and the night the word goes.
RETIRED = re.compile(r"\b(not supported|no longer|contradicted|does not hold|disproved|"
                     r"is not (?:the case|true)|was (?:wrong|incorrect)|ruled out|"
                     r"maintains his work routine|maintains her work routine)\b", re.I)
RUNS = [("family reads the log", "results/self_improve/wave_the_family_reads_the_log",
         "results/self_improve/varied_homes/ten_homes/banks"),
        ("told on the wider homes", "results/self_improve/wave_told_on_the_wider_homes",
         "results/self_improve/varied_homes/headline_five/banks")]


def text_on_night(claim, night, field="statement"):
    for r in sorted(claim.get("revision_history") or [], key=lambda r: (r.get("day") or 0)):
        if (r.get("day") or 0) > night:
            was = r.get("was")
            return (was.get(field) if isinstance(was, dict) else was) or ""
    return claim.get(field) or ""


def changed_on_night(claim, night):
    """True when this claim was rewritten in the pass that closed `night`."""
    return any((r.get("day") or 0) == night + 1 for r in claim.get("revision_history") or [])


def illness_words(hh, objects):
    """Per object, the places and rooms it sat in during the first illness, in plain words."""
    out = {}
    for obj in objects:
        words = set()
        for day in range(14, 24):
            for hour in range(8, 23):
                p = hh.place_of_object(obj, day * DAY_SECONDS + hour * 3600)
                if p and p not in (OUT_OF_HOUSE, ON_PERSON):
                    words.add(plain_place_name(p).lower())
                    words.add((hh.place_room.get(p) or "").lower().replace("_", " "))
        out[obj] = {w for w in words if w}
    return out


def main() -> int:
    rows = []
    for run_name, wave_dir, banks_dir in RUNS:
        wave, banks = pathlib.Path(wave_dir), pathlib.Path(banks_dir)
        cells = wave / "cells" / TOLD
        if not cells.exists():
            continue
        for cell in sorted(cells.iterdir()):
            home = cell.name
            hh = FrozenHousehold(banks / f"{home}.jsonl")
            who = the_unwell_spells(hh)[0][0]
            called = names_by_resident_id(str(banks / f"{home}.jsonl")).get(who, who)
            notes = json.loads((cell / "notes.json").read_text())
            movers = {o for o in sd.the_movers(hh) if o.endswith(called.lower())}
            if not movers:
                movers = set(sd.the_movers(hh))
            places = illness_words(hh, hh.asked_objects)

            # 1. the night-13 prediction: a note written that night that names the illness
            born = [c for c in notes["claims"] if c.get("first_written_day") == TOLD_NIGHT]
            predictions = [c for c in born if UNWELL.search(text_on_night(c, TOLD_NIGHT))]
            pred = predictions[0] if predictions else None
            pred_text = text_on_night(pred, TOLD_NIGHT) if pred else ""
            named_rooms = {r.replace("_", " ") for r in hh.rooms
                           if r.replace("_", " ").lower() in pred_text.lower()
                           or r.lower() in pred_text.lower()}

            # 2. day 14: questions about that resident's moved objects landing in a named room
            hit = total = 0
            for r in D.rows(wave / "cells", TOLD, home):
                if r["day"] != 14 or r["object_id"] not in movers:
                    continue
                total += 1
                true_room = (r.get("true_room") or "").lower().replace("_", " ")
                if any(true_room == n.lower() for n in named_rooms):
                    hit += 1

            # 3. two dates: the night the note stops conditioning on the illness (it says so, or
            # the word goes), and the night the word itself goes
            retired_on, replacing, word_gone = None, "", None
            if pred:
                for night in range(TOLD_NIGHT + 1, hh.n_days):
                    t = text_on_night(pred, night)
                    if not t:
                        continue
                    if word_gone is None and not UNWELL.search(t):
                        word_gone = night
                    if retired_on is None and (RETIRED.search(t) or not UNWELL.search(t)):
                        retired_on, replacing = night, t
                    if retired_on is not None and word_gone is not None:
                        break

            # 4. a confirming sighting filed as a standing fact in the same pass
            confirming = []
            if retired_on is not None:
                for c in notes["claims"]:
                    if c is pred or not changed_on_night(c, retired_on):
                        continue
                    t = text_on_night(c, retired_on)
                    low = t.lower()
                    for obj in movers:
                        if sd.where_an_object_is_named(t, obj) >= 0 if hasattr(
                                sd, "where_an_object_is_named") else False:
                            pass
                    for obj, words in places.items():
                        if obj not in movers:
                            continue
                        stem = obj.rsplit("_", 1)[0].replace("_", " ")
                        if stem in low and any(w in low for w in words) and not UNWELL.search(t):
                            confirming.append(t)
                            break
            rows.append(dict(run=run_name, home=home, who=called, word_gone=word_gone,
                             pred=pred_text, n_born=len(born), rooms=sorted(named_rooms),
                             hit=hit, total=total, retired_on=retired_on,
                             replacing=replacing, confirming=confirming))

    print(f"{'run':24s} {'household':14s} {'ill':8s} {'note?':6s} {'day 14 in a named room':>23s} "
          f"{'condition dropped':>18s} {'same-night fact':>16s}")
    for r in rows:
        dropped = ("night " + str(r["retired_on"])) if r["retired_on"] else "never"
        print(f"{r['run']:24s} {r['home']:14s} {r['who']:8s} {'yes' if r['pred'] else 'NO':6s} "
              f"{r['hit']:>11d} of {r['total']:<8d} {dropped:>18s} "
              f"{('yes' if r['confirming'] else 'no'):>16s}")

    within3 = [r for r in rows if r["pred"] and r["retired_on"]
               and r["retired_on"] <= TOLD_NIGHT + 3]
    print(f"\n{len(within3)} of {len(rows)} runs dropped the illness condition within three "
          f"nights of the prediction (by night {TOLD_NIGHT + 3}).")
    print(f"{sum(1 for r in rows if r['pred'])} of {len(rows)} wrote a prediction on night "
          f"{TOLD_NIGHT} at all.")

    for r in rows:
        print("\n" + "=" * 96)
        print(f"{r['run']} / {r['home']} - {r['who']} is unwell from day 14, "
              f"{r['n_born']} notes written on night {TOLD_NIGHT}")
        print(f"  PREDICTION (night {TOLD_NIGHT}): {r['pred'] or '(none naming the illness)'}")
        print(f"  rooms it names: {', '.join(r['rooms']) or '(none)'}")
        print(f"  day 14: {r['hit']} of {r['total']} questions about {r['who']}'s moved objects "
              f"landed in one of them")
        if r["retired_on"]:
            print(f"  STOPPED CONDITIONING ON THE ILLNESS on night {r['retired_on']}, "
                  f"the note then read:")
            print(f"     {r['replacing']}")
            if r["word_gone"] and r["word_gone"] != r["retired_on"]:
                print(f"  (the word itself survived until night {r['word_gone']})")
        else:
            print("  the illness condition was never dropped from that note")
        for t in r["confirming"][:3]:
            print(f"  FILED THE SAME NIGHT as a standing fact: {t}")
        if r["retired_on"] and not r["confirming"]:
            print("  no confirming sighting was filed as a standing fact that night")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
