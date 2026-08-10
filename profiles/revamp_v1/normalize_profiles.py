#!/usr/bin/env python3
"""Normalize revamp_v1 household profiles to one canonical YAML style.

Both generator sets (claude-fable-5/, chatgpt-5.6sol-high/) are authored by
hand or pasted from a model, so they drift in presentation: flow vs block
mappings, quoted vs folded prose, stray blank lines. This rewrites every
profile into the single canonical form documented in README.md, and fixes two
classes of real defect it finds along the way:

  * object ids that do not begin with their own `class` value
  * words split by a hyphen across a hand-wrapped line ("longest- running"),
    which YAML folds into a literal "- " inside the string

Canonical style
---------------
  key order      household_id, household_type, residents, relationships,
                 home_layout_notes, object_inventory, daily_life_summary,
                 quirks; resident = id, name, age, occupation, personality,
                 habits; object = id, class, owner, role
  block style    everywhere; no flow mappings, no blank lines inside lists
  folded (>-)    relationships, home_layout_notes, daily_life_summary, quirks
  plain          everything else, wrapped at 78 cols. PyYAML escalates a value
                 to quoted only where plain would be ambiguous (a "key: value"
                 lookalike, say), so quotes in the output mark real hazards
                 rather than authoring habit.

Usage:
  python normalize_profiles.py --check     # report changes, write nothing
  python normalize_profiles.py             # rewrite files in place
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

import yaml

SETS = ["claude-fable-5", "chatgpt-5.6sol-high"]

HOUSEHOLD_KEYS = [
    "household_id",
    "household_type",
    "residents",
    "relationships",
    "home_layout_notes",
    "object_inventory",
    "daily_life_summary",
    "quirks",
]
RESIDENT_KEYS = ["id", "name", "age", "occupation", "personality", "habits"]
OBJECT_KEYS = ["id", "class", "owner", "role"]
FOLDED_KEYS = {"relationships", "home_layout_notes", "daily_life_summary", "quirks"}

# A word split across a hand-wrapped line: YAML folds the break to a space, so
# "longest-\n running" parses as "longest- running". Real compound words never
# carry a space after the hyphen, so this pattern only matches the artifact.
HYPHEN_SPLIT = re.compile(r"(\w)- (\w)")


class Folded(str):
    """String to emit as a folded block scalar (>-)."""


class Text(str):
    """Free text: emit plain, letting PyYAML quote only when plain is unsafe.

    Plain scalars fold across lines on whitespace alone, so long values wrap
    without the backslash continuations a double-quoted scalar would need.
    """


class Dumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        # Indent block sequences under their parent key ("  - id:" not "- id:").
        return super().increase_indent(flow, False)


Dumper.add_representer(
    Folded, lambda d, v: d.represent_scalar("tag:yaml.org,2002:str", str(v), style=">")
)
Dumper.add_representer(
    Text, lambda d, v: d.represent_scalar("tag:yaml.org,2002:str", str(v), style=None)
)


def reorder(mapping: dict, keys: list[str], where: str) -> dict:
    """Return mapping with `keys` first, in order. Unknown keys are an error."""
    extra = set(mapping) - set(keys)
    if extra:
        raise ValueError(f"{where}: unexpected keys {sorted(extra)}")
    missing = [k for k in keys if k not in mapping]
    if missing:
        raise ValueError(f"{where}: missing keys {missing}")
    return {k: mapping[k] for k in keys}


def canonicalize(data: dict, log: list[str], where: str) -> dict:
    """Reorder keys, tag scalar styles, and fix id/hyphen defects."""

    def fix_text(value: str, field: str) -> str:
        fixed = HYPHEN_SPLIT.sub(r"\1\2", value)
        if fixed != value:
            for m in HYPHEN_SPLIT.finditer(value):
                log.append(f"{where}.{field}: joined split word {m.group(0)!r}")
        return fixed

    out = reorder(data, HOUSEHOLD_KEYS, where)

    residents = []
    for i, resident in enumerate(out["residents"]):
        r = reorder(resident, RESIDENT_KEYS, f"{where}.residents[{i}]")
        r["occupation"] = Text(fix_text(r["occupation"], f"residents[{i}].occupation"))
        r["personality"] = Text(fix_text(r["personality"], f"residents[{i}].personality"))
        r["habits"] = [
            Text(fix_text(h, f"residents[{i}].habits[{j}]"))
            for j, h in enumerate(r["habits"])
        ]
        residents.append(r)
    out["residents"] = residents

    objects = []
    for i, obj in enumerate(out["object_inventory"]):
        o = reorder(obj, OBJECT_KEYS, f"{where}.object_inventory[{i}]")
        if not o["id"].startswith(o["class"]):
            # Keep the discriminator, restore the class prefix the id must carry.
            suffix = o["id"].split("_", 1)[1] if "_" in o["id"] else o["id"]
            new_id = f"{o['class']}_{suffix}"
            log.append(f"{where}: renamed id {o['id']!r} -> {new_id!r} (class={o['class']})")
            o["id"] = new_id
        o["role"] = Text(fix_text(o["role"], f"object_inventory[{i}].role"))
        objects.append(o)
    out["object_inventory"] = objects

    for key in FOLDED_KEYS:
        out[key] = Folded(fix_text(out[key], key))

    return out


def strip_styles(value):
    """Recursively drop the Folded/Text wrappers, for round-trip comparison."""
    if isinstance(value, dict):
        return {k: strip_styles(v) for k, v in value.items()}
    if isinstance(value, list):
        return [strip_styles(v) for v in value]
    if isinstance(value, str):
        return str(value)
    return value


def validate(data: dict, where: str) -> list[str]:
    """Structural checks that normalization must not paper over."""
    problems = []
    ids = [o["id"] for o in data["object_inventory"]]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        problems.append(f"{where}: duplicate object ids {sorted(dupes)}")
    resident_ids = {r["id"] for r in data["residents"]}
    for o in data["object_inventory"]:
        if o["owner"] != "shared" and o["owner"] not in resident_ids:
            problems.append(f"{where}: object {o['id']} has unknown owner {o['owner']!r}")
    for i, r in enumerate(data["residents"], start=1):
        if r["id"] != f"resident_{i}":
            problems.append(f"{where}: resident {i} has id {r['id']!r}, expected resident_{i}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report changes, write nothing")
    ap.add_argument("--root", default=pathlib.Path(__file__).parent, type=pathlib.Path)
    args = ap.parse_args()

    log: list[str] = []
    problems: list[str] = []
    rewritten = unchanged = 0

    for gen in SETS:
        for path in sorted((args.root / gen / "households").glob("*.yaml")):
            where = f"{gen}/{path.name}"
            original_text = path.read_text()
            data = yaml.safe_load(original_text)

            canonical = canonicalize(data, log, where)
            problems += validate(strip_styles(canonical), where)

            text = yaml.dump(
                canonical,
                Dumper=Dumper,
                sort_keys=False,
                allow_unicode=True,
                width=78,
                indent=2,
                default_flow_style=False,
            )

            # The rewrite must preserve content exactly, modulo the logged fixes.
            if strip_styles(yaml.safe_load(text)) != strip_styles(canonical):
                problems.append(f"{where}: ROUND-TRIP MISMATCH — not written")
                continue

            if text == original_text:
                unchanged += 1
            else:
                rewritten += 1
                if not args.check:
                    path.write_text(text)

    for line in log:
        print(f"  fix: {line}")
    for line in problems:
        print(f"  PROBLEM: {line}", file=sys.stderr)

    verb = "would rewrite" if args.check else "rewrote"
    print(f"\n{verb} {rewritten} file(s); {unchanged} already canonical; "
          f"{len(log)} content fix(es); {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
