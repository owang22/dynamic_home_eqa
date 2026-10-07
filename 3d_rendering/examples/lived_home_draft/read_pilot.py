"""Turn a pilot run into a readable replay and a short summary.

    python -m lived_home.read_pilot results/lived_home/pilot_luna

Writes replay.md (every action in time order, with the residents' thoughts and
inner state) and summary.md (counts that show whether behavior is lifelike and
learnable) into the run folder.
"""
from __future__ import annotations

import collections
import json
import pathlib
import sys


def load(run: pathlib.Path):
    spec = json.loads((run / "household.json").read_text())
    days = sorted(p for p in run.glob("day_*") if p.is_dir())
    per_day = [{f.stem: json.loads(f.read_text()) for f in d.glob("*.json")} for d in days]
    states = json.loads((run / "inner_states.json").read_text())
    thoughts = json.loads((run / "thoughts.json").read_text())
    return spec, per_day, states, thoughts


def replay(spec, per_day, states, thoughts) -> str:
    out = []
    by_key = {(t["day"], t["time"], t["resident"], t["stage"]): t["thinking"] for t in thoughts}
    state_key = {(s["day"], s["time"], s["resident"], s["stage"]): s for s in states}
    for i, day in enumerate(per_day, start=1):
        out.append(f"\n## Day {i}  (situations: {', '.join(day['active_situations']) or 'none'})\n")
        rows = []
        for rid, plan in day["plans"].items():
            first = plan[0]["start"]
            s = state_key.get((i, first, rid, "plan"), {})
            rows.append((plan[0]["start_min"] - 0.5, f"**{rid} plans the day** "
                         f"(stress {s.get('stress')}, tired {s.get('tiredness')}, mood {s.get('mood')}, "
                         f"health {s.get('health')}): " + "; ".join(
                             f"{a['start']} {a['activity']} ({a['room']})" for a in plan)))
        seen_calls = set()
        for e in day["events"]:
            key = (i, e["time"], e["resident"], "act")
            if key in by_key and key not in seen_calls:
                seen_calls.add(key)
                s = state_key.get(key, {})
                habit = s.get("habit_followed")
                rows.append((e["minute"] - 0.1, f"> *{e['resident']} thinks:* {by_key[key][:400]}"
                             + (f" [habit: {habit}]" if habit and habit != "none" else "")))
            thing = e["object"] or e["text"] or ""
            dest = f" -> {e['to']}" if e["verb"] in ("go", "put_down", "give", "pick_up") else ""
            why = f"  _({e['why']})_" if e.get("why") else ""
            rows.append((e["minute"], f"{e['time']} {e['resident']} {e['verb']} {thing}{dest}{why}"))
        for f in day["failed"]:
            rows.append((int(f["time"][:2]) * 60 + int(f["time"][3:]) + 0.05,
                         f"{f['time']} {f['resident']} FAILED {f['action']['verb']} "
                         f"{f['action'].get('object') or f['action'].get('place') or ''}: {f['message']}"))
        out += [r for _, r in sorted(rows, key=lambda x: x[0])]
    return "\n".join(out)


def summary(spec, per_day, states) -> str:
    homes = {o["id"]: o["home"] for o in spec["objects"]}
    out = ["# Pilot summary\n", "## Per day\n",
           "| day | situations | actions | failed | objects moved | objects away from usual place at end |",
           "|---|---|---|---|---|---|"]
    moved_days = collections.Counter()
    for i, day in enumerate(per_day, start=1):
        ev = day["events"]
        moved = {e["object"] for e in ev if e["verb"] in ("pick_up", "give") and e["object"]}
        moved_days.update(moved)
        away = sum(1 for o, spot in day["end_of_day"].items() if spot != homes[o])
        out.append(f"| {i} | {', '.join(day['active_situations']) or '-'} | {len(ev)} | "
                   f"{len(day['failed'])} | {len(moved)} | {away} |")
    never = [o for o in homes if o not in moved_days]
    out.append(f"\nObjects never moved: {len(never)} of {len(homes)}: {', '.join(never)}\n")
    out.append("## Where each moved object ended each day\n")
    out.append("Learnable objects end up in a few places, not one and not many.\n")
    for oid in sorted(moved_days, key=lambda o: -moved_days[o])[:25]:
        ends = [d["end_of_day"][oid] for d in per_day]
        out.append(f"- {oid} (usual: {homes[oid]}): {' | '.join(ends)}")
    out.append("\n## Response habits followed\n")
    out.append("A habit is learnable if it shows up when its trigger is present, but not every time.\n")
    habits = {(r["id"], h["id"]): h for r in spec["residents"] for h in r["response_habits"]}
    counts = collections.Counter((s["resident"], s["habit_followed"]) for s in states
                                 if s.get("habit_followed") not in (None, "none"))
    for (rid, hid), h in habits.items():
        days_used = sorted({s["day"] for s in states if s["resident"] == rid
                            and s.get("habit_followed") == hid})
        out.append(f"- {rid} / {hid} (when {h['trigger']}): {counts[(rid, hid)]} times, "
                   f"days {days_used or '-'}")
    out.append("\n## Inner state by day (mean over the day's calls)\n")
    out.append("| day | resident | stress | tiredness | mood | health |")
    out.append("|---|---|---|---|---|---|")
    groups = collections.defaultdict(list)
    for s in states:
        groups[(s["day"], s["resident"])].append(s)
    for (day, rid), rows in sorted(groups.items()):
        mean = lambda k: sum(r[k] for r in rows) / len(rows)
        out.append(f"| {day} | {rid} | {mean('stress'):.1f} | {mean('tiredness'):.1f} | "
                   f"{mean('mood'):.1f} | {mean('health'):.1f} |")
    return "\n".join(out)


def main() -> None:
    run = pathlib.Path(sys.argv[1])
    spec, per_day, states, thoughts = load(run)
    (run / "replay.md").write_text(replay(spec, per_day, states, thoughts))
    (run / "summary.md").write_text(summary(spec, per_day, states))
    print(f"wrote {run / 'replay.md'} and {run / 'summary.md'}")


if __name__ == "__main__":
    main()
