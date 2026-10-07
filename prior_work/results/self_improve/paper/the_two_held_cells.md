# The two cells a gate held back, and why they are on the page anyway

Written 2026-09-28, after a subagent's audit found them shown as ordinary complete cells.

## What they are

`results/self_improve/overnight_wave_24_questions/cells/MemGPT_as_published/hh_s32_t03` and
`.../hh_s48_t03`. Both ran the full 31 days and recorded all 744 questions. Each was held by the
"a completion that did not parse" gate, and each cell's own `why.txt` says why:

> hh_s32_t03/MemGPT as published: the completion did not parse on nights [8], so those nights
> wrote nothing while the call SUCCEEDED

> hh_s48_t03/MemGPT as published: the completion did not parse on nights [6], so those nights
> wrote nothing while the call SUCCEEDED

One night each. The night's model call returned, the text did not parse, so the memory was not
updated that night and nothing in the run reported a failure.

## Why the page could not tell

`run_one_cell` writes `cell.json` and *then* the gates run; a held cell's file is renamed to
`cell_HELD_FOR_REVIEW.json` (`overnight_wave.py:265`). But the page decides a cell is finished by
`maxday >= lastday`, which a held cell passes — it did reach its last day. And the rebuild's skip
list covered only `superseded_` and `stopped_early_` trees. So both cells arrived on the page with
full traces and no mark.

A stale comment helped it along: `overnight_wave.py:40` said a held cell becomes
`cell_REFUSED.json`. That name belongs to a different gate, in `three_prompts.py:366`. Anyone
checking the page against the documented name would have found nothing. Corrected.

## The decision: shown, and labelled

Kept rather than excluded. Excluding them would have hidden a failure the study means to report,
and the rule this page was built on is that it cannot hide a run. What changes is that they are
now named:

- `rebuild_the_artifact.py` reads `cell_HELD_FOR_REVIEW.json` and the first line of `why.txt` into
  a `held` field on the cell, and no longer counts a held cell as finished. The rebuild now prints
  **252 cells (250 finished, 2 HELD BY A GATE)**.
- `live_runs.html` prints a warning above the reading whenever a held cell is among the ones being
  read, giving the household, the arm and the gate's own words.

## The rate, counted rather than quoted

`the_completion_did_not_parse` across every cell on disk: **2 nights of 7,431 with a note-writing
call, 0.03%** — one in `MemGPT_as_published/hh_s32_t03`, one in `.../hh_s48_t03`, and none anywhere
else. Both are the two held cells; no other cell in the study has a single unparsed night.
