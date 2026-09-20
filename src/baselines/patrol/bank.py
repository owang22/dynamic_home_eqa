"""Build a patrol bank from a situation_sim run.

    python3 -m baselines.patrol.bank --run ../data/situation_sim/week8/hh_s0 \
        --patrol-hours 4 --out ../results/overnight/banks/hh_s0_p4.jsonl

What goes into the bank (all rows the loader in baselines.bank understands):

* the sim's header, plus a ``protocol`` block every agent may read (the
  resident intro cards, patrol density, walkthrough time, day 0's weekday)
  and harness-only fields (``day_causes``, ``shift_days``,
  ``hint_messages``) that never reach an agent's context;
* the sim's truth and resident rows (ground truth, harness-only);
* the walkthrough: one ``initial_tour`` observation per object found in
  the home on Tuesday at 18:00, plus one ``room_visit`` per room listing
  the EMPTY spots (so the walkthrough's exclusions reach the beliefs);
* the patrol: every ``patrol_hours`` hours after the walkthrough, one
  ``room_visit`` per room with the full contents of every spot in it
  (residents present are stamped on by the loader from the resident rows);
* 32 questions per scored day (Wednesday .. next Tuesday), uniform over
  movable objects, at times uniform over 07:00-23:00.

Same seed and patrol density -> byte-identical file.
"""
from __future__ import annotations

import argparse
import bisect
import json
import pathlib
import random
import sys
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from baselines.types import DAY_SECONDS, ON_PERSON, OUT_OF_HOUSE

WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WEEKEND = {"Saturday", "Sunday"}
MAJOR_EVENTS = ("guest_visit", "sick_day")
"""Generator events that mark a day as a shift (besides the weekend)."""
QUESTIONS_PER_DAY = 32
WAKING_MINUTES = (7 * 60, 23 * 60)
TOUR_MINUTE = 18 * 60

ROLE_WORDS = {
    "worker_out": "works in an office in town",
    "worker_home": "works from home",
    "student": "is a student",
    "shift_worker": "works afternoon-to-night shifts",
    "retired": "is retired",
}
ROLE_WEEKDAY = {
    "worker_out": "out at work from about 8 in the morning to 5:30, then home for the evening",
    "worker_home": "at the desk at home from 9 to about 5:30, sometimes out for lunch",
    "student": "at classes from about 8:40 to 2:30, then studying at home",
    "shift_worker": "home in the morning, out at work from about 1:40 in the afternoon until 11 at night",
    "retired": "home most of the day, with a morning walk and afternoon errands",
}
ROLE_WEEKEND = {
    "worker_out": "sleeps in, errands around midday, home the rest of the day",
    "worker_home": "sleeps in, errands around midday, home the rest of the day",
    "student": "sleeps in, studies in the afternoon, home in the evening",
    "shift_worker": "off work; errands around midday, home the rest of the day",
    "retired": "home most of the day, with a late-morning walk",
}
ROLE_AGE_BANDS = {
    "worker_out": ["late twenties", "thirties", "forties", "early fifties"],
    "worker_home": ["late twenties", "thirties", "forties", "early fifties"],
    "student": ["early twenties"],
    "shift_worker": ["late twenties", "thirties", "forties"],
    "retired": ["sixties", "seventies"],
}
HOBBY_WORDS = {"reading_living": "reading", "family_calls": "calls with family",
               "friends": "seeing friends", "plants": "houseplants", "music": "music",
               "movies": "movies", "board_games": "board games", "puzzles": "jigsaw puzzles"}


def _rows(path: pathlib.Path) -> List[dict]:
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


class _Truth:
    """Piecewise-constant object locations from the truth rows."""

    def __init__(self, truth_rows: List[dict]) -> None:
        self._t: Dict[str, List[int]] = defaultdict(list)
        self._r: Dict[str, List[str]] = defaultdict(list)
        for r in sorted(truth_rows, key=lambda r: (r["object_id"], r["t"])):
            self._t[r["object_id"]].append(r["t"])
            self._r[r["object_id"]].append(r["receptacle_id"])

    def at(self, obj: str, t: int) -> Optional[str]:
        i = bisect.bisect_right(self._t[obj], t) - 1
        return self._r[obj][i] if i >= 0 else None


def resident_cards(state: dict) -> List[dict]:
    """The intro card of every resident: name, age band, occupation, one
    sentence each for the weekday and the weekend, hobbies, pet."""
    hh = state["household"]
    seed = int(state["seed"])
    cards = []
    for rid, r in sorted(hh["residents"].items()):
        rng = random.Random(f"intro_card:{seed}:{rid}")
        name = r["name"].capitalize()
        hobbies = [HOBBY_WORDS.get(h, h.replace("_", " ")) for h in sorted(r["hobbies"])]
        card = {
            "resident_id": rid, "name": name,
            "age_band": rng.choice(ROLE_AGE_BANDS[r["role"]]),
            "occupation": ROLE_WORDS[r["role"]],
            "weekday": f"Weekdays: {ROLE_WEEKDAY[r['role']]}.",
            "weekend": f"Weekends: {ROLE_WEEKEND[r['role']]}.",
            "hobbies": hobbies,
            "bedroom": r["bedroom"],
        }
        if hh.get("pet") and hh.get("carer") == rid:
            card["pet"] = f"looks after the household's {hh['pet']}"
        cards.append(card)
    return cards


def card_sentences(card: dict) -> str:
    s = (f"{card['name']} (in their {card['age_band']}) {card['occupation']}. "
         f"{card['weekday']} {card['weekend']}")
    if card["hobbies"]:
        s += f" Hobbies: {', '.join(card['hobbies'])}."
    if card.get("pet"):
        s += f" {card['name']} {card['pet']}."
    return s


