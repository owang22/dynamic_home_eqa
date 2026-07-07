# Generation pipeline — where things live, and what's actually random

This covers the LLM-driven dataset generator in this package: `pipeline.py`
orchestrates five LLM stages (clutter placement → persona → activity trace →
displacement → realism judge) plus a deterministic grounding step and a
stochastic selection step. Run via `scripts/gen_dataset.py`; output lands
under `generation_out/<scene_id>_<household_type>[_v<variant>]/`.

## Object tiers

Every object belongs to one of three tiers (full rationale and vocabulary in
`env/inventory.py`'s module docstring — this is a summary, not a second
source of truth):

- **Tier 1 — static furniture** (`TIER1_FURNITURE`: table, counter, bed,
  couch, fridge, ...). Present from scene-init, real HSSD positions, never
  spawned/despawned/moved by activities. Anchors only.
- **Tier 2 — static clutter**. Present at scene-init, *moved* by activities
  but never spawned/despawned. Two sub-sources:
  - **2a** (`TIER2_HSSD_NATIVE`: chair, stool, potted_plant, cushion) — HSSD's
    `scenes-uncluttered/` variant places these with real positions, so
    they're loaded the same way Tier 1 is (`env/inventory.load_scene_state`).
    Chairs/stools are Tier 2, not Tier 1, precisely because they're still
    move-eligible (pulled out for a meal, tucked back by tidiness) —
    Tier 1's "anchor, never moved" property doesn't hold for them.
  - **2b** (`TIER2_CLUTTER_CATALOG`: book, candle, vase, bowl, cup, drinkware,
    bottle) — HSSD's uncluttered variant omits these entirely, so they have
    no ground-truth starting position. `generation/clutter/` runs a single
    LLM pass per (scene, household), before persona/activities/displacements,
    to invent one — the new Stage 0. `generation/manifest.py` merges its
    output into the same instance pool Tier 2a loads from, so a Tier 2b
    object enters the Change-log as `move_existing` from t=0, exactly like
    Tier 1/2a furniture, never as a mid-timeline `insert_new`. That was the
    actual bug this tier split fixes: an object "existing" only because a
    flat catalog assumed it, not because anything ever placed it.
- **Tier 3 — mobile objects** (`TIER3_MOBILE`: phone, wallet, keys, laptop).
  Carried items that genuinely leave and re-enter observable space (in a
  bag, a pocket, another room entirely). **Spawn/despawn mechanics are not
  implemented yet** — Tier 3 is still a flat per-scene assumed-count, and
  still enters the Change-log as `insert_new` the same way the old flat model
  did. This is an explicit, known gap, not a silent omission: closing it
  means teaching the displacement/manifest stages that a Tier 3 object can
  have no prior instance for a while (genuinely offscreen), which the
  current move_existing/insert_new binary in `manifest.py` doesn't model.

## Where to look at the generated content

Everything lives in one file per (scene, household_type, variant):
`generation_out/<scene_id>_<household_type>[_v<N>]/generation_result.json`.

**a) Clutter placements** — `clutter`, a list of Tier 2b starting positions
(see "Object tiers" above), each a `{object_category, target_relationship,
target_anchor, reason}` dict — same shape as a displacement proposal, minus
the activity/occupant/time fields (clutter is placed once, not tied to a
day's activities). Empty on the live-WorldGraph path (no anchor census wired
for it yet).

**b) Personas** — `persona.occupants`, a list of dicts, one per occupant:
```json
{"name": "Harold", "age_band": "senior", "role": "retired",
 "typical_wake": 7.0, "typical_sleep": 21.5, "tidiness": 0.7,
 "habits": "reads the newspaper from cover to cover each morning, then
            takes a walk around the neighborhood with his dog, Biscuit"}
```
`persona.household_type` and `persona.schedule_notes` describe the household
as a whole (tidiness is per-occupant, not here — see the randomness section).

**c) Household activities** — `traces`, a list parallel to `persona.occupants`,
each with an `activities` array:
```json
{"activity": "walk_with_dog", "location": "outdoor", "start": 8.5, "end": 9.5}
```
`location` is one of `ACTIVITY_LOCATIONS` (`generation/schemas.py`) — `"away"`
means genuinely outside the house (school, commute, errands).

**d) Object changes** — two places, depending on what you want:
- `displacements` in `generation_result.json` — the final *selected* subset,
  each entry carrying its own provenance: `object_category`,
  `target_relationship`, `target_anchor`, `reason` (the LLM's stated
  justification), plus `_activity`/`_occupant`/`_start`/`_end` tying it back
  to the activity that caused it. This is "John takes his backpack to
  school", in the model's own words.
- `manifest.json` in the same folder — the same displacements translated into
  the Change-log format the rest of the pipeline (`qa/questions.py`,
  `agents/harness.py`) actually consumes: `t` (a concrete hour), `label`
  (persistent instance id, e.g. `backpack_1`), `change_type`
  (`move_existing`/`insert_new`), `from_semantic`/`to_semantic` (slot
  strings). Read this one if you want "what moved, from where, to where, at
  what time" without the narrative framing.

