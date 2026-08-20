"""Story-driven generation: the LLM writes the household's three weeks as
a STORY first, then does object-level freeform movement against it.

The weekly-template L2 could only say what recurs, so one-off happenings
had no home and 6-15 of the 50 activity names ever got used. Here the
model authors the 21 days directly — the recurring spine, the weekday/
weekend texture, and storylike arcs (a cold, a visitor, a deadline week)
— one week per call, each call re-reading what it already wrote. That
calendar IS the schedule: its blocks become residents.jsonl, and the
per-day movement pass (same shape as freeform_motion) reads its own
story's day instead of a rule-based simulator's output.

Personas and starting object homes come from the rule_based household so
every method shares one world. Thinking mode throughout; no plausibility
gates — a day that fails to parse is recorded and the run continues.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import pathlib
import sys

import yaml

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT / "src"))

import freeform_motion as fm                                  # noqa: E402
from prompts import ACTIVITY_VOCAB, TIME_PATTERN              # noqa: E402

from dynamic_home_eqa.generation import llm_client            # noqa: E402
from dynamic_home_eqa.generation.cache import (               # noqa: E402
    ResponseCache, make_seed)

try:
    import jsonschema
except ImportError:                                           # pragma: no cover
    jsonschema = None

STORY_MAX_TOKENS = 24000

STORY_SYSTEM = """\
You write the lived three weeks of one simulated household as a concrete
calendar: who does what, when, where — day by day, not as a repeating
template. You are writing for yourself: a later pass will use this
calendar to decide how the household's objects move, so it must be the
kind of specific, believable record a person's actual three weeks leaves.

What three real weeks contain, and a weekly template misses:
- a recurring spine (work, school, sleep) that holds MOST days;
- weekly texture: weekends unlike weekdays, a laundry day, a groceries
  run, the gym nights that actually happen;
- storylike happenings that play out ACROSS days — someone catches a
  cold and is home for two days, a friend visits for a weekend, a work
  deadline makes one week late-heavy, an appointment interrupts a
  morning. Invent arcs the persona supports and let them show in the
  schedule, not just the summary.

Activity names come from a closed list. Pick by WHAT THE PERSON IS
DOING, never by the clock: a night worker sleeping 09:30-17:00 is in
day_sleep (not night_sleep), and their hours before a night shift are
dinner / relax / get_ready (not wake_up). Every resident sleeps every
day. If a block crosses midnight (night shift, sleep), write its end as
the clock time it actually ends the next morning.

Respond only with valid JSON matching the provided schema. No
commentary."""

STORY_USER = """\
The household (persona, verbatim):

{persona}

Places in this home (`at` for each block; ELSEWHERE = out of the house):
{locations}

Activity names (the closed list — use the range of it where the persona
supports it; occasional chores and outings belong somewhere in three
weeks):
{vocab}

{recap}

