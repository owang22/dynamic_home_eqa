#!/usr/bin/env python3
"""Does reasoning BEFORE choosing the room change anything? The paired test, not a wave contrast.

`overnight_wave_24_questions` and `wave_reasons_first` are the same three households, the same
banks, the same 24 questions a day and the same arms. They differ in the room-choice schema: the
first names the room before the reason and caps the explanation at 240 characters, the second
reasons first with 1,200. So the pair isolates the chooser, and comparing either of them with the
ten-household run does not - that also changes the households, the budget and the object list.

last-seen is the control: it makes no model call, so its rows must be IDENTICAL across the two
waves. If they are not, something other than the chooser moved.

    PYTHONPATH=src python3 results/self_improve/paper/scripts/does_the_chooser_matter.py
"""
import json
import pathlib
import statistics
import sys

sys.path.insert(0, "src")
from self_improve import search_driven as sd                       # noqa: E402
from self_improve.frozen_household import FrozenHousehold          # noqa: E402

ROOM_FIRST = pathlib.Path("results/self_improve/overnight_wave_24_questions/cells")
REASON_FIRST = pathlib.Path("results/self_improve/wave_reasons_first/cells")
BANKS = pathlib.Path("results/self_improve/varied_homes/ten_homes/banks")
HOMES = ("hh_s2_t03", "hh_s32_t03", "hh_s48_t03")
ARMS = {"the_log_and_notes_about_the_routine": "log and notes",
        "incremental_edits": "claim store",
        "ACE_as_published": "ACE",
        "ours_allowance_derived": "log and notes, counted allowance",
        "last_seen_no_model": "last-seen (control: no model call)"}
WINDOWS = {"settled 1-13": range(1, 14), "day 14": range(14, 15), "days 15-17": range(15, 18),
           "spell 18-23": range(18, 24), "day 24": range(24, 25), "days 25-26": range(25, 27),
           "normal 27-31": range(27, 32)}
MEAS = {"first": lambda r: r.get("found_at_step") == 1,
        "found": lambda r: bool(r.get("found_it"))}


def rows(wave, arm, home):
    out = []
    for line in (wave / arm / home / "searches.jsonl").open():
        r = json.loads(line)
        if r.get("kind") == "search":
            out.append(r)
    return out


def movers_of(home):
    return sd.the_movers(FrozenHousehold(BANKS / f"{home}.jsonl"))


def share(rs, fn):
    return 100 * sum(1 for r in rs if fn(r)) / len(rs) if rs else None


def main() -> int:
    print("the control first: last-seen makes no model call, so its rows must not move\n")
    for home in HOMES:
        a = rows(ROOM_FIRST, "last_seen_no_model", home)
        b = rows(REASON_FIRST, "last_seen_no_model", home)
        keys = ("question_id", "rooms_opened", "found_at_step", "answer_place")
        same = [{k: r.get(k) for k in keys} for r in a] == [{k: r.get(k) for k in keys} for r in b]
        print(f"  {home:12s} {len(a)} rows vs {len(b)}: "
              + ("identical, as it must be" if same else "DIFFERENT - something else changed"))

    for measure, fn in MEAS.items():
        for movers_only in (False, True):
            what = "moved objects" if movers_only else "every question"
            print(f"\n\n=== {'first room right' if measure == 'first' else 'found within 3'}, "
                  f"{what}: reason-first MINUS room-first, paired on household")
            print(f"{'arm':36s}" + "".join(f"{w:>14s}" for w in WINDOWS))
            for arm, label in ARMS.items():
                line = f"{label:36s}"
                for window, days in WINDOWS.items():
                    diffs, n = [], 0
                    for home in HOMES:
                        movers = movers_of(home) if movers_only else None
                        pick = lambda rs: [r for r in rs if r["day"] in days
                                           and (not movers_only or r["object_id"] in movers)]
                        x, y = pick(rows(ROOM_FIRST, arm, home)), pick(rows(REASON_FIRST, arm, home))
                        if len(x) < 8 or len(y) < 8:
                            continue
                        diffs.append(share(y, fn) - share(x, fn))
                        n += len(y)
                    if len(diffs) < 2:
                        line += f"{'-':>14s}"
                        continue
                    tse = 2 * statistics.stdev(diffs) / len(diffs) ** 0.5
                    line += f"{f'{statistics.mean(diffs):+.1f} ({tse:.0f})':>14s}"
                print(line)
            print(f"{'':36s}" + "".join(f"{'':>14s}" for w in WINDOWS)
                  + "\n  cells: 3 households, 2 SE in brackets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
