# OracleBelief on the representative grid: stopped at the ESS gate

Status: the grid did NOT run. The brief's degeneracy rule ("if median ESS
on the fleet banks falls below 5, STOP and report before running the
grid") fired on every bank. Questions (1)-(3) of the brief are therefore
unanswered; the code (`beliefs/oracle_program_posterior.py`, registered as
`oracle_program_posterior`, display name `OracleBelief`; the study driver
`oracle_posterior_study.py`) is complete and the grid stage runs as soon
as an owner picks a fix and passes `--force-grid` or changes the setting.

Inputs: the 20 seed-0 fleet banks of `results/conformal_sweep_v2/`, the
routine oracle's 800 re-realizations per household (seeds 1001-1800; the
bank's seed-0 world is never in the ensemble), eps 0.05 per disagreeing
observation, soft weights, the passive diet (NeverSense at the bank's
own budget). Per-question ESS in `ess_passive.csv`; the fleet and
per-household summary in `ess_gate.md`.

## What the gate measured

| quantity | value |
|---|---|
| questions | 45 000 (20 banks x 2 250) |
| fleet median ESS | 1.00 |
| fleet quartiles | 1.00 / 1.01 |
| fleet maximum ESS (any question, any bank) | 3.41 |
| per-household median ESS | 1.00 on 19 banks, 1.01 on hh_017 |
| per-household p90 | 1.10-2.00 |

ESS is already 1.0 on the first query day (day 3, median 1.01) and
stays there: the weights collapse onto one realization within the first
three days of ambient room visits and never recover.

## Why it collapses (diagnostic run, not part of the study outputs)

Two checks on all 20 banks, feeding the initial tour plus the full
ambient stream (18 000-47 000 object-level observations per bank: each
room-visit sense result is one positive or empty look per known object):

1. **The matching is right.** A one-seed control ensemble at the bank's
   own seed 0 disagrees with 0 of the observations on 18 of 20 banks
   (hh_004: 12 disagreements of 26 638, hh_005: 11 of 25 937; a small
   export-vs-realization drift on those two, not a matching bug).
2. **No realization is close to the bank.** The BEST of the 800
   realizations disagrees with 480-846 observations per bank (2-3% of
   the stream); the median realization with 554-950; the worst with
   645-1 053. The gap between the best and the second-best realization
   is 1-15 disagreements, and each disagreement costs a factor 0.05
   (3.0 nats), so the second-best carries at most 0.05 of the best's
   weight and usually far less: ESS 1.0 by arithmetic.

Disagreement counts, best / median / worst realization per bank:

| bank | observations | best | median | worst |
|---|---|---|---|---|
| hh_001 | 24 850 | 676 | 793 | 918 |
| hh_002 | 46 680 | 805 | 910 | 997 |
| hh_003 | 32 445 | 701 | 793 | 896 |
| hh_004 | 26 638 | 480 | 554 | 645 |
| hh_005 | 25 937 | 652 | 722 | 794 |
| hh_006 | 17 750 | 516 | 592 | 670 |
| hh_007 | 31 724 | 650 | 730 | 815 |
| hh_008 | 33 166 | 703 | 790 | 877 |
| hh_009 | 32 185 | 789 | 879 | 993 |
| hh_010 | 40 230 | 782 | 868 | 944 |
| hh_011 | 27 339 | 846 | 950 | 1 053 |
| hh_012 | 21 300 | 575 | 695 | 803 |
| hh_013 | 30 280 | 792 | 867 | 946 |
| hh_014 | 22 720 | 647 | 775 | 883 |
| hh_015 | 26 677 | 571 | 658 | 739 |
| hh_016 | 23 310 | 681 | 805 | 917 |
| hh_017 | 28 741 | 736 | 825 | 918 |
| hh_018 | 29 442 | 693 | 778 | 865 |
| hh_019 | 22 720 | 631 | 728 | 811 |
| hh_020 | 22 320 | 651 | 750 | 844 |

The realization randomness (daily misplace draws, rule destination draws,
tidy races, skips, jitter) is enough that no other seed reproduces the
bank's world for more than a few days; consistency-weighting a fixed
ensemble of whole-episode realizations therefore selects the least-wrong
one rather than a posterior over routines.

## What the owner has to decide (not decided here)

- **eps.** With ~800 disagreements per realization and a best-to-median
  spread of ~100, any eps below about 0.95 keeps ESS near 1; eps near 1
  makes the weights nearly uniform (the routine oracle again). There is
  no eps that gives a middle ground on whole-episode realizations.
- **Matching granularity.** Weighting per observation over the whole
  episode is the problem; weighting only recent evidence (a window, or
  a forgetting factor on the log-weights) would let realizations that
  match the last day matter even if they diverged earlier.
- **Seed count.** 800 -> 8 000 would lower the best realization's
  disagreement count somewhat but not change the picture: the gap
  between neighbours in the sorted disagreement list is what sets ESS.
- **A different estimator.** Re-realizing from the current observed
  state (particle filtering the program rather than reweighting fixed
  trajectories) is the standard fix; it is a different design, out of
  this brief.

Until then the representative grids of the value-of-information and
delayed-label studies run without OracleBelief and say so.
