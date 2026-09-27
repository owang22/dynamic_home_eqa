# Why this experiment may produce a null, worked out before running it

Written 2026-09-24. Analysis only: no runs, no GPU. Everything below is measured from
data already on disk.

**What I read**

- The ten frozen households used by the memory study:
  `/home/oliver/robot/dynamic_home_eqa_fm/results/fm_memory/banks_f1/hh_s*_t03.jsonl`
  (these are the `sick10_owner` scenario: one resident off sick for ten days, and every
  question is about that resident's things).
- The alternative frozen regimes and their configs under
  `/home/oliver/robot/dynamic_home_eqa/results/regime_search/*/` — in particular
  `sick10_partial/banks/`, `sick10_all/banks/`, `sick2x_owner/banks/`, `guests10/banks/`,
  `nightshift/banks/`.
- The classical per-question logs with full distributions:
  `/home/oliver/robot/dynamic_home_eqa/results/regime_search/sick10_owner/classical/hh_s*_t03.jsonl`.
- The earlier language-model arms:
  `/home/oliver/robot/dynamic_home_eqa/results/confidence_shift_2026-09-20/uq/llm_strategies/chain_person/nottold/*/run_log.jsonl`.
- The experiment code as it stood at 01:08: `/home/oliver/robot/dynamic_home_eqa/src/self_improve/`.

**What the data contains.** Each frozen household file has a header (rooms, places,
residents, which days are the disrupted ones), the complete true movement history of every
object (`kind: truth`), the questions that were asked with their exact times
(`kind: question`), the recorded room sweeps with full contents (`kind: room_visit`), and
the observations the robot was given (`kind: observation`). That is enough to reconstruct,
for any object at any second, where it actually was — which is what every number below rests on.

---

## The ranked list

| # | Risk | Fatal or fixable | One-line fix |
|---|---|---|---|
| 1 | In the disrupted window there is almost nothing for a memory to get right or wrong: one fact scores 78%, perfect per-object knowledge scores 83% | Fatal as designed | Switch the study to the `sick10_partial` regime (headroom 22 points instead of 5) |
| 2 | A look at 3am cannot see the disruption at all | Fatal as designed; already fixed | Look during 10:00-17:00 (adopted 01:08) |
| 3 | The ten households are one scenario measured ten times: 35 of 37 moved objects land on the same coffee table | Fatal to the claim, not to the run | Switch regime, report per household, cluster errors on object not question |
| 4 | Three rooms a day leaves the "robot chooses" arm nothing to win: a sensible fixed schedule already covers 95% of disrupted-window answers | Fatal to one factor; already fixed | One room a day (adopted 01:08) |
| 5 | The frozen test at day 23 is ten days after the change, by which time the fixed rota has caught up — so the looking factor is invisible at that freeze point | Fatal to one factor | Add an early freeze point at day 16 |
| 6 | The disrupted period makes the task *easier*: every recency-weighted learner already on disk scores higher during it than during the ordinary routine | Fatal to the paper's story, not to the run | Stop predicting a dip; predict and measure the reversion cost instead |
| 7 | Where the change is biggest the answer is a constant, and where the answer is informative the change is small | Fixable | Score by time-of-day band and report all three |
| 8 | The return window is thin and contaminated: 8 usable questions in the worst household, and 20% of objects do not revert cleanly | Fixable | Widen the window, switch regime, report drift separately |
| 9 | The day-31 freeze asks questions from days the notes already cover | Fixable | Freeze at day 28, ask days 29-31 |
| 10 | Removing feedback is survivable, but only because the old accounting was wrong | Not fatal | Watch 0.8 sightings per object per day at the one-room budget |
| 11 | The retrieval budget of 12 claims is bigger than the number of things ever asked about, so selective retrieval never has to choose | Fixable | Cut the budget to 4, or grow the question set |
| 12 | Household s4 is a household where the event did not happen | Fixable | Exclude it on a stated rule, in advance |
| 13 | If a look that finds nothing is not written down, the choosing arm loses its only signal | Fixable | Record absence explicitly, identically in both memory formats |

---

## Risk 1. There is nothing to get right in the disrupted window

**Measured.** For every household and every window, two baselines that need no real memory:

- **One-fact baseline**: answer the single commonest place in that window to every question.
  No per-object knowledge at all.
- **Per-object baseline**: answer each object's own commonest place in that window. Perfect
  per-object knowledge, no sense of time.

The gap between them is all the headroom a per-object memory can possibly win. Ten households,
`sick10_owner`:

| window | one-fact | per-object | headroom |
|---|---|---|---|
| settled (days 1-13) | 0.52 (range 0.27-0.74) | 0.70 (0.62-0.82) | 18 points |
| disrupted (14-23) | **0.78 (0.71-0.82)** | **0.83 (0.81-0.86)** | **5 points** |
| back to normal (24-31) | 0.51 (0.29-0.72) | 0.73 (0.58-0.86) | 22 points |

**What it means.** In the exact window the primary measurement freezes and tests, answering
"coffee table" to every question scores 78 out of 100, and knowing every object individually
and perfectly scores 83. Five points of headroom, against a noise floor of 3-5% of answers
changing on a rerun, one to two points of accuracy, and up to ten points for a single window
in a single household. All four cells of the 2x2 will land inside the noise, not because the
arms are equal but because the question set cannot tell them apart.

It is worse inside the window. Broken down by the hour the question was asked, in the
disrupted period:

| band | questions per household | one-fact | per-object | headroom |
|---|---|---|---|---|
| 07:00-09:00 | 22 | 0.65 | 0.76 | 11 points |
| 10:00-17:00 | 99 | **0.99** | **0.99** | **0 points** (per-household range 0.00-0.01) |
| 18:00-22:00 | 38 | 0.42 | 0.70 | 29 points |

62% of the disrupted-window questions sit in a band where a memory holding one sentence and a
memory holding perfect per-object knowledge both score 99%. That subset carries literally zero
information about which memory is better.

**Fatal as designed. Fixable by changing the scenario.** The `sick10_partial` regime — same
simulator, same households, already frozen on disk, one resident off sick but questions asked
about *everyone's* things — gives:

| window | one-fact | per-object | headroom |
|---|---|---|---|
| settled | 0.44 (0.29-0.60) | 0.70 (0.61-0.79) | 26 points |
| disrupted | **0.58 (0.31-0.70)** | **0.80 (0.78-0.86)** | **22 points** |
| back to normal | 0.46 (0.23-0.67) | 0.70 (0.57-0.81) | 24 points |

Four to five times the headroom, at no cost in compute, and 744 questions per household
instead of 490.

---

## Risk 2. A 3am look cannot see the disruption

**Measured.** For each object that is actually asked about (4 to 7 per household in
`sick10_owner`, 53 in total), its true room at 03:00 on each settled day against each
disrupted day; then the same for the daytime moments when questions are asked; then the same
at all 24 hours.

- Daytime: the usual room changes for **32 of 53** asked objects.
- At 03:00: the usual room changes for **9 of 53**. Per household: s0 0/6, s1 0/7, s5 0/4,
  s2 1/5, s4 1/4, s6 1/7, s8 1/6, s9 1/4, s3 2/7, s7 2/5.
- Three households out of ten (s0, s1, s5) have **no** asked object whose night-time resting
  place changes.

Share of asked objects whose move a look at that hour would reveal, averaged over the ten
households:

```
00-08  17-20%
09     48%
10-17  71-75%   <- flat plateau, peak 75% at 13:00, 15:00, 16:00
18     66%
19     58%
20     49%
21-23  24-33%
```

**What it means.** The disruption is a daytime phenomenon. The sick resident uses their things
in the living room through the working day; overnight they are tidied back to the bedroom or
the desk. A robot that looks only at 3am sees the tidied world, which is identical in both
periods, and cannot learn that anything happened — at any budget, with any memory, however
cleverly it chooses.

**Fatal as designed; already fixed.** `study_settings.py` now has `visit_times = ["13:00"]`.
I would spread multiple looks across 10:00-17:00 rather than bunch them, because the plateau is
flat and spreading also catches objects that move within the day.

**Second, quieter number from the same table:** the settled-period floor at 3am is 17%, not
zero. Even in the ordinary fortnight about one asked object in six is in a different room at
3am from one night to the next. Any change-detection rule must clear 17%, not 0%.

---

## Risk 3. Ten households, one scenario

**Measured.** For every asked object in every household, its commonest true place at question
moments in the settled period against the disrupted period. In `sick10_owner`:

- Every asked object in all ten households belongs to the sick resident. There are no control
  objects.
- 37 asked objects change place. **35 of the 37 land on the same receptacle id,
  `coffee_table_l1`.** The other two go to `dining_table_d1` and `cupboard_k1`.
- The correct answer in the disrupted window is "coffee table" for 71-86% of questions, in all
  ten households.

Per household the whole disruption is one fact: *this person's things are on the coffee table
now.* Ten households are ten draws of that one fact.

**Two consequences.**

1. **The statistics will flatter.** Paired standard errors across households assume the
   households are ten instances. They are one instance with ten cosmetic variations. A pooled
   p-value on this design is not defensible unless the shared scenario is stated.
2. **It kills the memory-format factor.** The 2x2 asks whether per-claim bookkeeping, with
   supporting and contradicting observations attached to each claim, beats a wholesale nightly
   rewrite. But there is nothing per-claim to learn: one sentence — "Tomas is home sick, his
   things are on the coffee table" — covers every object. A summary that writes that sentence
   scores the same as a claim store holding five separately revised claims. Per-claim machinery
   pays off only when different claims move in different directions at different times. Here
   they all move together, to the same place, on the same day.

**Fatal to the claim the paper wants to make. Fixable by changing regime.** `sick10_partial`,
measured the same way:

| | `sick10_owner` | `sick10_partial` |
|---|---|---|
| asked objects per household | 5.5 (4-7) | 12.2 (8-18) |
| of those, move | 3.7 | 4.8 |
| of those, stay put (real controls) | 1.8 | 6.8 |
| distinct destinations per household | 1.3 | 2.2 (range 1-4) |
| moved objects going somewhere other than the coffee table, all 10 households | 2 of 37 | 12 of 48 |
| destinations seen | coffee table, dining table, kitchen cupboard | coffee table, bed_b2, kitchen table, bathroom shelf, armchair, nightstand, bathroom sink, bed_b1, cupboard |

A memory now has to hold roughly twelve claims, revise five of them to two to four different
destinations, and leave seven alone. That is a real test of per-claim bookkeeping. It is still
coffee-table-dominated and the paper should say so, but it is no longer a single fact.

**The other regimes I checked, for the record.** `guests10` has a question-level swing of only
+10 points between settled and disrupted, `nightshift` only +5 — both too weak to measure
anything. `sick10_all` makes everyone sick, so 8.8 of 12.4 objects move and only 3.2 controls
survive; the controls are the point, so it is worse. `sick2x_owner` has two disrupted spells,
which is attractive, but only 5.5 asked objects and 1.4 destinations, so it inherits risk 1 and
risk 3 unchanged. `sick10_partial` is the best of what exists.

---

## Risk 4. Three rooms a day leaves nothing to choose

**Measured.** Households have 6 to 9 rooms (s0 7, s1 7, s2 9, s3 9, s4 8, s5 6, s6 6, s7 7,
s8 6, s9 8) and 32 to 47 individual places. The answers to the questions that are actually
asked only ever live in 3 to 5 rooms. Three rooms cover 82-100% of settled-period answers in
all ten households. In the disrupted window a single room — the living room, in all ten —
holds 71-86% of the answers, and two rooms hold over 90% everywhere.

Take the schedule any sensible person would write in advance: kitchen, living room, main work
room. Its coverage of the disrupted-window answers, per household: 82, 88, 93, 94, 95, 95, 96,
97, 100, 100. **Mean 95 out of 100.**

The only way to open a gap is to hand the fixed arm a schedule that omits the living room.
I tried it (fixed = the three commonest settled-period rooms, which excludes the living room in
s1, s2, s3): the gap becomes 0.72-0.84 in exactly those three households and **0.00 in the other
seven**. Three households carrying an effect and seven at exactly zero is the signature of a
rigged control, not a finding.

Second number: at 3 rooms a day a fixed round-robin sweeps the entire house every 2.0 to 3.0
days. Over a ten-day disruption the choosing arm can at best be two days earlier.

**Fatal to the looking factor at 3 rooms a day; already fixed.** `study_settings.py` now has
`budget_per_look = 1`. At one room a day a rotation takes 6 to 9 days for a full pass, which is
comparable to the length of the disruption, so there is something to win.

**Why I recommended rooms rather than places.** At place level with 3 looks a day, I simulated a
fixed rotation over all 32-47 places at 10:00/13:00/16:00 through the disruption and recorded
when it first sees a moved object in its new place: s1 all 5 by day 3, s5 both by day 3,
s0 all 5 by day 4, s4 its 1 by day 4, s2 4 of 5, s3 3 of 4, s7 3 of 4, s6 1 of 3 (day 9),
**s8 0 of 4, s9 0 of 2**. Two households detect nothing in ten days, and the difference between
day 3 and never is just where the arbitrary rotation order happens to start. A full pass over
places takes 10.7 to 15.3 days, longer than the disruption. Covering every place within two
days would need 16 to 24 looks a day.

**And a check that mattered.** I verified that a room visit misses nothing: I compared every
recorded room sweep against ground truth at that instant across three households — 7,347
object sightings, **zero objects present but unreported**, and no receptacle ever omitted from
its room's visit, including cupboards, drawers, wardrobes and the medicine cabinet. So a room
look has a hit rate of one and sees inside closed containers. The arithmetic above holds.

**At one room a day the gap is real but moderate.** Simulating a one-room-a-day rotation at
13:00 over the ten disrupted days, 20 random rotation orders per household: the fixed rota sees
79-100% of moved objects (mean 92%), mean first sighting on day 4.4. A robot that reasons its
way to the right room gets there on day 1. So the fixed arm holds correct information for about
6 of the 10 days against 10 of 10 — roughly a third of the window.

---

## Risk 5. The day-23 freeze is too late to see the looking factor

**Measured.** From risk 4: at one room a day the fixed rotation has already seen 92% of the
moved objects by a mean of day 4.4, and 79-100% of them by day 23.

**What it means.** The primary freeze at day 23 is ten days after the change. By then both
looking arms have seen the disruption. The frozen test at day 23 will show the two looking arms
on top of each other, and the honest conclusion — "choosing where to look buys you three days,
not a better final memory" — will look like a null.

**Fatal to the looking factor at the current freeze points. Fixable: add an early freeze.**
The window where the arms genuinely differ is days 16-19. Numbers for early freeze points in
`sick10_partial`:

| freeze / ask | questions per household | of which a settled memory gets wrong | headroom |
|---|---|---|---|
| d15 -> d16-18 | 72 | 46 (29-65) | 23 points (0.08-0.47) |
| d16 -> d17-19 | 72 | 46 (31-65) | 23 points (0.14-0.43) |
| d17 -> d18-20 | 72 | 48 (26-66) | 24 points (0.12-0.44) |

Any of these works; d16 is the cleanest, three days after the change, roughly when the fixed
rota first stumbles on the new room. **Report the looking factor at the early freeze and the
memory factor at the late freeze.** They live in different windows and reporting both at day 23
guarantees one of them reads as a null.

---

## Risk 6. The disruption makes the task easier, not harder

**Measured.** Per-household accuracy by window, straight from the classical logs already on
disk (`regime_search/sick10_owner/classical/`), ten households:

| learner | settled | disrupted | back to normal |
|---|---|---|---|
| timetable lookup, 24h half-life | 0.72 | **0.80** | 0.73 |
| timetable lookup, 72h half-life | 0.73 | **0.77** | 0.72 |
| most-frequent place, 24h half-life | 0.58 | **0.73** | 0.57 |
| most-frequent place, 72h half-life | 0.58 | **0.68** | 0.51 |
| periodic persistence, 24h half-life | 0.62 | **0.68** | 0.67 |
| Perpetua*, lognormal | 0.63 | **0.68** | 0.57 |
| last observation | 0.46 | **0.57** | 0.48 |
| most-frequent place, no forgetting | 0.56 | 0.42 | 0.57 |
| timetable lookup, no forgetting | 0.72 | 0.65 | 0.79 |

**What it means.** Every learner with any recency weighting does *better* during the disruption
than during the ordinary routine. Only the two with no forgetting drop. This follows directly
from risk 1: the disrupted period is a low-variety period, everything is in one place, so a
short memory wins. If the paper's story is "accuracy falls at the shift and recovers", the data
already on disk says the opposite.

**Fatal to the story, not to the run. The fix is the claim, not the code.** The interesting
quantity is not the dip at the shift but the cost at the *return*: when the resident comes back,
did the memory still hold the ordinary routine, or had it been overwritten? That is where the
no-forgetting learners win (timetable with no forgetting: 0.79 on return against 0.73 for the
24-hour version) and it is exactly what the two memory formats should differ on. Frame the
study around the return, not the shift. `sick10_partial` widens the return headroom to 24 points.

---

## Risk 7. The informative questions and the visible change do not overlap

**Measured.** Question times are spread across the whole waking day, not concentrated. Share of
all questions by hour: 07:00 6%, 08:00 4%, 09:00 7%, 10:00 5%, 11:00 6%, 12:00 5%, 13:00 6%,
14:00 6%, 15:00 7%, 16:00 5%, 17:00 4%, 18:00 2%, 19:00 7%, 20:00 8%, 21:00 8%, 22:00 14%.
Only about 43% fall in the 10:00-17:00 plateau; 37-42% are after 19:00.

Putting risk 1's band table beside risk 2's hour table:

| band | how visible the change is (risk 2) | headroom for a per-object memory (risk 1) |
|---|---|---|
| 10:00-17:00 | 71-75% | **0 points** in `sick10_owner`, 14 in `sick10_partial` |
| 18:00-22:00 | 24-49% | **29-32 points** in both |

**What it means.** Where the change is biggest the answer is a constant, so no memory design can
distinguish itself. Where the answer carries real per-object information, the change is only
about a third visible. These two facts pull in opposite directions and their product is small.
This is the subtlest reason the four cells could land on top of each other.

**Fixable.** Report the frozen test broken down by the three bands (morning 07-09, daytime
10-17, evening 18-22) and treat the evening band as the primary, because its headroom is 29-32
points and stable across every window and both regimes with a tight per-household range
(0.22-0.43). Do not average the bands into one number: a rise in the degenerate daytime band
will mask a real change in the evening band.

---

## Risk 8. The return window is thin and the world does not revert cleanly

**Measured**, questions per household and how many of them a settled memory gets wrong (only
those can separate arms):

| window | `sick10_owner` | `sick10_partial` |
|---|---|---|
| first 3 disrupted days | 48 questions, 34 wrong (22-48) | 72, 46 (28-64) |
| whole disrupted window | 160, 113 (69-156) | 240, 155 (95-209) |
| first 3 return days | 35, **11 wrong (2-19)** | 68, 21 (12-30) |
| whole return window | 96, **30 wrong (8-48)** | 183, 59 (37-88) |

In `sick10_owner` one household has **2** usable questions in the first three return days and
**8** across the whole return window. Nothing can be measured on 8 questions.

And the return is contaminated. Of the 34 objects that moved and have return-window questions:
**28** go back to their settled place, **2** stay in the disrupted place, **4** end up somewhere
third. Separately, **4 of the 18** objects that never moved during the disruption have a
different commonest place in the return window anyway, from ordinary drift. So "did the memory
revert correctly" is roughly 20% contaminated by the world not reverting.

**Fixable.** Use the whole return window rather than a three-day slice; switch to
`sick10_partial`, which roughly doubles the counts; and report the objects that did not revert
as a separate line rather than scoring them as memory failures.

**The number that matters more than the question count.** Per household the disrupted window
contains only 5.5 distinct asked objects and 14.7 distinct object-and-place facts in
`sick10_owner`, and 11.8 and 30.9 in `sick10_partial`. 240 questions about 12 objects are not
240 independent observations — about 20 questions concern the same object. The effective sample
size is the objects: roughly 48 moved objects across ten households, not 2,400 questions. Any
interval must be clustered on household, and preferably on object. A per-question binomial
interval will be about four times too narrow and will manufacture significance.

---

## Risk 9. The day-31 freeze asks about days the notes already cover

**Measured.** `frozen_memory_test.py` sets `FREEZE_POINTS["end of the back-to-normal period"] =
{notes_through_day: 31, questions_from_days: [29, 30, 31]}`. Households run days 0-31, so there
are no days after 31 to ask about. The notes at day 31 already include the robot's looks on days
29, 30 and 31.

**What it means.** That freeze point is not comparable with the other two. It is the only one
where the memory may have seen the very day it is being questioned about, so it will score
higher for a reason that has nothing to do with the intervention, and it will favour whichever
arm records raw recent sightings most faithfully.

**Fixable.** Freeze at day 28 and ask days 29-31. In `sick10_partial` that window has 70
questions per household (62-72), 23 of them ones a settled memory gets wrong (11-39), and 29
points of headroom — the best of the three freeze points.

---

## Risk 10. Removing the feedback, quantified

**Measured**, sightings per asked object per day, reconstructed from the true trajectories:

| household | old: told the truth after each question | old: nightly sweep | old total | new: 3 daytime room visits | new: days with at least one sighting |
|---|---|---|---|---|---|
| s0 | 2.67 | 1.00 | 3.67 | 3.00 | 100% |
| s1 | 1.75 | 1.00 | 2.75 | 1.99 | 66% |
| s2 | 3.20 | 1.00 | 4.20 | 2.28 | 83% |
| s3 | 1.41 | 1.00 | 2.41 | 2.12 | 72% |
| s4 | 2.62 | 1.00 | 3.62 | 1.74 | 58% |
| s5 | 2.31 | 1.00 | 3.31 | 3.00 | 100% |
| s6 | 2.11 | 1.00 | 3.11 | 2.18 | 73% |
| s7 | 3.20 | 1.00 | 4.20 | 2.49 | 88% |
| s8 | 2.54 | 1.00 | 3.54 | 2.61 | 90% |
| s9 | 3.35 | 1.00 | 4.35 | 3.00 | 100% |
| mean | 2.52 | 1.00 | **3.52** | **2.44** | 83% |

**What it means.** Evidence falls to about 69% of its old level, not to a fraction of it. So the
answer to "how much signal is left after removing feedback" is: most of it. Removing feedback is
survivable.

**The 70/29 accounting was wrong and it matters.** Counting events in a frozen household gives
496 question-time observations, 222 room sweeps and 66 initial-tour observations, which is where
63/28/8 comes from. But each sweep is one *event* recording every object in the house — 75 to
105 sightings, not one. Corrected, the nightly sweep was a comparable channel to the feedback,
not a third of it, which is why its removal would have been the bigger loss and its retiming
is the bigger fix.

**What to watch.** At the adopted one-room-a-day budget the figure drops to roughly a third of
the three-room number — about 0.8 sightings per asked object per day. I think that is enough,
because the robot needs to learn one thing per object rather than track it continuously, but it
is the number I would instrument first. Two side facts from the same calculation: the asked
object is out of the house or in someone's pocket at 0-19% of look moments, so a look
legitimately finding nothing is normal; and **no question in either regime has an unanswerable
truth** — 0 of 4,130 in `sick10_owner` and 0 of 7,189 in `sick10_partial` have a true answer of
out-of-house or on-a-person, so nothing needs excluding on that ground.

**Free power that is currently being discarded.** With feedback removed, asking a question
teaches the robot nothing, so there is no leakage from using a question during the run. There is
no reason to hold out a *subset*. Use every question in the window.

---

## Risk 11. The retrieval budget is larger than the problem

**Measured.** `study_settings.py` sets `retrieval_budget = 12`. The number of distinct objects
ever asked about is 5.5 per household in `sick10_owner` and 12.2 in `sick10_partial`.

**What it means.** A budget of 12 claims can hold every claim that could possibly be relevant.
So the claim-store arm never has to *choose* what to retrieve, and one of the two real
advantages of a per-claim memory — selective retrieval — is switched off by the budget. The two
memory formats are then being compared on writing alone.

**Fixable.** Either cut the retrieval budget to about 4, a third of the relevant claims, so
retrieval has to discriminate; or keep 12 and say plainly that the study tests how memory is
*written*, not how it is read. Do not leave it at 12 and then claim a per-claim memory was
tested fairly.

---

## Risk 12. Household s4 is a household where nothing happened

**Measured.** In `sick10_owner`, 1 of s4's 4 asked objects changes its commonest place; its
question-level swing between settled and disrupted is +5 points against a settled churn floor
of 34%. In `sick10_partial`, 1 of 13 objects moves and the swing is +6 points. Every other
household swings between +14 and +64 points.

**Fixable, and it must be done in advance.** Exclude s4 on a stated rule — *"households in
which fewer than two asked-about objects change their commonest place during the disruption are
excluded"* — written down before the run. That rule drops only s4. Dropping it after seeing
results would be indefensible; dropping it now is clean.

---

## Risk 13. If a look that finds nothing is not written down, the choosing arm has no signal

**Measured.** During the disrupted window, at 13:00, the object is **absent** from the place the
settled memory expects on 84% of object-days in `sick10_owner` (447 of 530) and 88% in
`sick10_partial` (1,053 of 1,200).

**What it means.** This is good news: without any feedback, a robot that checks where it thinks
a thing is will find it gone almost nine times in ten. That is a strong, clean signal and it is
the mechanism by which the choosing arm is supposed to work its way to the living room. But it
only exists if "I looked at the desk and the mug was not there" is recorded. The regime configs
on disk all have `negative_evidence: false`, so the classical learners never used it, and if the
new memory modules inherit that habit the choosing arm loses its only channel.

**Fixable, and it is a confound if handled asymmetrically.** Absence must be recorded, and it
must be handed to *both* memory formats in the same form. A claim store naturally holds
contradicting observations; a wholesale summary must be given the same absence records in its
nightly input, or the memory factor and the absence-recording factor will be tangled together
and whatever is found will be uninterpretable.

---

## What I would do tonight

1. **Switch the scenario to `sick10_partial`.** It is already frozen on disk, it needs no
   simulation, and it turns the disrupted-window headroom from 5 points into 22, gives 6.8
   control objects per household that must not be disturbed, spreads the destinations over two
   to four places, and doubles the return-window counts. This is the single highest-value change
   and it costs nothing.
2. **Exclude s4 by a written rule, before running.**
3. **Add a freeze at day 16** (ask days 17-19) for the looking factor, keep day 23 (ask the
   whole return window) for the memory factor, and move the last freeze to day 28 (ask 29-31).
4. **Report by time-of-day band**, with the evening band as primary.
5. **Cluster the error bars on household and object, not on question.**
6. **Make absence a first-class observation in both memory formats.**
7. **Change the prediction.** The interesting effect is at the return, not at the shift. The
   classical logs already show accuracy rising during the disruption.

## What I could not answer from the data on disk

Whether the two memory formats, written by the same model at temperature 0 from the same
observations, actually produce different notes. That is not in any existing log and it is the
one thing I would spend a small amount of compute on before the full run: take one household,
run both formats through the settled fortnight and the first three disrupted days, and read the
two sets of notes side by side. If they say the same thing in different words, the memory factor
is dead regardless of everything above, and half an hour of a single GPU establishes it.
