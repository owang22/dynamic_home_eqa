#!/usr/bin/env python3
"""Rate each resident's forgetfulness for households built before the
persona schema carried one. One small guided-JSON call per household;
writes `forgetfulness: {level, cites}` onto persona.yaml's residents and
the mapped `forget_p` / `forget_cites` onto program.yaml's residents.
Does NOT re-realize — run `households.reseed` after.

New households get the rating from the persona pass itself
(schemas.forgetfulness_schema); this is the back-fill.

Usage:
  python -m households.annotate_forgetfulness            # every household
  python -m households.annotate_forgetfulness --household hh_001
  python -m households.annotate_forgetfulness --dry-run  # print, write nothing
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib

import yaml

from . import generate as g
from . import grid
from . import normalize
from . import prompts
from . import schemas
from . import simulate as sim
from dynamic_home_eqa.generation import llm_client
from dynamic_home_eqa.generation.cache import ResponseCache, make_seed
from dynamic_home_eqa.generation.hosted_spend import SpendGuard

RATE = prompts.PromptTemplate("forgetfulness_rating", """\
You rate how often each resident of a simulated household walks out of
the front door WITHOUT one of their pocket items (phone, keys, wallet).
Read the persona and give every resident exactly one level:
  rarely     — checks pockets, keeps things by the door, routine-bound
  sometimes  — an ordinary adult: the occasional rushed morning
  often      — scattered, rushed, distracted, or a child
Ground the level in what the persona actually says (personality, habits,
quirks, how their days go); do not invent traits. `cites` is one clause
quoting or paraphrasing the persona detail that decided it.

Respond only with valid JSON matching the provided schema.""")


def rating_schema(resident_ids: list[str]) -> dict:
    items = []
    for rid in resident_ids:
        items.append({
            "type": "object", "additionalProperties": False,
            "required": ["id", "level", "cites"],
            "properties": {
                "id": {"type": "string", "const": rid},
                "level": {"enum": list(schemas.FORGET_LEVELS)},
                "cites": {"type": "string", "maxLength": 200},
            }})
    return {
        "type": "object", "additionalProperties": False,
        "required": ["residents"],
        "properties": {"residents": {"type": "array", "minItems": len(items),
                                     "maxItems": len(items),
                                     "prefixItems": items,
                                     "items": False}},
    }


def persona_excerpt(persona: dict) -> str:
    keep = {k: persona[k] for k in ("household_type", "residents",
                                    "relationships", "daily_life_summary",
                                    "quirks") if k in persona}
    keep["residents"] = [{k: v for k, v in r.items() if k != "forgetfulness"}
                         for r in keep.get("residents", [])]
    return yaml.safe_dump(keep, sort_keys=False, allow_unicode=True,
                          width=100)


def annotate(hh_dir: pathlib.Path, client, cache, force: bool,
             dry_run: bool) -> list[tuple[str, str, str]]:
    persona = yaml.safe_load((hh_dir / "persona.yaml").read_text())
    program = yaml.safe_load((hh_dir / "program.yaml").read_text())
    rids = [r["id"] for r in persona["residents"]]
    have = all(r.get("forgetfulness") for r in persona["residents"])
    if have and not force:
        ratings = {r["id"]: r["forgetfulness"] for r in persona["residents"]}
    else:
        schema = rating_schema(rids)
        tag = RATE.tag("forgetfulness", builder=True, schema=schema)
        parsed = llm_client.generate_json(
            client, RATE.text, persona_excerpt(persona), schema,
            seed=make_seed(persona["household_id"], 0, tag), stage=tag,
            cache=cache, force=force)
        ratings = {r["id"]: {"level": r["level"], "cites": r["cites"]}
                   for r in parsed["residents"]}
    params = sim.load_params()
    rows = []
    for r in persona["residents"]:
        r["forgetfulness"] = dict(ratings[r["id"]])
        rows.append((r["id"], r["forgetfulness"]["level"],
                     r["forgetfulness"]["cites"]))
    if dry_run:
        return rows
    log: list[str] = []
    canonical = normalize.canonicalize(persona, log, persona["household_id"])
    problems = normalize.validate(normalize.strip_styles(canonical),
                                  persona["household_id"])
    if problems:
        raise SystemExit(f"{hh_dir.name}: {problems}")
    (hh_dir / "persona.yaml").write_text(yaml.dump(
        canonical, Dumper=normalize.Dumper, sort_keys=False,
        allow_unicode=True, width=78, indent=2, default_flow_style=False))
    by_id = {r["id"]: r for r in persona["residents"]}
    for pr in program["residents"]:
        pr.pop("forget_p", None)
        pr.pop("forget_cites", None)
        pr.update(g.forget_fields(by_id[pr["id"]], params))
    (hh_dir / "program.yaml").write_text(
        "# GENERATED — the realization input: the story's days as dated\n"
        "# entries, plus the movement rules.\n"
        + yaml.safe_dump(program, sort_keys=False, width=100,
                         allow_unicode=True))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--household", default=None)
    ap.add_argument("--model", default=os.environ.get("GENERATION_MODEL",
                                                      "gpt-5.6-terra"))
    ap.add_argument("--model-dir", type=pathlib.Path,
                    default=grid.DATA_DIR / "generated" / "gpt-5.6-terra")
    ap.add_argument("--cache-dir", default=None)
    ap.add_argument("--force", action="store_true",
                    help="re-rate residents that already carry a rating")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    slug = llm_client.model_slug(args.model)
    cache = ResponseCache(
        args.cache_dir
        or f"/tmp/dynamic-home-eqa-gen-cache-households-{slug}")
    os.environ.setdefault("HOSTED_RATES_YAML",
                          str(g.HERE / "hosted_rates.yaml"))
    os.environ.setdefault("HOSTED_SPEND_CAP", "0.50")
    os.environ.setdefault(
        "HOSTED_SPEND_LEDGER",
        f"/tmp/dynamic-home-eqa-households-forgetfulness-{slug}.json")
    client = llm_client._get_client(args.model)
    if getattr(client, "hosted", False):
        client.guard = SpendGuard.from_env()

    hh_dirs = sorted(d for d in args.model_dir.glob("hh_*")
                     if (d / "program.yaml").exists())
    if args.household:
        hh_dirs = [d for d in hh_dirs if d.name == args.household]
    for hh_dir in hh_dirs:
        for rid, level, cites in annotate(hh_dir, client, cache,
                                          args.force, args.dry_run):
            print(f"{hh_dir.name} {rid:12s} {level:9s} {cites}")
    if getattr(client, "hosted", False):
        print(client.guard.summary())


if __name__ == "__main__":
    main()
