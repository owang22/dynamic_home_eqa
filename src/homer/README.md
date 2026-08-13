# homer/ — HOMER+ baseline harness (pilot)

Non-LLM baselines on HOMER+ producing the two pilot tables: **E1**
(standard localization) and **E2** (held-out object generalization). The
pilot exists to test whether persona-conditioned prediction can beat
per-object and pooled statistical models on objects never observed —
these are the floors that claim must clear.

**Package location deviation**: the brief's `src/baselines/` was already
occupied by the sense-or-answer bank-health instrument; this harness
lives in `src/homer/` instead.

## Acquisition

`git clone --depth 1 https://github.com/Maithili/HOMER_PLUS third_party/HOMER_PLUS`
(4.3 GB, gitignored). Patel, Prakash & Chernova, *Predicting Routine
Object Usage for Proactive Robot Assistance*, CoRL 2023. The canonical
traces derived from it (~150 KB) ARE committed, so all results reproduce
without the clone.

## Canonical trace format (`data/homer_traces/`)

`object_id, timestamp, receptacle_id, household_id, day_index, split` —
change-points of a piecewise-constant state; timestamps in minutes from
midnight (the dataset's native anchor; days are self-contained scripts).
Receptacle = nearest non-movable ancestor, chosen by specificity (room
only as a last resort). Full rules in `loader.py`'s docstring. Held-out
masks (`heldout_masks.json`) and the inventory are separate artifacts;
rows are never deleted. `tests/test_homer_loader.py` asserts row counts
against the independently-computed inventory and pins receptacle counts.

## Protocols (`protocol.py`)

Queries: hourly on the hour, 07:00–23:00, every object, every test day.
**No test-day observations are ever fed to a method** — with change-point
rows, feeding them would make the persistence floor an oracle. E1 trains
on all 65 train days. E2 withholds k=2 mover objects entirely (5 seeded
draws per household); every method receives the held-out object's
day-0 initial placement as a static fact, and nothing else about it.

## Baselines (`baselines.py`, `fremen.py`)

All expose `predict(object_id, t) -> {receptacle: prob}`; each docstring
states its E2 fallback. Floors: `uniform`, `persistence` (E2: initial
placement), `modal` (E2: initial placement blended 50/50 with pooled
receptacle popularity — documented choice over uniform). Per-object:
`frequency` (hour-conditioned, shrunk to the object's overall habit),
`markov` (first-order hourly chain, Laplace 0.5, run forward from the
modal 06:00 state), `fremen` (below). Pooled cross-object: `pooled` —
P(receptacle | initial_receptacle, hour) shared across objects with
per-object empirical-Bayes deviation (m=12); under E2 it backs off to the
pure pooled component.

### FreMEn

Per (object, receptacle) binary occupancy as mean + top-2
highest-amplitude components from the paper's harmonic candidate set
(24 h/k plus 7-day/k), normalized across receptacles at query time.
Deviations from Krajnik et al. (T-RO 2017), each with a reason, in
`fremen.py`'s docstring — the substantive ones: HOMER+ supplies complete
state so uniform projection is exact (no sparse-visit machinery), and a
**Nyquist guard** drops candidates with periods ≤ 2× the sampling step.
The guard exists because without it the hourly grid aliased spurious
amplitude onto 1 h/0.5 h candidates and understated FreMEn's E1 by a
point — exactly the silent-underrating failure the validation
requirement anticipates. `tests/test_fremen_synthetic.py` recovers known
periodicities, survives 40% observation gaps, and ranks a two-frequency
signal correctly. Recovered spectra: `reports/homer_spectra/` (24 h
dominant, 12 h second, weekly ≈ 0 in all three households).

## Results

`results/raw_results.csv` (regenerate: see below; gitignored at 11 MB) is
the single source of every number; `results/tables.md` holds E1/E2.
Unit of analysis is the household (n=3) — aggregates are descriptive, no
CIs. E2 reports mean [min–max] over the five held-out draws.

## Reproduction

```bash
PYTHONPATH=src python -c "import pathlib; from homer.loader import write_traces; write_traces(pathlib.Path('data/homer_traces'), seed=0)"
PYTHONPATH=src python -m homer.run --out results   # ~2 min
PYTHONPATH=src python -m homer.spectra
PYTHONPATH=src python -m pytest tests/test_homer_loader.py tests/test_fremen_synthetic.py -q
```

## Limitations

n=3 households; ~90% of object-hours are spent at an object's home base,
so E1 top-1 saturates near 0.95 and top-3 is uninformative (~1.0 for all
methods); E2's shared fallback makes all per-object methods identical by
construction on held-out objects (see `results/tables.md` and the pilot
report for what that implies); HOMER-Noise and original-HOMER variants
not yet loaded.
