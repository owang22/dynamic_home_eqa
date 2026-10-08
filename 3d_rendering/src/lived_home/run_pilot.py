"""Generate one household and live through N days with roleplaying residents.

    PYTHONPATH=3d_rendering/src python -m lived_home.run_pilot \
        --model gpt-5.6-luna --effort medium --days 7 \
        --out 3d_rendering/results/lived_home/pilot_luna

--create_only stops after household creation. A run can be read while it runs:
calls.jsonl (every model call), responses.jsonl (every plan and activity
answer, with what the engine did with each action) and events.jsonl (every
action that happened, as it happens).
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import pathlib
import random
from concurrent.futures import ThreadPoolExecutor

from lived_home import director, prompts
from lived_home.calls import Caller, to_minute
from lived_home.household import create
from lived_home.layout import Layout
from lived_home.schemas import WEEKDAYS, act_schema_fitting, plan_schema
from lived_home.world import World, clock

MAX_REPLANS = 3     # per activity, after an action fails
MAX_INTERRUPTS = 3  # per activity; further news waits for the next call


def lines(items) -> str:
    return "\n".join(f"- {x}" for x in items) or "- (none)"


class Household:
    def __init__(self, caller: Caller, spec: dict, days: int, variation: float,
                 seed: int, forced: list, out: pathlib.Path) -> None:
        self.caller, self.spec, self.out = caller, spec, out
        self.days, self.variation, self.seed = days, variation, seed
        self.layout = Layout.from_json(spec["layout"])
        self.people = {r["id"]: r for r in spec["residents"]}
        self.rids = list(self.people)
        self.objects = {o["id"]: o for o in spec["objects"]}
        self.types = collections.Counter(o["type"] for o in spec["objects"])
        self.situations = {s["id"]: s for s in spec["situations"]}
        self.schedule = director.schedule_situations(
            spec["situations"], days, seed, [f[:3] for f in forced])
        # a forced situation happens to the residents named, or to one of those it can
        # happen to, chosen with the seed; saved with the schedule as ground truth
        self.subjects = {}
        rng = random.Random(f"{seed}-subjects")
        for f in forced:
            sid = f[0]
            can = next(s["happens_to"] for s in spec["situations"] if s["id"] == sid)
            self.subjects[sid] = [f[3]] if len(f) > 3 else [rng.choice(sorted(can))]
        self.world = World(self.layout, self.objects, self.rids,
                           {r: self.people[r]["sleeps_at"] for r in self.rids},
                           names={r: self.people[r]["name"].split()[0] for r in self.rids})
        self.rooms = list(self.layout.rooms)
        self.systems = {r: self._system(r) for r in self.rids}
        self.act_schemas = {}
        for r in self.rids:
            habit_ids = [h["id"] for h in self.people[r]["response_habits"]]
            self.act_schemas[r], self.enums = act_schema_fitting(
                list(self.objects), self.layout.place_ids, self.rids, habit_ids)
        self.recap = {r: "This is the first day of the simulation." for r in self.rids}
        self.inbox = {r: [] for r in self.rids}
        self.states, self.thoughts = [], []
        self.interrupts = []
        self._flushed = 0

    def _system(self, rid: str) -> str:
        p = self.people[rid]
        others = ", ".join(f"{o['name']} (id {o['id']}, {o['age']}, {o['job']})"
                           for o in self.spec["residents"] if o["id"] != rid)
        habits = [f"{h['id']}: when {h['trigger']}, {h['behavior']} ({h['how_often']})"
                  for h in p["response_habits"]]
        groups = {"Yours": {}, "Shared": {}}
        names = {r: self.people[r]["name"].split()[0] for r in self.rids}
        for o in self.objects.values():
            g = "Yours" if o["owner"] == rid else ("Shared" if not o["owner"] else f"{names.get(o['owner'], o['owner'])}'s")
            groups.setdefault(g, {})
            groups[g][o["type"]] = groups[g].get(o["type"], 0) + 1
        types = "\n".join(f"  {g}: " + ", ".join(f"{t} ({c})" for t, c in sorted(kinds.items()))
                          for g, kinds in groups.items() if kinds)
        return prompts.RESIDENT_SYSTEM.format(
            name=p["name"], age=p["age"], job=p["job"], personality=p["personality"],
            others=others, household=(" " + p["household"]) if p.get("household") else "",
            object_habits=lines(p["object_habits"]),
            response_habits=lines(habits), stressors=lines(p["scheduled_stressors"]),
            types=types, layout=self.layout.describe())

    def _situations_for(self, rid: str, day: int) -> str:
        out = []
        for sid in self.schedule[day]:
            s = self.situations[sid]
            run, d = 0, day
            while d >= 0 and sid in self.schedule[d]:
                run, d = run + 1, d - 1
            when = "starts today" if run == 1 else f"day {run} of this"
            who = self.subjects.get(sid, s["happens_to"])
            text = s["what_it_is_like"] if rid in who else s["what_others_notice"]
            if sid in self.subjects:
                names = " and ".join(self.people[w]["name"] for w in who if w != rid)
                text = (f"This is happening to you{' and ' + names if names else ''}. " if rid in who
                        else f"This is happening to {names}, not to you. ") + text
            out.append(f"{text} ({when})")
        return lines(out) if out else "- Nothing unusual."

    def _log(self, name: str, row: dict) -> None:
        with open(self.out / name, "a") as f:
            f.write(json.dumps(row) + "\n")

    def _flush_events(self) -> None:
        for e in self.world.log[self._flushed:]:
            self._log("events.jsonl", e)
        self._flushed = len(self.world.log)

    # ---- one resident's calls ----
    def plan_day(self, rid: str, day: int, weekday: str):
        routine = [f"{r['start']}-{r['end']} {r['activity']} ({r['room']})"
                   for r in self.people[rid]["weekly_routine"] if weekday in r["days"]]
        off = director.off_routine_today(rid, day, self.variation, self.seed)
        variation = ("\nToday is not quite a usual day for you: do some things differently "
                     "than usual, in ways that make sense for you.\n") if off else ""
        others = []
        for o in self.rids:
            if o == rid:
                continue
            name = self.people[o]["name"].split()[0]
            others += [f"{name}: {r['start']}-{r['end']} {r['activity']} ({r['room']})"
                       for r in self.people[o]["weekly_routine"] if weekday in r["days"]]
        user = prompts.PLAN_USER.format(
            weekday=weekday, day=day + 1, routine=lines(routine), others_routine=lines(others),
            situations=self._situations_for(rid, day), variation=variation,
            yesterday=self.recap[rid])

        def check(plan):
            for a in plan["activities"]:
                if to_minute(a["start"]) is None or to_minute(a["end"]) is None:
                    return f"Times must be HH:MM, got {a['start']} and {a['end']}."
            return ""
        plan = self.caller.call(f"plan/{rid}/{day + 1}", self.systems[rid], user,
                                plan_schema(self.rooms, sorted(self.types)), check)
        acts = []
        wake = to_minute(plan["activities"][0]["start"])
        for a in plan["activities"]:
            start, end = to_minute(a["start"]), to_minute(a["end"])
            if start < wake - 180:          # 00:30 sleep after 23:30 reading: still tonight
                start += 24 * 60
            while end <= start:
                end += 24 * 60
            acts.append(dict(a, start_min=start, end_min=end))
        acts.sort(key=lambda a: a["start_min"])
        return acts, plan, off

    def _record_plan(self, rid, day, acts, plan, off) -> None:
        self._note(rid, day, acts[0]["start_min"], "plan", plan)
        self._log("responses.jsonl", {"day": day + 1, "resident": rid, "stage": "plan",
                                      "off_routine": off, **plan})

    def act(self, rid: str, day: int, weekday: str, activity: dict, minute: int,
            rest: list[dict], events: list[str], problem: str, last: bool,
            done: list = (), interrupted: bool = False, first: bool = False) -> list[dict]:
        heard = [f"At {t} {who} {how}: {text}" if who else f"At {t}: {text}"
                 for t, who, how, text in self.inbox[rid]]
        self.inbox[rid] = []
        hands, pocket, worn = self.world.holding_view(rid)
        user = prompts.ACT_USER.format(
            time=clock(minute), weekday=weekday, day=day + 1,
            activity=activity["activity"], start=activity["start"], end=activity["end"],
            room=activity["room"], intention=activity["intention"],
            rest="; ".join(f"{a['start']} {a['activity']}" for a in rest[:6]) or "nothing",
            situations=self._situations_for(rid, day),
            events="\n".join(events + heard) + ("\n" if events or heard else ""),
            view=self.world.room_view(rid), hands=hands, pocket=pocket, worn=worn,
            memory=self.world.memory_view(rid, set(activity.get("uses") or [])),
            problem=(f"\nSo far in this activity you have: {'; '.join(done) or 'done nothing yet'}.\n"
                     f"Then this did not work: {problem}\n"
                     "Carry on from here; do not repeat what you already did.\n") if problem else
                    (prompts.INTERRUPTED.format(done="; ".join(done) or "nothing yet") if interrupted else ""),
            woke=prompts.WOKE_UP if first and not problem and not interrupted else "",
            bedtime=prompts.BEDTIME if last else "")
        out = self.caller.call(f"act/{rid}/{day + 1}/{clock(minute)}/{len(self.thoughts)}",
                               self.systems[rid], user, self.act_schemas[rid])
        self._note(rid, day, minute, "act", out)
        self._log("responses.jsonl", {"day": day + 1, "time": clock(minute), "resident": rid,
                                      "stage": "act", "activity": activity["activity"],
                                      "problem_given": problem or None,
                                      "interrupted_by": events if interrupted else None, **out})
        return out["actions"]

    @staticmethod
    def _away_minutes(action: dict, activity: dict, pending: list, now: int) -> None:
        """Time away comes from the resident's own plan when the answer leaves it
        out or gives too little: if the current activity is out of the house, or
        an out-of-house stretch starts within the hour, they are away until that
        stretch ends (back from the commute, out again for work would otherwise
        happen). Home activities in between are skipped as missed."""
        block_end = None
        for a in [activity] + pending:
            out = a["room"] == "out_of_house"
            if block_end is None:
                if out and (a is activity or a["start_min"] <= now + 60):
                    block_end = a["end_min"]
                elif a is not activity and a["start_min"] > now + 60:
                    break
                continue
            if not out or a["start_min"] > block_end + 15:
                break
            block_end = max(block_end, a["end_min"])
        given = action.get("minutes") or 0
        if block_end is None:
            if not given:
                action["minutes"], action["minutes_filled"] = 30, "default"
            return
        need = block_end - now
        if need > given:
            action["minutes_as_written"] = given
            action["minutes"], action["minutes_filled"] = need, "from the plan"

    def _note(self, rid, day, minute, stage, out) -> None:
        self.states.append({"day": day + 1, "time": clock(minute or 0), "minute": minute,
                            "resident": rid, "stage": stage, **out["inner_state"],
                            "habit_triggers_now": out.get("habit_triggers_now"),
                            "habit_followed": out.get("habit_followed")})
        self.thoughts.append({"day": day + 1, "time": clock(minute or 0), "minute": minute,
                              "resident": rid, "stage": stage, "thinking": out["thinking"]})

    # ---- one day, both residents interleaved in time order ----
    def run_day(self, day: int, start_weekday: int = 0) -> dict:
        world, weekday = self.world, WEEKDAYS[(start_weekday + day) % 7]
        world.day = day + 1
        for person in world.people.values():
            if person.at is None and person.back_at >= 24 * 60:
                person.back_at -= 24 * 60        # out past midnight: today's clock
        log_start = len(world.log)
        with ThreadPoolExecutor(len(self.rids)) as pool:
            got = list(pool.map(lambda r: self.plan_day(r, day, weekday), self.rids))
        plans = {}
        for rid, (acts, plan, off) in zip(self.rids, got):   # recorded in a fixed order
            self._record_plan(rid, day, acts, plan, off)
            plans[rid] = acts
        pending = {r: list(plans[r]) for r in self.rids}
        now = {r: plans[r][0]["start_min"] for r in self.rids}
        disturbances = {r: director.daily_disturbances(
            self.spec["small_disturbances"], r, day, self.variation, self.seed) for r in self.rids}
        script, current, replans, done = {r: [] for r in self.rids}, {}, {}, {}
        failed, skipped, dropped_after_leaving, ran = [], [], [], {r: [] for r in self.rids}
        news = {r: [] for r in self.rids}          # (minute, text) waiting to interrupt
        n_int = {r: 0 for r in self.rids}
        last_do = {r: None for r in self.rids}    # (log index, start, end) of a do in progress

        def asleep(o, t):
            return (t < plans[o][0]["start_min"]
                    or (not pending[o] and o in current and "sleep" in current[o]["activity"].lower()
                        and t >= current[o]["start_min"]))

        def tell(o, t, text, capped=True):
            """Something reaches o at minute t: it interrupts what they are doing if
            they are awake, at home and in an activity; otherwise it waits."""
            if asleep(o, t):
                return
            if world.people[o].at is None or o not in current or (capped and n_int[o] >= MAX_INTERRUPTS):
                self.inbox[o].append((clock(t), None, None, text))
                return
            news[o].append((t, text))
            ld = last_do[o]
            if ld and ld[1] < t < ld[2] and now[o] == ld[2]:   # cut a long do short
                now[o] = t
                world.log.append({"day": world.day, "minute": t, "time": clock(t), "resident": o,
                                  "verb": "interrupted", "object": None, "from": None, "to": None,
                                  "minutes": t - ld[1], "text": text, "why": "(stopped what they were doing)"})
                last_do[o] = None
            now[o] = max(now[o], t) if now[o] < t else now[o]

        while True:
            live = [r for r in self.rids if script[r] or pending[r]]
            if not live:
                break
            rid = min(live, key=lambda r: now[r])
            world.come_home_if_due(rid, now[rid])
            if world.people[rid].at is None:
                now[rid] = world.people[rid].back_at
                continue
            free_until = pending[rid][0]["start_min"] if pending[rid] else 10 ** 6
            if news[rid] and rid in current and (script[rid] or now[rid] < free_until):
                texts = [f"At {clock(t)}: {x}" for t, x in news[rid]]
                news[rid] = []
                n_int[rid] += 1
                heard = [f"At {t} {who} {how}: {text}" if who else f"At {t}: {text}"
                         for t, who, how, text in self.inbox[rid]]
                self.inbox[rid] = []
                self.interrupts.append({"day": day + 1, "time": clock(now[rid]), "resident": rid,
                                        "news": texts})
                script[rid] = self.act(rid, day, weekday, current[rid], now[rid], pending[rid],
                                       heard + texts, "", not pending[rid], done[rid], interrupted=True)
                continue
            if not script[rid] and rid in current:
                # idle until the next activity: a disturbance in that gap still happens on time
                gap = next((d for d in disturbances[rid] if now[rid] <= d[0] < free_until), None)
                if gap is not None:
                    disturbances[rid].remove(gap)
                    now[rid] = gap[0]
                    tell(rid, now[rid], gap[1], capped=False)
                    continue
            if not script[rid]:
                # news that came between activities is told at the next call
                self.inbox[rid] += [(clock(t), None, None, x) for t, x in news[rid]]
                news[rid] = []
                activity = pending[rid].pop(0)
                if activity["end_min"] <= now[rid] and pending[rid]:
                    skipped.append({"resident": rid, "activity": activity["activity"],
                                    "planned": f"{activity['start']}-{activity['end']}",
                                    "now": clock(now[rid]),
                                    "while_out": activity["room"] == "out_of_house"})
                    continue
                current[rid], replans[rid], done[rid], n_int[rid] = activity, 0, [], 0
                ran[rid].append(activity["activity"])
                now[rid] = max(now[rid], activity["start_min"])
                # disturbances already past (while out or asleep) are told now; later ones
                # wait for their own time
                due = [d for d in disturbances[rid] if d[0] <= now[rid]]
                disturbances[rid] = [d for d in disturbances[rid] if d not in due]
                events = [f"At {clock(t)}: {text}" for t, text in due]
                script[rid] = self.act(rid, day, weekday, activity, now[rid],
                                       pending[rid], events, "", not pending[rid],
                                       first=len(ran[rid]) == 1)
                continue
            # a disturbance whose time has come interrupts; a do that spans one stops there
            action = script[rid][0]
            nxt = next((d for d in disturbances[rid] if d[0] <= now[rid]), None)
            if nxt is None and action.get("verb") == "do":
                span = now[rid] + max(1, action.get("minutes") or 1)
                nxt = next((d for d in disturbances[rid] if d[0] < span), None)
                if nxt is not None and nxt[0] > now[rid]:
                    action = dict(action, minutes=nxt[0] - now[rid], cut_short=True)
                    script[rid][0] = action
                elif nxt is not None:
                    nxt = None
            if nxt is not None and nxt[0] <= now[rid]:
                disturbances[rid].remove(nxt)
                tell(rid, now[rid], nxt[1], capped=False)    # a disturbance always gets through
                continue
            script[rid].pop(0)
            if action.get("verb") == "leave_home":
                self._away_minutes(action, current[rid], pending[rid], now[rid])
            ok, message, minutes = world.apply(rid, action, now[rid])
            if ok:
                done[rid].append(_short(action))
                if action.get("verb") == "leave_home" and script[rid]:
                    dropped_after_leaving.append({"resident": rid, "time": clock(now[rid]),
                                                  "actions": [_short(a) for a in script[rid]]})
                    script[rid] = []
                last_do[rid] = ((len(world.log) - 1, now[rid], now[rid] + minutes)
                                if action.get("verb") == "do" else None)
            if ok and action["verb"] in ("say", "give") and action.get("person") in self.people \
                    and action["person"] != rid:
                o = action["person"]
                other = world.people[o]
                name = self.people[rid]["name"].split()[0]
                if action["verb"] == "give":
                    text = f"{name} handed you {action.get('object')}."
                elif other.at is None:
                    text = f"{name} texted you: {action.get('text')}"
                elif world.room_of_person(rid) == world.room_of_person(o):
                    text = f"{name} said to you: {action.get('text')}"
                else:
                    text = f"{name} called out to you from another room: {action.get('text')}"
                tell(o, now[rid], text)
            if not ok:
                failed.append({"day": day + 1, "time": clock(now[rid]), "resident": rid,
                               "activity": current[rid]["activity"], "action": action,
                               "message": message})
                self._log("failed.jsonl", failed[-1])
                replans[rid] += 1
                script[rid] = []
                if replans[rid] <= MAX_REPLANS:
                    tried = f"{action['verb']} {action.get('object') or action.get('place') or ''}"
                    script[rid] = self.act(rid, day, weekday, current[rid], now[rid],
                                           pending[rid], [], f"You tried to {tried.strip()}. {message}",
                                           not pending[rid], done[rid])
            now[rid] += minutes
            self._flush_events()
        self._flush_events()
        night = {r: {"hands": list(world.people[r].hands), "at": world.people[r].at}
                 for r in self.rids}
        world.end_of_day()
        for rid in self.rids:
            last = [s for s in self.states if s["resident"] == rid][-1]
            done = ", ".join(ran[rid]) or "nothing you had planned"
            self.recap[rid] = (f"You did: {done}. At the end of the day you felt stress "
                               f"{last['stress']}, tiredness {last['tiredness']}, mood "
                               f"{last['mood']}, health {last['health']} ({last['reason']}).")
        return {"plans": plans, "events": world.log[log_start:], "failed": failed,
                "positions": world.positions(self.spec.get("scene")),
                "skipped_activities": skipped, "dropped_after_leaving": dropped_after_leaving,
                "at_night": night,
                "end_of_day": world.snapshot(), "active_situations": self.schedule[day]}


def _short(a: dict) -> str:
    bits = [a.get("verb", "")]
    for k in ("object", "place", "person"):
        if a.get(k):
            bits.append(a[k])
    if a.get("verb") in ("do", "say") and a.get("text"):
        bits.append(f'"{a["text"][:60]}"')
    return " ".join(bits)


def _save_checkpoint(home: "Household", out: pathlib.Path, day: int) -> None:
    """Everything the next day needs (world, memories, inbox, recaps), without the
    model client."""
    import pickle
    caller, home.caller = home.caller, None
    try:
        (out / "checkpoints").mkdir(exist_ok=True)
        (out / "checkpoints" / f"day_{day:02d}.pkl").write_bytes(pickle.dumps(home))
    finally:
        home.caller = caller


def _load_checkpoint(out: pathlib.Path, day: int, caller) -> "Household":
    import pickle
    home = pickle.loads((out / "checkpoints" / f"day_{day:02d}.pkl").read_bytes())
    home.caller = caller
    # the saved state carries the prompts and schemas of the code that wrote it; a
    # resume runs the current code, so rebuild them
    home.systems = {r: home._system(r) for r in home.rids}
    for r in home.rids:
        habit_ids = [h["id"] for h in home.people[r]["response_habits"]]
        home.act_schemas[r], home.enums = act_schema_fitting(
            list(home.objects), home.layout.place_ids, home.rids, habit_ids)
    (out / "resumes.json").open("a").write(json.dumps({"after_day": day, "commit": _commit()}) + "\n")
    return home


def _commit() -> str:
    import subprocess
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                              text=True, cwd=pathlib.Path(__file__).parent).stdout.strip()
    except OSError:
        return "unknown"


def _cut_logs(out: pathlib.Path, day: int) -> None:
    """Drop log rows from days after the resume point (a resumed run rewrites them)."""
    for name in ("events.jsonl", "responses.jsonl", "failed.jsonl"):
        p = out / name
        if p.exists():
            keep = [l for l in p.read_text().splitlines() if l.strip() and json.loads(l).get("day", 0) <= day]
            p.write_text("".join(k + "\n" for k in keep))
    for d in out.glob("day_*"):
        if d.is_dir() and int(d.name.split("_")[1]) > day:
            for f in d.iterdir():
                f.unlink()
            d.rmdir()


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
                    help="first day (0-based):length[:resident] of the forced 'sick' situation; 'none' to skip")
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--household", type=pathlib.Path,
                    help="reuse this household.json instead of creating one")
    ap.add_argument("--pilot_layout", action="store_true",
                    help="(fake runs) use the hand-written layout instead of generating one")
    ap.add_argument("--scene", default=None,
                    help="build the home from this HSSD scene id (lived_home.hssd_layout)")
    ap.add_argument("--create_only", action="store_true")
    ap.add_argument("--resume", type=int, default=0,
                    help="continue from the saved state at the end of this day (1-based); "
                         "logs after that day are cut back first")
    ap.add_argument("--fake", action="store_true", help="offline scripted residents, for testing")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    caller = Caller(make_client(args.model, args.fake, args.effort), args.out / "cache",
                    args.model, args.effort, log_path=args.out / "calls.jsonl")
    if args.household:
        spec = json.loads(args.household.read_text())
        (args.out / "household.json").write_text(json.dumps(spec, indent=1))
    else:
        spec = create(caller, args.seed, args.out, scene=args.scene)
    print(f"household: {len(spec['layout']['places'])} places, {len(spec['objects'])} objects, "
          f"calls {caller.calls}, ${caller.cost:.2f}", flush=True)
    if args.create_only:
        return
    forced = []
    if args.sick != "none":
        parts = args.sick.split(":")
        forced = [("sick", int(parts[0]), int(parts[1]), *parts[2:3])]
    home = Household(caller, spec, args.days, args.variation, args.seed, forced, args.out)
    first_day = 0
    if args.resume:
        first_day = args.resume
        home = _load_checkpoint(args.out, args.resume, caller)
        _cut_logs(args.out, args.resume)
        print(f"resumed after day {args.resume}", flush=True)
    (args.out / "schedule.json").write_text(json.dumps(home.schedule, indent=1))
    (args.out / "code_version.txt").write_text(_commit() + "\n")
    (args.out / "subjects.json").write_text(json.dumps(home.subjects, indent=1))
    print(f"forced situations happen to: {home.subjects}", flush=True)
    print(f"act schema uses enums: {home.enums}", flush=True)
    for day in range(first_day, args.days):
        result = home.run_day(day)
        folder = args.out / f"day_{day + 1:02d}"
        folder.mkdir(exist_ok=True)
        for name, value in result.items():
            (folder / f"{name}.json").write_text(json.dumps(value, indent=1))
        _save_checkpoint(home, args.out, day + 1)
        (args.out / "inner_states.json").write_text(json.dumps(home.states, indent=1))
        (args.out / "interrupts.json").write_text(json.dumps(home.interrupts, indent=1))
        (args.out / "thoughts.json").write_text(json.dumps(home.thoughts, indent=1))
        print(f"day {day + 1}: {len(result['events'])} actions, {len(result['failed'])} failed, "
              f"calls {caller.calls} (cached {caller.cached_hits}), ${caller.cost:.2f}", flush=True)
        (args.out / "usage.json").write_text(json.dumps(
            {"calls": caller.calls, "cached": caller.cached_hits, "check_failures": caller.failures,
             "check_problems": caller.problems, "cost_usd": caller.cost, "model": args.model,
             "effort": args.effort, "days_done": day + 1}, indent=1))


if __name__ == "__main__":
    main()
