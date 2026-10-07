# Study 2, noticing a routine changed: report

**Verdict: drop, with a finding that changes the question.** At eight questions a day, the change is
barely visible in the robot's own sightings: neither of two rule-based detectors notices it at the
false-alarm bar, and the language-model notes never say that anyone is ill. Status 2026-10-02
01:25 PDT; counts from stored sightings and notes, no new model calls; blind recount agrees.

## Setup and predictions (written before each count)

SETUP.md 01:04: the brief's surprise count was predicted to detect within a day in eight of ten
households. Addendum 01:12, after the first count: a second rule, persistent new place per object,
was predicted to detect within two days in seven of ten. Both predictions were wrong.

## Measured

Ten households, 31 days, 8 questions a day, change on day 14, sightings from the last-seen cells so
the stream does not depend on a model's choices. Threshold chosen leave-one-out on the other nine
households' days 1-13 for zero false alarm days (the brief's "at most one a month" cannot be met
with fewer than zero on 13 calibration days).

| detector | households detecting (days 14-23) | delay when detected | false alarm days | return alarms (days 24-31) |
|---|---|---|---|---|
| surprise count, last-seen room | 0 of 10 | | 1 (hh_s2) | 1 of 10 |
| surprise count, seven-day commonest room | 3 of 10 | 2, 2, 2 | 2 (hh_s151) | 3 of 10 |
| persistent new place, confirmed by the next sighting | 1 of 10 | 1 | 0 | 1 of 10 |
| persistent new place, confirmed on a later day | 0 of 10 | | 1 | 0 of 10 |
| nightly notes, word match on the text written that night | 7 of 10 have a matching night | mean 3.0, sd 2.5 | 5 of 10 have false matches on nights 1-13 | |

Why the rules fail: settled days already hold 1.5 to 8 "surprising" sightings a day (crockery
between kitchen and dining room at meals, chargers and headphones carried about), with three-day
sums up to 47; the illness adds 5 to 9 movers, and the robot sees only 3 to 6 of them move inside
days 14-23, 0 to 6 confirmed moves a day. For the persistent-place rule the threshold is set by
the first week, when every object's first visit to each ordinary room counts as new. A labelled
contrast that calibrates on days 8-13 only (not the pre-written rule) detects 4 of 10 with delays
0 to 4 and raises warm-up alarms in 4 households: the signal is there but marginal.

Why the notes fail: the words ill, sick, illness, unwell and "not well" occur in no night's text in
any household (checked twice, by the counting script and by a direct search of the files). The
matches that do occur are about one object's place ("The previous belief is no longer supported by
recent evidence", a plate; "It has been on the sink since Day 9", a razor). The notes record
moves; they never record a cause, because the model is never told one and never infers one.

The 50-day run (3 households, 24 questions a day) sees three times as many sightings; the
seven-day-commonest surprise count detects both spells in all three (delays 0 to 2) but raises
return alarms everywhere, and the persistent-place rule detects only in hh_s48, with false alarms.

## Keep or drop

Under the brief's rule the question is whether a method detects within a day of the best rule at
equal false alarms. No method, rule or model, detects reliably, so there is no gap to measure and
the study is dropped as written. What survives is a different and sharper finding: **with eight
questions a day the robot's own looks do not sample the ill resident's rooms often enough for the
change to be seen as a change**, by any method; and the written memory holds no notion of cause at
all. That is a statement about the question schedule and about what the notes contain, not about
detection methods.

## What would reopen it

- More looks (24 a day already triples the signal), or looks chosen to watch the people, not the
  asked-about objects; this is the closed-loop question from the earlier strand.
- Asking the model nightly whether anything changed (the brief's method 3) could still be run, but
  the notes' silence on cause suggests it would name object moves, not a routine change; a
  prediction to write before running it.
- A random change day in new banks does not fix visibility and is not the first thing to do.

## Checkers

- Blind recount (01:24): a fresh agent given only the raw looks.jsonl files and the two rule
  definitions reproduced every threshold, detection, false-alarm day and return alarm in the first
  four rows of the table (surprise count under last-seen; persistent new place confirmed by the next
  sighting), and found nothing odd in the files.
- The "never says ill" claim was checked independently by study-lead with a word search of
  `notes.json` in all ten cells: no match.
- Plan critic: not run (no new run). Leak hunter: not applicable.

## Blocked

Opus (usage file). Nothing else.

Files: `RESULTS_baseline.md`, `RESULTS_baseline2_and_notes.md`, `surprise_count.py`,
`persistent_move.py`, `counts.json`, `persistent_move.json` in this folder.
