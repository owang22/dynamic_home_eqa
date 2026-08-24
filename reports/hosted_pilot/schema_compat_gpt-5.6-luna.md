# Hosted schema compatibility (Task 2 probe)

Model: `gpt-5.6-luna` — one strict-mode call per schema against `https://api.openai.com`, trivial prompt, `max_completion_tokens=64`. Acceptance is judged by the API's up-front schema validation (a 400 names the offending keyword verbatim below); rejected schemas are re-probed after `to_hosted_schema()`.

| schema | raw: accepted | transformed: accepted | props | enums (total values / max) | depth | chars raw -> hosted |
|---|---|---|---|---|---|---|
| persona | NO | yes | 19 | 3 (44 / 35) | 7 | 2025 -> 2061 |
| l2_calendar | NO | yes | 70 | 22 (481 / 46) | 8 | 11325 -> 11347 |
| l2_objects | NO | yes | 431 | 132 (3795 / 35) | 12 | 90180 -> 74386 |
| l2_special_events | NO | yes | 22 | 8 (176 / 46) | 16 | 4366 -> 4393 |
| story_day | yes | (not needed) | 9 | 3 (77 / 46) | 9 | 1824 -> 1824 |
| bind_pass | NO | yes | 299 | 132 (2508 / 34) | 12 | 62763 -> 56764 |
| leak_audit | yes | (not needed) | 3 | 1 (10 / 10) | 3 | 505 -> 505 |

## Rejections, verbatim

### persona (raw)

```
hosted API 400: {
  "error": {
    "message": "Invalid schema for response_format 'probe': In context=('properties', 'household_id'), schema must have a 'type' key.",
    "type": "invalid_request_error",
    "param": "response_format",
    "code": null
  }
}
```

### l2_calendar (raw)

```
hosted API 400: {
  "error": {
    "message": "Invalid schema for response_format 'probe': In context=('properties', 'household'), schema must have a 'type' key.",
    "type": "invalid_request_error",
    "param": "response_format",
    "code": null
  }
}
```

### l2_objects (raw)

```
hosted API 400: {
  "error": {
    "message": "Invalid schema for response_format 'probe': In context=('properties', 'object_rules', 'prefixItems', '0', 'properties', 'object'), schema must have a 'type' key.",
    "type": "invalid_request_error",
    "param": "response_format",
    "code": null
  }
}
```

### l2_special_events (raw)

```
hosted API 400: {
  "error": {
    "message": "Invalid schema for response_format 'probe': In context=('properties', 'special_events', 'items', 'properties', 'patch', 'properties', 'add', 'items'), 'required' is required to be supplied and to be an array including every key in properties. Missing 'end'.",
    "type": "invalid_request_error",
    "param": "response_format",
    "code": null
  }
}
```

### bind_pass (raw)

```
hosted API 400: {
  "error": {
    "message": "Invalid schema for response_format 'probe': In context=('properties', 'bindings', 'prefixItems', '0', 'properties', 'rules', 'items', 'properties', 'phase'), schema must have a 'type' key.",
    "type": "invalid_request_error",
    "param": "response_format",
    "code": null
  }
}
```

## Transform removals and their covering checks

- **persona**:
  - `const+=type` at /household_id, /household_type
    - covered by: purely ADDITIVE (strict mode wants a type key beside every const; the inferred type is the const value's own) — nothing removed, nothing to re-check
- **l2_calendar**:
  - `const+=type` at /household, /source_persona, /days, … (20 sites)
    - covered by: purely ADDITIVE (strict mode wants a type key beside every const; the inferred type is the const value's own) — nothing removed, nothing to re-check
  - `items=false` at /residents, /sleep_schedule
    - covered by: same as prefixItems (the two encode one shape)
  - `optional->required+nullable` at /residents/prefixItems[0]/cites, /residents/prefixItems[1]/cites, /residents/prefixItems[2]/cites, … (20 sites)
    - covered by: mechanically inverted by hosted_schema.drop_nulls before the original-schema re-validation in llm_client._hosted_check — null never reaches a validator or an artifact
  - `enum-dedup->$defs` at <root> (4 enums, 36 sites)
    - covered by: semantically IDENTICAL rewrite (repeated enum bodies hoisted behind $ref to fit the probed 1000-enum-value cap) — nothing widened, nothing to re-check
- **l2_objects**:
  - `items=false` at /object_rules
    - covered by: same as prefixItems (the two encode one shape)
  - `const+=type` at /object_rules/prefixItems[0]/object, /object_rules/prefixItems[0]/rules/items/phase, /object_rules/prefixItems[1]/object, … (132 sites)
    - covered by: purely ADDITIVE (strict mode wants a type key beside every const; the inferred type is the const value's own) — nothing removed, nothing to re-check
  - `optional->required+nullable` at /object_rules/prefixItems[0]/rules/items/only_from, /object_rules/prefixItems[0]/rules/items/seq, /object_rules/prefixItems[0]/p_misplace, … (198 sites)
    - covered by: mechanically inverted by hosted_schema.drop_nulls before the original-schema re-validation in llm_client._hosted_check — null never reaches a validator or an artifact
  - `enum-dedup->$defs` at <root> (3 enums, 264 sites)
    - covered by: semantically IDENTICAL rewrite (repeated enum bodies hoisted behind $ref to fit the probed 1000-enum-value cap) — nothing widened, nothing to re-check
- **l2_special_events**:
  - `optional->required+nullable` at /special_events/items/patch/add/items/end, /special_events/items/patch/add/items/note, /special_events/items/patch/drop, … (5 sites)
    - covered by: mechanically inverted by hosted_schema.drop_nulls before the original-schema re-validation in llm_client._hosted_check — null never reaches a validator or an artifact
  - `enum-dedup->$defs` at <root> (1 enums, 2 sites)
    - covered by: semantically IDENTICAL rewrite (repeated enum bodies hoisted behind $ref to fit the probed 1000-enum-value cap) — nothing widened, nothing to re-check
- **story_day**: no removals (already inside the strict subset)
- **bind_pass**:
  - `items=false` at /bindings
    - covered by: same as prefixItems (the two encode one shape)
  - `const+=type` at /bindings/prefixItems[0]/rules/items/phase, /bindings/prefixItems[1]/rules/items/phase, /bindings/prefixItems[2]/rules/items/phase, … (66 sites)
    - covered by: purely ADDITIVE (strict mode wants a type key beside every const; the inferred type is the const value's own) — nothing removed, nothing to re-check
  - `optional->required+nullable` at /bindings/prefixItems[0]/rules/items/only_from, /bindings/prefixItems[1]/rules/items/only_from, /bindings/prefixItems[2]/rules/items/only_from, … (66 sites)
    - covered by: mechanically inverted by hosted_schema.drop_nulls before the original-schema re-validation in llm_client._hosted_check — null never reaches a validator or an artifact
  - `enum-dedup->$defs` at <root> (36 enums, 264 sites)
    - covered by: semantically IDENTICAL rewrite (repeated enum bodies hoisted behind $ref to fit the probed 1000-enum-value cap) — nothing widened, nothing to re-check
- **leak_audit**: no removals (already inside the strict subset)

## Behavior probes

- `temperature=0.7 alongside strict outputs`: accepted
- `seed alongside strict outputs`: accepted

Spend after probe: see the ledger (`HOSTED_SPEND_LEDGER`).
