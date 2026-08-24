#!/usr/bin/env python3
"""Task 2 of the hosted-generation pilot: probe OpenAI strict structured
outputs with every REAL schema the revamp_v2 pipeline uses, before any
pilot generation spends real money on them.

For each schema — persona, the three L2 schemas (calendar / objects /
special events; the split pipeline's actual contracts), the per-day story
schema, the bind-pass schema, and the leak-audit schema — one strict-mode
call is attempted with a trivial prompt and a tiny completion budget (the
probe tests schema ACCEPTANCE, which OpenAI validates up front and
rejects with a 400 before generating; the budget only caps the accepted
calls' cost to pennies). A rejected schema is re-probed after
to_hosted_schema(); the API's error text is recorded verbatim either way.

All schemas are built for hh4 (family_teen_and_child, 4 residents — the
pilot household), with object/receptacle ids from the committed
qwen3.8-27b build, so enum sizes match what the pilot will actually send.

Two cheap behavior probes ride along (evidence over memory):
  - `temperature` on a gpt-5.x call — the adapter drops it; this records
    the API's actual response to sending it;
  - `seed` acceptance.

Output: reports/hosted_pilot/schema_compat.md (+ schema_compat.json with
the raw records). Requires OPENAI_API_KEY and the committed rate table;
every call is priced into the pilot's spend ledger.

Usage:
  OPENAI_API_KEY=... python src/revamp_v2/probe_hosted_schemas.py \
      [--model gpt-5.6-luna] [--hh-src profiles/revamp_v2/rule_based/qwen3.8-27b/hh4]
"""
from __future__ import annotations

import argparse
import copy
import json
import pathlib
import sys
import time

import yaml

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT / "src"))

import schemas                                                 # noqa: E402
import story_calendar as sc                                    # noqa: E402
import story_driven as sd                                      # noqa: E402

from dynamic_home_eqa.generation.hosted_schema import (        # noqa: E402
    to_hosted_schema)
from dynamic_home_eqa.generation.llm_client import (           # noqa: E402
    HostedOpenAIClient)

ENDPOINT = "https://api.openai.com"
TRIVIAL_SYSTEM = "Return any minimal instance that satisfies the schema."
TRIVIAL_USER = "Any valid instance. Content does not matter."
PROBE_MAX_COMPLETION = 64   # acceptance is judged before generation; this
                            # only caps what an ACCEPTED probe can spend

# Why each keyword the transform removes stays safe: the downstream check
# that re-enforces it. Consulted per removal; a removal with no entry here
# fails the probe loudly (the brief's rule: named coverage or a new
# assertion in check_referential, never a silent drop).
KEYWORD_COVERAGE = {
    "prefixItems": (
        "llm_client._hosted_check re-validates EVERY hosted response "
        "against the original schema (jsonschema, prefixItems included) "
        "before any caller sees it; for L2 additionally validate.py "
        "check_schema (original schema) and check_referential's "
        "one-entry-per-inventory-object assertion"),
    "items=false": "same as prefixItems (the two encode one shape)",
    "optional->required+nullable": (
        "mechanically inverted by hosted_schema.drop_nulls before the "
        "original-schema re-validation in llm_client._hosted_check — "
        "null never reaches a validator or an artifact"),
    "uniqueItems": "validate.py check_referential (repeated-weekday check)",
    "contains": "validate.py check_referential",
    "dependentRequired": ("never relied on (xgrammar accepted but did not "
                          "enforce it; profiles/revamp_v2/README.md) — "
                          "validate.py's jsonschema pass enforces it where "
                          "declared"),
    "const+=type": ("purely ADDITIVE (strict mode wants a type key beside "
                    "every const; the inferred type is the const value's "
                    "own) — nothing removed, nothing to re-check"),
    "enum-dedup->$defs": ("semantically IDENTICAL rewrite (repeated enum "
                          "bodies hoisted behind $ref to fit the probed "
                          "1000-enum-value cap) — nothing widened, "
                          "nothing to re-check"),
}


def schema_stats(schema: dict) -> dict:
    n_props = n_enums = enum_values = max_enum = 0
    max_depth = 0

    def walk(node, depth):
        nonlocal n_props, n_enums, enum_values, max_enum, max_depth
        max_depth = max(max_depth, depth)
        if isinstance(node, dict):
            props = node.get("properties")
            if isinstance(props, dict):
                n_props += len(props)
            enum = node.get("enum")
            if isinstance(enum, list):
                n_enums += 1
                enum_values += len(enum)
                max_enum = max(max_enum, len(enum))
            for v in node.values():
                walk(v, depth + 1)
        elif isinstance(node, list):
            for v in node:
                walk(v, depth)

    walk(schema, 0)
    return {"properties": n_props, "enums": n_enums,
            "enum_values_total": enum_values, "enum_values_max": max_enum,
            "nesting_depth": max_depth,
            "chars": len(json.dumps(schema))}


