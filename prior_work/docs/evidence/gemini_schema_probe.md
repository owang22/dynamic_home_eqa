# Hosted schema compatibility (Task 2 probe)

Model: `gemini-3.7-flash` — one strict-mode call per schema against `https://api.openai.com`, trivial prompt, `max_completion_tokens=64`. Acceptance is judged by the API's up-front schema validation (a 400 names the offending keyword verbatim below); rejected schemas are re-probed after `to_hosted_schema()`.

| schema | raw: accepted | transformed: accepted | props | enums (total values / max) | depth | chars raw -> hosted |
|---|---|---|---|---|---|---|
| persona | NO | NO; no-prefixItems: NO | 19 | 3 (44 / 35) | 7 | 2025 -> 1970 |
| l2_calendar | NO | NO; no-prefixItems: NO | 70 | 22 (481 / 46) | 8 | 11325 -> 11129 |
| l2_objects | NO | NO; no-prefixItems: NO | 431 | 132 (3795 / 35) | 12 | 90180 -> 88323 |
| l2_special_events | NO | NO; no-prefixItems: NO | 22 | 8 (176 / 46) | 16 | 4366 -> 4149 |
| story_day | NO | NO; no-prefixItems: NO | 9 | 3 (77 / 46) | 9 | 1824 -> 1731 |
| bind_pass | NO | NO; no-prefixItems: NO | 299 | 132 (2508 / 34) | 12 | 62763 -> 60279 |
| leak_audit | yes | (not needed) | 3 | 1 (10 / 10) | 3 | 505 -> 474 |

## Rejections, verbatim

### persona (raw)

```
hosted API 400: [{
  "error": {
    "code": 400,
    "message": "Request contains an invalid argument.",
    "status": "INVALID_ARGUMENT"
  }
}
]
```

### persona (hosted)

```
hosted API 400: [{
  "error": {
    "code": 400,
    "message": "Request contains an invalid argument.",
    "status": "INVALID_ARGUMENT"
  }
}
]
```

### persona (hosted_noprefix)

```
hosted API 400: [{
  "error": {
    "code": 400,
    "message": "Request contains an invalid argument.",
    "status": "INVALID_ARGUMENT"
  }
}
]
```

### l2_calendar (raw)

```
hosted API 400: [{
  "error": {
    "code": 400,
    "message": "Request contains an invalid argument.",
    "status": "INVALID_ARGUMENT"
  }
}
]
```

### l2_calendar (hosted)

```
hosted API 400: [{
  "error": {
    "code": 400,
    "message": "Request contains an invalid argument.",
    "status": "INVALID_ARGUMENT"
  }
}
]
```

### l2_calendar (hosted_noprefix)

```
hosted API 400: [{
  "error": {
    "code": 400,
    "message": "Request contains an invalid argument.",
    "status": "INVALID_ARGUMENT"
  }
}
]
```

### l2_objects (raw)

```
hosted API 400: [{
  "error": {
    "code": 400,
    "message": "Request contains an invalid argument.",
    "status": "INVALID_ARGUMENT"
  }
}
]
```

### l2_objects (hosted)

```
hosted API 400: [{
  "error": {
    "code": 400,
    "message": "Request contains an invalid argument.",
    "status": "INVALID_ARGUMENT"
  }
}
]
```

### l2_objects (hosted_noprefix)

```
hosted API 400: [{
  "error": {
    "code": 400,
    "message": "Request contains an invalid argument.",
    "status": "INVALID_ARGUMENT"
  }
}
]
```

### l2_special_events (raw)

```
hosted API 400: [{
  "error": {
    "code": 400,
    "message": "Request contains an invalid argument.",
    "status": "INVALID_ARGUMENT"
  }
}
]
```

### l2_special_events (hosted)

```
hosted API 400: [{
  "error": {
    "code": 400,
    "message": "Request contains an invalid argument.",
    "status": "INVALID_ARGUMENT"
  }
}
]
```

### l2_special_events (hosted_noprefix)

```
hosted API 400: [{
  "error": {
    "code": 400,
    "message": "Request contains an invalid argument.",
    "status": "INVALID_ARGUMENT"
  }
}
]
```

### story_day (raw)

```
hosted API 400: [{
  "error": {
    "code": 400,
    "message": "Request contains an invalid argument.",
    "status": "INVALID_ARGUMENT"
  }
}
]
```

### story_day (hosted)

```
hosted API 400: [{
  "error": {
    "code": 400,
    "message": "Request contains an invalid argument.",
    "status": "INVALID_ARGUMENT"
  }
}
]
```

### story_day (hosted_noprefix)

```
hosted API 400: [{
  "error": {
    "code": 400,
    "message": "Request contains an invalid argument.",
    "status": "INVALID_ARGUMENT"
  }
}
]
```

### bind_pass (raw)

```
hosted API 400: [{
  "error": {
    "code": 400,
    "message": "Request contains an invalid argument.",
    "status": "INVALID_ARGUMENT"
  }
}
]
```

