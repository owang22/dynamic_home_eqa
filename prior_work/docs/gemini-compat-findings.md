# Gemini 3.7 Flash structured outputs — why the backend exists but is unused

Probed 2026-08-24 against `gemini-3.7-flash` through Google's
OpenAI-compatibility layer
(`https://generativelanguage.googleapis.com/v1beta/openai/`).
Total probe cost **$0.0009** — schema rejections are 400s raised before
generation, so they bill nothing; only the two accepted schemas cost.

## Verdict

**The backend works; our schemas do not fit it.** The blocker is a cap on
the TOTAL EXPANDED LEAF OBJECTS a response schema may describe, roughly
**64**. It is not a keyword-support problem and no schema transform can
work around it — only reducing repetition counts helps.

## What the probe actually found

Every JSON-Schema keyword we use is supported *in isolation*:

| keyword | result |
|---|---|
| `enum`, `const`, `anyOf`, `$ref`/`$defs` | accepted |
| `prefixItems`, `additionalProperties`, `propertyOrdering` | accepted |
| `pattern` (incl. `{2,39}` range quantifiers, anchors) | accepted |
| `minItems`/`maxItems`, `minimum`/`maximum`, `minLength`/`maxLength` | accepted |
| type arrays with `null`, optional properties | accepted |

The failure is combinatorial. Bisected boundary:

| shape | leaf objects | result |
|---|---|---|
| 3 days x 18 blocks (nested) | 54 | accepted |
| 5 days x 18 blocks (nested) | 90 | **rejected** |
| flat array, `maxItems: 50` | 50 | accepted |
| flat array, `maxItems: 100` | 100 | **rejected** |

Against what this pipeline needs:

| schema | leaf objects | over the cap |
|---|---|---|
| storyfirst month (21 days x 18 blocks) | 378 | ~6x |
| movement pass (33 objects x 8 rules) | 264 | ~4x |
| persona `object_inventory` (`maxItems: 60`) | 60 | at the edge |

Removing every enum and pattern from the 21x18 month schema still fails,
which is what proves the cap is on repetition rather than on grammar
richness.

## Two further API facts

- **`seed` is rejected outright**, not silently ignored:
  `Invalid JSON payload received. Unknown name "seed": Cannot find field.`
  Any Gemini path must strip it. `temperature` is accepted.
- **Schema rejections carry no detail** — every one returns
  `Request contains an invalid argument.` with no field named. Diagnose
  by bisection; reading the message tells you nothing.

## If Gemini is wanted later

1. **Chunk to <= 3-day story calls** (~28 calls/household instead of 4) —
   fits the cap, but discards the efficiency that motivated storyfirst.
2. **Drop structured outputs** and lean on `story_driven.repair_story` +
   the validators, as the local qwen thinking path already does — keeps
   the 4-call shape, gives up grammar enforcement.
3. **Stay on OpenAI**, where every schema is accepted.

At present (3) is chosen: storyfirst on `gpt-5.6-terra` costs ~$0.50-0.70
per household, so the whole 10-household set is ~$6-8 and Gemini would
save only ~$4 — not worth the architectural compromise. The backend, its
schema dialect, rates and the backend-agnostic probe all remain in place
so this decision can be revisited cheaply.
