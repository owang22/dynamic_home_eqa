"""Arm B of the rules-vs-reasoning experiment: object movements written
directly by the LLM, one day at a time, with no rule formalism at all.

Both arms share everything upstream and downstream — the same persona, the
same L2 schedule, the same L3 *human* realization (skips, fragments,
jitter), the same trace/viewer plumbing — so the single difference is the
movement engine. Arm A expands authored per-object rules; this arm shows
the model the world and asks what happened today:

    for each day d:
        prompt = persona + relationships
               + today's realized resident schedule (from residents.jsonl)
               + where every object is right now
               + the movements of the last two days (its own prior output)
        -> JSON list of {time, object, to, why} for day d

The prompt states the GOAL (an ordinary lived-in day) and deliberately no
distributional targets — no "some objects should rarely move", no cycle
warnings — because whether free reasoning lands a realistic mix is exactly
what the experiment measures. Bias the prompt and the measurement is of
the prompt.

Outputs the same timeline shape simulate.py produces (events.jsonl,
hourly.csv, residents.jsonl, meta.json), so spatialize.py and the viewer
consume it unchanged. Seeded + response-cached like every other LLM call
in the pipeline; the CLI cannot seed sampling but the cache still makes a
finished run replay byte-identically.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

import yaml

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT / "src"))

from dynamic_home_eqa.generation import llm_client            # noqa: E402
from dynamic_home_eqa.generation.cache import (               # noqa: E402
    ResponseCache, make_seed)

try:
    import jsonschema
except ImportError:                                           # pragma: no cover
    jsonschema = None

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
# One pass, with room to finish. The think block and the answer share
# this budget: measured prompt ~2.2k tokens and answer ~0.8k against
# max_model_len 32768, so 28k lets reasoning run long and still land the
# JSON. Retrying a TRUNCATED answer is the wrong instrument — it re-rolls
# a ~15k-token think block hoping for a shorter reply, and it selects for
# terser (worse) days. A budget costs nothing when it goes unused.
MAX_TOKENS = 8192
# 24k, not 28k: the prompt carries two days of movement history, so a busy
# day pushes it past ~4k tokens and prompt+max_tokens crossed the served
# 32768 — vLLM REJECTS such a request (400) rather than truncating it, so
# the day is lost outright. 24k leaves ~8k of prompt headroom and still
# gives the think block far more room than it has been observed to use.
THINKING_MAX_TOKENS = 24000

SYSTEM = """\
You reconstruct the object life of one simulated household, one day at a
time. You are given who lives there, what today's schedule actually was
(including what got skipped), where every object is right now, and what
happened on recent days. Write out every object movement that happens
today: each time a resident picks something up, sets it down, takes it
along, puts it away, or leaves it somewhere.

An object moves only because someone moved it, on purpose or by accident,
and only at a moment when the schedule puts that person there to do it.
Your job is simply to say what these particular people, being who they
are, actually did with their things today. Respond only with valid JSON
matching the provided schema. No commentary.
"""

USER_TEMPLATE = """\
The household (persona, verbatim):

{persona}

Places in this home (`to` must be one of these; `person:<resident_id>`
means carried on that person, ELSEWHERE means out of the house with
whoever took it):
{locations}

Today is day {day} of {days} — {weekday}. What each resident ACTUALLY did
today — this is AFTER real-life slippage, so a routine that got skipped
today is simply absent from the list:

{schedule}

Where every object is at the start of today:

{state}

{history}

Write today's object movements in chronological order: `time` (HH:MM),
`object`, `activity` (which scheduled activity this movement belongs to —
pick from today's schedule above; use "other" only for something outside
any scheduled activity, like absent-minded drift), `to` (where it ends
up), and optionally `note` — a few words on who and what, only when the
activity alone does not say it. An object not mentioned simply stays
where it is all day.
"""


def build_schema(object_ids: list[str], locations: list[str],
                 activities: list[str]) -> dict:
    """Each movement names the ACTIVITY it belongs to, from the household's
    own realized schedule (plus "other" for off-schedule acts like drift).
    Declared before `to`, so the destination is chosen with its context
    already stated — and downstream QA generation gets a machine-readable
    "what was happening" on every event instead of free prose."""
    return {
        "type": "object", "additionalProperties": False,
        "required": ["movements"],
        "properties": {"movements": {
            "type": "array", "minItems": 0, "maxItems": 80,
            "items": {
                "type": "object", "additionalProperties": False,
                "required": ["time", "object", "activity", "to"],
                "properties": {
                    "time": {"type": "string",
                             "pattern": "^([01][0-9]|2[0-3]):[0-5][0-9]$"},
                    "object": {"enum": object_ids},
                    "activity": {"enum": sorted(set(activities)) + ["other"]},
                    "to": {"enum": locations},
                    "note": {"type": "string", "maxLength": 60},
                },
            },
        }},
    }


def load_schedule(timeline: pathlib.Path, days: int) -> dict[int, list]:
    """Per-day realized resident blocks from arm A's residents.jsonl."""
    by_day: dict[int, list] = {d: [] for d in range(days)}
    for line in (timeline / "residents.jsonl").open():
        b = json.loads(line)
        d = int(b["t0"]) // 1440
        if d in by_day:
            by_day[d].append(b)
    return by_day


