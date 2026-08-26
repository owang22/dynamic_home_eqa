# Bake-off recommendation — candidate beliefs for the paper baselines

Evidence: `leaderboard.md` / `bakeoff_results.json` in this directory
(the OFFICIAL run: the one gate-passing bank from the fleet, revamp_v1
hh1) and `exploratory_all_banks/` (the same protocol over all 12 fleet
banks, gate-failing ones included — labeled exploratory because the
instrument marks those banks unhealthy, but it is the only place
multi-resident and routine-shift dynamics exist at all today). All runs:
horizon-controlled passive protocol, seed 0, no sensing, all candidate
hyperparameters at their fixed a-priori defaults.

The fleet context matters for reading everything below: only ONE bank
passes the gates, and the dominant fleet failure is evidence starvation
(10 sightings/day over 30-50-object inventories — see
`../fleet/failures.md`), which compresses ACCURACY differences between
all sighting-driven models. Log-loss still separates models cleanly; the
accuracy rankings should be re-read after the generation workstream
fixes the sighting-rate scale.

## Promote (2)

1. **periodic_persistence** — promote as the headline classical
   per-object comparator. It is the strongest or tied-strongest
   candidate on accuracy in most cells (official headline D=7, h=1:
   0.559 vs LastObservation 0.593 on hh1; exploratory aggregate 0.469 vs
   0.476, inside every interval), it is the model class the paper will
   be judged against (hazard decay + time-of-day return), and it
   degrades gracefully: on the strict-periodic fixture it is exact
   (1.0 at h <= 1 day, tested), on fast churn it converges to the
   frequency floor (tested). Its hazard estimator is unit-tested on
   hand-computed censored-dwell cases.
2. **hierarchy_backoff** — promote as the calibration baseline. It wins
   mean log-loss on 10 of 12 exploratory households and on the
   aggregate (2.68 vs 3.04-3.62 for everything else) at a small
   accuracy cost, because sharing class/global statistics keeps it from
   the confident one-hot misses that dominate the panel's log-loss.
   Top-1 and log-loss genuinely dissociate here — exactly the
   two-metric comparison the protocol exists to make. (One global fix
   during the bake-off, recorded in STATUS.md: backoff weights now use
   raw counts, not decayed counts, so old-but-plentiful own evidence is
   not abandoned for the global histogram; stale-bin accuracy went from
   0.105 to 0.432, in line with the other models.)

## Keep conditionally (1)

3. **daytype_mixture** — keep registered as the regime-inference probe,
   but do NOT run LLM comparisons against today's banks on its account.
   **It does not separate from the per-object models on any bank.** Its
   two accuracy "wins" (+0.022 on storyfirst hh2, +0.036 on hh7 at
   D=7, h=1, n~90) are inside binomial noise, and it loses the
   remaining 22 of 24 headline/D=14 cells by 0.01-0.13. This is not a
   model defect: on the synthetic two-regime fixture (weekday/weekend
   layouts) it scores 1.0 where the 24 h-half-life frequency model
   scores 0.0 (tested), so the mechanism works when regimes exist. The
   plain conclusion: **the current banks do not reward cross-object
   regime inference** — household days do not fall into layout regimes
   that sightings of one object could reveal about another. Until
   generation makes routines more coupled (shared day-types that move
   many objects together: trip days, cleaning days, guest days), an LLM
   "knows what kind of day it is" comparison has nothing to win, and
   running it would be wasted compute. daytype_mixture is the cheap
   detector for when that changes.

## Drop (1)

4. **markov1** — drop. At realistic sighting rates it is empirically
   indistinguishable from most_frequent (identical to three decimals in
   most exploratory cells): consecutive sightings arrive hours apart,
   so its "transitions" mix through unobserved moves and carry no
   dynamics, and beyond the 24 h mixing cutoff — most stale queries —
   it IS the frequency model by construction. It adds a hyperparameter
   surface without adding a distinguishable prediction; nothing in any
   cell justifies keeping it.

## Panel note

The frozen three-member instrument panel is untouched by all of this;
candidates remain registry-tagged `candidate` and the healthcheck
refuses them by construction (tested).
