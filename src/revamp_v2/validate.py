#!/usr/bin/env python3
"""The four revamp_v2 build-time checks, deterministic and ordered:

  1. schema       — the raw LLM program against its guided-JSON schema
                    (guided decoding should guarantee this; re-checked
                    anyway with jsonschema).
  2. referential  — every id exists; placements match the persona
                    inventory exactly; block/binding cross-references.
  3. reachability — the v1 simulator's own lint, run on the expanded
                    program (every non-static object reaches >= 2
                    receptacles, statics appear in no rule), plus the
                    fragmentation `only_from` requirement, plus at-home
                    coverage (an at-home, non-sleep weekly block whose
                    activity no object rule or reset_all names fails,
                    named in the reason).
  4. leak audit   — strip `cites`, show only object ids + receptacle ids
                    to the generation LLM under a fixed classification
                    prompt; a correct household-type guess (chance 1/10)
                    rejects the program. The prediction is logged either
                    way.

Any other correctness concern is a pytest assertion or is not written —
the realism panel (reporting-only) is the only other named check.

CLI (checks 1-3; --leak adds 4, which needs GENERATION_ENDPOINT):
  python src/revamp_v2/validate.py profiles/revamp_v2/<slug>/hh1 [--leak]
"""
from __future__ import annotations

import argparse
import copy
import pathlib
import sys

import jsonschema
import yaml

HERE = pathlib.Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import expand_calendar as xc   # noqa: E402
import prompts                 # noqa: E402
import schemas                 # noqa: E402
import simulate as sim         # noqa: E402

# Keys generate.py injects into the program AFTER the LLM call (they are
# deterministic pipeline data, not model output, so the model never has to
# echo them and the schema never has to admit them).
INJECTED_KEYS = ("receptacles", "household_type", "object_semantics",
                 "arc_events")   # arc_events: authored by the SECOND call
                                 # (special events), never by the program
                                 # response the schema check replays

# Fake-movement (inert) objects tolerated per program before rejection.
# Authored statics (`rules: []`) are never counted against this — the gate
# exists to make rejection-and-resample filter a generator habit, not to
# forbid still objects.
MAX_INERT_FRACTION = 0.25
MIN_ALLOWED_INERT = 2


def strip_injected(program: dict) -> dict:
    return {k: v for k, v in program.items() if k not in INJECTED_KEYS}


def check_schema(raw_program: dict, schema: dict) -> list[str]:
    validator = jsonschema.Draft202012Validator(schema)
    return [
        "schema: " + ("/".join(str(p) for p in e.absolute_path) or "<root>")
        + f": {e.message[:200]}"
        for e in validator.iter_errors(raw_program)]


