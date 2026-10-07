"""Turn a pilot run into a readable replay and a report.

    PYTHONPATH=3d_rendering/src python -m lived_home.read_pilot <run folder>

Works on a finished run and on a run in progress (it reads the day folders
that exist, plus events.jsonl and responses.jsonl for the day being lived).
Writes replay.md and report.md into the run folder.

report.md sections:
  1. cost, calls and the rate of rejected actions
  2. per object type: instances moved, and where each instance ended each day
  3. per response habit: how often its trigger occurred and the habit followed
  4. sick days against normal days, for both residents
  5. (written by hand from replay.md: lifelike and wrong-looking excerpts)
"""
from __future__ import annotations

import collections
import json
import pathlib
import statistics
import sys

MOVES = ("pick_up", "pocket", "give", "put_down")


def jl(path: pathlib.Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def load(run: pathlib.Path) -> dict:
    spec = json.loads((run / "household.json").read_text())
    days = []
    for d in sorted(p for p in run.glob("day_*") if p.is_dir()):
        days.append({f.stem: json.loads(f.read_text()) for f in d.glob("*.json")})
    schedule = json.loads((run / "schedule.json").read_text()) if (run / "schedule.json").exists() else []
    return {"spec": spec, "days": days, "schedule": schedule,
            "events": jl(run / "events.jsonl"), "responses": jl(run / "responses.jsonl"),
            "failed": jl(run / "failed.jsonl"), "calls": jl(run / "calls.jsonl"),
            "usage": json.loads((run / "usage.json").read_text()) if (run / "usage.json").exists() else {}}


def where(snap: dict) -> str:
    if snap["place"]:
        return snap["place"] + (" (hidden)" if snap["hidden"] else "")
    return f"with {snap['holder']}" if snap["holder"] else snap["text"]


# ---------------------------------------------------------------- replay
def replay(r: dict) -> str:
    out = []
    by_day_events = collections.defaultdict(list)
    for e in r["events"]:
        by_day_events[e["day"]].append(e)
    by_day_resp = collections.defaultdict(list)
    for x in r["responses"]:
        by_day_resp[x["day"]].append(x)
    by_day_failed = collections.defaultdict(list)
    for f in r["failed"]:
        by_day_failed[f["day"]].append(f)
    for day in sorted(set(by_day_events) | set(by_day_resp)):
        active = r["schedule"][day - 1] if day - 1 < len(r["schedule"]) else []
        out.append(f"\n## Day {day}  (situations: {', '.join(active) or 'none'})\n")
        rows = []
        for x in by_day_resp[day]:
            s = x["inner_state"]
            feel = (f"stress {s['stress']}, tired {s['tiredness']}, mood {s['mood']}, "
                    f"health {s['health']}")
            if x["stage"] == "plan":
                acts = x["activities"]
                start = acts[0]["start"] if acts else "00:00"
                rows.append((_m(start) - 0.5, f"**{x['resident']} plans the day** ({feel})"
                             + (" [off-routine day]" if x.get("off_routine") else "") + ": "
                             + "; ".join(f"{a['start']} {a['activity']} ({a['room']})" for a in acts)
                             + f"\n> *{x['resident']} thinks:* {x['thinking']}"))
            else:
                habit = x.get("habit_followed")
                trig = x.get("habit_triggers_now") or []
                tag = []
                if trig:
                    tag.append(f"triggers: {', '.join(trig)}")
                if habit and habit != "none":
                    tag.append(f"follows: {habit}")
                prob = f" (after a failed action: {x['problem_given']})" if x.get("problem_given") else ""
                rows.append((_m(x["time"]) + (0.07 if x.get("problem_given") else -0.1),
                             f"> **{x['resident']} {x['time']} — {x['activity']}**{prob} ({feel}"
                             + (f"; {'; '.join(tag)}" if tag else "") + f")\n> {x['thinking']}"))
        for e in by_day_events[day]:
            if e.get("implied"):
                rows.append((e["minute"], f"{e['time']} {e['resident']} (steps over to {e['to']})"))
                continue
            thing = e["object"] or e["text"] or ""
            extra = ""
            if e["verb"] in ("go", "put_down", "give", "pick_up", "pocket"):
                extra = f" -> {e['to']}"
            if e["verb"] == "put_down" and e.get("hidden_after"):
                extra += " [hidden]"
            if e["verb"] in ("leave_home", "come_home") and e.get("carried"):
                extra += f" carrying {', '.join(e['carried'])}"
            if e.get("settled"):
                extra += f" (now loose: {', '.join(e['settled'])})"
            why = f"  _({e['why']})_" if e.get("why") else ""
            to_whom = f" to {e['person']}" if e.get("person") else ""
            rows.append((e["minute"], f"{e['time']} {e['resident']} {e['verb']}{to_whom} {thing}{extra}{why}"))
        for f in by_day_failed[day]:
            a = f["action"]
            rows.append((_m(f["time"]) + 0.05,
                         f"{f['time']} {f['resident']} **REJECTED** {a['verb']} "
                         f"{a.get('object') or a.get('place') or ''}: {f['message']}"))
        out += [t for _, t in sorted(rows, key=lambda x: x[0])]
    return "\n".join(out)


def _m(t: str) -> int:
    h, m = t.split(":")
    return int(h) * 60 + int(m)


# ---------------------------------------------------------------- report
def report(r: dict) -> str:
    spec, days, events = r["spec"], r["days"], r["events"]
    objects = {o["id"]: o for o in spec["objects"]}
    out = ["# Pilot report\n"]

    # 1. cost, calls, rejections
    live = [c for c in r["calls"] if not c["cached"]]
    cost = sum(c["cost"] or 0 for c in live)
    real = [e for e in events if not e.get("implied") and e["verb"] != "come_home"]
    rejected = len(r["failed"])
    out.append("## 1. Cost, calls, rejected actions\n")
    out.append(f"- days lived: {len(days)} complete" + (f" (+ day {events[-1]['day']} in progress)"
                                                        if events and events[-1]["day"] > len(days) else ""))
    out.append(f"- model calls: {len(live)} (cache hits {len(r['calls']) - len(live)}), cost ${cost:.2f}")
    by_stage = collections.defaultdict(list)
    for c in live:
        by_stage[c["stage"].split("/")[0]].append(c)
    for stage, cs in sorted(by_stage.items()):
        pt = [c["prompt_tokens"] for c in cs if c["prompt_tokens"]]
        ct = [c["completion_tokens"] for c in cs if c["completion_tokens"]]
        rt = [c["reasoning_tokens"] for c in cs if c["reasoning_tokens"] is not None]
        secs = [c["seconds"] for c in cs]
        out.append(f"  - {stage}: {len(cs)} calls, ${sum(c['cost'] or 0 for c in cs):.2f}; prompt tokens "
                   f"median {_med(pt)} max {max(pt, default=0)}; output median {_med(ct)} "
                   f"(reasoning {_med(rt)}); {_med(secs)} s median")
    probs = [c for c in r["calls"] if c.get("problem")]
    out.append(f"- answers that failed a check and were retried: {len(probs)}")
    for c in probs[:10]:
        out.append(f"  - {c['stage']}: {c['problem'][:200]}")
    out.append(f"- actions carried out: {len(real)}; rejected: {rejected} "
               f"({100 * rejected / max(1, len(real) + rejected):.1f}% of attempted)")
    out.append(f"- steps within a room the engine filled in (picked up from another spot in the room): "
               f"{sum(1 for e in events if e.get('implied'))}")
    kinds = collections.Counter(f["action"]["verb"] for f in r["failed"])
    out.append(f"- rejected by verb: {dict(kinds)}")
    msgs = collections.Counter(_shape(f["message"]) for f in r["failed"])
    out.append("- rejection reasons: " + "; ".join(f"{m} ({n})" for m, n in msgs.most_common(8)))
    rel = collections.Counter((e.get("relation") or "default") for e in events if e["verb"] == "put_down")
    out.append(f"- put_down relations used: {dict(rel)}; put down out of sight: "
               f"{sum(1 for e in events if e['verb'] == 'put_down' and e.get('hidden_after'))}")
    into = [e for e in events if e["verb"] == "put_down" and (e.get("to_pos") or {}).get("at") == "inside"]
    out.append(f"- put into a bag or basket: {len(into)}")
    outings = [e for e in events if e["verb"] == "leave_home"]
    out.append(f"- times someone left home: {len(outings)}; carrying: "
               + "; ".join(f"{e['resident']} d{e['day']} {e['time']}: {', '.join(e.get('carried') or []) or 'nothing'}"
                           for e in outings[:12]))
    for d, day in enumerate(days, start=1):
        held = {rid: v["hands"] for rid, v in day.get("at_night", {}).items() if v["hands"]}
        if held:
            out.append(f"- day {d}: still holding at night: {held}")
        if day.get("skipped_activities"):
            out.append(f"- day {d}: activities skipped because their time had passed: "
                       + "; ".join(f"{s['resident']} {s['activity']} ({s['planned']}, now {s['now']})"
                                   for s in day["skipped_activities"]))

    # 2. per type
    out.append("\n## 2. Object types: instances moved, and where each instance ended each day\n")
    out.append("Learnable objects end up in a few places, not one and not many. "
               "Columns: start, then the end of each day. * marks a day it moved.\n")
    moved_on = collections.defaultdict(set)
    for e in events:
        if e["verb"] in MOVES and e.get("object") and not e.get("implied"):
            moved_on[e["object"]].add(e["day"])
    by_type = collections.defaultdict(list)
    for oid, o in objects.items():
        by_type[o["type"]].append(oid)
    rows = []
    for t, ids in by_type.items():
        moved = [i for i in ids if moved_on.get(i)]
        rows.append((len(moved), t, ids, moved))
    out.append(f"Types: {len(rows)}; with any instance moved: {sum(1 for r_ in rows if r_[0])}; "
               f"objects moved at least once: {len(moved_on)} of {len(objects)}\n")
    for n, t, ids, moved in sorted(rows, key=lambda x: (-x[0], x[1])):
        if not n:
            continue
        out.append(f"### {t}: {n} of {len(ids)} instances moved")
        for oid in sorted(ids, key=lambda i: -len(moved_on.get(i, ()))):
            if oid not in moved_on:
                continue
            start = objects[oid]["start"]
            cells = [start.get("place") or f"inside {start.get('carrier')}"]
            ends = set()
            for d, day in enumerate(days, start=1):
                snap = day["end_of_day"][oid]
                ends.add(snap["place"] or f"with {snap['holder']}")
                cells.append(where(snap) + ("*" if d in moved_on[oid] else ""))
            out.append(f"- {oid}: " + " | ".join(cells) + f"  ({len(ends)} distinct end places)")
        out.append("")
    never = sorted(t for n, t, ids, _ in rows if n == 0)
    out.append(f"Types never moved ({len(never)}): {', '.join(never)}\n")

    # 3. habits
    out.append("## 3. Response habits: trigger present, habit followed\n")
    out.append("From each activity answer: which habits' triggers the resident said were true, "
               "and which habit they followed.\n")
    acts = [x for x in r["responses"] if x["stage"] == "act"]
    out.append("| resident | habit | how often (stated) | answers with trigger | followed | followed with trigger | followed without trigger | days followed |")
    out.append("|---|---|---|---|---|---|---|---|")
    for res in spec["residents"]:
        mine = [x for x in acts if x["resident"] == res["id"]]
        for h in res["response_habits"]:
            trig = [x for x in mine if h["id"] in (x.get("habit_triggers_now") or [])]
            fol = [x for x in mine if x.get("habit_followed") == h["id"]]
            both = [x for x in fol if h["id"] in (x.get("habit_triggers_now") or [])]
            out.append(f"| {res['id']} | {h['id']}: when {h['trigger']}, {h['behavior']} | {h['how_often']} | "
                       f"{len(trig)} of {len(mine)} | {len(fol)} | {len(both)} | {len(fol) - len(both)} | "
                       f"{sorted({x['day'] for x in fol}) or '-'} |")

    # 4. sick days
    out.append("\n## 4. Sick days against normal days\n")
    sick_days = [d + 1 for d, active in enumerate(r["schedule"]) if "sick" in active]
    sick = next((s for s in spec["situations"] if s["id"] == "sick"), None)
    out.append(f"Sick days: {sick_days}; sick: {sick['happens_to'] if sick else '?'}\n")
    done_days = sorted({e["day"] for e in events})
    for res in spec["residents"]:
        rid = res["id"]
        role = "sick" if sick and rid in sick["happens_to"] else "the other resident"
        out.append(f"### {rid} ({role})\n")
        out.append("| day | sick day | wake | sleep | minutes out | objects moved | rooms by actions | stress | tired | mood | health |")
        out.append("|---|---|---|---|---|---|---|---|---|---|---|")
        per_day_objs = {}
        for d in done_days:
            ev = [e for e in events if e["day"] == d and e["resident"] == rid and not e.get("implied")]
            plan = next((x for x in r["responses"] if x["day"] == d and x["resident"] == rid
                         and x["stage"] == "plan"), None)
            wake = plan["activities"][0]["start"] if plan and plan["activities"] else "-"
            sleep = plan["activities"][-1]["start"] if plan and plan["activities"] else "-"
            out_min = sum(e["minutes"] for e in ev if e["verb"] == "leave_home")
            objs = {e["object"] for e in ev if e["verb"] in MOVES and e["object"]}
            per_day_objs[d] = objs
            rooms = collections.Counter(_room(spec, e) for e in ev if e["verb"] in ("do", "put_down", "pick_up"))
            st = [x["inner_state"] for x in r["responses"] if x["day"] == d and x["resident"] == rid]
            mean = lambda k: f"{statistics.mean(s[k] for s in st):.1f}" if st else "-"
            out.append(f"| {d} | {'yes' if d in sick_days else ''} | {wake} | {sleep} | {out_min} | {len(objs)} | "
                       + ", ".join(f"{k} {v}" for k, v in rooms.most_common(4))
                       + f" | {mean('stress')} | {mean('tiredness')} | {mean('mood')} | {mean('health')} |")
        on = set().union(*[per_day_objs[d] for d in done_days if d in sick_days]) if sick_days else set()
        off = set().union(*[per_day_objs[d] for d in done_days if d not in sick_days]) if done_days else set()
        out.append(f"\nMoved only on sick days: {', '.join(sorted(on - off)) or '-'}")
        out.append(f"\nMoved only on other days: {', '.join(sorted(off - on)) or '-'}\n")
    out.append("## 5. Excerpts\n\nSee the hand-written section in the pilot write-up, chosen from replay.md.\n")
    return "\n".join(out)


def _room(spec, e):
    places = {p["id"]: p["room"] for p in spec["layout"]["places"]}
    to = e.get("to_pos") or {}
    p = to.get("place") or (e["to"] if isinstance(e["to"], str) else None)
    if e["verb"] == "do":
        p = e["to"]
    return places.get(p, "elsewhere")


def _shape(msg: str) -> str:
    import re
    return re.sub(r"\b[a-z]+(_[a-z0-9]+)+\b", "X", msg)[:70]


def _med(xs):
    return round(statistics.median(xs)) if xs else 0


def main() -> None:
    run = pathlib.Path(sys.argv[1])
    r = load(run)
    (run / "replay.md").write_text(replay(r))
    (run / "report.md").write_text(report(r))
    print(f"wrote {run / 'replay.md'} and {run / 'report.md'}")


if __name__ == "__main__":
    main()
