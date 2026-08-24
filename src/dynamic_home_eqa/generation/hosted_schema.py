"""Mechanical JSON-Schema transform for OpenAI hosted strict structured
outputs (the Task-2 `to_hosted_schema()` of the hosted-generation pilot).

OpenAI strict mode enforces a different subset than the xgrammar backend
the vLLM path uses. The two known-structural requirements:

  - every object must set `additionalProperties: false` (ours already do)
    and list EVERY property in `required`;
  - a property that was optional therefore becomes required-but-NULLABLE,
    and the model signals "absent" by emitting null.

Everything else is keyword removal, driven by probing the live API
(src/revamp_v2/probe_hosted_schemas.py), never by a remembered keyword
list. The transform is purely mechanical: it never changes what a
compliant instance MEANS, it only widens what the grammar admits — every
constraint it drops is re-checked downstream against the ORIGINAL schema
(llm_client re-validates hosted responses with jsonschema before any
caller sees them), so a removed keyword can burn a retry but never leak a
bad artifact.

`drop_nulls()` is the instance-side inverse: the original schemas admit
null nowhere, so every null in a hosted response is an "absent optional"
marker and is stripped before original-schema validation.
"""
from __future__ import annotations

import copy
import json
from typing import Any

# Keywords OpenAI strict mode rejects, to be CONFIRMED (and extended if
# the probe finds more) by probe_hosted_schemas.py — seeded with the ones
# that are documented as unsupported, not trusted from memory.
UNSUPPORTED_KEYWORDS = frozenset({
    "uniqueItems", "contains", "minContains", "maxContains",
    "dependentRequired", "dependentSchemas", "if", "then", "else",
    "not", "oneOf", "allOf", "patternProperties", "propertyNames",
    "unevaluatedProperties", "unevaluatedItems", "default",
})


def _nullable(sub: dict) -> dict:
    """Widen `sub` so null is a valid instance (the strict-mode encoding
    of an optional property). Idempotent."""
    sub = dict(sub)
    if "$ref" in sub:
        return {"anyOf": [sub, {"type": "null"}]}
    if "type" in sub:
        t = sub["type"]
        types = t if isinstance(t, list) else [t]
        if "null" not in types:
            sub["type"] = types + ["null"]
    elif "enum" in sub:
        if None not in sub["enum"]:
            sub["enum"] = list(sub["enum"]) + [None]
    elif "const" in sub:
        value = sub.pop("const")
        sub["enum"] = [value, None]
    elif "anyOf" in sub:
        if {"type": "null"} not in sub["anyOf"]:
            sub["anyOf"] = list(sub["anyOf"]) + [{"type": "null"}]
    else:
        sub["type"] = ["null"]
    return sub


_JSON_TYPE = {str: "string", bool: "boolean", int: "integer",
              float: "number", list: "array", dict: "object",
              type(None): "null"}


def _typed_const(sub: dict, path: str, removals: list) -> dict:
    """Strict mode requires every subschema to carry a `type` key (probed
    2026-08-23: bare `{"const": ...}` is rejected with "schema must have a
    'type' key"; bare `enum` is accepted). Purely additive — the inferred
    type is exactly the const value's own."""
    if "const" in sub and "type" not in sub:
        t = _JSON_TYPE.get(type(sub["const"]))
        if t is not None:
            sub = {"type": t, **sub}
            removals.append(f"{path}: const+=type")
    return sub


