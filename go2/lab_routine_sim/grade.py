"""Grade the written memories (notes, hypotheses) against the true rules, with Qwen as grader (thinking on).

    python grade.py [--methods notes,hypotheses,hypotheses_rerun] [--days 5,10,15,20,25,30]

Writes grades/<method>/seed_<k>_day_<d>.json. A grader cannot see the run's scores or the other methods."""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import world as W  # noqa: E402
from llm import ask_json_budget  # noqa: E402
from methods import PROPS, memory_as_text  # noqa: E402

SYSTEM = ("You grade what a robot wrote in its memory about where objects in a lab are kept, against the true rules "
          "that people in the lab followed. Be strict and literal: credit only what the memory actually says.")
LEVELS = ["correct", "partial", "wrong", "absent"]
SCHEMA = {"type": "object", "properties": {p: {"type": "object", "properties": {
    "rule": {"type": "string", "enum": LEVELS},
    "change_noticed": {"type": "string", "enum": ["yes", "no", "not_applicable"]},
    "reason": {"type": "string", "maxLength": 300}}, "required": ["rule", "change_noticed", "reason"]} for p in PROPS},
    "required": PROPS}

ASK = """The robot's memory at the end of lab day {day} ({wd}):
<<<
{memory}
>>>

The true rules on day {day} (people also broke them on about 1 day in 10: moved an object somewhere else, or took it
out of the lab):
{rules}

For each object, grade what the memory currently believes (for a list of hypotheses: the active ones, mainly the
most confident; set-aside ones count only as past beliefs):
- "correct": it states this rule well enough that following it would give the right place on days the rule was
  followed (for a rule with days, both the places and the days; for a rotation, the places and their order; for
  "at random", that it moves among those places without a pattern, naming them).
- "partial": part of the rule (one of the places, or the right kind of pattern with wrong or missing details).
- "wrong": it states a different rule.
- "absent": it says nothing usable about the object.
"change_noticed": for an object whose rule changed on day {change} (marked below), "yes" only if the memory says in
words that the earlier pattern changed or stopped holding (for example "used to be at X, since day 16 at Y"). Merely
naming the new place, without saying it is a change, is "no". For every other object
"not_applicable". Give a one-sentence reason for each."""


def rules_text(world, day):
    lines = []
    for p in PROPS:
        rt = world.rule_text[p]
        if rt["after"] and day >= W.CHANGE_DAY:
            lines.append(f"- {p}: {rt['after']}  [CHANGED on day {W.CHANGE_DAY}; before that: {rt['before']}]")
        else:
            lines.append(f"- {p}: {rt['before']}")
    return "\n".join(lines)


def grade_one(method, seed, day):
    out = HERE / "grades" / method / f"seed_{seed}_day_{day}.json"
    if out.exists():
        return
    run = json.loads((HERE / "runs" / method / f"seed_{seed}.json").read_text())
    if len(run["days"]) < day:
        return
    mem = memory_as_text(method, {"memory": run["days"][day - 1]["memory_after"]}) or "(empty)"
    world = W.make_world(seed)
    prompt = ASK.format(day=day, wd=W.weekday(day), memory=mem, rules=rules_text(world, day), change=W.CHANGE_DAY)
    res, info = ask_json_budget(SYSTEM, prompt, SCHEMA, think_budget=4000, answer_tokens=4000)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"method": method, "seed": seed, "day": day, "grades": res,
                               "info": {k: info.get(k) for k in ("finish", "usage", "seconds", "think_tokens", "thinking_cut")}}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--methods", default="notes,hypotheses,hypotheses_rerun")
    ap.add_argument("--days", default="5,10,15,20,25,30")
    ap.add_argument("--seeds", default="0-9")
    a = ap.parse_args()
    lo, _, hi = a.seeds.partition("-")
    jobs = [(m, s, int(d)) for m in a.methods.split(",") for s in range(int(lo), int(hi or lo) + 1)
            for d in a.days.split(",") if (HERE / "runs" / m / f"seed_{s}.json").exists()]
    with ThreadPoolExecutor(32) as ex:
        list(ex.map(lambda j: grade_one(*j), jobs))
    print(f"graded {len(jobs)} memories")


if __name__ == "__main__":
    main()
