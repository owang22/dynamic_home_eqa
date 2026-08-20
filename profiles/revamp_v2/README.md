# revamp_v2 — programmatic household generation (third generation)

One LLM boundary, everything else deterministic. The LLM authors a compact,
schema-validated **routine program** once per household; a seeded simulator
realizes it. There is no LLM judge anywhere: the correctness properties the
legacy judge policed per-event are impossible by construction when events
are emitted by a simulator from a validated program.

**Code lives in `src/revamp_v2/`** — `prompts.py` (the prompt registry:
every LLM-facing string, content-hash versioned), `schemas.py` (the
guided-JSON contracts), `expand_calendar.py`, `simulate.py`,
`validate.py`, `generate.py`, `realism_panel.py`,
`make_viewer_configs.py`, `realization_params.yaml`, `build.sh` (kept separate from the legacy
`src/dynamic_home_eqa/` generation package and from `profiles/revamp_v1/`,
both of which it reuses read-only). This directory holds only data:
`control.yaml` (the 10 household slots, copied from revamp_v1) and one
`<model_slug>/hh<N>/` folder per generated household.

## Layers

```
L0 scene       (no LLM)  receptacle list (id, room): synthetic template
                         scaled by control.yaml `bedrooms`, or --scene
                         <hssd_id> via data/anchor_census/
L1 persona     (LLM x1)  revamp_v1 persona prompt, guided JSON, written in
                         normalize_profiles.py canonical style
L2 program     (LLM x1)  routine_program.yaml: weekly_blocks + placements +
                         activity bindings + 4-8 dated arc_events
L3 realization (no LLM)  src/revamp_v2/simulate.py -> events.jsonl,
                         hourly.csv, residents.jsonl, meta.json
L4 projection  (no LLM)  python -m baselines.export_bank (unchanged);
                         visualization/spatialize.py + viewer (unchanged)
```

## Files per household (`<model_slug>/hh<N>/`)

- `persona.yaml` — WHO lives here; canonical revamp_v1 style.
- `routine_program.yaml` — the whole program: `residents` (jitter_scale),
  `receptacles` (echoed from L0), **`sleep_schedule`** (one entry per
  resident), `weekly_blocks` (the rest of each week: resident, activity,
  days Mo-Su, start/end "HH:MM"[+1], at, jitter class, skip_p, sleep,
  cites), **`object_rules`** (one entry per object carrying its `home`,
  optional `p_misplace` drift, and the rules that move it — each naming an
  activity, a phase and a destination), `activities` (per-activity extras:
  reset_all, fragment), `arc_events` (dated patches: drop / add /
  after_override).

  `sleep_schedule` and `object_rules` are both there for one reason: they
  are the two enumerations the generator kept dropping items from, and a
  fixed-length array indexed by the thing being enumerated (one entry per
  resident, one per object) makes an omission unrepresentable rather than
  something a validator has to catch. `sleep_schedule` alone removed
  "residents with no sleep block", the dominant failure for every
  multi-resident household.

  `object_rules` is keyed BY OBJECT rather than by activity, and that is
  the single most important design decision in the schema. Authored by
  activity, the generator reliably forgot one or two objects per program —
  which the reachability gate then rejected, five attempts running, with
  no prompt wording able to fix it. Keyed by object, the array carries
  exactly one entry per inventory item, so "every object that moves has a
  rule" cannot be violated; an object that never moves says so with
  `rules: []`, and there is no separate static flag to contradict. The
  same household went from 0/5 attempts passing to clean on the first.
  The simulator wants the transpose, and `expand_calendar.pivot_object_rules`
  is it — rules carry an optional `seq` so a translated revamp_v1 program
  keeps that world's per-activity rule order (which the RNG depends on).
- `build_log.json` — full provenance: model, prompt content-hashes,
  builder version, per-attempt seeds and failure reasons, leak-audit
  prediction. Programs are NEVER hand-edited; failures mean fix the
  prompt/schema and regenerate.
- `timeline_seed<K>/` — the standard timeline artifacts (same formats as
  revamp_v1, so export_bank / spatialize / the topdown viewer work as-is).

## Semantics in one paragraph

