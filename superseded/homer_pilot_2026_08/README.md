# SUPERSEDED: HOMER+ E1/E2 localization pilot (August 2026)

**Status: superseded 2026-08-13. Do not cite these numbers.** The pilot ran
correctly — the code did what it was asked — but it measured a quantity that
cannot support the claim it was built to test. The replacement experiment is
the budgeted whole-house belief-tracking setup in `src/beliefsim/`, with
results in `results/`.

This directory is kept as a reproducible record: what was run, what came out,
and why it was retired.

## What the pilot measured

Two protocols over the HOMER+ dataset (Patel, Prakash & Chernova, CoRL 2023;
3 households, 65 train / 10 test days of VirtualHome full-state graphs):

* **E1 — standard localization.** Fit a belief model on all 65 training days
  of complete state, then answer "where is object *o*?" at every hour from
  07:00 to 23:00 on every test day. No test-day observations, so persistence
  is a forecast rather than an oracle.
* **E2 — held-out object generalization.** As E1, but *k*=2 objects per draw
  (5 seeded draws per household) are removed from training; only their day-0
  placement is given. Scored on the held-out objects only.

Methods: `uniform`, `persistence`, `modal`, `frequency`, `markov`, `pooled`
(`src/homer/baselines.py`) and `fremen` (`src/homer/fremen.py`, order 2).

## Provenance

| | |
|---|---|
| commit | `fa290a6b` ("Add HOMER+ learning curves: accuracy vs days of observation") |
| traces | `data/homer_traces/` (committed; built from `third_party/HOMER_PLUS/`) |
| seeds | scoring seed 0; held-out mask seed and *k* in `provenance.json` |

Regenerate (from the repository root, at that commit):

```bash
PYTHONPATH=src python -m homer.run --out results          # raw_results.csv, tables.md, provenance.json
PYTHONPATH=src python -m homer.learning_curves            # learning_curves.csv   (~25 min)
PYTHONPATH=src python -m homer.plot_curves                # learning_curves_e1/e2.png
```

`raw_results.csv.gz` here is the gzipped original (11 MB raw, 1.9 M rows); the
live path `results/raw_results.csv` is gitignored because it is regenerable.

## Files

| file | contents |
|---|---|
| `tables.md` | the headline E1/E2 tables, **annotated inline** with the three defects below |
| `raw_results.csv.gz` | per-query-instant long-format results, the source of `tables.md` |
| `learning_curves.csv` | accuracy vs training-prefix size, 3 seeded day-orderings |
| `learning_curves_e1.png`, `learning_curves_e2.png` | rendered curves |
| `provenance.json` | seeds, mask *k*, FreMEn order, row count |

## Why it was superseded

### 1. Inertia dominates the headline number

91% of query instants have the object sitting at its habitual location. A
static predictor ("always guess this object's usual spot") scores 0.910; the
best method scores 0.955. Almost the entire reported number is inertia, and
the 4.5-point band above it is what every method is actually competing over.
Restricted to the 9% of instants where the object is displaced from its
per-object modal receptacle, accuracy falls to 0.39–0.61 and the methods
separate. The learning curves make the same point from a second angle: every
method is within ~2 points of its 65-day value after **4 days** of
observation, so sixty more days of complete state buy ~1.5 accuracy points.

### 2. E2 had no resolution

`persistence`, `modal`, `frequency`, `markov` and `fremen` produced
bit-identical E2 numbers (0.880 mean, identical per-draw min/max) because all
five delegate to the same `Modal` fallback for an object with no training
history, and that fallback's argmax is always the object's given initial
placement. Five table rows were one method printed five times. The
supplementary moved-only slice was added to expose this and did — the shared
fallback scores exactly 0.000 there — but the main E2 table still reads as
five independent results.

### 3. The setup hands the baselines everything

Both protocols grant 65 days of complete state for every object at every
timestep. In that regime counting is near-optimal and world knowledge cannot
help: there is nothing to infer that has not already been observed hundreds of
times. This is not a defect in the baselines, it is a defect in the
evaluation. A real robot cannot observe the whole house at once, and the
replacement experiment constrains the sensing channel instead.

## Defects in the writeup itself

Annotated inline in `tables.md`; summarized here so they are not re-cited.

**(a) `uniform` is not a random floor.** `_score` in `src/homer/run.py` ranks
with a stable sort on descending probability, so a flat distribution resolves
to whichever receptacle the distribution dict yields first — the
alphabetically-first one. HH-A and HH-C therefore always predict
`bathroom_cabinet#17` (0.0999 and 0.1026 of their instants, matching the
reported 0.100/0.103), and HH-B always predicts `bathroom#1`, which is never
occupied, giving 0.000. Chance is 1/|R| ≈ 0.034–0.040. The paragraph
concluding that "uniform beats pooled, therefore pooled points at the wrong
receptacles" is struck: `uniform`'s 0.278 on the moved-only slice is HH-C's
0.842 alone, i.e. one constant predictor getting lucky in one household.

Carried forward: `src/beliefsim/scoring.py` breaks argmax ties with a seeded
RNG, averages over ≥5 seeds, and `tests/test_scoring.py` asserts that a
uniform predictor scores within tolerance of 1/|R|.

**(b) One quantity, three numbers, two code paths.** Pooled's E2 moved-only
result is reported as 0.196 (`tables.md`, micro-average over instants), 0.052
(`learning_curves.csv`, unweighted mean over non-empty household × ordering ×
draw cells) and 0.076 (the same cells, macro-averaged over households). All
three are defensible; none was labelled; they were compared to each other in
discussion. The 0.052 is additionally biased low because 6 of HH-A's 15 cells
had no displaced instants and were silently dropped — under-weighting the only
household with a non-zero result.

Carried forward: every table and plot derives from one long-format CSV through
one shared function, micro vs macro is an explicit argument, and every emitted
table states which it used in its header.

**(c) The aggregate hides a single household.** Pooled's moved-only effect is
entirely HH-A: 0.519 (n=231) against HH-B 0.000 (n=179) and HH-C 0.000
(n=202). The 0.196 mean describes no household. With n=3 and two exact zeros,
this is one household's idiosyncrasy.

## What is still in use

`src/homer/loader.py` (canonical traces, specificity-ranked parent
resolution), `src/homer/fremen.py` (FreMEn with the Nyquist guard),
`src/homer/protocol.py`, `src/homer/baselines.py`,
`reports/homer_inventory.md` and `reports/homer_spectra/` all carry forward
into the replacement experiment, along with their tests. Only the E1/E2
protocol layer (`src/homer/run.py`, `learning_curves.py`, `plot_curves.py`)
is retired, and it is retained in place so this directory can be regenerated.