def probe_once(client: HostedOpenAIClient, name: str, schema: dict,
               extra_body: dict | None = None) -> dict:
    body = {
        "model": client.model,
        "messages": [{"role": "system", "content": TRIVIAL_SYSTEM},
                     {"role": "user", "content": TRIVIAL_USER}],
        "max_completion_tokens": PROBE_MAX_COMPLETION,
        "reasoning_effort": "none",
        "response_format": {"type": "json_schema",
                            "json_schema": {"name": "probe", "strict": True,
                                            "schema": schema}},
    }
    body.update(extra_body or {})
    t0 = time.time()
    try:
        data = client._post_chat(body)
    except RuntimeError as e:
        return {"name": name, "accepted": False, "error": str(e),
                "wall_s": round(time.time() - t0, 2)}
    return {"name": name, "accepted": True, "error": None,
            "model_snapshot": data.get("model"),
            "finish_reason": data["choices"][0].get("finish_reason"),
            "usage": data.get("usage"),
            "wall_s": round(time.time() - t0, 2)}


def build_all_schemas(hh_src: pathlib.Path) -> dict:
    """Every real schema, sized for hh4 from the committed build."""
    import simulate as sim
    control = yaml.safe_load((sim.PROFILES_DIR / "control.yaml").read_text())
    slot = next(h for h in control["households"]
                if h["household_id"] == "hh_004")
    types = [h["household_type"] for h in control["households"]]
    persona = yaml.safe_load((hh_src / "persona.yaml").read_text())
    program = yaml.safe_load((hh_src / "routine_program.yaml").read_text())
    params = sim.load_params()
    residents = [r["id"] for r in persona["residents"]]
    receptacles = [r["id"] for r in program["receptacles"]]
    object_ids = [o["id"] for o in persona["object_inventory"]]
    scheduled = sorted({b["activity"]
                        for b in (program.get("sleep_schedule") or [])
                        + program["weekly_blocks"]})
    days = int(program["days"])
    return {
        "persona": schemas.build_persona_schema(
            slot["household_id"], slot["household_type"],
            int(slot["residents"]), control["object_vocabulary"]),
        "l2_calendar": schemas.build_calendar_schema(
            slot["household_id"], residents, receptacles, days, params),
        "l2_objects": schemas.build_objects_schema(
            slot["household_id"], residents, object_ids, receptacles,
            days, params, scheduled),
        "l2_special_events": schemas.build_special_schema(
            days, scheduled, residents, receptacles, object_ids, params),
        "story_day": sd.build_story_schema([residents[0]], receptacles,
                                           0, 0),
        "bind_pass": sc.build_binding_schema(
            object_ids, scheduled[:8] or ["dinner"], receptacles,
            residents),
        "leak_audit": schemas.build_leak_schema(types),
    }