`raw_proposals` / `grounded_proposals` / `len(displacements)` on the top-level
result give you the propose → ground → select funnel size at each stage, and
`mean_realism_score` gives the mean judge score of what was actually kept.

## What's actually random, precisely

Nothing here is "LLM temperature is on, so it's random" in an uncontrolled
sense — every generation call is given an **explicit seed**
(`llm_client._LLMClient.generate(..., seed=...)`), so the same seed + same
prompt reproduces the same output byte-for-byte (verified directly against
the real model: identical seed → identical JSON; different seed → different
JSON). All seeds derive from `household_id = f"{scene_id}_{household_type}"`
(plus `_v{variant}` — see below), so the practical source of variation is
*which seed a given call gets*, not raw nondeterminism.

**0. Clutter placement (Tier 2b, new).** LLM-generated under
`build_clutter_schema` (`generation/clutter/`), pinned to `(household_id, 0,
"clutter", 0)` the same way persona is — day-invariant by construction, since
a clutter object's home is a property of the house + household, not of any
one day. `object_category`/`target_anchor` are enum-constrained to
`TIER2_CLUTTER_CATALOG` and this scene's real furniture/room census; which
valid combination gets picked, quantities, and `reason` are LLM sampling.

Four more genuinely different mechanisms feed into that, by stage:

**1. Persona (who lives here).** Entirely LLM-generated under
`PERSONA_SCHEMA` — there is no separate rule-based sampler choosing household
composition. The `household_type` string (e.g. `"family_with_teens"`) and the
system prompt are the only steering; the model decides occupant count
(1–4, schema-bounded), ages, roles, habits, and tidiness itself, conditioned
on that one string. Structural constraints exist only where a wrong answer
was actually observed and worth ruling out by schema: `age_band` is an enum
(6 bands), `typical_wake`/`typical_sleep` are range-bounded to stop
AM/PM confusion. `habits` and `role` are free text — their variety is pure
LLM sampling given the seed.

**2. Activities (the day's schedule).** Two layers:
  - A **day-context flavor string** is picked deterministically from a fixed,
    hand-authored pool of 31 scenarios (`_DAY_SCENARIOS` in `stages.py`, e.g.
    `"Sick day."`, `"Deadline crunch day."`, each with a longer description)
    via `seed % len(_DAY_SCENARIOS)`. This is the one place with a literal
    pre-written list — closer to what you'd call a "ruleset" than anything
    else in the pipeline. Each entry is tagged `weekday`/`weekend`/`flex` so
    the model knows whether school/work absence applies.
  - The **actual trace** (activity labels, `location`, `start`/`end`) is then
    LLM-generated under `ACTIVITY_SCHEMA`, conditioned on the persona +
    day-context text. `location` is enum-constrained (9 values); activity
    labels and exact timing are free LLM sampling. A deterministic Python
    pass (`_repair_activity_trace`) clips any overlapping windows the model
    produces despite being told not to — not random, just cleanup.

**3. Object changes (displacements) — four sub-stages, three different
   randomness sources:**
  - **Propose** (LLM, `generate_displacements`): samples a pool of candidate
    displacements, deliberately over-generating (more candidates than would
    plausibly all happen). `object_category` and `target_anchor` are
    enum-constrained to this scene's real inventory/furniture census — the
    model can't hallucinate a category, but which of the valid ones it picks,
    and its stated `reason`, are LLM sampling.
  - **Ground** (deterministic, `grounding.py`): checks each candidate against
    real per-scene data (does this furniture exist, does this room exist).
    Zero randomness — a candidate either matches the scene or it doesn't.
  - **Score** (LLM, `score_realism_batch`): a *separate* LLM call judges each
    grounded candidate's behavioral plausibility in [0, 1], independent of
    whether it's physically placeable. LLM sampling again, on a different
    seed than the proposal call.
  - **Select** (`generation/selection.py`, **not** an LLM call): a seeded
    `numpy` RNG draws a Poisson-distributed count around a per-activity mean
    (`lambda_moves_for`), then samples that many candidates *without
    replacement*, weighted by realism score (softmax, not top-k) — so a
    high-scoring candidate is more likely but not guaranteed to be picked,
    and a low scorer isn't impossible either. This is genuine
    algorithmic randomness (seeded, reproducible), not an LLM authoring a
    score with noise on top — the LLM only supplies the score; the sampling
    decision is separate, deterministic-given-seed code.

**4. The `variant` knob (new).** `generate_for_scene(..., variant=N)` folds
`_v{N}` into `household_id` when `N != 0`. Because *every* stage's seed
derives from `household_id`, bumping variant changes the persona seed **and**
the activity, displacement, and realism seeds together — verified directly:
three variants of `single_retiree` on the same scene produced three
genuinely different people (Harold/Eleanor/Marjorie), different habits,
different-length schedules (16 vs. 21 vs. 21 activities), and different
displacement sets (44 vs. 33 vs. 31 selected, different objects/reasons) —
not just a name swap with the same day underneath. `run_batch(...,
n_variants=k)` / `scripts/gen_dataset.py --n-variants k` generates k such
variants per scene automatically. This is the "k examples of personas" knob:
a different household for the same house, not a different day of the same
household (`day` still exists separately for that).

## Reproducibility

Every LLM call's raw response is cached to disk (`--cache-dir`, keyed by
seed) — rerun without `--force` and you get the identical result, not a fresh
draw. `--force` bypasses the cache but, per the seeding above, still
reproduces the same output for the same `(household_id, day, variant)` unless
you also change the model, temperature, or a prompt. Malformed-JSON retries
(rare, guided decoding) are logged via Python's `logging` module with the
full raw output and are resampled with a distinct seed per attempt
(`llm_client.generate_json`) — check logs for `guided-JSON failure` if a
batch run behaves unexpectedly.