def to_hosted_schema(schema: dict,
                     extra_remove: frozenset = frozenset()
                     ) -> tuple[dict, list[str]]:
    """(hosted_schema, removals). Removals are human-readable
    "path: keyword" strings for the compat report. Idempotent: applying
    the transform to its own output changes nothing and reports no new
    removals beyond re-noting nothing."""
    remove = UNSUPPORTED_KEYWORDS | extra_remove
    removals: list[str] = []
    nullable_paths: list[str] = []

    def walk(node: Any, path: str) -> Any:
        if isinstance(node, list):
            return [walk(x, f"{path}[{i}]") for i, x in enumerate(node)]
        if not isinstance(node, dict):
            return node
        out: dict = {}
        for k, v in node.items():
            # prefixItems is handled by its own conversion branch below,
            # never by plain deletion.
            if k in remove and k != "prefixItems":
                removals.append(f"{path or '<root>'}: {k}")
                continue
            out[k] = v
        out = _typed_const(out, path or "<root>", removals)
        # prefixItems (the slot-pinning shape): KEPT by default — the
        # probe showed OpenAI's schema validator recursing into it, and
        # keeping it preserves the one-entry-per-id guarantee that killed
        # the drop-an-object failure mode. If the API rejects it after
        # all, pass extra_remove={"prefixItems"} (the probe tries this
        # variant automatically): mechanical widening to one plain
        # `items` anyOf of the distinct slot schemas, with the lost
        # pinning re-checked by original-schema validation downstream.
        if "prefixItems" in out:
            prefix = out["prefixItems"]
            distinct: list = []
            seen: set = set()
            for sub in prefix:
                key = json.dumps(sub, sort_keys=True)
                if key not in seen:
                    seen.add(key)
                    distinct.append(sub)
            union = distinct[0] if len(distinct) == 1 \
                else {"anyOf": distinct}
            if out.get("items") is False:
                # `items: false` is rejected outright ("array schema
                # items is not an object"), and an items-less array is
                # rejected too ("array schema missing items") — probed.
                # The union of the slot schemas stands in; with
                # minItems == maxItems == len(prefixItems) it applies to
                # no position, and the original-schema re-check still
                # enforces items:false downstream.
                removals.append(f"{path or '<root>'}: items=false")
            if "prefixItems" in remove:
                out.pop("prefixItems")
                removals.append(f"{path or '<root>'}: prefixItems")
                out["items"] = union
            else:
                # Keep the slot-pinning; the union rides along as the
                # `items` schema the API insists on.
                out["prefixItems"] = [
                    walk(s, f"{path}/prefixItems[{i}]")
                    for i, s in enumerate(prefix)]
                out["items"] = copy.deepcopy(union)
        # Recurse into schema-valued members.
        for k in ("items", "additionalProperties"):
            if isinstance(out.get(k), (dict, list)):
                out[k] = walk(out[k], f"{path}/{k}")
        if isinstance(out.get("anyOf"), list):
            out["anyOf"] = walk(out["anyOf"], f"{path}/anyOf")
        if isinstance(out.get("$defs"), dict):
            out["$defs"] = {k: walk(v, f"{path}/$defs/{k}")
                            for k, v in out["$defs"].items()}
        if isinstance(out.get("properties"), dict):
            props = {k: walk(v, f"{path}/{k}")
                     for k, v in out["properties"].items()}
            required = list(out.get("required") or [])
            for name in props:
                if name not in required:
                    props[name] = _nullable(props[name])
                    required.append(name)
                    nullable_paths.append(f"{path}/{name}")
            out["properties"] = props
            out["required"] = required
            out["additionalProperties"] = False
        return out

    hosted = walk(copy.deepcopy(schema), "")
    for p in nullable_paths:
        removals.append(f"{p}: optional->required+nullable")
    hosted = _dedup_enums(hosted, removals)
    return hosted, removals


def _dedup_enums(hosted: dict, removals: list) -> dict:
    """Hoist REPEATED identical enum-bearing subschemas into $defs/$ref.

    Strict mode caps a schema at 1000 enum values IN TOTAL (probed: the
    objects schema counted 1035 because the same location/activity enums
    repeat once per object slot). A $ref'd definition carries its values
    once, and the substitution is semantically identical — nothing is
    widened, so nothing needs a downstream re-check. Idempotent: after
    hoisting, every enum body exists exactly once (in $defs), so a second
    pass finds no duplicates."""
    counts: dict[str, int] = {}

    def scan(node):
        if isinstance(node, dict):
            if "enum" in node:
                key = json.dumps(node, sort_keys=True)
                counts[key] = counts.get(key, 0) + 1
            for v in node.values():
                scan(v)
        elif isinstance(node, list):
            for v in node:
                scan(v)

    scan(hosted)
    dups = [k for k, c in counts.items() if c > 1]
    if not dups:
        return hosted
    names = {k: f"enum_{i}" for i, k in enumerate(dups)}

    def substitute(node):
        if isinstance(node, dict):
            if "enum" in node:
                key = json.dumps(node, sort_keys=True)
                if key in names:
                    return {"$ref": f"#/$defs/{names[key]}"}
            return {k: substitute(v) for k, v in node.items()}
        if isinstance(node, list):
            return [substitute(v) for v in node]
        return node

    out = substitute(hosted)
    defs = dict(out.pop("$defs", None) or {})
    defs.update({names[k]: json.loads(k) for k in dups})
    out["$defs"] = defs
    n_sites = sum(counts[k] for k in dups)
    removals.append(f"<root> ({len(dups)} enums, {n_sites} sites): "
                    f"enum-dedup->$defs")
    return out


def drop_nulls(instance: Any) -> Any:
    """Strip null-valued object members recursively. The original schemas
    admit null nowhere, so a null in a hosted response can only be the
    strict-mode encoding of an absent optional property."""
    if isinstance(instance, dict):
        return {k: drop_nulls(v) for k, v in instance.items()
                if v is not None}
    if isinstance(instance, list):
        return [drop_nulls(x) for x in instance]
    return instance