`weekly_blocks` + `arc_events` expand deterministically
(`expand_calendar.py`) into the dated calendar the revamp_v1 simulator
consumes; a block runs until the same resident's next block, and an
authored `end` is honoured by a synthesized `linger_<receptacle>` gap
block (empty rules) so `after` rules fire at the authored end. Realization
adds per-day skip (before jitter) and Poisson bout fragmentation, each on
its own seeded stream — a program using neither reproduces the v1 pipeline
byte-for-byte (the hh1 regression fixture in tests/ proves it). All
numeric knobs live in `src/revamp_v2/realization_params.yaml`, with
calibration sources cited per value.

## The five named checks (and only these)

1. **schema** — guided-JSON schema, re-checked with jsonschema.
2. **referential** — ids exist; placements ≡ persona inventory exactly;
   and the program cannot contradict what its own names mean (a sleep
   block is never skipped and never carries a tidy walk; every resident
   has one; a `p` branch has an `else`).
3. **reachability** — the v1 lint on the expanded program (mobile objects
   reach ≥2 receptacles; statics appear in no rule), and its inverse for
   the calendar: an at-home, non-sleep activity scheduled by
   `weekly_blocks` that appears in no object rule and carries no
   `reset_all` fails, with the activity named — objects move because of
   what people do at home, not only because they leave. How MANY objects
   are static is reported (panel `never_move`, meta `inert_objects`),
   never gated: static objects are a welcome part of a household.
4. **leak audit** — the generation LLM must NOT be able to classify the
   household type from bare object + receptacle ids (chance = 0.1). Run at
   L1, not L2: those ids come from the persona and the scene, so a correct
   guess resamples the HOUSEHOLD. Re-rolling the routine program cannot
   change an inventory, and did nothing but burn five attempts. Logged
   either way. Some types cannot pass — see below.
5. **realism panel** — `realism_panel.py`, REPORTING ONLY, never a gate:
   sporadicity stats vs the real-ADL reference (casas/aruba).

Anything else is a pytest assertion (`tests/test_revamp_v2_*.py`) or is
not written.

### Carrying, and leaving the house

An object homed at `person:<owner>` rides that person — out of the house
included — and reaches a receptacle only when a rule or `p_misplace` sets
it down. Whether a pocket item lives on its owner is the MODEL's choice,
encouraged per item and per persona (a pinned version of this was tried
and overshot: wallets rode their owners for 21 days with zero put-downs).
Two realization behaviours make it lifelike, both in
`realization_params.yaml`:
- `carry_on_departure` — every block starting at ELSEWHERE picks up the
  departing resident's person-homed items, so nobody's phone stays home
  just because the author forgot one going-out activity;
