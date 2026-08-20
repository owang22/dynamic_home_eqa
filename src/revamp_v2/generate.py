#!/usr/bin/env python3
"""revamp_v2 generation CLI: L0 (receptacles) + L1 (persona, one LLM call)
+ L2 (routine program, one LLM call per accepted attempt) for one household
or --all. Everything downstream of the accepted program is deterministic.

L0 is symbolic by default (a fixed synthetic receptacle template, scaled
only by the slot's bedroom count); `--scene <hssd_id>` derives the list
from the legacy anchor census (data/anchor_census/<id>.json, built by
scripts/compute_anchor_census.py) so every receptacle carries a real
anchor. Downstream layers never branch on which mode produced the list.

Rejection loop: a program failing any of the four checks (validate.py) is
resampled with a distinct derived seed — the attempt index folds into
make_seed, same pattern as llm_client.generate_json retry seeding — up to
--max-attempts (5). Every attempt's failure reasons land in the
household's build_log.json. Programs are NEVER hand-edited; a household
that keeps failing means the prompt or schema is wrong.

Usage:
  GENERATION_ENDPOINT=http://127.0.0.1:8300 \\
      python src/revamp_v2/generate.py --household hh1
  ... --all [--scene 102343992] [--force]
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import os
import pathlib
import sys

import yaml

HERE = pathlib.Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import claude_cli_client as ccc    # noqa: E402
import prompts                     # noqa: E402
import schemas                     # noqa: E402
import simulate as sim             # noqa: E402
import validate as v2v             # noqa: E402

from dynamic_home_eqa.generation import llm_client          # noqa: E402
from dynamic_home_eqa.generation.cache import (             # noqa: E402
    ResponseCache, make_seed)

REPO_ROOT = HERE.parent.parent
MAX_ATTEMPTS = 5
# The client's own 4096 default truncates any real program; and 10240 was
# still short for the largest household in the set (5 residents, 40
# objects, ~27.5k characters of JSON) which died on "Unterminated string".
# Keep this comfortably under the served --max-model-len minus the prompt:
# the largest household needs ~32k of context to fit prompt + program, and
# vLLM rejects (not truncates) a request whose sum exceeds the served
# length, so raising the budget without raising --max-model-len turns a
# truncation into a 400.
PROGRAM_MAX_TOKENS = 20480


class _LongFormClient:
    """Pass a higher max_tokens where the backend supports it (the HTTP
    client does; the in-process client hardcodes its own)."""

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


def _load_normalizer():
    """profiles/revamp_v1/normalize_profiles.py — the canonical-style
    authority; its functions are reused, its rules never duplicated."""
    path = REPO_ROOT / "profiles" / "revamp_v1" / "normalize_profiles.py"
    spec = importlib.util.spec_from_file_location("rv1_normalize", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- L0 -----

def synthetic_receptacles(bedrooms: int) -> list[dict]:
    """The symbolic-mode template: one fixed home, scaled by bedroom count
    alone (never by household type — the receptacle list must not leak
    it). Naming follows the v1 convention <thing>_<room-initial><n>."""
    recs: list[dict] = []
    for i in range(1, bedrooms + 1):
        room = "bedroom" if bedrooms == 1 else f"bedroom_{i}"
        s = f"b{i}"
        recs += [{"id": f"bed_{s}", "room": room},
                 {"id": f"nightstand_{s}", "room": room},
                 {"id": f"desk_{s}", "room": room},
                 {"id": f"bedroom_floor_{s}", "room": room}]
    recs += [{"id": "couch_l1", "room": "living"},
             {"id": "coffee_table_l1", "room": "living"},
             {"id": "tv_stand_l1", "room": "living"},
             {"id": "bookshelf_l1", "room": "living"},
             {"id": "armchair_l1", "room": "living"},
             {"id": "counter_k1", "room": "kitchen"},
             {"id": "sink_k1", "room": "kitchen"},
             {"id": "cupboard_k1", "room": "kitchen"},
             {"id": "dish_rack_k1", "room": "kitchen"},
             {"id": "kitchen_table_k1", "room": "kitchen"},
             {"id": "chair_k1", "room": "kitchen"},
             {"id": "chair_k2", "room": "kitchen"},
             {"id": "bathroom_shelf_ba1", "room": "bathroom"},
             {"id": "towel_rack_ba1", "room": "bathroom"},
             {"id": "entry_table_e1", "room": "entry"},
             {"id": "entry_hook_e1", "room": "entry"},
             {"id": "entry_floor_e1", "room": "entry"}]
    return recs


def census_receptacles(scene_id: str) -> list[dict]:
    """--scene mode: surface-eligible anchors from the precomputed census.
    The extra `anchor` field is provenance for later spatial grounding;
    no downstream layer reads it."""
    path = REPO_ROOT / "data" / "anchor_census" / f"{scene_id}.json"
    census = json.loads(path.read_text())
    recs = []
    for label, rec in sorted(census["anchors"].items()):
        if rec["active_receptacles"] < 1:
            continue
        recs.append({"id": label.replace(".", "_"), "room": rec["room"],
                     "anchor": label})
    if not recs:
        raise SystemExit(f"scene {scene_id}: no surface-eligible anchors")
    return recs


# ---------------------------------------------------------------- L1 -----

def generate_persona(slot: dict, control: dict, client, cache,
                     force: bool, attempt: int = 0) -> tuple[dict, str, int]:
    """(persona_data, canonical_yaml_text, seed). One call; the validate
    callback inside generate_json retries (distinct seeds) on canonical-
    style problems the normalizer reports. `attempt` folds into the seed so
    the leak audit (which tests the persona's OWN vocabulary) can ask for a
    genuinely different household."""
    np_mod = _load_normalizer()
    other = [h["household_type"] for h in control["households"]
             if h["household_id"] != slot["household_id"]]
    schema = schemas.build_persona_schema(
        slot["household_id"], slot["household_type"], int(slot["residents"]),
        control["object_vocabulary"])
    tag = prompts.PERSONA.tag("persona", builder=True, schema=schema)
    seed = make_seed(slot["household_id"], 0, tag, attempt)

    def _validate(parsed: dict) -> dict:
        log: list[str] = []
        canonical = np_mod.canonicalize(parsed, log, slot["household_id"])
        problems = np_mod.validate(np_mod.strip_styles(canonical),
                                   slot["household_id"])
        if problems:
            raise ValueError("; ".join(problems))
        return canonical

    canonical = llm_client.generate_json(
        client, prompts.PERSONA.text,
        prompts.persona_user_prompt(slot, other),
        schema, seed=seed, stage=tag, cache=cache, force=force,
        validate=_validate)
    text = yaml.dump(canonical, Dumper=np_mod.Dumper, sort_keys=False,
                     allow_unicode=True, width=78, indent=2,
                     default_flow_style=False)
    return np_mod.strip_styles(canonical), text, seed


# ---------------------------------------------------------------- L2 -----

def _inject(raw: dict, slot: dict, receptacles: list[dict]) -> dict:
    """Add the deterministic pipeline fields the LLM never authors, in a
    stable key order."""
    program = {"household": raw["household"],
               "household_type": slot["household_type"],
               "source_persona": raw["source_persona"],
               "days": raw["days"], "day0": raw["day0"],
               "residents": raw["residents"],
               "receptacles": copy.deepcopy(receptacles)}
    for key in ("sleep_schedule", "weekly_blocks", "object_rules",
                "activities", "arc_events"):
        program[key] = raw[key]
    return program


def generate_program(slot: dict, control: dict, persona: dict,
                     persona_text: str, receptacles: list[dict], days: int,
                     client, cache, force: bool,
                     max_attempts: int = MAX_ATTEMPTS
                     ) -> tuple[dict | None, list[dict]]:
    """(accepted_program | None, attempt_records)."""
    params = sim.load_params()
    inventory = persona["object_inventory"]
    schema = schemas.build_program_schema(
        slot["household_id"],
        [r["id"] for r in persona["residents"]],
        [o["id"] for o in inventory],
        [r["id"] for r in receptacles], days, params,
        object_owners={o["id"]: o["owner"] for o in inventory},
        object_classes={o["id"]: o["class"] for o in inventory})
    tag = prompts.ROUTINE_PROGRAM.tag("routine_program", builder=True,
                                      schema=schema)
    user = prompts.program_user_prompt(persona_text, receptacles, days,
                                       "Monday")
    attempts: list[dict] = []
    for attempt in range(max_attempts):
        seed = make_seed(slot["household_id"], 0, tag, attempt)
        record: dict = {"attempt": attempt, "seed": seed}
        try:
            raw = llm_client.generate_json(
                _LongFormClient(client, PROGRAM_MAX_TOKENS),
                prompts.ROUTINE_PROGRAM.text, user, schema,
                seed=seed, stage=tag, cache=cache, force=force)
        except Exception as e:                      # guided-JSON exhaustion
            record["failures"] = [f"generation: {e!r}"]
            attempts.append(record)
            continue
        program = _inject(raw, slot, receptacles)
        record["failures"] = failures = v2v.static_checks(
            raw, program, persona, schema)
        attempts.append(record)
        if not failures:
            return program, attempts
    return None, attempts


# ------------------------------------------------------------- driver ----

def build_household(slot: dict, control: dict, out_root: pathlib.Path,
                    model: str, scene: str | None, days: int, client,
                    cache, force: bool,
                    max_attempts: int = MAX_ATTEMPTS) -> bool:
    hh_dir = out_root / f"hh{int(slot['household_id'].split('_')[-1])}"
    hh_dir.mkdir(parents=True, exist_ok=True)
    receptacles = (census_receptacles(scene) if scene
                   else synthetic_receptacles(int(slot.get("bedrooms", 2))))
    types = [h["household_type"] for h in control["households"]]
    leak_schema = schemas.build_leak_schema(types)
    leak_tag = prompts.LEAK_AUDIT.tag("leak_audit", builder=True,
                                      schema=leak_schema)
    # The leak audit judges the OBJECT AND RECEPTACLE IDS, which are fixed
    # by the persona and the scene — nothing the routine program can
    # change. Auditing it here means a rejection resamples the household
    # that leaked, instead of re-rolling a program five times against a
    # persona that will give the type away every time.
    persona_attempts: list[dict] = []
    persona = persona_text = None
    leak_unresolved = False
    for attempt in range(max_attempts):
        persona, persona_text, persona_seed = generate_persona(
            slot, control, client, cache, force, attempt=attempt)
        leak_seed = make_seed(slot["household_id"], 0, leak_tag, attempt)
        leak_problems, leak_record = v2v.check_leak(
            {"object_rules": [{"object": o["id"]}
                              for o in persona["object_inventory"]],
             "receptacles": receptacles,
             "household_type": slot["household_type"]},
            types, client, cache, leak_seed, leak_tag, force=force)
        persona_attempts.append({"attempt": attempt, "seed": persona_seed,
                                 "leak_prediction": leak_record})
        if not leak_problems:
            break
    else:
        # Exhausted: every sampled household for this slot gave its type
        # away. For some types the closed 25-class object vocabulary makes
        # this unavoidable — a home with toys, a lunchbox and two backpacks
        # IS a family with young children, and no faithful persona hides
        # it. The household is still built, flagged here and surfaced in
        # the acceptance report, rather than silently passing or silently
        # dropping a slot from the set.
        leak_unresolved = True
    (hh_dir / "persona.yaml").write_text(persona_text)
    program, attempts = generate_program(
        slot, control, persona, persona_text, receptacles, days, client,
        cache, force)
    program_path = hh_dir / "routine_program.yaml"
    if program is not None:
        program_path.write_text(
            yaml.safe_dump(program, sort_keys=False, width=100,
                           allow_unicode=True))
    elif program_path.exists():
        # A failed regeneration must not leave the PREVIOUS program in
        # place: build.sh would simulate it as if this run had produced
        # it, and build_log.json would say FAILED beside a timeline.
        program_path.unlink()
    build_log = {
        "household": slot["household_id"],
        "household_type": slot["household_type"],
        "model": model, "model_slug": llm_client.model_slug(model),
        "builder_version": prompts.BUILDER_VERSION,
        "prompts": {t.name: t.version for t in
                    (prompts.PERSONA, prompts.ROUTINE_PROGRAM,
                     prompts.LEAK_AUDIT)},
        "scene": scene or "symbolic",
        "days": days,
        "persona_seed": persona_seed,
        "persona_attempts": persona_attempts,
        "leak_unresolved": leak_unresolved,
        "n_attempts": len(attempts),
        "accepted_attempt": (attempts[-1]["attempt"]
                             if program is not None else None),
        "attempts": attempts,
    }
    (hh_dir / "build_log.json").write_text(json.dumps(build_log, indent=2))
    status = "OK" if program is not None else "FAILED"
    flag = " [LEAKS TYPE]" if leak_unresolved else ""
    print(f"{slot['household_id']}: {status} after {len(attempts)} "
          f"attempt(s){flag} -> {hh_dir}")
    return program is not None


def _main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--household", help="e.g. hh1 or hh_001")
    group.add_argument("--all", action="store_true")
    ap.add_argument("--scene", default=None,
                    help="HSSD scene id: derive receptacles from its anchor "
                         "census instead of the symbolic template")
    ap.add_argument("--model",
                    default=os.environ.get("GENERATION_MODEL",
                                           llm_client.DEFAULT_MODEL))
    ap.add_argument("--cache-dir", default=None,
                    help="response cache (default: per-model dir under /tmp)")
    ap.add_argument("--out-root", type=pathlib.Path, default=None,
                    help="default: profiles/revamp_v2/<model_slug>/")
    ap.add_argument("--days", type=int, default=None,
                    help="default: control.yaml `days`")
    ap.add_argument("--force", action="store_true",
                    help="bypass the response cache")
    args = ap.parse_args()

    control = yaml.safe_load(
        (sim.PROFILES_DIR / "control.yaml").read_text())
    days = args.days or int(control["days"])
    slug = llm_client.model_slug(args.model)
    out_root = args.out_root or sim.PROFILES_DIR / slug
    cache = ResponseCache(args.cache_dir or
                          f"/tmp/dynamic-home-eqa-gen-cache-revamp-v2-{slug}")
    # A `claude-*` model is a hosted model on the user's subscription, which
    # only the Claude Code binary can spend — never a served endpoint. Route
    # it through the CLI backend; everything downstream is identical.
    client = (ccc.ClaudeCliClient(args.model)
              if ccc.is_claude_model(args.model)
              else llm_client._get_client(args.model))

    slots = control["households"]
    if not args.all:
        digits = "".join(c for c in args.household if c.isdigit())
        if not digits:
            raise SystemExit(f"--household {args.household!r} names no number")
        slots = [s for s in slots
                 if int(s["household_id"].split("_")[-1]) == int(digits)]
        if not slots:
            raise SystemExit(f"no household slot matches {args.household!r}")
    ok = all([build_household(s, control, out_root, args.model, args.scene,
                              days, client, cache, args.force)
              for s in slots])
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    _main()