### bind_pass (hosted)

```
hosted API 400: [{
  "error": {
    "code": 400,
    "message": "Request contains an invalid argument.",
    "status": "INVALID_ARGUMENT"
  }
}
]
```

### bind_pass (hosted_noprefix)

```
hosted API 400: [{
  "error": {
    "code": 400,
    "message": "Request contains an invalid argument.",
    "status": "INVALID_ARGUMENT"
  }
}
]
```

## Transform removals and their covering checks

- **persona**:
  - `additionalProperties` at <root>, /residents/items, /object_inventory/items
    - covered by: the Gemini subset has no additionalProperties; unknown keys are rejected downstream by the original-schema re-validation in _hosted_check
  - `const->enum` at /household_id, /household_type
    - covered by: a single-value enum says exactly what `const` said (the Gemini subset has no const) — semantically identical, nothing to re-check
- **l2_calendar**:
  - `additionalProperties` at <root>, /residents/items/anyOf[0], /residents/items/anyOf[1], … (13 sites)
    - covered by: the Gemini subset has no additionalProperties; unknown keys are rejected downstream by the original-schema re-validation in _hosted_check
  - `const->enum` at /household, /source_persona, /days, … (12 sites)
    - covered by: a single-value enum says exactly what `const` said (the Gemini subset has no const) — semantically identical, nothing to re-check
  - `items=false` at /residents, /sleep_schedule
    - covered by: same as prefixItems (the two encode one shape)
  - `prefixItems` at /residents, /sleep_schedule
    - covered by: llm_client._hosted_check re-validates EVERY hosted response against the original schema (jsonschema, prefixItems included) before any caller sees it; for L2 additionally validate.py check_schema (original schema) and check_referential's one-entry-per-inventory-object assertion
- **l2_objects**:
  - `additionalProperties` at <root>, /object_rules/items/anyOf[0], /object_rules/items/anyOf[0]/rules/items, … (100 sites)
    - covered by: the Gemini subset has no additionalProperties; unknown keys are rejected downstream by the original-schema re-validation in _hosted_check
  - `items=false` at /object_rules
    - covered by: same as prefixItems (the two encode one shape)
  - `prefixItems` at /object_rules
    - covered by: llm_client._hosted_check re-validates EVERY hosted response against the original schema (jsonschema, prefixItems included) before any caller sees it; for L2 additionally validate.py check_schema (original schema) and check_referential's one-entry-per-inventory-object assertion
  - `const->enum` at /object_rules/items/anyOf[0]/object, /object_rules/items/anyOf[0]/rules/items/phase, /object_rules/items/anyOf[1]/object, … (66 sites)
    - covered by: a single-value enum says exactly what `const` said (the Gemini subset has no const) — semantically identical, nothing to re-check
- **l2_special_events**:
  - `additionalProperties` at <root>, /special_events/items, /special_events/items/patch, … (7 sites)
    - covered by: the Gemini subset has no additionalProperties; unknown keys are rejected downstream by the original-schema re-validation in _hosted_check
- **story_day**:
  - `additionalProperties` at <root>, /days/items, /days/items/blocks/items
    - covered by: the Gemini subset has no additionalProperties; unknown keys are rejected downstream by the original-schema re-validation in _hosted_check
- **bind_pass**:
  - `additionalProperties` at <root>, /bindings/items/anyOf[0], /bindings/items/anyOf[0]/rules/items, … (100 sites)
    - covered by: the Gemini subset has no additionalProperties; unknown keys are rejected downstream by the original-schema re-validation in _hosted_check
  - `items=false` at /bindings
    - covered by: same as prefixItems (the two encode one shape)
  - `prefixItems` at /bindings
    - covered by: llm_client._hosted_check re-validates EVERY hosted response against the original schema (jsonschema, prefixItems included) before any caller sees it; for L2 additionally validate.py check_schema (original schema) and check_referential's one-entry-per-inventory-object assertion
  - `const->enum` at /bindings/items/anyOf[0]/rules/items/phase, /bindings/items/anyOf[1]/rules/items/phase, /bindings/items/anyOf[2]/rules/items/phase, … (33 sites)
    - covered by: a single-value enum says exactly what `const` said (the Gemini subset has no const) — semantically identical, nothing to re-check
- **leak_audit**:
  - `additionalProperties` at <root>
    - covered by: the Gemini subset has no additionalProperties; unknown keys are rejected downstream by the original-schema re-validation in _hosted_check

## Behavior probes

- `temperature=0.7 alongside strict outputs`: accepted
- `seed alongside strict outputs`: REJECTED: hosted API 400: [{
  "error": {
    "code": 400,
    "message": "Invalid JSON payload received. Unknown name \"seed\": Cannot find field.",
    "status": "INVALID_ARGUMENT",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.BadRequest",
        "fieldViolations": [
          {
            "description": "Invalid JSON payload received. Unknown name \"seed\": Cannot find fiel

Spend after probe: see the ledger (`HOSTED_SPEND_LEDGER`).