def check_referential(program: dict, persona: dict) -> list[str]:
    problems: list[str] = []
    inventory = [o["id"] for o in persona["object_inventory"]]
    entries = xc.placements_of(program)
    placed = [p["object"] for p in entries]
    if sorted(placed) != sorted(set(placed)):
        dupes = sorted({o for o in placed if placed.count(o) > 1})
        problems.append(
            f"referential: object_rules names {dupes} more than once (and "
            f"so must be missing another object — the array carries exactly "
            f"one entry per inventory item)")
    if set(placed) != set(inventory):
        missing = sorted(set(inventory) - set(placed))
        extra = sorted(set(placed) - set(inventory))
        problems.append(
            f"referential: placements != persona inventory "
            f"(missing {missing}, extra {extra})")
    persona_residents = [r["id"] for r in persona["residents"]]
    program_residents = [r["id"] for r in program["residents"]]
    if sorted(program_residents) != sorted(persona_residents):
        problems.append(
            f"referential: residents {program_residents} != persona "
            f"residents {persona_residents}")

    blocks = [dict(s, sleep=True, skip_p=0.0)
              for s in program.get("sleep_schedule") or []]
    blocks += program["weekly_blocks"]
    for arc in program.get("arc_events") or []:
        blocks += (arc.get("patch") or {}).get("add") or []
    used = {b["activity"] for b in blocks}
    for b in blocks:
        if b["activity"].startswith(xc.LINGER_PREFIX):
            problems.append(f"referential: activity name "
                            f"{b['activity']!r} uses the reserved "
                            f"'{xc.LINGER_PREFIX}' prefix")
    for arc in program.get("arc_events") or []:
        for ov in (arc.get("patch") or {}).get("after_override") or []:
            if ov["activity"] not in used:
                problems.append(
                    f"referential: arc day {arc['day']} overrides unknown "
                    f"activity {ov['activity']!r}")

    for b in program["weekly_blocks"]:
        if len(set(b["days"])) != len(b["days"]):
            problems.append(
                f"referential: block {b['activity']!r} repeats weekdays "
                f"{b['days']} (the schema cannot express uniqueItems)")

    # Sleep is the one block nobody skips, and nobody tidies while asleep.
    # Both belong to referential integrity rather than a new named check:
    # they are the program contradicting what it says about itself. Sleep
    # is taken from the block's declared `sleep` flag (and from the naming
    # convention too, so a block that says "nap" in its name but forgets
    # the flag is still caught).
    sleep_names = {b["activity"] for b in blocks
                   if b.get("sleep")
                   or any(s in b["activity"] for s in xc.SLEEP_TOKENS)}
    # Only a resident's PRIMARY (longest) sleep is non-negotiable: a nap,
    # a bedtime wind-down, a second doze are all things people skip.
    primary: dict[str, tuple[float, str]] = {}
    for b in blocks:
        if b["activity"] not in sleep_names or not b.get("end"):
            continue
        span = ((xc._minutes(b["end"]) - xc._minutes(b["start"])) % 1440)
        if span > primary.get(b["resident"], (0, ""))[0]:
            primary[b["resident"]] = (span, b["activity"])
    # ...and only if it is long enough to BE a night's sleep. When the
    # author flags the nap but not the overnight block, the longest
    # sleep-flagged block for that resident can be a one-hour doze, which
    # is precisely the kind of rest people skip.
    MIN_PRIMARY_SLEEP_MIN = 4 * 60
    unskippable = {a for span, a in primary.values()
                   if span >= MIN_PRIMARY_SLEEP_MIN}
    for b in blocks:
        if b["activity"] in unskippable and (b.get("skip_p") or 0) > 0:
            problems.append(
                f"referential: sleep block {b['activity']!r} has skip_p "
                f"{b['skip_p']} — a resident does not skip sleeping")

    sleepless = [r for r in persona_residents
                 if not any(b["resident"] == r and b["activity"] in sleep_names
                            for b in blocks)]
    if sleepless:
        problems.append(f"referential: residents with no sleep/nap block: "
                        f"{sleepless}")

    rules_by_obj = {e["object"]: e.get("rules") or []
                    for e in program.get("object_rules") or []}
    if set(rules_by_obj) != set(placed):
        problems.append(
            f"referential: object_rules covers {sorted(set(rules_by_obj))} "
            f"but placements cover {sorted(set(placed))}")
    for obj, rules in rules_by_obj.items():
        for r in rules:
            if r.get("dist"):
                total = sum(d["p"] for d in r["dist"])
                if abs(total - 1.0) > 1e-6:
                    problems.append(
                        f"referential: {obj}'s dist on {r['activity']} sums "
                        f"to {total}")
                # A dist that is entirely NO_OP is a rule that never does
                # anything — the expander drops it; naming it here keeps
                # the author honest rather than silently thinning rules.
                real = [d for d in r["dist"] if d["dest"] != "NO_OP"]
                if not real:
                    problems.append(
                        f"referential: {obj}'s dist on {r['activity']} is "
                        f"pure NO_OP — a rule that never moves anything")
            elif r.get("dest") is None:
                problems.append(
                    f"referential: {obj}'s rule on {r['activity']} has "
                    f"neither dest nor dist")
    for p in entries:
        static = not rules_by_obj.get(p["object"])
        if static and (p.get("p_misplace") or 0) > 0:
            problems.append(
                f"referential: {p['object']} is planned as never moving "
                f"yet declares p_misplace")
    return problems


