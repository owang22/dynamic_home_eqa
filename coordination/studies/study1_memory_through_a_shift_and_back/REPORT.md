# Study 1, memory through a shift and back: report

**Verdict: drop under the brief's rule, on the data already on disk; one slice is flagged for Oliver.**
Status 2026-10-02 01:06 PDT: computed from existing runs, no new model calls; blind recount agrees on
every number; the Opus check is blocked (see "What blocked the work").

## The setup this report scores

The 50-day second-illness run (`results/self_improve/wave_the_second_illness/`) is the design the
brief asks for: resident 1 is ill on days 14-23, back on 24-31, ill again 32-41, back again 42-49.
Three households (hh_s2, hh_s32, hh_s48, bank `all_generated_v2_twice`), 24 questions a day, every
method asked the same questions. Perfect perception (a thing is seen if its room is looked into).
Main score as the brief defines it: first guess right on days 1-5 after each return (days 24-28
and 42-46), pooled; 240 questions per household, 720 in all.

## Prediction, written before the count

Written 2026-10-02 00:56 by study-lead, before `coordination/study1_from_existing_runs.py` ran:
"The submitted draft found last-seen beats every summary-only memory and that the raw record closes
the gap rather than exceeding it. Prediction: no method beats last-seen by 10 points on the pooled
score; the second return is where a memory method might lead, by under 10 points overall and more
on moved objects."

## Measured

Paired per-household difference against last-seen, points of first guess right (n = 3 homes):

| method | days 24-28 | days 42-46 | pooled | pooled 2 SE | separated |
|---|---|---|---|---|---|
| log and notes (the raw record plus nightly notes) | -0.3 | **+7.5** | **+3.6** | 1.5 | yes |
| told the night before (log and notes, told of the illness) | -2.8 | +5.6 | +1.4 | 2.4 | no |
| ACE-style playbook, merge step fixed | -13.1 | -1.4 | -7.2 | 1.4 | yes, below |
| plain claim store | -20.8 | -7.8 | -14.3 | 2.0 | yes, below |
| last-seen with the first illness deleted from its trail | -1.9 | 0.0 | -1.0 | 1.5 | no |

Last-seen itself: 89.7% on days 24-28, 86.7% on days 42-46, 88.2% pooled.

The best non-baseline method beats the best baseline by **3.6 points pooled**, against a bar of 10.
The smallest gap this setup separates on the pooled score is 1.5 to 4.5 points, so 10 would have
been detectable; the gap is simply not there.

Where a 10-point gap does exist, on a slice the brief did not name:

| slice, days 42-46 only | log and notes over last-seen | 2 SE | questions per home |
|---|---|---|---|
| all objects | +7.5 | 1.9 | 120 |
| objects that moved in the first illness | +12.4 | 2.4 | 40 to 74 |
| objects that moved in both illnesses | +16.5 | 11.3 | 29 to 33 |

Same sign in all three homes. This is the "retained knowledge" result of the submitted draft:
after the second return, a method that kept the sightings from the first illness is less wrong
than one that did not.

## Why drop, and what would reopen it

The rule was written for the pooled score on days 1-5 after each return, and on that score the
gap is 3.6 points. Choosing the second-return mover slice now, after seeing it, is the winner's
curse the brief guards against. The baseline the brief names, recency-weighted last-seen, has not
been computed; it can only shrink the gap, never widen it.

To reopen the study honestly: write the mover-slice, second-return score as the main score
beforehand; compute recency-weighted last-seen first (its inputs, every sighting with room and
time, are in each cell's `looks.jsonl`; `paper/scripts/last_seen_without_the_first_illness.py` shows
the no-model rerun pattern, 3 to 4 s per household); run the 50-day bank on the other seven
households, since with three homes the both-spell slice has a 2 SE of 11 points and cannot
separate anything under that.

## Opus and Qwen

Qwen (local, the 50-day run): the numbers above. Opus: not run. The brief makes Opus subagents
conditional on a usage file under an hour old, and the file cannot exist until the status-line
setting is added (see below). Opus subagent calls used: 0.

## Checkers

- Blind recount (01:06): a fresh agent given only the raw `searches.jsonl` files and the scoring
  rule reproduced every count, share, paired difference and standard error in the tables above,
  for all rows and for the mover slice, and confirmed the question sets are identical across
  methods (120 rows per window per household, 1,176 search rows per file, no duplicates).
- Plan critic: not run, because no new run was made.
- Leak hunter: not applicable to a count of stored answers.

## What blocked the work

- `coordination/usage.json` does not exist; the status-line setting in `~/.claude/settings.json`
  can only be added by Oliver (the script is `coordination/usage_statusline.py`). Until then no
  Opus subagents, by the brief's own rule.
- Four of the brief's named methods are not in the 50-day run (prior-only, reduced claim store,
  working memory and archive, log-only); they exist only on the 31-day ten-household bank.
- Rerun noise: a model method rerun against itself moves 1.9 points in a settled window and 2.5 to
  6.2 in a change window; last-seen has no such noise. Differences of a few points that clear 2 SE
  are still inside that floor.

Numbers: `coordination/study1_from_existing_runs.md`, produced by
`coordination/study1_from_existing_runs.py`.
