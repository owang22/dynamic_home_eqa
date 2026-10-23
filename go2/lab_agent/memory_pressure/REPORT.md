# Memory pressure, offline replay (2026-10-23)

**Search survives keeping 9% of the pictures; the history of changes does not.**

- **Search:** keeping 100 of the 1,109 pictures by novelty still finds a relevant picture in the top 5 for 0.89 of
  the labelled queries. Keeping everything scores 0.94.
- **History:** with only one level, no policy keeps more than about a third of object moves with a view both before
  and after.
- **Levels fix it:** described key views in L1 and cheap history in L2 keep every move, in 11 MB instead of 39 MB.

Run: `CUDA_VISIBLE_DEVICES= python3 go2/lab_agent/memory_pressure/run.py [--selftest]`. It takes about 45 s on CPU
and reads `go2/data/lab_agent/` without writing to it. Outputs go to `go2/data/memory_pressure/`:

| file | contents |
|---|---|
| `results_offline.json` | all scores below |
| `features.jsonl` | per-picture features for a learned scorer |
| `recall_coverage.png` | the three panels |

## Setup

- **Replay:** the pictures in time order. Each policy's `observe(i)` must keep L1 within its budget after every picture.
- **Levels:**
  - L1: picture, description and embedding.
  - L2: embedding and a one-line summary, about 7 KB.
  - Anything else is dropped.
- **Search:** `M.search` itself, with picture scores from the stored SigLIP embeddings.
- **Grid cells:** 1.5 m × 45°.
- **Query score:** a relevant picture, or a near-copy of one (cos ≥ 0.95), in the top 5. 35 of the 40 queries have
  labelled pictures.

## Results

Query score by number of L1 pictures kept; coverage and size at 100 kept.

| policy | 25 | 50 | 100 | 200 | objects with a kept picture @100 | moves with before and after @100 | MB @100 |
|---|---|---|---|---|---|---|---|
| keep all 1,109 | | | | 0.94 | 1.00 | 1.00 | 39.4 |
| uniform in time | 0.43 | 0.69 | 0.66 | 0.86 | 0.25 | 0.16 | 3.6 |
| newest first | 0.37 | 0.54 | 0.74 | 0.83 | 0.17 | 0.00 | 4.6 |
| place × heading grid | 0.54 | 0.77 | 0.80 | 0.89 (146 kept) | 0.23 | 0.10 | 4.0 |
| novelty | 0.51 | 0.66 | **0.89** | **0.91** | 0.25 | 0.10 | 4.5 |
| change-aware | 0.54 | 0.77 | 0.83 | 0.91 (146 kept) | 0.23 | 0.10 | 8.9 with L2 |
| tiered (search L1+L2) | 0.94 | 0.94 | 0.94 | 0.91 | — | **1.00** | 11.0 |

- **Change-aware is not detecting change.** The list of described objects changes by more than half on 604 of 963
  revisits of the same spot, mostly from description noise. In practice it behaves like the newest-per-spot grid.
  It also needs every picture described first: 1,109 description calls.
- **Novelty decides from the embedding alone,** so only the pictures it keeps need describing.
- **The simple per-picture scores don't pick out useful views.** The 20% most novel pictures contain no more
  move or disappearance views than average.

## Limits

- **The labels are partial:** they were made from a pool of about 40 candidates per query.
- **The data is three days of mostly trail pictures,** with no staged changes and no questions about time.
- **Today's staged patrol is the real test:** known changes, and questions about time asked of Opus.
