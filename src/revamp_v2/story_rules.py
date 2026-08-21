"""story_rules: the fourth cell of the 2x2 — a STORY calendar realized by
the RULES engine.

|                        | movement: rules | movement: freeform |
|------------------------|-----------------|--------------------|
| calendar: weekly       | rule_based/     | freeform/          |
| calendar: story        | story_rules/    | story_driven/      |

The story stage is story_driven.py's, verbatim (same prompt, schema,
seeding, cache — the two story arms share one calendar per household).
The movement engine is simulate.py's, verbatim: the story's blocks become
the dated calendar the v1 simulator consumes, and the rule_based
household's own object_rules fire against it. Nothing new is authored —
personas, starting homes and object_rules come from the corresponding
rule_based household, so this arm differs from each neighbour on exactly
one axis.

The binding is a JOIN, not a translation: story activity names come from
the same closed ACTIVITY_VOCAB the rules reference, so most bind
directly. A story activity no rule names realizes with no bindings —
informative, counted as `unbound_story_activities`, never an error. A
rule whose activity the story never schedules is `orphaned_rules_story`
(the expander's own orphan accounting). Both land in meta.json.

Mechanically, the story is expressed as a synthetic program whose weekly
sections are empty and whose every block is an arc-event `add` on its
day. expand_calendar.expand() then does everything it already does for
template blocks — per-location activity splitting (the
`activity__receptacle` variants, so `at`/`jitter` keying stays valid),
linger synthesis for authored ends, carry-on-departure, and
pivot_object_rules — so the story arm and the rule_based arm share one
realization path rather than a re-implementation of it. Skips and
fragmentation apply to story blocks exactly as to template blocks
(skip_p/jitter joined per activity from the rule_based program's own
blocks), composing with the day-level variation the story itself wrote.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import sys

import yaml

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT / "src"))

import expand_calendar as xc                                  # noqa: E402
import simulate as sim                                        # noqa: E402
import story_driven as sd                                     # noqa: E402

from dynamic_home_eqa.generation import llm_client            # noqa: E402
from dynamic_home_eqa.generation.cache import ResponseCache   # noqa: E402

BUILDER_VERSION = "story-rules-b2"   # b1 -> b2: optional story-aware
                                     # binding pass (--bind-unbound)

try:
    import jsonschema as _jsonschema
except ImportError:                                   # pragma: no cover
    _jsonschema = None

# ---------------------------------------------------------------- bind --
# The story ranges over the closed 50-name vocabulary; the rule_based
# program only ever bound the ~8 activities its weekly template scheduled,
# so 60-84% of story blocks moved nothing (measured across both models).
# This pass authors rules for the story's UNBOUND at-home activities in
# ONE guided-JSON call per household — grammar-enforced enums (activity =
# the story's own names, object = the inventory, dest = real places), the
# only constraint mechanism this generator reliably obeys. Away activities
# are excluded (departure-carry already covers them; authored ELSEWHERE
# rules are the hh5 churn pattern), as are sleep blocks.

import prompts as _prompts                                    # noqa: E402


def build_binding_schema(object_ids, activities, receptacles, residents):
    dests = receptacles + [f"person:{r}" for r in residents]
    # The SAME rule grammar the routine program uses (after-only dist
    # with NO_OP) — one contract, not a dialect per stage.
    rule = {
        "type": "object", "additionalProperties": False,
        "required": ["cites", "activity", "phase", "dist"],
        "properties": {
            "cites": {"type": "string", "maxLength": 90},
            "activity": {"enum": activities},
            "phase": {"const": "after"},
            "only_from": {"type": "array", "minItems": 1, "maxItems": 6,
                          "items": {"enum": dests}},
            "dist": {"type": "array", "minItems": 2, "maxItems": 6,
                     "items": {"type": "object",
                               "additionalProperties": False,
                               "required": ["dest", "p"],
                               "properties": {
                                   "dest": {"enum": dests + ["NO_OP"]},
                                   "p": {"type": "number", "minimum": 0.0,
                                         "maximum": 1.0}}}},
        },
    }
    # One entry per object, in inventory order — the fixed-length
    # prefixItems shape that made omission unwritable for object_rules.
    entries = [{"type": "object", "additionalProperties": False,
                "required": ["object", "rules"],
                "properties": {"object": {"enum": [oid]},
                               "rules": {"type": "array", "maxItems": 4,
                                         "items": rule}}}
               for oid in object_ids]
    return {"type": "object", "additionalProperties": False,
            "required": ["bindings"],
            "properties": {"bindings": {
                "type": "array", "minItems": len(object_ids),
                "maxItems": len(object_ids), "prefixItems": entries,
                "items": False}}}


class _LongForm:
    """Raise max_tokens where the backend supports it (generate.py's
    pattern; the binding answer for a 40-object household overruns the
    client's 4096 default)."""

    def __init__(self, inner, max_tokens: int) -> None:
        self.inner = inner
        self.max_tokens = max_tokens

    def generate(self, system, user, schema, seed=None, temperature=0.7):
        try:
            return self.inner.generate(system, user, schema, seed=seed,
                                       temperature=temperature,
                                       max_tokens=self.max_tokens)
        except TypeError:
            return self.inner.generate(system, user, schema, seed=seed,
                                       temperature=temperature)


def bind_unbound(program, story, persona_text, client, cache, force):
    """(merged_program, bind_stats). One guided-JSON call authoring rules
    for the story's unbound at-home activities; merged into a deep copy of
    the program (the source rule_based program is never mutated)."""
    import copy
    from dynamic_home_eqa.generation.cache import make_seed
    from dynamic_home_eqa.generation.llm_client import generate_json

    bound = {r["activity"] for e in program.get("object_rules") or []
             for r in e.get("rules") or []}
    bound |= {a["name"] for a in program.get("activities") or []
              if a.get("reset_all")}
    at_of: dict = {}
    away = set()
    for d in story:
        for b in d["blocks"]:
            if b["at"] == "ELSEWHERE":
                away.add(b["activity"])
            else:
                at_of.setdefault(b["activity"], b["at"])
    unbound = sorted(a for a in at_of
                     if a not in bound and a not in away
                     and not any(s in a for s in xc.SLEEP_TOKENS))
    if not unbound:
        return program, {"n_unbound_targeted": 0, "n_rules_added": 0}

    object_ids = [e["object"] for e in program["object_rules"]]
    receptacles = [r["id"] for r in program["receptacles"]]
    residents = [r["id"] for r in program["residents"]]
    schema = build_binding_schema(object_ids, unbound, receptacles,
                                  residents)
    obj_lines = []
    for e in program["object_rules"]:
        have = ", ".join(sorted({r["activity"] for r in
                                 (e.get("rules") or [])})) or "none"
        obj_lines.append(f"  {e['object']} (home: {e['home']}; "
                         f"already bound to: {have})")
    user = _prompts.BINDING_USER.format(
        persona=persona_text,
        activities="\n".join(f"  {a} @ {at_of[a]}" for a in unbound),
        objects="\n".join(obj_lines),
        places="\n".join(f"  {r}" for r in receptacles))
    tag = _prompts.BINDING.tag("story_bind", schema=schema) + "_u" + \
        hashlib.sha256(_prompts.BINDING_USER.encode()).hexdigest()[:8]
    seed = make_seed(program["household"], 0, tag)

    def _validate(parsed):
        if _jsonschema is not None:
            _jsonschema.validate(parsed, schema)
        return parsed

    parsed = generate_json(
        _LongForm(client, 12288), _prompts.BINDING.text, user, schema,
        seed=seed, stage=tag, cache=cache, force=force, validate=_validate)

    merged = copy.deepcopy(program)
    by_obj = {e["object"]: e for e in merged["object_rules"]}
    n_added = 0
    dropped_noop: list[str] = []
    for entry in parsed["bindings"]:
        obj = entry["object"]
        home = by_obj[obj]["home"]
        for rule in entry.get("rules") or []:
            # A rule whose every REAL outcome (NO_OP aside) is the
            # object's own home is fake movement: the expander would mark
            # the object inert and strip ALL its rules, freezing it for
            # the whole run (measured on hh1's wallet_1 — three
            # home-pointing rules, 504 h at the counter). Home as ONE
            # outcome among others is fine — that is what a tidy dist
            # looks like.
            real = [d for d in (rule.get("dist") or [])
                    if d["dest"] != "NO_OP"]
            if not real or all(d["dest"] == home for d in real):
                dropped_noop.append(f"{obj}@{rule['activity']}")
                continue
            by_obj[obj].setdefault("rules", []).append(rule)
            n_added += 1
    if dropped_noop:
        print(f"  binding pass: dropped {len(dropped_noop)} no-op rule(s) "
              f"whose dest was the object's own home: {dropped_noop[:6]}")
    stats = {"n_unbound_targeted": len(unbound),
             "targeted_activities": unbound,
             "n_rules_added": n_added,
             "n_dropped_noop_rules": len(dropped_noop),
             "dropped_noop_rules": dropped_noop, "tag": tag}
    return merged, stats


def story_prompt_hash() -> str:
    """Content hash of the (shared) story stage's prompt surface, for
    provenance — the story templates are module strings, not
    PromptTemplates, so the hash is derived here the same way."""
    return hashlib.sha256(
        (sd.STORY_SYSTEM + sd.STORY_USER).encode()).hexdigest()[:8]


def story_to_arc_program(program: dict, story: list[dict],
                         days: int) -> dict:
    """rule_based program + story calendar -> the synthetic program whose
    dated calendar IS the story (see module docstring). object_rules,
    activities extras, placements, residents, receptacles all pass
    through verbatim; only the schedule is replaced."""
    # jitter / skip_p join per activity from the rule_based program's own
    # blocks (first occurrence wins — deterministic), so a story
    # `breakfast` keeps the same realization texture the template's
    # breakfast had. A story activity the program never scheduled gets
    # the routine defaults; sleep never skips, whatever the join says.
    src_blocks = [dict(s, sleep=True, skip_p=0.0)
                  for s in program.get("sleep_schedule") or []]
    src_blocks += program["weekly_blocks"]
    jitter_of: dict[str, str] = {}
    skip_of: dict[str, float] = {}
    for b in src_blocks:
        jitter_of.setdefault(b["activity"], b["jitter"])
        skip_of.setdefault(b["activity"], float(b.get("skip_p") or 0.0))
    arcs = []
    for d in sorted(story, key=lambda x: x["day"]):
        adds = []
        for blk in d["blocks"]:
            a = blk["activity"]
            is_sleep = any(s in a for s in xc.SLEEP_TOKENS)
            adds.append({
                "resident": blk["resident"], "activity": a,
                "start": blk["start"], "end": blk["end"], "at": blk["at"],
                "jitter": jitter_of.get(a, "routine"),
                "skip_p": 0.0 if is_sleep else skip_of.get(a, 0.0),
            })
        if adds:
            arcs.append({"day": d["day"], "note": d.get("summary", ""),
                         "patch": {"add": adds}})
    out = dict(program)
    out["days"] = days
    out["sleep_schedule"] = []
    out["weekly_blocks"] = []
    out["arc_events"] = arcs
    return out


def run_household(hh_src: pathlib.Path, out_hh: pathlib.Path, model: str,
                  cache, days: int, seed: int, force: bool,
                  per_week: bool = False, bind: bool = False):
    """One household: story stage -> synthetic program -> rules engine.
    Returns the final meta dict, or None when refused (no story)."""
    program = yaml.safe_load((hh_src / "routine_program.yaml").read_text())
    persona_text = (hh_src / "persona.yaml").read_text()
    client = llm_client._get_client(model)

    story, failed_calls, call_stats = sd.generate_story(
        program, persona_text, cache, client, days, force,
        out_hh=out_hh, per_week=per_week)
    sd._write_story(out_hh, program["household"], story)
    for name in ("persona.yaml", "routine_program.yaml"):
        (out_hh / name).write_text((hh_src / name).read_text())
    if not story:
        print(f"  {program['household']}: every story call failed — "
              f"NO TIMELINE WRITTEN")
        return None

    bind_stats = {"n_unbound_targeted": 0, "n_rules_added": 0}
    if bind:
        program, bind_stats = bind_unbound(program, story, persona_text,
                                           client, cache, force)
        # The merged program is a generated artifact: the source
        # rule_based program stays verbatim in routine_program.yaml, the
        # additions live here for inspection.
        (out_hh / "bound_program.yaml").write_text(
            "# GENERATED by src/revamp_v2/story_rules.py --bind-unbound —\n"
            "# the rule_based object_rules plus story-aware bindings for\n"
            "# the story's unbound at-home activities.\n"
            + yaml.safe_dump(program, sort_keys=False, width=100,
                             allow_unicode=True))
        print(f"  binding pass: {bind_stats['n_rules_added']} rules for "
              f"{bind_stats['n_unbound_targeted']} unbound activities")

    synth = story_to_arc_program(program, story, days)
    # The synthetic program is a generated artifact, kept for
    # inspectability (what the simulator actually consumed), never
    # authored or hand-edited.
    (out_hh / "story_program.yaml").write_text(
        "# GENERATED by src/revamp_v2/story_rules.py — the story calendar\n"
        "# as arc-event adds over the rule_based program's object_rules.\n"
        + yaml.safe_dump(synth, sort_keys=False, width=100,
                         allow_unicode=True))

    sa = sim.load_v1()
    params = sim.load_params()
    log, hourly, blocks, stats, acts, motions = sim.simulate_program(
        synth, days, seed, sa=sa, params=params)
    sim.tag_event_kinds(log)
    carry_cfg = params.get("carry_on_departure", {})
    stats["carry_rehome_suppressed"] = sim.suppress_carry_rehome(
        log, hourly, float(carry_cfg.get("carry_rehome_min", 0)))
    out_tl = out_hh / f"timeline_seed{seed}"
    sa.write_outputs(out_tl, motions, log, hourly, blocks, stats, days,
                     seed, hh_src)
    (out_hh / "expanded_motions.yaml").write_text(
        "# GENERATED by src/revamp_v2/story_rules.py from the story\n"
        "# calendar + the rule_based object_rules (revamp_v1 shape, for\n"
        "# spatialize.py/the viewer).\n"
        + yaml.safe_dump(motions, sort_keys=False, width=100,
                         allow_unicode=True))

    # The activity-name join, counted (see module docstring).
    story_acts = sorted({b["activity"] for d in story for b in d["blocks"]})
    bound = {r["activity"] for e in program.get("object_rules") or []
             for r in e.get("rules") or []}
    bound |= {a["name"] for a in program.get("activities") or []
              if a.get("reset_all")}
    unbound = sorted(a for a in story_acts if a not in bound)
    fallback_days = sorted(
        set(range(days)) - {d["day"] for d in story})

    meta = json.loads((out_tl / "meta.json").read_text())
    meta.update({
        "engine": "story_rules",
        "model": model,
        "source": str(hh_src),
        "builder_version": BUILDER_VERSION,
        "prompts": {"story": story_prompt_hash()},
        "story_call_stats": call_stats,
        "failed_story_calls": failed_calls,
        "fallback_days": fallback_days,
        "n_fallback_days": len(fallback_days),
        "not_story_driven": len(fallback_days) > 0.3 * days,
        "story_activities": story_acts,
        "n_story_activities": len(story_acts),
        "unbound_story_activities": unbound,
        "n_unbound_story_activities": len(unbound),
        "orphaned_rules_story": acts.get("orphaned_rules", []),
        "n_orphaned_rules_story": len(acts.get("orphaned_rules", [])),
        "binding_pass": bind_stats,
        "realization_params": {
            "skip": params["skip"],
            "fragmentation": params["fragmentation"],
            "carry_on_departure": carry_cfg},
    })
    if meta["not_story_driven"]:
        print(f"  {program['household']}: {len(fallback_days)}/{days} "
              f"fallback days — marked NOT story-driven")
    (out_tl / "meta.json").write_text(json.dumps(meta, indent=2))
    return meta


def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--households", nargs="+", required=True,
                    help="rule_based household dirs (persona + program)")
    ap.add_argument("--out-root", type=pathlib.Path, required=True)
    ap.add_argument("--model",
                    default=os.environ.get("GENERATION_MODEL",
                                           llm_client.DEFAULT_MODEL))
    ap.add_argument("--days", type=int, default=21)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--cache-dir", default=None)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--bind-unbound", action="store_true",
                    help="one guided-JSON call per household authoring "
                         "rules for the story's unbound at-home "
                         "activities (merged copy; the rule_based "
                         "program is never mutated)")
    ap.add_argument("--per-week", action="store_true",
                    help="one story call per week instead of per day "
                         "(replays existing per-week story caches, so both "
                         "story arms keep one calendar per household)")
    args = ap.parse_args()
    slug = llm_client.model_slug(args.model)
    # The STORY cache is shared with story_driven.py on purpose: same
    # seeds, same tag, same cache dir -> the two story arms author one
    # calendar per household, so the 2x2's story cells differ only in
    # the movement engine.
    cache = ResponseCache(args.cache_dir or
                          f"/tmp/dynamic-home-eqa-gen-cache-story-{slug}")
    failed = []
    for hh in args.households:
        hh_src = pathlib.Path(hh)
        out_hh = args.out_root / hh_src.name
        print(f"{hh_src.name}: story_rules, {args.days} days")
        meta = run_household(hh_src, out_hh, args.model, cache, args.days,
                             args.seed, args.force, per_week=args.per_week,
                             bind=args.bind_unbound)
        if meta is None:
            failed.append(hh_src.name)
            continue
        print(f"{meta['household']}: {meta['n_events']} events, "
              f"{meta['n_story_activities']} story activities "
              f"({meta['n_unbound_story_activities']} unbound, "
              f"{meta['n_orphaned_rules_story']} orphaned rules) "
              f"-> {out_hh}")
    if failed:
        print(f"FAILED (no story, no timeline): {failed}")
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