def render_report(rows: list[dict], behavior: list[dict],
                  model: str) -> str:
    lines = [
        "# Hosted schema compatibility (Task 2 probe)", "",
        f"Model: `{model}` — one strict-mode call per schema against "
        f"`{ENDPOINT}`, trivial prompt, `max_completion_tokens="
        f"{PROBE_MAX_COMPLETION}`. Acceptance is judged by the API's "
        "up-front schema validation (a 400 names the offending keyword "
        "verbatim below); rejected schemas are re-probed after "
        "`to_hosted_schema()`.", "",
        "| schema | raw: accepted | transformed: accepted | props | "
        "enums (total values / max) | depth | chars raw -> hosted |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        st, ht = r["stats_raw"], r["stats_hosted"]
        raw_ok = "yes" if r["raw"]["accepted"] else "NO"
        hosted = r.get("hosted")
        hosted_ok = ("(not needed)" if hosted is None
                     else "yes" if hosted["accepted"] else "NO")
        nop = r.get("hosted_noprefix")
        if nop is not None:
            hosted_ok += ("; no-prefixItems: "
                          + ("yes" if nop["accepted"] else "NO"))
        lines.append(
            f"| {r['name']} | {raw_ok} | {hosted_ok} | {st['properties']} "
            f"| {st['enums']} ({st['enum_values_total']} / "
            f"{st['enum_values_max']}) | {st['nesting_depth']} | "
            f"{st['chars']} -> {ht['chars']} |")
    lines += ["", "## Rejections, verbatim", ""]
    any_rej = False
    for r in rows:
        for kind in ("raw", "hosted", "hosted_noprefix"):
            rec = r.get(kind)
            if rec and not rec["accepted"]:
                any_rej = True
                lines += [f"### {r['name']} ({kind})", "", "```",
                          rec["error"][:1500], "```", ""]
    if not any_rej:
        lines += ["(none)", ""]
    lines += ["## Transform removals and their covering checks", ""]
    for r in rows:
        if not r["removals"]:
            lines.append(f"- **{r['name']}**: no removals (already inside "
                         "the strict subset)")
            continue
        lines.append(f"- **{r['name']}**:")
        by_kw: dict[str, list[str]] = {}
        for rem in r["removals"]:
            path, kw = rem.rsplit(": ", 1)
            by_kw.setdefault(kw, []).append(path)
        for kw, paths in by_kw.items():
            cover = KEYWORD_COVERAGE.get(kw)
            assert cover, (f"removed keyword {kw!r} has NO covering check "
                           f"— add one to check_referential before piloting")
            preview = ", ".join(paths[:3]) + \
                (f", … ({len(paths)} sites)" if len(paths) > 3 else "")
            lines.append(f"  - `{kw}` at {preview}")
            lines.append(f"    - covered by: {cover}")
    lines += ["", "## Behavior probes", ""]
    for b in behavior:
        verdict = "accepted" if b["accepted"] else f"REJECTED: {b['error'][:400]}"
        lines.append(f"- `{b['name']}`: {verdict}")
    lines += ["", f"Spend after probe: see the ledger "
              f"(`HOSTED_SPEND_LEDGER`).", ""]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", default="gpt-5.6-luna")
    ap.add_argument("--hh-src", type=pathlib.Path,
                    default=REPO_ROOT / "profiles" / "revamp_v2"
                    / "rule_based" / "qwen3.8-27b" / "hh4")
    ap.add_argument("--out-dir", type=pathlib.Path,
                    default=REPO_ROOT / "reports" / "hosted_pilot")
    args = ap.parse_args()

    client = HostedOpenAIClient(ENDPOINT, args.model)
    all_schemas = build_all_schemas(args.hh_src)
    rows = []
    for name, schema in all_schemas.items():
        hosted_schema, removals = to_hosted_schema(schema)
        row = {"name": name,
               "stats_raw": schema_stats(schema),
               "stats_hosted": schema_stats(hosted_schema),
               "removals": removals,
               "raw": probe_once(client, name, copy.deepcopy(schema))}
        print(f"{name}: raw {'accepted' if row['raw']['accepted'] else 'REJECTED'}")
        if not row["raw"]["accepted"]:
            row["hosted"] = probe_once(client, f"{name} (transformed)",
                                       hosted_schema)
            print(f"{name}: transformed "
                  f"{'accepted' if row['hosted']['accepted'] else 'REJECTED'}")
        if row.get("hosted") and not row["hosted"]["accepted"]:
            # third variant: the prefixItems-removal fallback (see
            # to_hosted_schema) — records whether the slot-pinning shape
            # is the remaining blocker.
            nop_schema, nop_removals = to_hosted_schema(
                schema, extra_remove=frozenset({"prefixItems"}))
            row["hosted_noprefix"] = probe_once(
                client, f"{name} (transformed, no prefixItems)", nop_schema)
            row["removals_noprefix"] = nop_removals
            print(f"{name}: transformed-noprefix "
                  f"{'accepted' if row['hosted_noprefix']['accepted'] else 'REJECTED'}")
        rows.append(row)

    leak = to_hosted_schema(all_schemas["leak_audit"])[0]
    behavior = [
        probe_once(client, "temperature=0.7 alongside strict outputs",
                   leak, {"temperature": 0.7}),
        probe_once(client, "seed alongside strict outputs",
                   leak, {"seed": 12345}),
    ]
    for b in behavior:
        print(f"behavior: {b['name']}: "
              f"{'accepted' if b['accepted'] else 'rejected'}")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "schema_compat.json").write_text(
        json.dumps({"model": args.model, "snapshot": client.snapshot,
                    "rows": rows, "behavior": behavior}, indent=2))
    report = render_report(rows, behavior, args.model)
    (args.out_dir / "schema_compat.md").write_text(report)
    print(f"\nwrote {args.out_dir / 'schema_compat.md'}")
    print(client.guard.summary())


if __name__ == "__main__":
    main()
