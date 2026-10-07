# Harness gotchas found while running the memory study (2026-09-21/22)

- **`--workers` in `baselines.patrol.llm` parallelises across ARMS, not within one.** Jobs are the cross product
  bank × memory × told × look, so `--bank ONE.jsonl --memory naive --told told --workers 8` is a SINGLE stream.
  To parallelise, pass many banks (or many memories) in one invocation. Cost us ~2 h before it was noticed.
- **Order the two message arms in phases, not per household**: run every start-message arm first, then every
  start+end arm. The second phase replays days 1-23 from the cache the first filled (~130 new calls per
  household instead of 496) and still gets full parallelism.
- **Prompt prefix**: the server's KV blocks are 784 tokens (Mamba-hybrid alignment), so a prompt whose static
  header comes first (~900 tokens) hits the prefix cache; with the time-varying "Now:" line first, hit rate is 0%.
  `--enable-prefix-caching` is NOT on by default.
- **`--max-num-seqs` defaults low (8 here)**: raising it to 64 was a ~4x throughput change on its own.
- **FlashInfer sampler misdetects the sm_120 GPU from a bare shell**: export `VLLM_USE_FLASHINFER_SAMPLER=0` or
  the engine dies in the profile run with "FlashInfer requires GPUs with sm75 or higher".
- **Greedy decoding is not bit-reproducible across batch compositions** on vLLM; each run's own prompt cache
  replays exactly, so keep the cache with the run.
- **Bank buildability is a household property**: a day where the resident draws a tidying mood plus a restless
  evening leaves every target object in hand at every candidate moment, so `activity_question_rows` finds zero
  sensable candidates and the build fails. Seeds 12 and 15 of the F1 regime are unusable for this reason.

## Reporting conventions (agreed with the companion study, 2026-09-22)
- **Contrasts**: mean of paired per-household differences, with its standard error and n. **Detected** at >= 2 se.
  The sd is reported beside it as between-household heterogeneity, never as the test. Below n=6 use the stricter
  bar (effect must exceed the spread) and name the rule in force.
- The spread bar is **stricter** than the 2-se bar for n >= 5 (the spread is sqrt(n) standard errors), so moving
  to the 2-se bar can only add claims; nothing stated under the old rule loses standing.
- **Levels**: mean of per-household values, every household weighted equally, over households with at least 10
  answers in that cell; print the household count. Same weighting as the contrasts, so a level can never move one
  way while its contrast moves the other, and the largest household cannot dominate a cell.
- Beware the winner's curse on the first sample: our return-day numbers halved when eight fresh households were
  added (-11.3 -> -7.0 all questions), while the in-spell effect replicated (+36.3 -> +29.5 cold).

## Degeneracy assay (standing practice, 2026-09-22)
`tools/assay.py` runs over every finished arm and flags: top-answer share **relative to the truth's own
concentration** in that arm (ratio > 1.6), repeated consecutive answers (> 85%), confidence sd < 0.02 or fewer
than 4 distinct values, confidence that carries no signal (accuracy above vs below the arm's median confidence
differs by < 5 points), and parse failures. Inspect the first ~30 rows of any new arm before launching the rest.
- **Use task-relative thresholds.** An absolute "one answer > 50% is degenerate" rule fired on half these arms,
  because households genuinely have objects that sit at one spot most of the day. Noisy assays get ignored.
- **The discrimination check is the one that catches a constant-output arm**, not the concentration check.
- Result on this study's 90 arms: no degenerate arm, 2 parse failures in ~60,000 calls (both counted as errors).
- A suspiciously constant metric is a bug until proven otherwise: our LLM confidence is 0.87 in every stage,
  which turned out to be real — it varies (sd 0.10-0.14) and discriminates (+21 to +42 points) *within* a stage;
  only the stage mean is flat. Checking it sharpened the claim rather than killing it.
