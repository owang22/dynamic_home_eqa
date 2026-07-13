# Prompting Infrastructure — Phase 1 checkpoint P1b (judge baseline)

The number Phase 2 has to beat. Judge scores measured against the 48-item
EVAL set (human-labeled bands; the 12 EXEMPLAR items are held out of every
metric). Per-config detail in `results/reports/judge_harness/{asis,strict,
strict_thinking}.md`; side-by-side index in `judge_harness/INDEX.md`.

## Baseline — current judge variants on EVAL

| config | Spearman ↑ | exact band | **over-scored** | under | mean score @ human band 0/1/2/3 |
|---|---|---|---|---|---|
| **strict** (default) | 0.75 | 58% | **29%** | 12% | 0.23 / 0.38 / 0.55 / 0.82 |
| strict + thinking | **0.79** | 46% | 48% | 6% | 0.32 / 0.55 / 0.73 / 0.85 |
| asis | 0.64 | 54% | 35% | 0.45 / 0.40 / 0.60 / 0.88 |

(Spearman = rank correlation of judge score vs human band. "over-scored" =
fraction where the judge's predicted band exceeded the human's — the judge's
known failure mode. mean@band = mean judge score within each human band;
monotonic increasing with separation = good.)

**Take `strict` as the baseline to beat: Spearman 0.75, 29% over-scored.**
It is the best-*calibrated* variant — highest exact-match, lowest
over-scoring, and cleanly monotonic band separation (0.23/0.38/0.55/0.82).

### What each variant gets wrong

- **strict** separates the bands but **won't use the bottom of the scale.**
  Of 10 human "absurd" (band-0) items, it predicts band-0 for only 4 and
  inflates the other 6 to band-1; nothing human-rated absurd is scored below
  0.15. The worst misses are exactly the "shouldn't move at all" objects the
  labeler flagged — `vase on cabinet @ sleeping` (human 0, judge 0.4),
  `potted_plant → bedroom @ sleeping` (human 0, judge 0.4). It also leaks
  band-2 up to band-3 (3 of 13).
- **strict + thinking** has the best *ranking* (0.79) but the worst
  *calibration*: it shifts every score up (48% over-scored, band-0 mean
  0.32). Thinking improves order, not absolute placement — useful only if
  paired with something that pulls the scale back down.
- **asis** is broken at the low end: its band-0 mean (0.45) is **higher**
  than its band-1 mean (0.40) — it scores "absurd" above "contrived,"
  non-monotonic. Confirms asis should not be built on.

### Dinner-laptop archetype (the case the exemplars must fix)

All four laptop-on-an-eating-surface EVAL items are **over-scored by strict**:
`laptop @ eating_breakfast` human 2 → 0.8 (band 3); `laptop @ lunch` human 1
→ 0.7 (band 2). Note the labeler rates *phones* at the table as plausible
(band 2–3: "as a teen Emily uses her phone more"), so the real miss is
laptop-specific, not all electronics — the exemplars should teach that
distinction, not a blanket "electronics at meals = bad."

## Cross-cutting conclusion

Every variant **over-scores, concentrated at the low bands** — the judge
rarely reaches for the 0.0–0.2 "absurd/contrived" range the labeler used
freely (the human called 13/60 absurd; strict predicts absurd ~half as
often). This is the single biggest lever for Phase 2: context + low-band
exemplars (vase/plant/candle "doesn't move", laptop-at-meal) should pull the
bottom of the scale down and lift Spearman.

**Judge-score sampling noise:** the same strict judge scored Spearman 0.84 on
the generation-time scores but 0.75 on this fresh re-score (temperature 0.7,
different seed under the versioned tag). Single-sample judge scores are
noisy — direct motivation for Phase 2.3's k=3 self-consistency.

## Infra state entering Phase 2

- **Labeled set + split** — `results/judge_label_set/`:
  `labeled_candidates.csv` (60, human bands), `split_manifest.json` (seed 0:
  48 EVAL / 12 EXEMPLAR, 3 per band, includes a dinner-laptop case, no
  leakage). Human vs. machine on the full 60: 60% exact, **37% machine-higher
  vs 3% lower.**
- **Harness** — `scripts/judge_harness.py` + `dynamic_home_eqa/judge_eval/`
  (labels, metrics, harness). Re-scores EVAL in each candidate's real
  activity-batch context, through the normal cache; writes a per-config
  report and an accumulating index. `--config baseline` reproduces this table
  for free (cached).
- **Prompt versioning** — `generation/prompt_registry.py`: all 7 system
  templates relocated byte-identical, each with an auto sha256 version folded
  into its stage tag (e.g. `realism_strict_p84389307_b1`); `BUILDER_VERSION`
  covers hand-assembled user prompts. Phase-2 prompt variants get new hashes
  → clean cache splits by construction.
- **Judge robustness** (from P0, extended here): empty/partial/truncated AND
  now key-renamed (`realism_score`) thinking-judge outputs all degrade to a
  logged fallback; none can crash a run.

**STOP — Checkpoint P1b. Awaiting review before Phase 2 (context + exemplars
+ self-consistency, measured against this table).**
