"""Generate one household and live through N days with roleplaying residents.

    python -m lived_home.run_pilot --model gpt-5.6-luna --effort medium \
        --days 7 --out results/lived_home/pilot_luna
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import random

from lived_home import director, prompts
from lived_home.calls import Caller, check_household, check_plan, to_minute
from lived_home.home_layout import Layout
from lived_home.schemas import WEEKDAYS, act_schema, household_schema, plan_schema
from lived_home.world import World, clock

MAX_REPLANS = 3     # per activity, after an action fails
START_PLACE = "bed"


def lines(items) -> str:
    return "\n".join(f"- {x}" for x in items) or "- (none)"


class Household:
    def __init__(self, caller: Caller, layout: Layout, spec: dict, days: int,
                 variation: float, seed: int, forced: list) -> None:
        self.caller, self.layout, self.spec = caller, layout, spec
        self.days, self.variation, self.seed = days, variation, seed
        self.people = {r["id"]: r for r in spec["residents"]}
        self.rids = list(self.people)
        self.objects = {o["id"]: o for o in spec["objects"]}
        self.situations = {s["id"]: s for s in spec["situations"]}
        self.schedule = director.schedule_situations(spec["situations"], days, seed, forced)
        self.world = World(layout, self.objects, self.rids, {r: START_PLACE for r in self.rids})
        self.rooms = list(layout.rooms)
        self.systems = {r: self._system(r) for r in self.rids}
        self.recap = {r: "This is the first day of the simulation." for r in self.rids}
        self.inbox = {r: [] for r in self.rids}
        self.states, self.thoughts = [], []

    def _system(self, rid: str) -> str:
        p = self.people[rid]
        others = ", ".join(f"{o['name']} (id {o['id']}, {o['age']}, {o['job']})"
                           for o in self.spec["residents"] if o["id"] != rid)
        habits = [f"{h['id']}: when {h['trigger']}, {h['behavior']} ({h['how_often']})"
                  for h in p["response_habits"]]
        return prompts.RESIDENT_SYSTEM.format(
            name=p["name"], age=p["age"], job=p["job"], personality=p["personality"],
            others=others, object_habits=lines(p["object_habits"]),
            response_habits=lines(habits), stressors=lines(p["scheduled_stressors"]),
            layout=self.layout.describe())

    def _situations_for(self, rid: str, day: int) -> str:
        out = []
        for sid in self.schedule[day]:
            s = self.situations[sid]
            run, d = 0, day
            while d >= 0 and sid in self.schedule[d]:
                run, d = run + 1, d - 1
            when = "starts today" if run == 1 else f"day {run} of this"
            text = s["what_it_is_like"] if rid in s["happens_to"] else s["what_others_notice"]
            out.append(f"{text} ({when})")
        return lines(out) if out else "- Nothing unusual."

    # ---- one resident's calls ----
    def plan_day(self, rid: str, day: int, weekday: str) -> list[dict]:
        routine = [f"{r['start']}-{r['end']} {r['activity']} ({r['room']})"
                   for r in self.people[rid]["weekly_routine"] if weekday in r["days"]]
        off = director.off_routine_today(rid, day, self.variation, self.seed)
        variation = ("\nToday is not quite a usual day for you: do some things differently "
                     "than usual, in ways that make sense for you.\n") if off else ""
        user = prompts.PLAN_USER.format(
            weekday=weekday, day=day + 1, routine=lines(routine),
            situations=self._situations_for(rid, day), variation=variation,
            yesterday=self.recap[rid])
        plan = self.caller.call(f"plan/{rid}/{day}", self.systems[rid], user,
                                plan_schema(self.rooms), check_plan)
        self._note(rid, day, to_minute(plan["activities"][0]["start"]), "plan", plan)
        acts = []
        for a in plan["activities"]:
            start, end = to_minute(a["start"]), to_minute(a["end"])
            if end <= start:
                end += 24 * 60
            acts.append(dict(a, start_min=start, end_min=end))
        acts.sort(key=lambda a: a["start_min"])
        return acts

    def act(self, rid: str, day: int, weekday: str, activity: dict, minute: int,
            rest: list[dict], events: list[str], problem: str) -> list[dict]:
        person = self.world.people[rid]
        heard = [f"At {t} {who} said to you: {text}" for t, who, text in self.inbox[rid]]
        self.inbox[rid] = []
        user = prompts.ACT_USER.format(
            time=clock(minute), weekday=weekday, day=day + 1,
            activity=activity["activity"], start=activity["start"], end=activity["end"],
            room=activity["room"], intention=activity["intention"],
            rest="; ".join(f"{a['start']} {a['activity']}" for a in rest[:6]) or "nothing",
            situations=self._situations_for(rid, day),
            events="\n".join(events + heard) + ("\n" if events or heard else ""),
            view=self.world.room_view(rid),
            hands=", ".join(person.hands) or "nothing",
            pocket=", ".join(person.pocket) or "nothing",
            memory=self.world.memory_view(rid),
            problem=f"\nThat did not work: {problem}\n" if problem else "")
        habit_ids = [h["id"] for h in self.people[rid]["response_habits"]]
        schema = act_schema(list(self.objects), self.layout.place_ids, self.rids, habit_ids)
        out = self.caller.call(f"act/{rid}/{day}/{minute}", self.systems[rid], user, schema)
        self._note(rid, day, minute, "act", out)
        return out["actions"]

    def _note(self, rid, day, minute, stage, out) -> None:
        self.states.append({"day": day + 1, "time": clock(minute or 0), "resident": rid,
                            "stage": stage, **out["inner_state"],
                            "habit_followed": out.get("habit_followed")})
        self.thoughts.append({"day": day + 1, "time": clock(minute or 0), "resident": rid,
                              "stage": stage, "thinking": out["thinking"]})

    # ---- one day, both residents interleaved in time order ----
    def run_day(self, day: int, start_weekday: int = 0) -> dict:
        world, weekday = self.world, WEEKDAYS[(start_weekday + day) % 7]
        world.day = day + 1
        log_start = len(world.log)
        plans = {r: self.plan_day(r, day, weekday) for r in self.rids}
        pending = {r: list(plans[r]) for r in self.rids}
        now = {r: plans[r][0]["start_min"] for r in self.rids}
        disturbances = {r: director.daily_disturbances(
            self.spec["small_disturbances"], r, day, self.variation, self.seed) for r in self.rids}
        script, current, replans, failed = {r: [] for r in self.rids}, {}, {}, []
        while True:
            live = [r for r in self.rids if script[r] or pending[r]]
            if not live:
                break
            rid = min(live, key=lambda r: now[r])
            world.come_home_if_due(rid, now[rid])
            if world.people[rid].at is None:
                now[rid] = world.people[rid].back_at
                continue
            if not script[rid]:
                activity = pending[rid].pop(0)
                current[rid], replans[rid] = activity, 0
                now[rid] = max(now[rid], activity["start_min"])
                due = [d for d in disturbances[rid] if d[0] < activity["end_min"]]
                disturbances[rid] = [d for d in disturbances[rid] if d not in due]
                events = [f"At {clock(t)}: {text}" for t, text in due]
                script[rid] = self.act(rid, day, weekday, activity, now[rid],
                                       pending[rid], events, "")
                continue
            action = script[rid].pop(0)
            ok, message, minutes = world.apply(rid, action, now[rid])
            if ok and action["verb"] == "say" and action.get("person") in self.inbox:
                self.inbox[action["person"]].append((clock(now[rid]), rid, action.get("text")))
            if not ok:
                failed.append({"day": day + 1, "time": clock(now[rid]), "resident": rid,
                               "action": action, "message": message})
                replans[rid] += 1
                script[rid] = []
                if replans[rid] <= MAX_REPLANS:
                    tried = f"{action['verb']} {action.get('object') or action.get('place') or ''}"
                    script[rid] = self.act(rid, day, weekday, current[rid], now[rid],
                                           pending[rid], [], f"You tried to {tried.strip()}. {message}")
            now[rid] += minutes
        for rid in self.rids:
            last = [s for s in self.states if s["resident"] == rid][-1]
            done = ", ".join(a["activity"] for a in plans[rid])
            self.recap[rid] = (f"You did: {done}. At the end of the day you felt stress "
                               f"{last['stress']}, tiredness {last['tiredness']}, mood "
                               f"{last['mood']}, health {last['health']} ({last['reason']}).")
        return {"plans": plans, "events": world.log[log_start:], "failed": failed,
                "end_of_day": world.snapshot(), "active_situations": self.schedule[day]}


def make_client(model: str, fake: bool, effort: str):
    if fake:
        from lived_home.fake_client import FakeClient
        return FakeClient()
    os.environ["HOSTED_REASONING_EFFORT"] = effort
    from dynamic_home_eqa.generation.llm_client import HostedOpenAIClient
    return HostedOpenAIClient("https://api.openai.com", model)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", default="gpt-5.6-luna")
    ap.add_argument("--effort", default="medium")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--variation", type=float, default=0.2,
                    help="0 to 1: how often a day strays from routine, and how many small disturbances")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--sick", default="2:3",
                    help="first day (0-based) and length of the forced 'sick' situation; 'none' to skip")
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--fake", action="store_true", help="offline scripted residents, for testing")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    caller = Caller(make_client(args.model, args.fake, args.effort),
                    args.out / "cache", args.model, args.effort)
    layout = Layout()
    spec = caller.call("household", prompts.HOUSEHOLD_SYSTEM,
                       prompts.HOUSEHOLD_USER.format(layout=layout.describe()),
                       household_schema(layout.place_ids, list(layout.rooms)),
                       check_household, max_tokens=32000)
    (args.out / "household.json").write_text(json.dumps(spec, indent=1))
    forced = [] if args.sick == "none" else [("sick", *map(int, args.sick.split(":")))]
    home = Household(caller, layout, spec, args.days, args.variation, args.seed, forced)
    (args.out / "schedule.json").write_text(json.dumps(home.schedule, indent=1))
    for day in range(args.days):
        result = home.run_day(day)
        folder = args.out / f"day_{day + 1:02d}"
        folder.mkdir(exist_ok=True)
        for name, value in result.items():
            (folder / f"{name}.json").write_text(json.dumps(value, indent=1))
        (args.out / "inner_states.json").write_text(json.dumps(home.states, indent=1))
        (args.out / "thoughts.json").write_text(json.dumps(home.thoughts, indent=1))
        print(f"day {day + 1}: {len(result['events'])} actions, {len(result['failed'])} failed, "
              f"calls {caller.calls} (cached {caller.cached_hits}), ${caller.cost:.2f}", flush=True)
    (args.out / "usage.json").write_text(json.dumps(
        {"calls": caller.calls, "cached": caller.cached_hits, "check_failures": caller.failures,
         "cost_usd": caller.cost, "model": args.model, "effort": args.effort}, indent=1))


if __name__ == "__main__":
    main()