## Trace integrity

Every exported day's Change-log must satisfy four hard invariants — chain
consistency, insert-once, no no-ops, and attendance — enforced by
`manifest.py` at generation time and independently re-checked by
`trace_validate.validate()` (pure, no I/O beyond `rooms.py`, the shared
room-vocabulary module both sides import). `run_batch(..., validate_trace=True)`
— the default — runs this as a post-generation gate: a manifest that fails
any hard invariant is treated as a generation failure for that (scene,
variant) and skipped, not written to disk. Pass `--no-validate-trace` to
`scripts/gen_dataset.py` to disable this (e.g. rebuilding manifests from
older `generation_result.json` data for before/after comparison, where
violations are expected).

- **Chain consistency**: `from_semantic` always comes from the pipeline's
  own tracked scene state, never from_semantic == to_semantic, and never
  taken from the LLM's own belief about prior state (see `assumed_from`
  below). A label's true first event has `from_semantic: null`.
- **Insert-once**: `insert_new` fires at most once per label — only for
  volatile (Tier 3) labels with no real starting instance. Real-instance-
  backed labels (Tier 1/2) are always `move_existing`, including their
  first event, and are tracked one real instance per category per day
  (`generation/manifest.py`'s module docstring explains why (category,
  occupant)-scoped assignment was the actual cause of chain breaks).
- **No no-ops**: a proposal whose resolved `to_semantic` equals the label's
  current `from_semantic` is dropped, not exported, and counted
  (`manifest.json`'s `integrity_stats.dropped_noop`).
- **Attendance**: every exported event is attributed to a `mover` — an
  occupant independently confirmed present (via the day's activity traces)
  in the event's source or destination room at event time. This is mostly a
  formality once generation room-scopes each displacement's anchor
  vocabulary to the acting occupant's current `activity.location`
  (`generate_displacements`'s `location` parameter) — the check is
  defense-in-depth against that upstream guarantee ever failing (e.g. the
  room-scoping fallback firing when a scene has no real anchors for a given
  room). Non-attributable proposals are dropped and counted
  (`integrity_stats.rejected_unattended`).

`assumed_from` is a diagnostic-only field: the displacement schema asks the
model to state where it believes the object currently is, before the move.
This is never used to write `from_semantic` — it's preserved verbatim as
`llm_claimed_from` on the exported event, and a divergence counter
(`integrity_stats.llm_claim_divergence`) tracks how often it disagrees with
the real tracked state, as a signal of model/prompt confusion, not something
acted on.

`confidence` (per event) is genuine per-event behavioral-plausibility
scoring (`plausibility.py`), not a placeholder constant — occupant-
capability (e.g. a toddler moving a laptop), egress (furniture heading
outdoors), and ping-pong (the same object bouncing between slots too often)
penalties, multiplied together. `plausibility.day_report()` re-derives the
same three checks as a whole-day warning report, independent of what
confidence values were actually written — a soft/advisory counterpart to
`trace_validate`'s hard gate, not something that rejects a proposal.

**Exports**: alongside `generation_result.json` and `manifest.json`,
`run_batch` writes `replay.json` (`generation/exports.py`) — a compact
replay-viewer format (`meta`, `occupants` as `[activity, room, start, end]`
tuples, `changes` as `[t, label, type, from, to, reason, mover]` tuples) plus
`category_stats` (per-category location-change count, distinct slots
visited, mean dwell time) — the input future hazard-rate calibration work
consumes, computed from real location-changes only (no-ops are already
excluded by construction).

**Geometry-faithful rendering** (`scripts/render_topdown.py`, `topdown_map.py`):
a top-down animation of a generated day over the scene's real navmesh —
object markers by category, occupant markers at room centroids from the
activity trace, a clock, and move-flash highlights — plus an anchor-sanity
check (`check_anchor_sanity`) that every `SLOT_ANCHORS` position this scene
resolves lands on or near navigable space. Requires `habitat_sim`, which
isn't installed in this repo's default LLM-generation environment — run it
from a conda env that has it (e.g. `explore-eqa`/`fine-eqa` on this
machine). No GPU rendering is needed to build the map itself (sensorless,
renderer-less `Simulator` config — navmesh/pathfinder only).
