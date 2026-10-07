#!/usr/bin/env python3
"""Two more no-model room-choosing rules on the 8-a-day rare-mover banks. No model call anywhere.

Both run the full search loop of the last-seen arm (`search_driven.LAST_SEEN`: open up to three
rooms, answer with the newest sighting, write no notes) and differ only in the FIRST room they
open. Later rooms on the same search follow last-seen's own order. They are patched onto the
module in this process only, the way paper/scripts/last_seen_without_the_first_illness.py did,
so the arm's source is untouched; each produces its own looks.jsonl and searches.jsonl.

  most frequent, no model      first room = the room where this robot's own earlier sightings of
                               the asked object are most numerous (ties by the most recent
                               sighting); nothing seen yet -> last-seen's order
  same time of day, no model   first room = the room where its earlier-day sightings of the
                               object within one hour of the current clock time are most
                               numerous (ties by recency); none -> last-seen's order
  alternate room, no model     first room = the room where the object was sighted most often
                               this month EXCLUDING the room it was last seen in (ties by
                               recency); no other room seen -> last-seen's order

A sighting is one look that found the object in a room (one per look, whatever the place).
Cells: results/self_improve/wave_rare_movers_8_a_day/cells/<most_frequent_no_model | same_time_of_day_no_model | alternate_room_no_model>/<home>/

    PYTHONPATH=src python3 results/self_improve/wave_rare_movers_8_a_day/run_no_model_rules.py [--load 8|24]
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import sys
from typing import Dict, List, Tuple

sys.path.insert(0, "src")
from baselines.types import DAY_SECONDS                              # noqa: E402
from self_improve import overnight_wave as ow                        # noqa: E402
from self_improve import search_driven as sd                         # noqa: E402

HOMES = ["hh_s2_t03", "hh_s19_t03", "hh_s20_t03", "hh_s32_t03", "hh_s48_t03", "hh_s63_t03",
         "hh_s93_t03", "hh_s109_t03", "hh_s123_t03", "hh_s151_t03"]
LOADS = {8: ("results/self_improve/varied_homes/rare_movers/banks_8_a_day", "results/self_improve/wave_rare_movers_8_a_day"),
         24: ("results/self_improve/varied_homes/rare_movers/banks", "results/self_improve/wave_rare_movers")}
ARMS = {"most frequent, no model": "most_frequent",
        "same time of day, no model": "same_time_of_day",
        "alternate room, no model": "alternate_room"}
HOUR = 3600

# this process's record of every sighting: object -> [(time, room)], in arrival order
SIGHTINGS: Dict[str, List[Tuple[int, str]]] = collections.defaultdict(list)
NOW = {"t": None}          # the question being searched for, set by the run_one_search wrapper
RULE = {"name": None}

_remember = sd._remember_where_it_was_seen
_last_seen_chooser = sd._the_next_room_it_was_seen_in
_run_one_search = sd.run_one_search


def remember_every_sighting(where_it_has_been, object_id, at_time, place_id, room):
    _remember(where_it_has_been, object_id, at_time, place_id, room)
    trail = SIGHTINGS[object_id]
    if not trail or trail[-1] != (at_time, room):      # one per look, whatever the place
        trail.append((at_time, room))


def run_one_search_noting_the_time(eyes, household, notes, question, *args, **kwargs):
    NOW["t"] = question["t_query"]
    return _run_one_search(eyes, household, notes, question, *args, **kwargs)


def _clock_gap(t1: int, t2: int) -> int:
    a, b = t1 % DAY_SECONDS, t2 % DAY_SECONDS
    d = abs(a - b)
    return min(d, DAY_SECONDS - d)


def _best(cands: List[Tuple[int, str]], allowed) -> Tuple[str, int, int]:
    """(room, count, newest time) for the room with the most sightings among `allowed`, ties by recency."""
    count: collections.Counter = collections.Counter()
    newest: Dict[str, int] = {}
    for t, room in cands:
        if room in allowed:
            count[room] += 1
            newest[room] = max(newest.get(room, -1), t)
    if not count:
        return None, 0, -1
    room = max(count, key=lambda r: (count[r], newest[r]))
    return room, count[room], newest[room]


def chooser(object_id, household, where_it_has_been, rooms_left, rng):
    first_room_of_the_search = len(rooms_left) == len(household.rooms)
    if first_room_of_the_search:
        allowed = set(rooms_left)
        now = NOW["t"]
        if RULE["name"] == "most_frequent":
            room, n, _ = _best(SIGHTINGS.get(object_id, []), allowed)
            if room is not None:
                return room, f"most frequent: seen there {n} of {len(SIGHTINGS[object_id])} times so far (ties by recency)"
        elif RULE["name"] == "same_time_of_day":
            today = now // DAY_SECONDS
            cands = [(t, r) for t, r in SIGHTINGS.get(object_id, []) if t // DAY_SECONDS < today and _clock_gap(t, now) <= HOUR]
            room, n, _ = _best(cands, allowed)
            if room is not None:
                return room, f"same time of day: seen there {n} of {len(cands)} times within an hour of this clock time on earlier days (ties by recency)"
        elif RULE["name"] == "alternate_room":
            trail = where_it_has_been.get(object_id) or ()
            last_room = trail[0][2] if trail else None
            cands = [(t, r) for t, r in SIGHTINGS.get(object_id, []) if r != last_room]
            room, n, _ = _best(cands, allowed)
            if room is not None:
                return room, f"alternate room: seen there {n} times this month, leaving out {last_room} where it was last seen (ties by recency)"
    room, why = _last_seen_chooser(object_id, household, where_it_has_been, rooms_left, rng)
    return room, ("last-seen's order: " + why) if first_room_of_the_search else why


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--load", type=int, choices=(8, 24), default=8)
    ap.add_argument("--arms", nargs="*", default=list(ARMS))
    a = ap.parse_args(argv)
    banks, out = LOADS[a.load]
    sd._remember_where_it_was_seen = remember_every_sighting
    sd._the_next_room_it_was_seen_in = chooser
    sd.run_one_search = run_one_search_noting_the_time
    for arm in a.arms:
        ow.ARMS[arm] = ("incremental edits", sd.LAST_SEEN, 10)     # the last-seen loop, no notes, no model
        RULE["name"] = ARMS[arm]
        for home in HOMES:
            cell = pathlib.Path(out) / "cells" / arm.replace(" ", "_").replace(",", "") / home
            if (cell / "cell.json").exists():
                print(f"{arm} / {home}: already there")
                continue
            SIGHTINGS.clear()
            ow.main(["--arm", arm, "--household", home, "--banks", banks, "--last-day", "31",
                     "--questions-per-day", "99", "--budget", "3", "--seed", "0", "--out", out,
                     "--cache", "llm_prior_cache/self_improve"])
            (cell / "RULE.txt").write_text(
                f"{arm}: the last-seen search loop (search_driven.LAST_SEEN, no notes, no model) with the FIRST room of\n"
                f"each search chosen by the '{ARMS[arm]}' rule in results/self_improve/wave_rare_movers_8_a_day/run_no_model_rules.py;\n"
                f"later rooms and the answer are last-seen's. The header of searches.jsonl says 'last seen, no model' because\n"
                f"that is the loop it ran in; why_each_room[0] names the rule that chose.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
