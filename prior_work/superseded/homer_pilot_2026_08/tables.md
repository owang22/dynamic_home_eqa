# HOMER+ pilot results

> **SUPERSEDED — DO NOT CITE THESE NUMBERS WITHOUT READING [README.md](README.md).**
> This table was produced by `PYTHONPATH=src python -m homer.run` at commit
> `fa290a6b` and is retained as a reproducible record only. Three defects
> are annotated inline below: the `uniform` row is a tie-break artifact and
> not a random floor; the moved-only slice is reported elsewhere under a
> different aggregation; and the one non-zero moved-only result is a single
> household. The experiment it belongs to was superseded on 2026-08-13 by
> the budgeted whole-house belief-tracking setup in `src/beliefsim/`.

Unit of analysis: the household (n=3). Aggregates are descriptive; no CIs are quoted because three households cannot support them.

**Aggregation (undeclared in the original):** every cell below is a
MICRO-average — the mean over individual query instants, so objects and days
with more instants weigh more. The E2 "mean over draws" columns are the mean
of per-draw micro-averages. The learning-curve CSV in this same directory
uses a different aggregation for the same quantities; see defect (b).

## E1 — standard localization (top-1 / top-3)

| method | HH-A | HH-B | HH-C | mean |
|---|---|---|---|---|
| fremen | 0.957 / 0.999 | 0.944 / 0.998 | 0.955 / 0.999 | 0.952 |
| frequency | 0.960 / 1.000 | 0.944 / 0.999 | 0.960 / 0.999 | 0.955 |
| markov | 0.940 / 1.000 | 0.938 / 0.999 | 0.932 / 0.999 | 0.937 |
| modal | 0.906 / 1.000 | 0.925 / 0.999 | 0.898 / 0.999 | 0.909 |
| persistence | 0.861 / 0.861 | 0.898 / 0.898 | 0.886 / 0.886 | 0.882 |
| pooled | 0.959 / 1.000 | 0.943 / 0.999 | 0.960 / 0.999 | 0.954 |
| uniform | 0.100 / 0.149 | 0.000 / 0.143 | 0.103 / 0.154 | 0.067 |

> **Defect (a) — the `uniform` row is not a random floor.** `_score` in
> `src/homer/run.py` ranks with `sorted(dist.items(), key=lambda kv: -kv[1])`.
> Python's sort is stable, so under a flat distribution every receptacle ties
> and the winner is whichever key the distribution dict yields first, which
> for `Uniform` is the alphabetically-first receptacle. Verified: HH-A and
> HH-C both always predict `bathroom_cabinet#17`, which holds 0.0999 and
> 0.1026 of their instants — exactly the reported accuracies. HH-B's
> alphabetically-first receptacle is `bathroom#1`, which is never occupied,
> hence 0.000. The row therefore measures the occupancy of one arbitrary
> receptacle per household, not chance. Chance is 1/|R| = 0.038 (A, 26
> receptacles), 0.034 (B, 29) and 0.040 (C, 25).

## E2 — held-out object generalization (top-1, mean over draws [min–max across draws])

| method | HH-A | HH-B | HH-C | mean |
|---|---|---|---|---|
| fremen | 0.864 [0.471–1.000] | 0.895 [0.750–0.962] | 0.881 [0.500–0.994] | 0.880 |
| frequency | 0.864 [0.471–1.000] | 0.895 [0.750–0.962] | 0.881 [0.500–0.994] | 0.880 |
| markov | 0.864 [0.471–1.000] | 0.895 [0.750–0.962] | 0.881 [0.500–0.994] | 0.880 |
| modal | 0.864 [0.471–1.000] | 0.895 [0.750–0.962] | 0.881 [0.500–0.994] | 0.880 |
| persistence | 0.864 [0.471–1.000] | 0.895 [0.750–0.962] | 0.881 [0.500–0.994] | 0.880 |
| pooled | 0.844 [0.553–1.000] | 0.752 [0.500–0.932] | 0.692 [0.000–0.994] | 0.763 |
| uniform | 0.200 [0.000–0.500] | 0.000 [0.000–0.000] | 0.200 [0.000–0.500] | 0.133 |

## E2 supplementary — moved-only slice

Restricting E2 scoring to the query instants where the held-out object is
AWAY from its initial placement (12.0% of instants) isolates transfer from
inertia:

| method | E2 all | E2 moved-only |
|---|---|---|
| every per-object method (shared fallback) | 0.880 | 0.000 |
| pooled | 0.763 | 0.196 |
| uniform | 0.133 | 0.278 |

The shared fallback never leaves the initial placement, so it scores zero
exactly where localization is non-trivial; pooled recovers a fifth of
those instants at the cost of the easy 88%.

> ~~Note uniform beats pooled on this slice: displaced objects visit
> receptacles roughly uniformly often enough that pooled's popularity-shaped
> guesses are WORSE than flat — the transferred (initial-receptacle, hour)
> structure is pointing at the wrong receptacles, not merely diluted.~~
>
> **STRUCK — the conclusion does not follow.** By defect (a), `uniform` here
> is not a flat guess; it is a constant prediction of `bathroom_cabinet#17`.
> Its 0.278 on this slice comes entirely from HH-C, where 0.842 of the
> displaced held-out instants happen to be that one receptacle (HH-A 0.000,
> HH-B 0.000). Nothing about pooled's aim can be inferred from a comparison
> against a constant predictor that got lucky in one household.
>
> **Defect (b) — undeclared aggregation.** The same quantity (pooled, E2,
> moved-only) appears as three different numbers across this directory,
> computed by two code paths:
>
> | value | source | aggregation |
> |---|---|---|
> | 0.196 | this table (`homer/run.py`) | micro over all held-out displaced instants |
> | 0.052 | `learning_curves.csv` (`homer/learning_curves.py`) | unweighted mean over non-empty household × ordering × draw cells |
> | 0.076 | `learning_curves.csv`, re-aggregated | macro over households of those cell means |
>
> The 0.052 figure is additionally biased low: 6 of HH-A's 15 cells had no
> displaced instants at all and were dropped, so the one household with a
> non-zero result is under-weighted. This is the defect that motivated the
> single-source aggregation rule (`src/beliefsim/scoring.py`): all three
> numbers were defensible, none was labelled, and they were compared to each
> other in discussion as if they were the same statistic.
>
> **Defect (c) — the aggregate hides a single household.** Pooled's entire
> moved-only effect is HH-A. Per household, over displaced held-out
> instants: HH-A 0.519 (n=231), HH-B 0.000 (n=179), HH-C 0.000 (n=202). The
> mean of 0.196 describes no household. With n=3 and two exact zeros this is
> one household's idiosyncrasy, not a transfer result.