Write days {lo}..{hi} (day 0 is a Monday; {weekday_map}). For each day:
`day`, a one-line `summary` of what this day is in the household's story,
and `blocks` — every resident's day in 4-10 coarse blocks: `resident`,
`activity`, `start`, `end` (HH:MM), `at`. Cover each resident's whole
day including sleep.
"""


def build_story_schema(resident_ids, receptacles, lo, hi):
    block = {
        "type": "object", "additionalProperties": False,
        "required": ["resident", "activity", "start", "end", "at"],
        "properties": {
            "resident": {"enum": resident_ids},
            "activity": {"enum": ACTIVITY_VOCAB},
            "start": {"type": "string", "pattern": TIME_PATTERN},
            "end": {"type": "string", "pattern": TIME_PATTERN},
            "at": {"enum": receptacles + ["ELSEWHERE"]},
        },
    }
    day = {
        "type": "object", "additionalProperties": False,
        "required": ["day", "summary", "blocks"],
        "properties": {
            "day": {"type": "integer", "minimum": lo, "maximum": hi},
            "summary": {"type": "string", "maxLength": 200},
            "blocks": {"type": "array", "minItems": 1, "maxItems": 60,
                       "items": block},
        },
    }
    n = hi - lo + 1
    return {"type": "object", "additionalProperties": False,
            "required": ["days"],
            "properties": {"days": {"type": "array", "minItems": n,
                                    "maxItems": n, "items": day}}}


def _normalize_story(parsed):
    if isinstance(parsed, list):
        parsed = {"days": parsed}
    elif isinstance(parsed, dict) and "days" not in parsed:
        for k in ("calendar", "schedule", "story"):
            if k in parsed and isinstance(parsed[k], list):
                parsed = {"days": parsed[k]}
                break
    return parsed


def _recap(days: list[dict]) -> str:
    """What the model already wrote, compact — summaries for all prior
    days, full blocks only for the most recent 3 (context budget)."""
    if not days:
        return ("This is the first week; nothing is written yet. Start the "
                "story from day 0.")
    lines = ["The story you have already written:"]
    for d in days:
        lines.append(f"  d{d['day']:02d} {fm.DAY_NAMES[d['day'] % 7]}: "
                     f"{d['summary']}")
    lines.append("The last days' blocks, so times stay coherent:")
    for d in days[-3:]:
        for b in d["blocks"]:
            lines.append(f"  d{d['day']:02d} {b['resident']} "
                         f"{b['start']}-{b['end']} {b['activity']} @ {b['at']}")
    return "\n".join(lines)


def _write_story(out_hh: pathlib.Path, household: str,
                 story: list[dict]) -> None:
    """Persist the calendar so far. Called after EVERY week: a household
    takes the better part of an hour, and a run that writes nothing until
    it finishes is a run nobody can check on."""
    out_hh.mkdir(parents=True, exist_ok=True)
    (out_hh / "story.yaml").write_text(
        "# GENERATED by src/revamp_v2/story_driven.py — the household's\n"
        "# 21-day calendar as authored by the model, week by week.\n"
        + yaml.safe_dump({"household": household, "days": story},
                         sort_keys=False, allow_unicode=True, width=100))


def generate_story(program, persona_text, cache, client, tag, days_total,
                   force, out_hh=None):
    residents = [r["id"] for r in program["residents"]]
    receptacles = [r["id"] for r in program["receptacles"]]
    loc_lines = "\n".join(f"  {x}" for x in receptacles + ["ELSEWHERE"])
    wmap = ", ".join(f"{i}={n}" for i, n in enumerate(fm.DAY_NAMES))
    story: list[dict] = []
    failed_weeks: list[dict] = []
    for week, lo in enumerate(range(0, days_total, 7)):
        hi = min(lo + 6, days_total - 1)
        schema = build_story_schema(residents, receptacles, lo, hi)

        def _validate(parsed):
            parsed = _normalize_story(parsed)
            if jsonschema is not None:
                jsonschema.validate(parsed, schema)
            return parsed

        user = STORY_USER.format(persona=persona_text, locations=loc_lines,
                                 vocab=", ".join(ACTIVITY_VOCAB),
                                 recap=_recap(story), lo=lo, hi=hi,
                                 weekday_map=wmap)
        seed = make_seed(program["household"], week, tag)
        try:
            parsed = llm_client.generate_json_thinking(
                client, STORY_SYSTEM, user, seed=seed, stage=tag,
                cache=cache, force=force, validate=_validate,
                max_tokens=STORY_MAX_TOKENS, max_retries=1)
        except Exception as e:
            failed_weeks.append({"week": week, "error": repr(e)[:200]})
            print(f"  week {week}: STORY FAILED ({type(e).__name__})")
            continue
        got = sorted(parsed["days"], key=lambda d: d["day"])
        story.extend(got)
        if out_hh is not None:
            _write_story(out_hh, program["household"], story)
        acts = {b["activity"] for d in got for b in d["blocks"]}
        print(f"  week {week}: days {lo}-{hi}, "
              f"{sum(len(d['blocks']) for d in got)} blocks, "
              f"{len(acts)} activities")
    return story, failed_weeks


def blocks_to_residents(story, days_total):
    """story blocks -> the same residents.jsonl rows simulate.py writes.
    A block whose end <= start crosses midnight into the next day."""
    rows = []
    for d in story:
        base = d["day"] * 1440
        for b in d["blocks"]:
            t0 = base + int(b["start"][:2]) * 60 + int(b["start"][3:])
            t1 = base + int(b["end"][:2]) * 60 + int(b["end"][3:])
            if t1 <= t0:
                t1 += 1440
            rows.append({"resident": b["resident"], "activity": b["activity"],
                         "t0": t0, "t1": min(t1, days_total * 1440),
                         "at": b["at"], "note": ""})
    rows.sort(key=lambda r: r["t0"])
    return rows


def run_household(hh_src, out_hh, model, cache, days, force):
    program = yaml.safe_load((hh_src / "routine_program.yaml").read_text())
    persona_text = (hh_src / "persona.yaml").read_text()
    motions = yaml.safe_load((hh_src / "expanded_motions.yaml").read_text())
    client = llm_client._get_client(model)

    story, failed_weeks = generate_story(
        program, persona_text, cache, client, "story_v1_think", days, force,
        out_hh=out_hh)
    _write_story(out_hh, program["household"], story)
    # Persona, program and starting homes belong on disk from the start —
    # they are what the movement pass reads, and a half-built household
    # should still be inspectable.
    for name in ("persona.yaml", "routine_program.yaml",
                 "expanded_motions.yaml"):
        (out_hh / name).write_text((hh_src / name).read_text())
    (out_hh / "timeline_seed0").mkdir(parents=True, exist_ok=True)
    with open(out_hh / "timeline_seed0" / "residents.jsonl", "w") as f:
        for r in blocks_to_residents(story, days):
            f.write(json.dumps(r) + "\n")

    object_ids = list(motions["placements"])
    residents = [r["id"] for r in program["residents"]]
    receptacles = [r["id"] for r in program["receptacles"]]
    locations = receptacles + ["ELSEWHERE"] + \
        [f"person:{r}" for r in residents]
    story_by_day = {d["day"]: d for d in story}
    all_acts = sorted({b["activity"] for d in story for b in d["blocks"]})
    mv_schema = fm.build_schema(object_ids, locations, all_acts)

    state = {o: p["home"] for o, p in motions["placements"].items()}
    events, hourly, history, failed_days = [], [], [], []
    loc_lines = "\n".join(f"  {x}" for x in locations)

    for day in range(days):
        weekday = fm.DAY_NAMES[day % 7]
        d = story_by_day.get(day)
        if d is None:                       # its story week failed
            failed_days.append({"day": day, "error": "no story"})
            d = {"summary": "(story missing)", "blocks": []}
        sched = "\n".join(
            f"  {b['resident']}  {b['start']}-{b['end']}  "
            f"{b['activity']} @ {b['at']}"
            for b in sorted(d["blocks"], key=lambda b: b["start"]))
        recent = [h for h in history if h.startswith(f"d{day-1:02d}")
                  or h.startswith(f"d{day-2:02d}")]
        if recent:
            hist = ("Movements over the last two days (your own earlier "
                    "output):\n" + "\n".join(f"  {h}" for h in recent))
        elif day == 0:
            hist = ("This is the first day; the home starts tidy, "
                    "everything at the spot listed above.")
        else:
            hist = ("No object moved in the last two days; positions above "
                    "are current.")
        user = fm.USER_TEMPLATE.format(
            persona=persona_text, locations=loc_lines, day=day, days=days,
            weekday=weekday,
            schedule=f"  Today in the story: {d['summary']}\n" + sched,
            state="\n".join(f"  {o}: {state[o]}" for o in object_ids),
            history=hist)
        seed = make_seed(program["household"], day, "story_motion_v1_think")

        def _validate(parsed):
            if isinstance(parsed, list):
                parsed = {"movements": parsed}
            elif isinstance(parsed, dict) and "movements" not in parsed:
                for k in ("moves", "events", "movement_log", "actions"):
                    if k in parsed and isinstance(parsed[k], list):
                        parsed = {"movements": parsed[k]}
                        break
            if jsonschema is not None:
                jsonschema.validate(parsed, mv_schema)
            return parsed

        try:
            parsed = llm_client.generate_json_thinking(
                client, fm.SYSTEM, user, seed=seed,
                stage="story_motion_v1_think", cache=cache, force=force,
                validate=_validate, max_tokens=fm.THINKING_MAX_TOKENS,
                max_retries=1)
        except Exception as e:
            failed_days.append({"day": day, "error": repr(e)[:200]})
            print(f"  day {day:2d} {weekday}: GENERATION FAILED "
                  f"({type(e).__name__}) — counted, not retried")
            parsed = {"movements": []}

        moves = sorted(parsed["movements"], key=lambda m: m["time"])
        day_moves = mi = 0

        def _apply(m):
            nonlocal day_moves
            src = state[m["object"]]
            if m["to"] == src:
                return
            t = day * 1440 + int(m["time"][:2]) * 60 + int(m["time"][3:])
            ev = {"t": t, "stamp": f"d{day:02d} {weekday} {m['time']}",
                  "object": m["object"], "from": src, "to": m["to"],
                  "by": f"activity:{m['activity']}"}
            if m.get("note"):
                ev["note"] = m["note"][:60]
            events.append(ev)
            state[m["object"]] = m["to"]
            history.append(
                f"d{day:02d} {m['time']} {m['object']}: {src} -> {m['to']} "
                f"({m['activity']})")
            day_moves += 1

        for hr in range(24):
            t_hour = day * 1440 + hr * 60
            while mi < len(moves):
                m = moves[mi]
                t_m = (day * 1440 + int(m["time"][:2]) * 60
                       + int(m["time"][3:]))
                if t_m > t_hour:
                    break
                _apply(m)
                mi += 1
            snap = {"t": t_hour, "stamp": f"d{day:02d} {weekday} {hr:02d}:00"}
            snap.update({o: state[o] for o in object_ids})
            hourly.append(snap)
        while mi < len(moves):
            _apply(moves[mi])
            mi += 1
        print(f"  day {day:2d} {weekday}: {day_moves} movements")

    out = out_hh / "timeline_seed0"
    out.mkdir(parents=True, exist_ok=True)
    events.sort(key=lambda e: e["t"])
    with open(out / "events.jsonl", "w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")
    with open(out / "hourly.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "stamp"] + object_ids)
        for row in hourly:
            w.writerow([row["t"], row["stamp"]] + [row[o] for o in object_ids])
    with open(out / "residents.jsonl", "w") as f:
        for r in blocks_to_residents(story, days):
            f.write(json.dumps(r) + "\n")
    moves_ct = {o: 0 for o in object_ids}
    for e in events:
        moves_ct[e["object"]] += 1
    meta = {"household": program["household"],
            "household_type": program.get("household_type"),
            "source": str(out_hh), "engine": "story_driven_llm",
            "model": model, "single_pass": True,
            "failed_weeks": failed_weeks, "failed_days": failed_days,
            "n_failed_days": len(failed_days), "days": days, "seed": 0,
            "n_events": len(events),
            "story_activities": all_acts,
            "n_story_activities": len(all_acts),
            "moves_per_object": dict(sorted(moves_ct.items(),
                                            key=lambda kv: -kv[1]))}
    (out / "meta.json").write_text(json.dumps(meta, indent=2))
    return meta


def _main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--households", nargs="+", required=True,
                    help="rule_based household dirs (persona + program + "
                         "expanded_motions)")
    ap.add_argument("--out-root", type=pathlib.Path, required=True)
    ap.add_argument("--model",
                    default=os.environ.get("GENERATION_MODEL",
                                           llm_client.DEFAULT_MODEL))
    ap.add_argument("--days", type=int, default=21)
    ap.add_argument("--cache-dir", default=None)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    slug = llm_client.model_slug(args.model)
    cache = ResponseCache(args.cache_dir or
                          f"/tmp/dynamic-home-eqa-gen-cache-story-{slug}")
    for hh in args.households:
        hh_src = pathlib.Path(hh)
        out_hh = args.out_root / hh_src.name
        print(f"{hh_src.name}: story-driven, {args.days} days")
        meta = run_household(hh_src, out_hh, args.model, cache,
                             args.days, args.force)
        print(f"{meta['household']}: {meta['n_events']} events, "
              f"{meta['n_story_activities']} story activities -> {out_hh}")


if __name__ == "__main__":
    _main()
