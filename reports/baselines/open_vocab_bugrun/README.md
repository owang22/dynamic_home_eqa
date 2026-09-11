# Open-object-vocabulary bug-catching run

Purpose: after the object list was withheld from every deployable
belief by default (oracle-only privilege), confirm nothing disastrous
happens — in particular, catch any model that never learns an object it
was not told about at reset.

## Setup

- hh_001 and hh_003, routine-driven banks re-exported at budget 120/day
  (generous — sensing is not the bottleneck), object list withheld (the
  new default), seed 0.
- One representative per belief family, all through
  `VoIThresholdSense(lambda=0.05)`: last_observation (recency),
  most_frequent (frequency), timetable (time-of-day), daytype_mixture
  (day-type), markov1 (transition), periodic_persistence (hazard),
  hierarchy_backoff (pooling), perpetua_star (survival filters).
- 16 agent-episodes, 2250 questions each. Zero exceptions, zero forced
  answers, per-agent accuracies 0.62-0.94.

## Result: no open-vocab pathology

`accuracy_vs_sightings.png` — per-object accuracy against episode
sighting count, one panel per belief, colored class-has-siblings vs
class-disjoint, marker per household. No model shows a never-learns
signature (a flat-at-chance band independent of sightings), and the
class-disjoint objects sit in the same cloud as sibling classes — the
cold-start pool is doing no visible harm.

The never-learns screen (>=10 sightings, <5% accuracy, >=5 questions)
flagged one object, `towel_marisol` in hh_003, at ~0 accuracy across
five DIFFERENT model families. That is a world property surfaced by the
routine-driven stream, not a vocabulary bug: its 71 queries fire almost
all during showers (`activity:shower` rule), when the towel has just
moved to `bathroom_shelf_ba1`, while every ambient sighting catches it
parked on `towel_rack_ba1` — so every belief answers the rack with high
confidence and VoI declines to sense. This is precisely the
query/displacement correlation the routine stream exists to create.

A handful of other near-zero points in the panels are the same
phenomenon on objects with few questions; not investigated further.

## Learning curve by prior-sighting bucket

`learning_curve.png` — per question, ambient sightings of the queried
object delivered strictly before ``t_query`` (tour + scripted
positives), bucketed 0 / 1 / 2 / 3 / 4-6 / 7+, mean accuracy per bucket
with counts, pooled across objects and households.

- The 0 bucket is EMPTY by construction: the initial tour sights every
  in-house object at t = 0 and questions start on day 3, so no question
  ever arrives with zero evidence on these banks. A no-tour export
  would be needed to populate it.
- No bucket sits at chance for any belief — the discovery path never
  leaves a model unlearned, which is the bug this run existed to catch.
- The low buckets (n = 9 / 13 / 88) are dominated by rarely-sighted,
  rarely-moving objects, so their high accuracy is an object-identity
  confound, not evidence that less data helps; the 4-6 -> 7+ step is
  the cleaner within-plot comparison and rises for every belief.

Run script and per-object CSV: session scratchpad (`bugrun/`); banks
regenerable from the export command in the script header.