def fmt_minutes(t: int) -> str:
    return f"{(t % 1440) // 60:02d}:{t % 60:02d}"


def fmt_schedule(blocks: list) -> str:
    lines = [f"  {b['resident']}  {fmt_minutes(b['t0'])}-"
             f"{fmt_minutes(b['t1'])}  {b['activity']} @ {b['at']}"
             for b in sorted(blocks, key=lambda b: b["t0"])]
    return "\n".join(lines) or "  (nobody home all day)"


def run_household(hh_a: pathlib.Path, out_hh: pathlib.Path, model: str,
                  cache: ResponseCache, seed_tag: str, days: int,
                  force: bool, thinking: bool = False) -> dict:
    program = yaml.safe_load((hh_a / "routine_program.yaml").read_text())
    persona_text = (hh_a / "persona.yaml").read_text()
    motions = yaml.safe_load((hh_a / "expanded_motions.yaml").read_text())
    timeline_a = hh_a / "timeline_seed0"

    object_ids = list(motions["placements"])
    residents = [r["id"] for r in program["residents"]]
    receptacles = [r["id"] for r in program["receptacles"]]
    locations = receptacles + ["ELSEWHERE"] + \
        [f"person:{r}" for r in residents]
    schedule = load_schedule(hh_a / "timeline_seed0", days)
    all_activities = sorted({b["activity"] for blocks in schedule.values()
                             for b in blocks})
    schema = build_schema(object_ids, locations, all_activities)
    client = llm_client._get_client(model)

    state = {o: p["home"] for o, p in motions["placements"].items()}
    events: list[dict] = []
    hourly: list[dict] = []
    failed_days: list[dict] = []
    history: list[str] = []      # one compact line per movement, tagged by day
    loc_lines = "\n".join(f"  {x}" for x in locations)

    for day in range(days):
        weekday = DAY_NAMES[day % 7]
        recent = [h for h in history if h.startswith(f"d{day-1:02d}")
                  or h.startswith(f"d{day-2:02d}")]
        if recent:
            hist_txt = ("Movements over the last two days (your own earlier "
                        "output — days before that happened too, they are "
                        "just not listed):\n"
                        + "\n".join(f"  {h}" for h in recent))
        elif day == 0:
            hist_txt = ("This is the first day; the home starts tidy, "
                        "everything at the spot listed above.")
        else:
            # Never claim day 0 again mid-run: after a quiet stretch that
            # lie contradicted the state block and invited more quiet.
            hist_txt = ("No object moved in the last two days; days before "
                        "that happened as normal. Positions above are "
                        "current.")
        user = USER_TEMPLATE.format(
            persona=persona_text, locations=loc_lines, day=day, days=days,
            weekday=weekday, schedule=fmt_schedule(schedule[day]),
            state="\n".join(f"  {o}: {state[o]}" for o in object_ids),
            history=hist_txt)
        seed = make_seed(program["household"], day, seed_tag)
        if thinking:
            # Fix #1 for the dead-day collapse: thinking mode. On this
            # stack the think block and the JSON grammar are mutually
            # exclusive (the grammar suppresses thinking outright), so
            # the schema drops from enforced grammar to a validator and
            # the model gets actual reasoning space before it must commit
            # to `{"movements": [...` — testing whether the empty-array
            # attractor was the absence of that space.
            def _validate(parsed) -> dict:
                # Without the grammar the shape drifts in known, harmless
                # ways (measured: a bare movement ARRAY instead of the
                # {"movements": [...]} wrapper; a renamed key). Normalize
                # deterministically, then validate strictly — rejecting a
                # perfect day over a missing wrapper wastes retries on
                # exactly the drift the docstring predicts.
                if isinstance(parsed, list):
                    parsed = {"movements": parsed}
                elif isinstance(parsed, dict) and "movements" not in parsed:
                    for k in ("moves", "events", "movement_log", "actions"):
                        if k in parsed and isinstance(parsed[k], list):
                            parsed = {"movements": parsed[k]}
                            break
                if jsonschema is not None:
                    jsonschema.validate(parsed, schema)
                return parsed
            # max_retries=1: a single attempt, no re-rolling. A day
            # that fails to parse is RECORDED as a failure and the run
            # continues — the failure rate is a reported number, not
            # something quietly resampled away.
            try:
                parsed = llm_client.generate_json_thinking(
                    client, SYSTEM, user, seed=seed, stage=seed_tag,
                    cache=cache, force=force, validate=_validate,
                    max_tokens=THINKING_MAX_TOKENS, max_retries=1)
            except Exception as e:
                failed_days.append({"day": day, "error": repr(e)[:200]})
                print(f"  day {day:2d} {weekday}: GENERATION FAILED "
                      f"({type(e).__name__}) — counted, not retried")
                parsed = {"movements": []}
        else:
            parsed = llm_client.generate_json(
                client, SYSTEM, user, schema, seed=seed, stage=seed_tag,
                cache=cache, force=force)
        # Movements and hourly snapshots are INTERLEAVED in time. Taking
        # the snapshots after replaying the whole day recorded the
        # end-of-day state against all 24 hours, so a resident who left at
        # 18:14 showed their keys ELSEWHERE from midnight and the day read
        # as frozen — events.jsonl right, hourly.csv wrong.
        moves = sorted(parsed["movements"], key=lambda m: m["time"])
        day_moves = mi = 0

        def _apply(m: dict) -> int:
            src = state[m["object"]]
            if m["to"] == src:      # not an event: nothing changed
                return 0
            t = (day * 1440 + int(m["time"][:2]) * 60 + int(m["time"][3:]))
            # Same `by` convention as the rule-based simulator, so the
            # viewer and any event consumer read both methods alike; the
            # engine provenance lives in meta.json, not on every line.
            ev = {"t": t, "stamp": f"d{day:02d} {weekday} {m['time']}",
                  "object": m["object"], "from": src, "to": m["to"],
                  "by": f"activity:{m['activity']}"}
            if m.get("note"):
                ev["note"] = m["note"][:60]
            events.append(ev)
            state[m["object"]] = m["to"]
            history.append(
                f"d{day:02d} {m['time']} {m['object']}: {src} -> {m['to']} "
                f"({m['activity']}{': ' + m['note'][:40] if m.get('note') else ''})")
            return 1

        for hr in range(24):
            t_hour = day * 1440 + hr * 60
            while mi < len(moves):
                m = moves[mi]
                t_m = (day * 1440 + int(m["time"][:2]) * 60
                       + int(m["time"][3:]))
                if t_m > t_hour:
                    break
                day_moves += _apply(m)
                mi += 1
            snap = {"t": t_hour, "stamp": f"d{day:02d} {weekday} {hr:02d}:00"}
            snap.update({o: state[o] for o in object_ids})
            hourly.append(snap)
        while mi < len(moves):            # anything after 23:00
            day_moves += _apply(moves[mi])
            mi += 1
        print(f"  day {day:2d} {weekday}: {day_moves} movements")

    # -- timeline dir in simulate.py's exact shape ------------------------
    out = out_hh / "timeline_seed0"
    out.mkdir(parents=True, exist_ok=True)
    events.sort(key=lambda e: e["t"])
    with open(out / "events.jsonl", "w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")
    import csv
    with open(out / "hourly.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "stamp"] + object_ids)
        for row in hourly:
            w.writerow([row["t"], row["stamp"]] + [row[o] for o in object_ids])
    (out / "residents.jsonl").write_text(
        (timeline_a / "residents.jsonl").read_text())
    moves: dict[str, int] = {o: 0 for o in object_ids}
    for e in events:
        moves[e["object"]] += 1
    meta = {"household": program["household"],
            "household_type": program.get("household_type"),
            "source": str(out_hh), "engine": "freeform_llm",
            "model": model, "single_pass": True,
            "failed_days": failed_days,
            "n_failed_days": len(failed_days), "days": days, "seed": 0,
            "n_events": len(events),
            "moves_per_object": dict(sorted(moves.items(),
                                            key=lambda kv: -kv[1]))}
    (out / "meta.json").write_text(json.dumps(meta, indent=2))
    # siblings spatialize/the viewer expect next to the timeline
    for name in ("persona.yaml", "routine_program.yaml",
                 "expanded_motions.yaml"):
        (out_hh / name).write_text((hh_a / name).read_text())
    return meta


def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--households", nargs="+", required=True,
                    help="arm A household dirs (need program+persona+"
                         "expanded_motions+timeline_seed0)")
    ap.add_argument("--out-root", type=pathlib.Path, required=True)
    ap.add_argument("--model",
                    default=os.environ.get("GENERATION_MODEL",
                                           llm_client.DEFAULT_MODEL))
    ap.add_argument("--days", type=int, default=21)
    ap.add_argument("--cache-dir", default=None)
    ap.add_argument("--thinking", action="store_true",
                    help="reason freely first, validate the JSON after — "
                         "no guided decoding (incompatible with thinking)")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    slug = llm_client.model_slug(args.model)
    cache = ResponseCache(args.cache_dir or
                          f"/tmp/dynamic-home-eqa-gen-cache-freeform-{slug}")
    for hh in args.households:
        hh_a = pathlib.Path(hh)
        out_hh = args.out_root / hh_a.name
        print(f"{hh_a.name}: freeform motions, {args.days} days")
        # v3: single pass at the larger budget. A fresh tag so nothing
        # replays from the retry-era cache — a day that only succeeded on
        # its second attempt is a selected sample, exactly what single
        # pass exists to avoid.
        tag = ("freeform_motion_v4_think" if args.thinking
               else "freeform_motion_v4")
        meta = run_household(hh_a, out_hh, args.model, cache, tag,
                             args.days, args.force, thinking=args.thinking)
        print(f"{meta['household']}: {meta['n_events']} events -> {out_hh}")


if __name__ == "__main__":
    _main()