def program_home(program: dict, obj: str) -> str:
    return next(p["home"] for p in xc.placements_of(program)
                if p["object"] == obj)


def check_reachability(program: dict) -> list[str]:
    """Expansion + the ported v1 lint; every failure is one message.

    Broadened (still the same named check — reachability is about rules
    reaching the life the blocks describe, in both directions): an at-home,
    non-sleep weekly block whose activity has zero bindings across all
    object_rules AND no reset_all fails, with the activity named. Rule
    sets that cluster on commute transitions leave at-home days with 1-3
    events where a real home-all-day resident produces ~49; an at-home
    block that touches no object is that gap, one activity at a time.
    Sleep blocks are exempt by name/flag (their stillness is real);
    linger names are reserved and already rejected by referential; a
    reset_all counts as a binding because a tidy walk moves objects —
    that is the hh1 fixture's own pattern for its tidying blocks."""
    try:
        acts, motions = xc.expand(program)
    except (ValueError, KeyError) as e:
        return [f"reachability: expansion failed: {e}"]
    try:
        sim.load_v1().validate(acts, motions)
    except AssertionError as e:
        return [f"reachability: {e}"]
    problems = []
    # Stillness comes in two kinds, and only one is a defect. An object
    # the model declares still (`rules: []`) is a welcome part of a
    # household — a charger on its dock, grandma's clock — reported,
    # never gated. An INERT object wrote movement rules whose every
    # destination is its own home: fake movement, normalized to a static
    # by the expander and counted in `inert_objects`. A few of those are
    # model slip-ups; when they are rampant the program is describing a
    # frozen house by accident, and only rejection-and-resample filters
    # that (measured: with no gate, first-attempt programs shipped with
    # 27/36 and 35/40 objects inert — every one fake movement, zero
    # authored statics; the schema cannot forbid it because dest != home
    # is a cross-field inequality xgrammar cannot express).
    inert = acts.get("inert_objects", [])
    n_objects = len(xc.placements_of(program))
    allowed = max(MIN_ALLOWED_INERT, MAX_INERT_FRACTION * n_objects)
    if len(inert) > allowed:
        problems.append(
            f"reachability: {len(inert)} of {n_objects} objects wrote "
            f"movement rules that only ever name their own home "
            f"({inert[:6]}{'...' if len(inert) > 6 else ''}) — fake "
            f"movement, not declared stillness; use `rules: []` for an "
            f"object that genuinely stays put")
    # At-home coverage (see docstring): weekly_blocks only — sleep_schedule
    # is exempt wholesale and arc `add` blocks are one-offs, not the
    # routine the rules are supposed to serve.
    bound = {r["activity"] for e in program.get("object_rules") or []
             for r in e.get("rules") or []}
    bound |= {a["name"] for a in program.get("activities") or []
              if a.get("reset_all")}
    uncovered = sorted({
        b["activity"] for b in program["weekly_blocks"]
        if b["at"] != xc.ELSEWHERE
        and not b.get("sleep")
        and not any(s in b["activity"] for s in xc.SLEEP_TOKENS)
        and b["activity"] not in bound})
    for name in uncovered:
        problems.append(
            f"reachability: at-home activity {name!r} is scheduled by "
            f"weekly_blocks but appears in no object rule (and carries no "
            f"reset_all) — a home block that touches nothing; objects move "
            f"because of what people do at home, not only because they "
            f"leave")
    # Fragmented activities' after-rules still need an `only_from` gate,
    # but it is DERIVED by the expander when absent (see its comment), so
    # by the time the expansion above succeeded every such rule has one.
    for name, act in motions["object_motions"].items():
        if "fragment" in act:
            ungated = [obj for obj, rule in act.get("after", {}).items()
                       if "only_from" not in rule]
            assert not ungated, (
                f"expander failed to gate {name}.{ungated} — a fragmented "
                f"after-rule without only_from re-fires every bout")
    return problems