- `carry_p` (0.85) — each (item, trip-type) pair is a stable hash-derived
  choice, so each household has a few standing omissions ("she never
  takes her wallet on the morning walk"); per-day forgetting comes from
  `p_misplace` having set the item down somewhere first.

### What the model actually gets wrong

Every constraint above earned its place from a real rejection, and each
was fixed by a schema constraint or a prompt change — never by editing a
generated program. Worth knowing before changing either:

- The guided-decoding backend (xgrammar) rejects `uniqueItems` and
  `contains` outright, so those constraints live in `check_referential`
  or in the prompt instead. `dependentRequired`, `oneOf` and `anyOf` do
  work — probe before relying on a keyword.
- The expander performs five deterministic normalizations, all counted in
  `meta.json` rather than silent, and all for the same reason: the thing
  the model wrote describes nothing, so rejecting a whole program over it
  protects no invariant.
  - `p_misplace: 0`, or a `p_misplace` with no `misplace_set`, means the
    drift mechanism is ABSENT (v1's lint tests presence, so a stored 0.0
    would make a declared-static object read as mobile).
  - `end` is the NEXT occurrence of that clock time after `start` — models
    carry "+1" inconsistently across midnight.
  - A block flagged `sleep: true` is renamed to contain "sleep", because
    `export_bank` and the v1 simulator detect sleep by substring while the
    model names blocks for what they mean ("morning_rest").
  - A `reset_all` on a sleep activity is dropped: a tidy walk is a walk,
    and the resident is asleep (`dropped_sleep_resets`).
  - An arc `drop` naming an activity that does not run that weekday is a
    no-op (`vacuous_arc_drops`); an arc naming an activity that exists
    nowhere is still fatal.
  What is NOT normalized away is the core invariant: an object the plan
  says moves, that no activity rule moves, rejects the program. Objects
  moving because of what residents do is the whole point of the dataset.
- `dependentRequired` is ACCEPTED by xgrammar but not enforced, so it can
  document a pairing but never gate one — re-check it, or normalize.
- Arc events name a day NUMBER while blocks name weekday CODES; making the
  model derive that mapping caused more rejections than everything else
  combined, so `program_user_prompt` now ships the calendar table.
- One activity may run in DIFFERENT places for different residents (four
  people, four beds, one "sleep"). The v1 simulator keys `at`/`jitter` by
  activity name alone, so the expander splits such an activity into
  per-location variants (`sleep`, `sleep__bed_b2`, ...) that share one set
  of bindings. Single-location activities keep their name, which is why
  the hh1 regression is unaffected.
- **The leak audit is unpassable for some household types**, and this is
  a property of the design rather than a bug. The object vocabulary is a
  closed 25-class list, ids must begin with their class, and a household
  with `toy_1`, `lunchbox_1` and two backpacks IS a family with young
  children — the auditor says so at 0.85 confidence, correctly, however
  the persona is resampled. Such households are still built, flagged
  `leak_unresolved` in `build_log.json` and called out in the acceptance
  report. Closing it for real means anonymised ids (`obj_07`) or dropping
  the distinctive types, both of which cost more than they buy.
- Raising the persona's object floor makes programs HARDER to get right
  (every extra object is another chance for the reachability lint to
  reject the whole program) without making the household richer — tried,
  measured, reverted.

## How to run

```bash
# Serve the generation model once — any OpenAI-compatible endpoint works.
# On this machine (driver 12.8) the repo's default env cannot start vLLM
# ("NVIDIA driver too old"); the cu129 venv can, single-GPU:
CUDA_VISIBLE_DEVICES=2 HF_HOME=/data/oliver/huggingface_cache \
  /data/oliver/venvs/vllm-v4-cu129/bin/vllm serve Qwen/Qwen3.6-35B-A3B-FP8 \
    --host 127.0.0.1 --port 8300 --max-model-len 16384 --max-num-seqs 32 \
    --gpu-memory-utilization 0.92 \
    --structured-outputs-config '{"backend":"xgrammar","disable_any_whitespace":true}'
# Two flags are not optional here. `disable_any_whitespace`: without it,
# long guided-JSON responses spend their token budget on whitespace and
# truncate. Single-GPU (no --tensor-parallel-size): TP=2 dies in torch's
# symmetric-memory allocator on this box, for this model and Qwen3-32B
# alike, and a 35B FP8 MoE fits one 94GB card anyway.

# full build: 10 households, validation, timelines, banks, viewer configs
GENERATION_ENDPOINT=http://127.0.0.1:8300 bash src/revamp_v2/build.sh

# single household / pieces
GENERATION_ENDPOINT=... python src/revamp_v2/generate.py --household hh1
python src/revamp_v2/validate.py profiles/revamp_v2/qwen3-32b/hh1 [--leak]
python src/revamp_v2/simulate.py profiles/revamp_v2/qwen3-32b/hh1 --seed 0
python -m baselines.export_bank --timeline .../timeline_seed0 \
    --spec .../routine_program.yaml --seed 0 --out banks/baselines/...jsonl
```

Viewer: `make_viewer_configs.py` (run by build.sh) writes a
`visualization/configs/revamp_v2_hh<N>_102343992.yaml` per household and
registers each timeline in `visualization/traces.json`; after
`visualization/spatialize.py <config> --timeline <timeline>` the trace
replays at `visualization/serve.py` → http://127.0.0.1:8710/ exactly like
the revamp_v1 households.

Reproducibility: every LLM call is seeded via `make_seed(household, stage,
attempt)` and disk-cached per model (`--cache-dir`); re-running build.sh
with the same cache dir reproduces all artifacts byte-for-byte.
