# Where current agent memories fall short when a household routine changes — the overnight story (draft 01:00, 2026-09-22)

For AI researchers. Every number is from the one-person-sick testbench (10 simulated households, 32 days: a settled
lead-up, one resident off sick for days 14–23, then normal life again) unless a section says otherwise. A robot answers
"where is X?" about that resident's everyday things while they are in use and learns the truth ten minutes later.
"Cold" = the first question about an object on a given day, before that day's feedback — the honest measure of what a
memory holds. Live tables (regenerated every 20 min as arms land): `STORY_numbers.md`. The page Oliver reads is
`results/regime_search/story.html`; its "What we found" box is the short form of this file.

Arms that are still running are marked; their numbers move a little as the last households land.

## (a) Every memory breaks at the shift; who re-learns inside it, who breaks again on the return

The break is the size of the routine change, not a property of any one memory: from the settled lead-up (days 9–13)
to the first three sick days, the 3-day timetable falls 81 → 58%, the never-forgets timetable 82 → 51%, the LLM buffer
78 → 58%, retrieval memory 81 → 62%, long-context 71 → 65% (still running), reflection 71 → 60% (still running), the
7-day routine table 60 → 58% (it never learned the lead-up well: 60% where the buffer reaches 78%).

What happens next separates memories by what they keep:
- Forgetters re-learn and break again. The 3-day timetable is back to 86% inside the spell and falls to 60% on the first
  days home; the 1-day timetable 87% then 66%; most-frequent-place (3-day) 78% then 32%.
- The never-forgets timetable stays stuck in the spell (70%) and is right at once when the old routine returns (78%).
- The hedge over memory lengths does both halves right for a counter: 77% in the spell, 76% on the return — it moves its
  trust to the short memories at the break and back to the long one on the return, so no second break.
- The LLM buffer with no message recovers slowly (58 → 66 → 74 → 77%) and shows NO second break — but on cold
  questions it is only 41% inside the spell: what looks like recovery is mostly same-day feedback about the same
  object, not a learned sick routine. Retrieval memory (no message): 62 → 73% in the spell, cold 44% (return not landed
  yet). Long-context: 65 → 72%, cold 52%.

## (b) What a one-sentence message buys, and costs, per memory kind

Every figure here is a PAIRED contrast — the difference on the same household between the told and untold runs,
averaged over households, with the spread across households beside it. An effect smaller than that spread is reported
as no measurable difference rather than as a number with a direction (Oliver's one-standard-deviation rule); the full
table is in STORY_numbers.md.

Telling the buffer "Yuki is home sick today" is worth +12.9 ± 9.5 points on the first three sick days and +16.3 ± 11.3
through the rest of the spell; on cold questions +23.5 ± 13.4 and +36.3 ± 18.8 — the sentence does what ten days of
feedback could not. The cost is the return: −11.3 ± 7.9 on the first days back, cold −20.4 ± 14.5 — told once, it keeps
believing the sick routine until feedback proves otherwise. Told again on the first day back, the cost is no longer measurable: with both
messages the first days back come out −3.6 ± 8.3 against never being told. How much of that is the retraction itself
is undecided — the direct comparison of telling twice against telling once is +7.7 ± 10.2 on all questions and
+13.4 ± 20.8 on cold ones, inside the noise at ten households. The workshop session is running ten more households on
those two arms to settle it.

The message is selective by object. On households where only one person is sick but everyone's things are asked (3
households, the workshop session's partial-shift arms): the buffer with the message moves the sick person's things
56 → 77% on the first sick days and leaves the other resident's alone (76 → 74%).

For the routine table the same sentence buys less (58 → 62% on the first sick days, cold 25 → 37%) and costs the same
on the return (cold 38 → 27%), because the table itself is a weaker memory here.

## (c) The LLM's stated confidence is flat while the counters' moves with the stage

Every LLM memory says ~0.85–0.90 in every window: buffer 88 → 87% from the lead-up to the first sick days while its
accuracy falls 78 → 58; retrieval 88 → 85 (accuracy 81 → 62); long-context 89 → 90 (71 → 65); routine table 86 → 87
(60 → 58). The counters' confidence tracks the stage: the 3-day timetable claims 46% then 37% across the same break.
The LLM never knows when it is wrong.

Removing each method's own level (a monotone map from stated confidence to accuracy fitted on the lead-up only) leaves
the tracking: the buffer is +15 points over-confident on the first sick days, retrieval +12, reflection +8 — and near
zero on the lead-up by construction. An adaptive answer-or-ask gate on the stated confidence (target 10% wrong among
what it answers) has to ask 55% of the time on the shift days (29% before) and still misses 28% of what it answers; the
gate does tighten at the shift (its confidence bar rises 0.78 → 0.90), it just cannot get ahead of a confidence signal
that does not move. With the start message the gate asks 41% and misses 18% — the message helps the gate more than
the confidence ever will.

Read three ways on the first sick day (buffer, no message, 3 households, bounded day list): 31% right while it says
84% (verbalized), 91% (agreement across five samples), 75% (token probability on a multiple choice). None of the three
channels reads the drop. Sample agreement is the worst of the three: the model is confidently consistent when wrong.

## (d) What conformal sets on the model's own probabilities do and do not fix

Honest sets built online on the model's multiple-choice probabilities (90% target, same machinery as the classical
honest-sets agents) do what they promise — coverage 88–100% across the listed days — but on the first sick day they
need 7.6 of 10 options to do it, shrinking to 5.5 by day 20 and 4.2 on the return. They fix the coverage guarantee, not
the informativeness: the set says "I am no longer sure" by getting large, which is honest, but it cannot tell the
robot WHERE to look, and it inherits the flat probabilities underneath (the token-probability channel is the one
being calibrated). On the classical side the same construction on the timetable balloons to 15–20 places for a day or
two at the shift and then recovers; the LLM version starts wider and recovers less.

