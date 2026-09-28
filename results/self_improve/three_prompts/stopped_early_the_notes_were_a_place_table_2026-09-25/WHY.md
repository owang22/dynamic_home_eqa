# Stopped early, by decision: the notes were a worse copy of a file we already have

Stopped 2026-09-25 on Oliver's instruction, with phase 1 warming 25 of 70 cells and no
full-month cell finished. **These cells are partial by DECISION, not by failure.** Nothing
here failed a gate; the wave was cut because the comparison below made four more hours of
GPU not worth spending. Nothing was deleted.

One cell continues: `control` on `hh_s2_t03`, the plain claim store, to day 31, because the
six variants are now a baseline rather than the experiment and one cell of one of them is
enough to show it.

## The four numbers that stopped it

Counted over all **1,906 claims** the claim-store arms wrote:

| | share |
|---|---|
| name a place | **91%** |
| mention any time, condition or change | **0.3%** |
| record their condition as the single word `"current"` | **99%** |
| cite even one piece of evidence **against** themselves | **0 of 1,906** |

The contradicting-evidence list is empty in every claim in every arm.

And the comparison that follows from it. Answering straight from the observation record, with
**no model at all**, gets the first room right for:

| | settled period | after the return |
|---|---|---|
| straight from the observation record, no model | **72%** | **70%** |
| every arm that writes notes | 44–52% | 44–52% |

So the notes are a **worse copy of a file the robot already has**. No prompt variant layered
on top of that comparison can change it, which is why the remaining variants were not worth
running to completion.

## What is in here

* `cells_from_the_repo_run/` — the partial full-month cells from the cap-12 wave.
* `phase1_warming_cells_nights_0_to_3/` — the phase-1 warm-up, nights 0 to 3 only. Its
  purpose was to make night 1's large generation where it fits inside the client's
  600-second socket limit so a fast phase 2 could replay it from the prompt cache. Phase 2
  never ran. **The completions it made are still in the prompt cache**, so any future wave on
  the same prompts gets night 1 free.
* the heartbeat and launcher logs for both.

## What from tonight is NOT affected

All three are measurements of the prompts and of what the writer did with them, not of how
well any arm performed, so none depends on the wave finishing. They stay in
`results/self_improve/three_prompts/`:

* **The compliance table.** The set-aside share moving from 12% in the control to 62% and
  88% under the rival-beliefs prompts, and the paired add-and-set-aside moving from 0 to 4
  and 5 — so that variant was complied with, whatever its outcome would have been. Also that
  half the control's set-asides replaced the readable wording, which an audit counting
  standings would have scored as non-destructive.
* **The rerun noise floor** (`the_rerun_noise_floor.json`). `control` and `told_unwell` are
  given byte-identical prompts on days 0–13, so that window is the same experiment run twice:
  1.5 to 2.2 points mean absolute difference on the accuracy and find-rate measures, up to
  7.3 points in the worst home, answer agreement as low as 68.8%. The cleanest demonstration
  is one prompt, one cache key, two different recorded answers.
* **The mechanism findings** (`MECHANISM_NOTES_BEFORE_THE_OUTCOMES.md`), in particular that
  96.3% of the first 270 claims recorded `holds_under` as exactly `"current"` and none named
  a routine — which is the same finding the 1,906-claim count above confirms at seven times
  the sample.

`DRAFT_a_variant_that_asks_for_a_real_condition.md` is **superseded** and was never launched.
The direction it belonged to has changed: the replacement lets the robot read its own
observation record when asked, and forbids its notes from saying where anything is, so the
notes must hold what a record cannot.
