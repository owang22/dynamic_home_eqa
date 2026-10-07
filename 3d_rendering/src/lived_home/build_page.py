"""Build the viewer page for a run (finished or in progress).

    PYTHONPATH=3d_rendering/src python -m lived_home.build_page <run folder>

Writes <run>/page/index.html: page_template.html with the run's data inlined.
"""
from __future__ import annotations

import datetime
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def jl(p: pathlib.Path) -> list:
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass                                    # a line being written right now
    return out


def build(run: pathlib.Path) -> dict:
    spec = json.loads((run / "household.json").read_text())
    schedule = json.loads((run / "schedule.json").read_text()) if (run / "schedule.json").exists() else []
    subjects = json.loads((run / "subjects.json").read_text()) if (run / "subjects.json").exists() else {}
    events = jl(run / "events.jsonl")
    responses = jl(run / "responses.jsonl")
    failed = jl(run / "failed.jsonl")
    calls = [c for c in jl(run / "calls.jsonl") if not c.get("cached")]
    keep_ev = ("day", "minute", "resident", "verb", "object", "from", "to", "to_pos", "why", "text",
               "person", "implied", "carried", "minutes", "relation", "ref", "settled",
               "minutes_filled", "minutes_as_written", "hidden_after")
    ev = [{k: e[k] for k in keep_ev if e.get(k) not in (None, "", [], False)} for e in events]
    resp = []
    for x in responses:
        r = {k: x[k] for k in ("day", "time", "resident", "stage", "activity", "thinking", "inner_state",
                               "habit_triggers_now", "habit_followed", "problem_given", "off_routine")
             if x.get(k) not in (None, "", [])}
        if x["stage"] == "plan":
            r["activities"] = [{k: a[k] for k in ("start", "end", "activity", "room", "intention", "uses")}
                               for a in x["activities"]]
        else:
            r["actions"] = [{k: v for k, v in a.items() if v not in ("", 0, None)} for a in x["actions"]]
        resp.append(r)
    by_day = {}
    for c in calls:
        parts = c["stage"].split("/")
        d = parts[2] if parts[0] in ("act", "plan") and len(parts) > 2 else "create"
        b = by_day.setdefault(d, {"calls": 0, "cost": 0.0, "prompt_tokens": 0, "output_tokens": 0})
        b["calls"] += 1
        b["cost"] += c.get("cost") or 0
        b["prompt_tokens"] += c.get("prompt_tokens") or 0
        b["output_tokens"] += c.get("completion_tokens") or 0
    days_done = len([p for p in run.glob("day_*") if p.is_dir()])
    last_day = max([e["day"] for e in events] + [0])
    create_calls = jl(run / "create_calls.jsonl")
    return {
        "built": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "run": run.name, "weekdays": WEEKDAYS,
        "home": spec.get("home"), "layout": spec["layout"], "residents": spec["residents"],
        "objects": spec["objects"], "situations": spec["situations"],
        "disturbances": spec["small_disturbances"], "schedule": schedule, "subjects": subjects,
        "events": ev, "responses": resp, "failed": failed, "calls_by_day": by_day,
        "create_cost": sum(c.get("cost") or 0 for c in create_calls if not c.get("cached")),
        "days_done": days_done, "last_day": last_day,
    }


def main() -> None:
    run = pathlib.Path(sys.argv[1])
    data = build(run)
    names = " and ".join(r["name"].split()[0] for r in data["residents"])
    html = (HERE / "page_template.html").read_text()
    html = html.replace("__TITLE__", f"{names} at Home")
    blob = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    html = html.replace("/*__DATA__*/", blob)
    out = run / "page"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(html)
    print(f"wrote {out / 'index.html'} ({len(html) / 1e6:.1f} MB; {len(data['events'])} actions, "
          f"{len(data['responses'])} answers, days done {data['days_done']}, last day {data['last_day']})")


if __name__ == "__main__":
    main()