## (e) The cold-question view

Day-level accuracy flatters every memory that is asked the same object several times a day: the second question
benefits from the feedback to the first. Cold-only, the buffer with no message holds 41% inside the spell (day-level
66%), 58% on the return (day-level 74%); retrieval 44% (73%); long-context 52% (72%); the routine table 25% (63%). The
message's effect is largest exactly here (41 → 79%), which is the point: a sentence is what these memories cannot get
from evidence.

## A message about one person is applied to that person's things only

In households where one resident is off sick but the robot is asked about everyone's things (6 households, all arms
finished; paired per-household contrasts, start message minus no message): telling the buffer "Yuki is home sick
today" is worth +15.3 ± 9.4 points on the sick resident's own things through the spell (+31.9 ± 8.6 on cold
questions) and +0.4 ± 5.1 on the other resident's (cold +0.7 ± 5.9) — no measurable difference where it should make
none. A memory that keeps a separate record per object could not spread it anywhere else in any case.

The nightly routine table behaves the same way on the other resident's things (−5.1 ± 10.5, not measurable) but is
worse everywhere: with no message it answers the sick resident's things 68% against the buffer's 70% and the other
resident's 53% against 71%, while its stated confidence sits at 82-89% in every window for both residents, message
or not.

RETRACTED: an earlier version of this section, written from the first three partial households, reported that the
routine table with a message DEGRADED the other resident's things (cold 42 → 26 → 27). With all six households that
is a wash — per household in the sick spell: −14, −10, −11, +8, +9, −12, and the two positives are the two
largest-n households. See uq/problems_found.md 05:15.

## Noticing only pays when it triggers a reset

At a matched 25% ask rate, in the sick spell the 3-day timetable searches 3.08 places per question; the same timetable
with a change alarm that wipes its diary when it fires, 2.48 (−20%); the hedge, which notices but does not reset, 3.14;
never-forgets 3.66. Knowing you are unsure buys nothing at the planner; acting on it does.

## What actually makes a disruption break these methods

Measure a disruption by how much of the household's stuff is out of its usual place — the share of questions where
the thing is somewhere other than where it normally lives. In a settled week about 35 in every 100 questions ask about
something that is not where it normally lives (35.0 sick regime, 34.6 friends-over, 36.6 holiday — the baselines
match). On the first three shift days that becomes 76.5 in 100 for the sick spell, 51.0 for friends-over-every-evening
and 44.0 for a holiday at home; the 3-day timetable's breaks are 23, 11 and 2 points. Being asked at an hour the robot has never seen is harmless on its own:
when the hour is new but the thing is in its usual place it is right 89-95% of the time in all three regimes, because
with nothing for that hour it falls back on where the thing normally lives and that is normally correct. And the
methods do not get worse at the questions they were already facing — the sick spell puts 41 more questions in every 100
into the kind they were always bad at, while their accuracy within each kind improves by 18 points.

Two earlier explanations of ours were tested against these three regimes and both failed: "the disruption moves the
hours" (a holiday at home moves the most hours and breaks the least) and "it moves the hours to ones where the
fallback is also wrong" (friends-over shifts the least into that state and breaks five times harder than the
holiday). Numbers and method: results/regime_search/tools/break_cells.py; both hypotheses are on the record in
uq/regime/EXPECTATIONS.md (E35).

## What this says about current agent memories

Every memory we tested — buffer, retrieval, long-context, reflection, a nightly routine table — breaks at a routine
change by as much as a plain counter does, and none of them knows it happened: their stated confidence is the same
number before, during and after, so no gate, set or planner built on that confidence can react in time. What moves
them is language: one sentence about the change is worth more than a week of feedback, is applied selectively to the
right objects, and is also the thing they cannot let go of without being told again — and, when the memory is a shared
document, the sentence about one person quietly degrades the other. The open problem is not more memory; it is a memory
whose confidence moves when the world does.

## When the same spell comes back: the simple learners keep the habit

Two-spells regime (one person sick days 14–20, back 21–27, sick again 28–34, back 35–41; 10 households; the language
memories are running and land ~08:00). First break → second break: 3-day timetable 81 → 58% then 79 → 74%; 1-day
timetable 79 → 65% then 77 → 78% (no second break at all); never-forgets 82 → 51% then 83 → 69%; hedge 81 → 58% then
83 → 71%. The second spell is as different from normal life as the first (28% vs 26% of asked things have moved
relative to the preceding normal week; a plain "last seen" answer does no better the second time), so this is memory,
not luck. The robot's simple learners keep a habit for each hour of the day, and nothing during normal days ever
replaces the sick-day habit at those hours: in the second spell 53% of the 1-day learner's questions fall in hours
only the first spell ever filled, and there it is 97% right. Forgetting in these learners is relative within an hour of
the day — a habit that nothing overwrites is kept for ever. Prediction written down before the language memories land
(E31b): retrieval, which looks up the same hour of the day, re-learns the second spell faster than the first; the
buffer, which keeps only recent sightings, does not.

Still to land tonight: retrieval / reflection with the start and start+end messages (10 / 5 households); long-context
on 3 households across all three messages; the two-spells LLM arms.
