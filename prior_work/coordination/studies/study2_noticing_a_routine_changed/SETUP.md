# Study 2, noticing a routine changed: setup, written before any count

Written 2026-10-02 01:04 PDT by study-lead. Nothing below has been computed yet.

## The question

Can a method tell, from the robot's own sightings, that a resident's routine has changed, and how
many days after the change does it say so, at how many false alarms a month?

## Data for the screening (existing, no new banks tonight)

The brief asks for a change "on a random day, without returning". No such bank exists yet, so the
screening uses what is on disk, where the change is on day 14 in every household:
- ten households, 31 days, 8 questions a day: `results/self_improve/overnight_wave/` (illness days
  14-23, return 24-31). Detection is scored on days 14-23; false alarms on days 1-13 and 24-31
  (a return is also a change, so an alarm on days 24-26 is counted separately, not as false).
- three households, 50 days, 24 questions a day: `results/self_improve/wave_the_second_illness/`.
Because every change is on day 14, a method that learned "day 14" would cheat; none of the methods
is told the day, and the surprise-count baseline is tuned on other households, not on the day.
The random-day bank is needed before any keep verdict is final; it is not needed for a drop.

## Baseline (the brief's): a surprise count

A sighting is surprising when the object is seen in a room other than the room the plain rule
would have predicted: its last-seen room (first definition) or its commonest room over the past
seven days (second definition; both are reported). Count surprising sightings per day. Raise an
alarm when the count over a three-day window exceeds a threshold. The threshold is chosen on the
other nine households (leave one out) as the smallest value giving at most one false alarm per
month on their days 1-13; the held-out household is scored with that threshold.

Scores: days from day 14 to the first alarm (14 = same day = 0 days); false alarms per month on
the non-change days.

## Methods under test

1. The nightly notes the log-and-notes method already wrote (`notes` in each cell): a reader
   decides each night whether the note says the routine changed. First pass is a word match
   (ill, sick, unwell, changed, no longer, used to, now stays), second pass a local Qwen judge
   reading only that night's note. Detection day = first night the note says so.
2. The told arms are excluded: they were told.
3. A new nightly prompt ("has anyone's routine changed? answer yes/no and name who") is only
   written if 1 is within reach of the baseline; it needs new model runs.

## Prediction

The surprise count detects on day 14 or 15 (0 to 1 days) in at least eight of ten households at
one false alarm a month or fewer, because most of the resident's things change their daytime
spot on the first sick day and 8 questions a day look into several rooms. The nightly notes
mention the change within 1 to 3 nights in most households but not all; the Qwen judge will not
beat the surprise count by a day. Expected verdict: drop, with the note that the notes do record
the change, just not earlier than counting does.

## Size and detectable gap

Ten households for the 31-day data. Days-to-detect is one integer per household per method; the
paired difference over ten households has a standard error of roughly 0.3 to 0.6 days if the
spread is one day, so a one-day difference is at the edge of two standard errors. False alarms are
counted over 21 non-change days per household, 210 in all.

## What would reopen the study after a drop

A random change day in new banks, a change that moves few things (so the count is weak), or a
change in who is at home rather than where things are.

## Addendum, 01:12 PDT, written AFTER the first count (RESULTS_baseline.md) and before the second

The brief's surprise count failed as a detector: 0 of 10 households (last-seen definition) and 3 of
10 (seven-day-commonest definition) at the one-false-alarm bar, because settled days already
hold 1.5 to 8 surprising sightings a day (crockery and bottles between kitchen and dining room at
meals), with three-day sums up to 47, while the illness adds at most 5 to 9 movers. My prediction
("detects within a day in eight of ten") was wrong: I counted movers, not the background.

A weak baseline must not be the thing a model is measured against. So a second rule-based
baseline is added, chosen for being the obvious next thing a person would try, and its prediction
is written here before it is computed:

**Baseline 2, persistent new place per object.** For each object, a sighting is "new" when its
room has had no sighting of that object in the previous seven days. An object "has moved" on the
first day on which it has two consecutive sightings in a new room (the second sighting confirms
the first). Alarm when at least k objects have moved within a three-day window, with k chosen
leave-one-out on the other nine households as the smallest value giving zero alarm days on their
days 1-13. Also reported: the same with the confirming sighting required to be on a later day.

Prediction for baseline 2: detects within 0 to 2 days in at least seven of ten households at
zero false-alarm days, because the illness movers stay in their new rooms for ten days and the
robot looks into those rooms on day 14 in nine of ten households, while meal-time moves do not
persist across two consecutive sightings in a room the object never used in the past week.
Return alarms are expected in most households, since the return is a change of the same size.

**Method under test, first pass (existing notes).** The nightly notes of the log-and-notes
cells: the first night whose note contains any of (ill, sick, unwell, not well, resting, changed,
no longer, used to, now stays, now keeps, since) applied to a resident or an object. Days from
day 14 to that night; false mentions on nights 1-13. This is a word match and will over-count;
it bounds what a reader of the notes could know, not what the model inferred.

If baseline 2 detects as predicted and the notes do not mention the change sooner, the study is
dropped and the brief's baseline is reported as too weak to be a baseline. If baseline 2 also
fails, the change is not visible in the sightings at all under this question schedule, and no
method can be expected to see it; that is a finding about the simulator, reported as such.