def check_leak(program: dict, household_types: list[str], client, cache,
               seed: int, model_stage: str,
               force: bool = False) -> tuple[list[str], dict]:
    """(problems, prediction_record). Needs an LLM client; cites are never
    shown — only bare id lists."""
    from dynamic_home_eqa.generation.llm_client import generate_json
    object_ids = [p["object"] for p in xc.placements_of(program)]
    receptacle_ids = [r["id"] for r in program["receptacles"]]
    result = generate_json(
        client, prompts.LEAK_AUDIT.text,
        prompts.leak_user_prompt(object_ids, receptacle_ids,
                                 household_types),
        schemas.build_leak_schema(household_types),
        seed=seed, stage=model_stage, cache=cache, force=force,
        temperature=0.0)
    record = {"predicted_type": result["predicted_type"],
              "confidence": result.get("confidence"),
              "reason": result.get("reason"),
              "actual_type": program["household_type"],
              "correct": result["predicted_type"] == program["household_type"]}
    problems = []
    if record["correct"]:
        problems.append(
            f"leak: object/receptacle vocabulary gives the household type "
            f"away ({record['predicted_type']}, "
            f"confidence {record['confidence']})")
    return problems, record


def static_checks(raw_program: dict, program: dict, persona: dict,
                  schema: dict) -> list[str]:
    """Checks 1-3 in order; a failure at one level does not hide the next."""
    problems = check_schema(raw_program, schema)
    problems += check_referential(program, persona)
    problems += check_reachability(program)
    return problems


def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("household", type=pathlib.Path)
    ap.add_argument("--leak", action="store_true",
                    help="also run the leak audit (needs GENERATION_ENDPOINT)")
    args = ap.parse_args()
    hh_dir = args.household
    persona = yaml.safe_load((hh_dir / "persona.yaml").read_text())
    program = yaml.safe_load((hh_dir / "routine_program.yaml").read_text())
    params = sim.load_params()
    inventory = persona["object_inventory"]
    schema = schemas.build_program_schema(
        program["household"],
        [r["id"] for r in program["residents"]],
        [p["object"] for p in xc.placements_of(program)],
        [r["id"] for r in program["receptacles"]],
        int(program["days"]), params)
    problems = static_checks(strip_injected(copy.deepcopy(program)),
                             program, persona, schema)
    if args.leak:
        import os
        from dynamic_home_eqa.generation import llm_client
        control = yaml.safe_load(
            (sim.PROFILES_DIR / "control.yaml").read_text())
        types = [h["household_type"] for h in control["households"]]
        model = os.environ.get("GENERATION_MODEL", llm_client.DEFAULT_MODEL)
        from dynamic_home_eqa.generation.cache import ResponseCache, make_seed
        cache = ResponseCache(
            f"/tmp/dynamic-home-eqa-gen-cache-revamp-v2-"
            f"{llm_client.model_slug(model)}")
        tag = prompts.LEAK_AUDIT.tag(
            "leak_audit", builder=True,
            schema=schemas.build_leak_schema(types))
        leak_problems, record = check_leak(
            program, types, llm_client._get_client(model), cache,
            make_seed(program["household"], 0, tag, 0), tag)
        print(f"leak prediction: {record}")
        problems += leak_problems
    for p in problems:
        print(f"PROBLEM: {p}", file=sys.stderr)
    print(f"{hh_dir}: {len(problems)} problem(s)")
    raise SystemExit(1 if problems else 0)


if __name__ == "__main__":
    _main()
