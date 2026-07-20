# E1 v2 pilot on gpt-5.4-mini (observation-history memory + proper scoring)

**Status: pilot, not the reportable pass** (reportable axis = local Qwen). This
run validates the v2 harness redesign and looks for preliminary patterns. n is
small per cell (typ 12/cell over 3 households, atyp 4/cell over the 1 night_shift
household) — directional only. 168 grid episodes + 3 comprehension probes, 0
API/parse errors. Cost: 369,567 in + 29,096 out tokens (mini). Raw:
`rows_gpt-5.4-mini.jsonl`, `probes_gpt-5.4-mini.json`, `summary_gpt-5.4-mini.md`.

What changed from v1 (all researcher-directed): memory is now the frozen bank's
**multi-day observation history** (2–4 jittered snapshots/day, the *same* stream
every arm reads) instead of last-seen; output is a **top-3 distribution** scored
by **Brier/log-loss**; "atypical" is now a **real night-shift household**
(night_shift_typ_v1), not a phase-shift artifact; and there are **comprehension
probes**.

## 1. The comprehension probes settle the diagnosis

| probe | blatant-from-history answer | mini | p(true) |
|---|---|---|---|
| static object (vase, never moves) | table_d1 | ✓ | 0.97 |
| immediate parrot (toaster seen 10 min ago) | counter_k1 | ✓ | 0.99 |
| periodic (mug at sink every day ~10:00) | sink_k1 | ✓ | 0.72 |

**3/3, at high confidence.** mini reads the history, tracks static objects,
uses fresh observations, and reads a daily periodic pattern. So the failures
below are **not** task-comprehension — and no prompt revision was the honest
fix. Per your framing: passing these + scoring near-zero on genuinely-moved
episodes localizes the failure to **forecasting unrecorded movement**.

## 2. The C1 adaptation curve now appears (the memory fix worked)

Accuracy vs history-days (profile_text=False):

| bank | D=0 | D=1 | D=3 | D=7 | D=14 |
|---|---|---|---|---|---|
| typ_v1 (3 typical) | 0.42 | 0.50 | 0.17 | 0.33 | 0.58 |
| **atyp_v1 (night_shift)** | 0.25 | 0.25 | 0.25 | **0.50** | **0.75** |

The atypical household climbs 0.25 → 0.75 as observation history accumulates;
the typical set stays flatter (0.42 → 0.58, noisy). This is the C1 shape —
in-context observations help *more* in the atypical home the prior misfits — and
it was invisible under the v1 last-seen memory (which showed noise). Your
jittered-snapshot fix is what surfaced it. (Caveat: atyp n=4/cell — one
household; needs the roommate/family atypical counterparts and more seeds.)

## 3. Calibration (Brier/log-loss), and the persistent moved-episode wall

- Brier improves with history on the atypical home (0.756 → 0.441).
- **Moved vs not-moved (pooled D≥1): not-moved 0.58–0.63 acc, moved 0.06 (typ) /
  0.25 (atyp); moved Brier 1.14 vs 0.60 not-moved.** When an object moved since
  its last snapshot, mini is both wrong and poorly calibrated.
- log-loss is spiky (a few confident-wrong predictions dominate the mean, e.g.
  8.3 at one atyp D=1 cell); read Brier as the stable calibration number and
  log-loss as an outlier-sensitive companion.

## 4. Read of the pilot

The redesign delivered what it was meant to: (a) comprehension is established
(3/3 probes), so (b) the moved-episode failure is cleanly attributable to
forecasting, not prompting; and (c) with a real observation history the C1
adaptation signal emerges (atyp 0.25→0.75). The profile-prose effect from v1 is
muddier here (mixed, tiny cells) — the richer history likely dilutes it; defer
judgement to the Qwen pass with more seeds.

**Next:** Qwen reportable pass (GPU); author roommate/family atypical
counterparts so atyp_v1 has n>4/cell; then E2 (one-shot prior help/harm) on this
substrate — the harness, banks, scoring, and probes are ready.
