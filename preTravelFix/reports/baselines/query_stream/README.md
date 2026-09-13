# Routine-driven query stream — figures for approval (STOP point)

Queries are now generated from the household's realized activities
instead of a uniform draw. This directory holds the figures the brief
asks the owner to confirm before anything downstream is built.

## What was built

- `baselines/query_stream.py`: `query_rule` schema (trigger
  before/during, `offset_minutes {mean, sd}`, objects by id or class,
  optional `resident_weight`), realized-activity parsing from the
  timeline's `residents.jsonl`, and the per-day draw. Every day emits
  exactly `questions_per_day` questions: a background count drawn from
  `background_query_rate` (uniform over objects and awake time), the
  remainder allocated to rule-matched activity instances.
- `baselines/export_bank.py`: `--query-generation routine_driven
  --query-rules <yaml>`; the header records `query_generation` (and the
  background rate + rules file), each question row records an `origin`
  (`background` or `activity:<name>`).
- Loader: `query_generation` header value validated; a question row
  carrying an `origin` in a bank whose header does not declare
  `query_generation` is rejected. Old banks (no such header) load
  unchanged as uniform.
- `baselines/configs/query_rules_v1.yaml`: one shared rules file for the
  fleet. Objects are named by CLASS so the file is portable across
  households (a household lacking the class never fires the entry);
  activity keys match realized block names up to the realizer's
  `__<location>` suffix. Rules can equally be embedded per household —
  the schema is the same mapping — but a shared file avoided editing 20
  generated profiles before the stream shape is approved.

## Exported banks (paired with the uniform fleet banks)

`banks/baselines/fleet_routine/` holds hh_001 (solo professional),
hh_003 (single parent, rotating shift), hh_009 (couple with toddler),
exported with the exact fleet settings (seed 0, room_visit patrol 6/day,
90 questions/day from day 3, budget 24). The uniform-mode partners are
the existing `banks/baselines/fleet/` banks; question totals match
(2250 each), so budget sweeps stay comparable.

## Figures

- `query_heatmap.png` — object class x hour of day, one panel per
  household. The routine structure is visible: mug/medication/towel
  spike at wake-up, plates/bowls at the dinner hour, phone spread over
  waking time, departure objects (keys, backpack) before work/school.
- `queries_per_day.png` — per-day counts split by origin. Totals are
  fixed at 90 by construction; the background floor is 6/day
  (`background_query_rate: 6` is an integer, so the count never
  varies; a fractional rate would).
- `query_offsets.png` — offsets from the triggering activity's start,
  hh_001: `work_away` centred near -20 min (rule mean 20, sd 8),
  `take_medication` near -5, `coffee` strictly inside the block.

## One-line observations (not investigated)

- Many realized `coffee`/`linger_*` blocks are only a few minutes long,
  so during-triggered offsets pile up near 0.
- Fleet-wide routine export is not wired into `baselines.fleet` yet;
  the three banks above were exported via the CLI. Wiring is a
  two-line config change once the stream is approved.

## Waiting on the owner

Per the brief this line STOPS here: nothing downstream (re-measurement
of the room-change-cost cells, forecaster, lookahead) is built until the
query stream is confirmed to look right.