def shift_info(state: dict, scored_days: List[int]) -> Tuple[List[int], Dict[int, List[str]], List[dict]]:
    """(shift_days, day -> active cause ids, hint messages).

    A shift day is a weekend day or a scored day with a major event. The
    hint is one dated sentence a resident would say, written here from the
    cause type, never from the internal cause name."""
    names = {rid: r["name"].capitalize() for rid, r in state["household"]["residents"].items()}
    shift_days: List[int] = []
    day_causes: Dict[int, List[str]] = {}
    hints: List[dict] = []
    for d in state["days"]:
        di = int(d["day_index"])
        day_causes[di] = sorted(c["id"] for c in d["causes"])
        if di not in scored_days:
            continue
        weekday = d["weekday"]
        sentences: List[str] = []
        if weekday in WEEKEND:
            sentences.append("It's the weekend, so we're off our usual routine and around the house more.")
        for c in sorted(d["causes"], key=lambda c: c["id"]):
            if c["kind"] != "event" or c["event"] not in MAJOR_EVENTS:
                continue
            if c["event"] == "guest_visit":
                sentences.append("We have friends coming over this evening.")
            elif c["event"] == "sick_day":
                sentences.append(f"{names[c['resident']]} is home sick today.")
        if sentences:
            shift_days.append(di)
            hints.append({"day_index": di, "weekday": weekday,
                          "text": f"{weekday}: " + " ".join(sentences)})
    return shift_days, day_causes, hints


def question_rows(seed: int, objects: dict, scored_days: List[int], eid: str) -> List[dict]:
    movable = sorted(o for o, spec in objects.items() if not spec.get("static"))
    rng = random.Random(f"patrol_questions:{seed}")
    rows = []
    for d in scored_days:
        minutes = sorted(rng.randrange(WAKING_MINUTES[0], WAKING_MINUTES[1]) for _ in range(QUESTIONS_PER_DAY))
        for k, minute in enumerate(minutes):
            obj = rng.choice(movable)
            rows.append({"kind": "question", "episode_id": eid, "question_id": f"d{d}q{k + 1:02d}",
                         "object_id": obj, "t_query": d * DAY_SECONDS + minute * 60, "day_index": d,
                         "object_class": objects[obj]["cls"]})
    return rows


def build_bank(run_dir: pathlib.Path, out: pathlib.Path, patrol_hours: int) -> pathlib.Path:
    rows = _rows(run_dir / "events.jsonl")
    header = dict(rows[0])
    assert header["kind"] == "episode_header"
    state = json.loads((run_dir / "hidden_state.json").read_text())
    seed = int(state["seed"])
    n_days = int(header["n_days"])
    objects = state["household"]["objects"]
    truth = _Truth([r for r in rows if r["kind"] == "truth"])
    eid = header["episode_id"]
    day0 = state["days"][0]["weekday"]
    scored_days = list(range(1, n_days))
    tour_t = TOUR_MINUTE * 60

    rooms: Dict[str, List[str]] = defaultdict(list)
    for rec, room in sorted(header["receptacle_rooms"].items()):
        if rec != ON_PERSON:
            rooms[room].append(rec)
    room_list = sorted(rooms)

    def visit(room: str, t: int, only_empty: bool) -> Optional[dict]:
        contents = {rec: sorted(o for o in sorted(objects) if truth.at(o, t) == rec) for rec in sorted(rooms[room])}
        if only_empty:
            contents = {rec: objs for rec, objs in contents.items() if not objs}
        if not contents:
            return None
        return {"kind": "room_visit", "episode_id": eid, "t": t, "room": room, "contents": contents}

    # walkthrough
    tour_obs = [{"kind": "observation", "episode_id": eid, "object_id": o, "receptacle_id": truth.at(o, tour_t),
                 "t": tour_t, "source": "initial_tour"}
                for o in sorted(objects) if truth.at(o, tour_t) not in (ON_PERSON, OUT_OF_HOUSE, None)]
    tour_visits = [v for room in room_list for v in [visit(room, tour_t, only_empty=True)] if v]
    # patrol: every patrol_hours hours, all rooms at the same instant
    patrol_rows = []
    step = patrol_hours * 3600
    t = step
    while t < n_days * DAY_SECONDS:
        if t > tour_t:
            for room in room_list:
                v = visit(room, t, only_empty=False)
                if v:
                    patrol_rows.append(v)
        t += step
    questions = question_rows(seed, objects, scored_days, eid)
    shift_days, day_causes, hints = shift_info(state, scored_days)
    cards = resident_cards(state)

    header["budget_per_day"] = 1
    header["tour_t"] = tour_t
    header["patrol_hours"] = patrol_hours
    header["day0_weekday"] = day0
    header["day_names"] = {str(d["day_index"]): d["weekday"] for d in state["days"]}
    header["scored_days"] = scored_days
    header["shift_days"] = shift_days
    header["day_causes"] = {str(k): v for k, v in sorted(day_causes.items())}   # harness-only
    header["hint_messages"] = hints                                              # LLM told arm only
    header["protocol"] = {
        "walkthrough_t": tour_t, "questions_per_day": QUESTIONS_PER_DAY, "first_question_day": 1,
        "patrol_hours": patrol_hours, "free_look": True, "room_level_looks": True,
        "pockets_visible": False, "day0_weekday": day0,
        "residents": cards,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        f.write(json.dumps(header, sort_keys=True) + "\n")
        for r in rows[1:]:
            f.write(json.dumps(r, sort_keys=True) + "\n")
        for r in tour_obs + tour_visits + patrol_rows + questions:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--patrol-hours", type=int, default=4)
    a = ap.parse_args(argv)
    p = build_bank(a.run, a.out, a.patrol_hours)
    print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
