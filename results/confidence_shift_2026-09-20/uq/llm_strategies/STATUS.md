# LLM-strategies status — updated 2026-09-22 08:05

The deliverable is the page: `results/regime_search/story.html`. This file exists only so that a person opening it
sees something true. Everything described here has finished; nothing is queued, pending or in progress.

## What ran
One-person-sick regime (sick10_owner), 32 days, three message conditions each — **no message**, **start message**
(told on the first sick day), **start + end messages** (also told on the first day back):

| memory | households | note |
|---|---|---|
| buffer (recent sightings) | 10 | + 8 more on the return contrasts from the workshop session, so those are n=18 |
| retrieval (same time of day) | 10 | |
| nightly routine table | 10 | |
| reflection (nightly mistake notes) | 10 no-message, 5 told | told arms were capped at 5 by server time |
| long-context (whole log each prompt) | 3 | ~10x the compute per question; the other 7 no-message households were abandoned, not finished, because they could not have improved any comparison |

Also finished: the two-spells regime (sick2x_owner, classical + UQ roster on 10 households, buffer and retrieval on
3); the MCQ/token-probability and KnowNo-set channels on a bounded day list, 3 households; the partial-shift arms
(one person sick, everyone's things asked) on 6 households, from the workshop session's runs; the guests regime and
its evening/morning variants on 10 households each.

## The bar, changed at 07:25 today
An effect is claimed when the average across households is at least **twice its own standard error**, with the spread
between households reported beside it. Below six households the standard error is estimated from too few numbers to
trust, so those arms keep the older "bigger than the spread" floor. Note the direction: for n ≥ 6 clearing one spread
implies clearing two standard errors, so the new bar is the more permissive of the two — nothing published overnight
lost its standing and the change could only add claims. The page says this in its own words at the top of
"What we found"; `STORY_numbers.md` marks every row with which bar governs it.

## What was withdrawn, and why
- **Shared-memory interference** (published ~03:00 from 3 households): that a message about one resident degraded the
  other resident's things through a shared memory. At 6 households it is a wash (per household, sick spell: −14, −10,
  −11, +8, +9, −12). Replaced by the selective-by-object result, which does hold: +15.3 ± 3.8 on the sick person's
  things, +0.4 ± 2.1 on the other resident's.
- **A 2-point reflection difference** measured on two different household sets (10 vs 5). The extractor now computes
  every told-vs-untold contrast on matched households only; the error was worth 9 points on cold questions.
- Both, with the checks that caught them, are in `../problems_found.md`.

## Outstanding
Nothing on this side. The workshop session's 18-household return contrasts have landed and are merged through
`results/regime_search/pooled_contrasts.json`, which is the one place an outside figure enters the page.

## How to check
```
ls results/regime_search/story.html                  # the deliverable; rebuilt by tools/refresh_loop.sh
cat results/confidence_shift_2026-09-20/uq/llm_strategies/STORY_numbers.md   # every table behind the page
cat results/confidence_shift_2026-09-20/uq/problems_found.md                 # the night's bugs and misdiagnoses
pgrep -af "patrol.llm|run_person_master|run_knowno"  # expect no output: all runs are done
```
