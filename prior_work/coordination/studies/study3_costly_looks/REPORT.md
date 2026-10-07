# Study 3, costly looks: report

**Verdict: drop by design, before any model call.** A ceiling policy that chooses perfectly among
the places the robot's own memory has ever seen the thing, and otherwise explores exactly as the
rule does, beats the best rule by 8.9 points on non-towel things at budget 60. A 10-point gap on
all things needs 23 points there. No memory-based chooser, model or not, can clear the bar on
this data. Status 2026-10-02 01:50 PDT; blind re-run of the gate requested.

## Setup and prediction (SETUP.md, 01:05)

Rendered search benchmark, one home, 164 positions in 34 places, 248 questions over a month,
perfect perception ("in view"), walking metres plus 5 units per look plus 10 if a resident is in
the room looked into, budgets 30 / 60 / 120, at most 12 looks. Prediction: a Qwen chooser lands
within 5 points of last-seen on all things and within 10 on other things; drop.

## What was built and checked before the gate

- Occupied-room penalty, budgets, "found within budget" and cost per question; a model-driven
  chooser with a structured answer (reasoning first, then a place pinned to the open places or
  "cannot be found"); two more rule baselines the plan critic asked for (same time of day; last
  seen by room); a distance-order baseline; budget-aware rules with one written overshoot rule for
  every policy.
- A fake model that parses its own prompt and picks the nearest untried affordable place
  reproduces the rule `last seen (nearest)` on every one of 1,240 searches at all three budgets;
  the distance fake reproduces `distance order` the same way. Default runs still reproduce the
  earlier benchmark numbers to the digit.
- Leak hunter (fresh): one real leak, fixed. The budget-left line carried room occupancy taken
  from the truth (the penalty is charged from the residents' recorded rooms, and the asked thing
  is in an occupied room 56% of the time, so the arithmetic was predictive). Now the shown budget
  excludes penalties, and the prompt says "saw: a person" only when the robot's own picture
  contained one. Also fixed: the shown walk is the walk charged; the cache is per model and
  server; each step records who decided (model or which fallback).
- Plan critic (fresh), 18 points; the decisive one was the ceiling check below. Others folded in:
  budget-aware rules, sightings listed as events not per camera position, the 12-look cap and the
  penalty size stated in the prompt, "cannot be found" described with its base rate (37.5% of
  questions have the thing in no picture), per-start rows and full column names, paired
  per-question scoring against the best rule at one start.

## The gate

"Found within budget, of findable other things" (67 questions; towels, 88 questions, are found by
every sensible method). n = 1 household.

| budget | ceiling: oracle among remembered places, then last-seen's exploration | best rule on other things | ceiling minus best rule |
|---|---|---|---|
| 30 | 38.8% | 35.8% (same time of day) | +3.0 |
| 60 | 53.7% | 44.8% (last seen, kind then nearest) | +8.9 |
| 120 | 61.2% | 53.7% (last seen, kind then nearest) | +7.5 |

On all findable things: ceiling 69.7 / 76.1 / 83.2% against the best rule 67.1 / 76.1 / 80.0%.
Paired at one start against the best rule, budget 60: 12 discordant questions, net 0.

Two definitions had to be settled. The ceiling as first specified (nearest remembered place that
truly shows the thing, else "cannot be found") never explores and scores below every rule (6% on
other things); it is kept on record as a floor. The ceiling reported adds last-seen's exploration
when memory has nothing; it bounds any method that works from this memory and explores no better
than the rule. A method that explores better is not bounded by it; the plain oracle (100%) is.

## Two facts found on the way

- **The five starting positions are five copies of one month.** The first question is a towel;
  every policy walks to the same towel-rack position and from then on the trajectories are
  identical, differing only in the first walk. The benchmark page's "lowest and highest over
  starts" columns are honest (they read 72% to 72% for the rules) but my setup note's "per-start
  spread of 1 to 8 points for the rules" was wrong; that spread belonged to the random policy.
  The sample is 248 questions, 155 findable, 67 findable non-towels, in one household.
- **73 of the 93 unfindable questions are things at three places** (the office desk, the dining
  table, the bathroom shelf) that no picture shows under "in view" from the Go2 rig. That is the
  camera-height finding of the main page seen from the other side, and it belongs there.

## Opus and Qwen

Neither run. Opus blocked (usage file); Qwen not warranted after the gate. Model calls: 0.

## Checkers

- Leak hunter and plan critic: above, both before any run.
- Blind re-run of the gate: requested 01:50 (fresh agent runs the benchmark command and compares
  the printed ceiling and best-rule rows with this table). Pending.

## What would reopen it

More households in the rendered benchmark (the place-to-furniture binding is hand-written for
this home), a camera that sees the desk, dining table and bathroom shelf (then the findable set
grows and the ceiling may move), or a question that is not "choose the next place from memory":
for example choosing where to stand inside a place, which the memory bound does not cover.

Files in this folder: `gate_oracle_within_memory.txt`, `dry_run_fake_nearest.txt`,
`dry_run_fake_distance_stand_nearest.txt`, `prompt_example*.txt`, `prompt_diff_before_after.txt`,
`baseline_before_changes.txt`; code in `src/rendered_look/searchbench/bench.py`.
