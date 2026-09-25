# What we expect, written down before anything runs

Registered 2026-09-24, before any arm has been launched. Every number below was
measured on the frozen households, which this study reads and never writes.

## The hypothesis

A robot remembers a home better when it looks where its own guesses disagree,
and edits its notes instead of rewriting them.

## The two things we are varying

**How the notes are written.** Either the model rewrites one summary of the
household from scratch each night, or it adds, revises and marks individual
claims, each claim carrying the ids of the sightings that support and contradict
it.

**Where the robot looks.** Three arms, not two:

1. **the fixed fair rotation** — one room a day over a seeded rota of every room.
2. **the naive chooser** — "look where your own notes disagree", taken literally.
   Kept as an arm rather than discarded, because its failure is a real result:
   measured on ten days of one household, it visited 2 distinct rooms against the
   schedule's 9, saw 5 asked objects against 11, and never once entered the room
   the change had moved into. The reason is structural, not a prompt fault — its
   notes held no claim about that room, and **a room the robot holds no claim about
   can never be the site of a disagreement**, which is precisely where an unnoticed
   change will be.
3. **the repaired chooser** — the same policy with two changes of different kinds,
   and the write-up must keep them distinct:
   - it is told **how long since it last looked in each room**. This RESTORES
     INFORMATION a real robot plainly has about its own history; withholding it
     handicaps the policy rather than testing it.
   - the two competing claims must be about the **same thing**. This CORRECTS THE
     SPECIFICATION: two claims about two unrelated objects are not a disagreement
     about the world, and the looser version was written by accident.

   Each is a separate switch, so leaving one out in turn says which did the work.

Everything else is held identical: same model, same temperature, same
households, same traces, same number of looks, same question stream, same
retrieval budget at answer time, and prompts that differ only in the
intervention.

## The prediction that survives a null on accuracy

This is the point of pre-registering. Accuracy may come out flat. The following
is a property of the notes file itself and can be checked without the model:

> The arms that edit their notes incrementally still hold the ordinary-routine
> claim at the end of the disrupted period, and reuse it when the resident comes
> back. The arms that rewrite their notes wholesale have lost it.

Checked by `memory_notes.ordinary_routine_claims_still_present`. For the
incremental arms it is exact: claim ids persist and we check whether the claim
written during the ordinary fortnight is still readable and still names the same
place. For the wholesale-rewrite arms we can only check the newest summary text,
so we check whether the ordinary-routine wording still appears in it.

Secondary and also pre-registered: the choosing arm finds the disruption on an
earlier day than the schedule does.

## The scenario

**`results/self_improve/runs/illness_v1/banks`**. One resident unwell for ten
weekdays, questions about **everyone's** things, so the well residents' objects are
controls that never move. Every number below was reproduced here independently of
the generator.

It passes all six scenario checks and all four legs of the gate: learn +14.2, break
-13.3, re-learn +13.5, break again -8.9, with 5 of 10 households showing the full
four-phase shape.

**A correction to the record.** "illness_v1 failed seven ways" was said several
times, including by this file's author. It was true of an EARLIER build and is not
true of the directory now at `results/self_improve/runs/illness_v1/`. It must not be
described as the failed scenario anywhere.

**illness_v2 is superseded**, and its sweep moved to
`results/self_improve/superseded/`. It fails the fourth leg outright: a forgetting
learner loses only 1.6 points on the first two days back to normal against a
5-point bar, with a household-clustered error of 4.2. Its return is not a change, so
no arm can be measured on it - and a temporary disruption that costs nothing to
un-learn removes half of what this paper is about.

| Measured on the disrupted window | illness_v1 | sick10_partial (superseded) | sick10_owner (superseded) |
| --- | --- | --- | --- |
| One fact for the whole house | **30%** | 58% | 78% |
| Every object's own commonest place, known perfectly | **71%** | 80% | 83% |
| Headroom between them | **42 points** | 22 | 5 |
| Asked objects per household | 11 to 21 | 8 to 18 | 4 to 7 |
| Objects the disruption moves, per household | **4 to 10** | 3 to 8 | 3 to 6 |
| Households the exclusion rule drops, on either measure | **none** | none / s4 | — |

**One number goes the other way and must be said out loud.** The headroom that
decides whether an *updating* memory can beat a *non-updating* one is the oracle
minus a memory that learned the settled fortnight and never revised. That is:

| Freeze point | illness_v2 | sick10_partial |
| --- | --- | --- |
| did it learn the new routine | **16 points** (range 1 to 27) | 46 points (range 20 to 69) |
| did it keep the old routine | **9 points** (range 0 to 33) | 7 points |

illness_v2 is three times weaker here, and for a structural reason: the controls
that give the memory something to preserve are also objects a non-updating memory
gets right for free, which raises the baseline. 16 points is still well clear of
the 5% noise floor, but the effect we can detect is smaller than in the scenario
this replaced, and **four households have little room to show it at all**: s9 (1
point), s4 and s8 (8), s5 (12). Their memory-factor results are reported with
their headroom printed beside them, not pooled into a mean that hides them.

Good news on the read budget: every household here has 11 to 21 asked objects, so
the 8-line budget binds in **all ten**. The caveat that applied to a household with
exactly eight objects no longer applies.

Why not the owner-only regime we started from: there every asked object belongs
to the sick resident and nearly all of them land on the same coffee table, so one
sentence covers the whole disruption and a per-claim memory cannot beat a
wholesale rewrite by construction. Worse, its disrupted window is *easier* than
ordinary life. Both scenarios, measured the same way on the disrupted window:

| Yardstick on the disrupted window | owner-only | this scenario |
| --- | --- | --- |
| One fact for the whole house ("coffee table") | 78% | **58%** |
| Every object's own commonest place, known perfectly | 83% | **80%** |
| Room between them | 5 points | **22 points** |

Reproduced independently and to the point on 2026-09-24: 58% and 80%.

Per household here: 644 to 744 questions, 8 to 18 asked objects, of which 3 to 8
change their usual place and the rest never move — so the memory has both
revision and preservation to do.

## The sensing design

Locked 2026-09-24. Room-level looks, **one room per look, one look a day, at
13:00**. Not three rooms, not place-level, no 3am sweep.

| Measured on the frozen households | Number |
| --- | --- |
| Rooms per household | 6 to 9 (median 7) |
| Places (spots things rest in) per household | 33 to 47 |
| Share of answers sitting in a household's three commonest rooms | 84% to 100%, median 92% |
| Asked objects whose usual room differs between periods, seen in the daytime | 32 of 53 |
| The same, seen at 3am | 9 of 53, and zero in three households |
| Share of the disruption a look reveals, by hour | 17-20% midnight to 08:00; 48% at 09:00; a flat 71-75% from 10:00 to 17:00; 66% at 18:00; 24-33% late evening |
| Days for one full pass of a fixed rotation, one room a day | 6 to 9 |
| Days for one full pass, three places a day | 11 to 15, longer than the ten-day disruption |

- **Rooms, not places.** A place-level rotation cannot finish a pass inside the
  disruption, so whether a household notices depends on where the rota started.
  That is a coin flip, not an experiment.
- **One room, not three.** At three rooms a day a rotation sweeps the house every
  two to three days and a robot that chooses has nothing left to find.
- **13:00, not 3am.** The disruption is a daytime phenomenon: the sick resident
  uses their things in the living room through the working day and they are
  tidied back overnight, so the night world looks the same in both periods.
- **The fixed schedule rotates over every room, fairly.** The obvious
  alternative — rotate only the rooms that usually held things during the
  ordinary fortnight — is not fairer but rigged: the living room is in the
  settled-period top three in only **1 of 10** households, so that schedule never
  visits the room the disruption moves into in **9 of 10** households and could
  not detect the change at any budget.
- **The rota order is a seed, chosen and recorded per household.** When a full
  pass takes longer than the thing being detected, the order carries the result.

Two budgets, kept separate: three curation looks per asked object across the
whole study (about 36, so roughly one a day), and up to three places checked when
answering one question. The second is the headline search cost and is reported
apart from accuracy.

**The shared warm start is ON.** One walkthrough of the whole house on day 0 at
18:00, identical for every arm, using the bank's own opening walkthrough time. The
reason is measured: one room a day gives 4.0 sightings per asked-about object
across the whole month, evidence on only 17.6 of 32 days (8 of 32 in the worst
household), and 0.7 objects per household never seen at all — a claim about the
ordinary routine would rest on about two sightings. One walkthrough gives 14 of 15
objects at once. **The write-up must say plainly that the settled routine was
GIVEN rather than learned.** This study is about revising a routine, not acquiring
one, and the warm start cannot favour an arm because every arm gets the same one.

**The read budget is 8 lines, the same for both ways of writing notes, and it is
what makes the memory factor architectural rather than prompted.** Both formats
put at most 8 lines of notes into an answer prompt, counted in one shared unit —
one fact to a line. Eight is below one line per asked-about object in 9 of the 10
households (they have 10 to 18 objects; only s2, with exactly 8, is unconstrained,
and its memory-factor result must be read with that said out loud). So:

- the **wholesale rewrite** is a single artifact and has to decide what to LOSE in
  order to fit, which forces generalisation for a real reason. It is told the limit
  when it writes, so it chooses what to drop rather than having its tail cut off.
- the **claim store** keeps everything and decides what to SHOW inside the same
  window: claims about the object being asked about first, then the most recently
  revised.

This is deliberately *not* a length cap imposed on the rewrite by fiat, which
would be choosing the result. The constraint sits at read time and falls on both
formats equally. Whether it bit, and how many lines were available, is recorded
per question.

## The freeze points

The primary measurement freezes each arm's notes and answers with no further
looking, so that "the memory is better" is separated from "the policy searches
better". Every question in the window is used; nothing is held out, because with
the post-question truth removed a question teaches the robot nothing.

| Freeze point | Notes through | Questions | What it can show |
| --- | --- | --- | --- |
| before anything changed | day 13 | days 14-23 | the control: every arm has the same information and they should agree |
| did it learn the new routine | day 23 | days 14-23 | revision. Floor 34%, ceiling 80%: 46 points of room |
| did it keep the old routine | day 23 | days 24-31 | preservation, where the prediction lives. Keeping the ordinary routine is worth about 68% and is within 2 points of this window's own oracle; replacing it with the disrupted routine is worth about 45%. Predicted gap: about 23 points |

240 questions per household at the first two, 164 to 192 at the third. We also
report, separately, the score on the subset a settled memory gets wrong (40-87%
of the disrupted window, 19-51% of the return window) — those are the only
questions that can separate the arms.

## The exclusion rule: corrected before any run, and why

**Settled 2026-09-24: no household is excluded. s4 is kept.** The rule was first
written to be measured at question times, which would have dropped s4; that was
wrong and is recorded here as a correction rather than quietly dropped.

The rule as it now stands: **drop any household where fewer than two asked objects
change their usual place, measured over the daytime hours a look could happen.**
On the ten frozen households it drops nobody.

Which households that drops depends on a choice that had not been made explicit,
and the two answers differ:

- measured **over daytime hours** (the hours a look could happen): no household
  has fewer than three movers, so the rule drops **nobody**;
- measured **at question times**: s4 has one mover and every other household has
  three or more, so the rule drops **s4**.

In s4 six of thirteen asked objects change their usual daytime place — the
disruption plainly happened — but the question stream does not sample those
objects at the hours they have moved. So excluding s4 excludes it because the
*measurement* cannot see the event, not because the event did not happen.

Why the question-times version was wrong: excluding on it selects households
where the outcome variable moves, which inflates whatever the survivors show —
the same fault the rest of this pre-registration is written to avoid. And s4 is
the household whose movers are *most* heterogeneous — five distinct destinations,
only 33% of movers on the commonest one, against 100% on a single destination in
s2 and s9 — so it is the household best suited to the memory factor, not the
worst. Both counts are recorded per household in `which_objects_moved.json`.

## Amendment, 2026-09-24, after the memory-format diff on one household

Written down as an amendment rather than a silent edit, because it changes the
pre-registered prediction before the four cells run.

**Measured.** One household (s3, the most heterogeneous: 15 asked objects, 8
movers, 5 destinations), same look stream, same words describing what was seen,
only the instruction about how to write differing. Over 23 nights the wholesale
rewrite arm:

- wrote a per-object location table, one sentence per object, not a summary of
  routines;
- filled the "which routine or condition does this hold under" slot with the
  *date of the sighting*, never with a routine;
- copied forward, verbatim, every object it had not re-observed. 13 of 22
  consecutive nights were 100% identical to the night before, and the nights that
  changed changed only the lines for objects that day's look had found;
- therefore still contained settled-period facts untouched deep inside the
  disruption: on night 21 it still recorded places first seen on days 4, 10 and
  13.

**What it means.** The pre-registered prediction — that the wholesale-rewrite arm
loses the ordinary-routine claim — is **false as the arm currently behaves**.
Told that whatever it does not write down is gone, the model does not forget; it
copies. A rewrite of a fifteen-object household fits in the allowed length one
line per object, so nothing forces it to generalise.

**Restated prediction, still checkable in the notes file and still surviving a
null on accuracy:**

> The wholesale-rewrite arm keeps only the latest place per object, tagged with
> the date it was seen, and so cannot say which routine a place belongs to. The
> incremental arm can, and therefore can re-promote the ordinary-routine place
> when the resident returns rather than having to re-observe it. The measurable
> consequence is at the return, not during the disruption.

The original prediction is kept on the record as refuted rather than removed.

## Second amendment, 2026-09-24: the first cell on illness_v2 reverses the
## restated prediction too

One household (s3, 19 asked objects), 29 nights, same look stream, same words,
warm start on, 8-line read budget on both. Measured:

| | wholesale rewrite | claim store |
| --- | --- | --- |
| size of the notes at day 28 | 8 lines, 751 characters | 38 claims, 5,916 characters |
| text in common with the other format | **1-2%** | |
| claims or lines that group several objects | most lines | **0** |
| what fills the "which routine does this hold under" slot | "as stable storage", "during daily kitchen use", "stable daily routines" | **"current", on all 38 claims** |
| revisions | n/a | 59 |
| claims resting on an absence ("not in the kitchen") | n/a | 17 |
| nights identical to the night before | 12 of 29 | n/a |
| edits that carried something new | n/a | **59%** (below the 60% threshold; concern fired) |

**The restated prediction is refuted in the opposite direction from the first
one.** We predicted the claim store could name the routine a place belongs to and
the rewrite could not. On this scenario the **rewrite names conditions and
generalises across objects and residents, and the claim store does neither** — it
writes one flat claim per object-and-place and tags every single one "current".

The cause is an asymmetry introduced by the read budget itself, and it is worth
stating rather than patching away: the 8-line window puts **write-time pressure on
the rewrite arm only**, because the rewrite is one artifact that has to fit. The
claim store faces the budget only at *read* time, so nothing ever pushes it to
abstract; it accumulates. Worse, at read time it shows 8 of 38 claims chosen by
recency, which during the disruption means it shows the new facts and hides the
settled ones — the wrong way round for answering the return.

Two honest readings, and the choice is not ours to make alone:

1. **Accept it as the finding.** A single-artifact memory under pressure abstracts;
   an append-only claim store under no pressure does not. That is a real
   architectural result and it is the opposite of the paper's premise.
2. **Treat "current" as a specification failure and tighten it**, the same way
   requiring one-thing disagreements tightened the chooser. We asked for "the regime
   or condition it holds under" and the arm answered "current", which is not a
   condition. This is a correction, not a policy change — but it will move the
   result, so it is not made unilaterally.

**Two silently empty arms, found and fixed before the cells ran.** Both are worth
recording because neither would have shown up in an accuracy number - each would
have looked like "a weak memory".

1. With the explanation of what an edit is placed BEFORE the instruction to make
   edits, the model replied `{"edits": []}` to a night with six fresh sightings
   and an empty notes file. Putting the imperative first fixed that one night.
2. That was not enough. Over a full 29-night run the incremental arm then made no
   edit on **17 of the 19 nights on which it saw something it is asked about**,
   finishing a 15-object household with 6 claims and 1 revision. Three different
   wordings did not fix it. What fixed it was structural: on any night whose look
   found an asked-about object, the schema now REQUIRES at least one edit. Nights
   that found nothing may still make none, so the model is never forced to
   invent. After the fix, over nine nights: 14 claims, 9 revisions, and no night
   that saw something and said nothing.

The comparison numbers quoted above for the incremental arm come from the run
BEFORE this fix and are not a fair reading of the format; the rewrite-arm numbers
are unaffected by it. The full comparison will be rerun.

**The lever, if a genuine rewrite contrast is wanted.** A length cap is the
honest one: cap the summary at fewer sentences than the household has objects and
abstraction becomes compulsory, which is what makes forgetting real. That is a
design change and it is not made unilaterally.

## Third amendment, 2026-09-24: coverage is the wrong measure, and the chooser's
## candidate list was the cause of its collapse

**Coverage is unwinnable by construction and we are dropping it as the looking
factor's measure.** Measured on one household over the ten disrupted days, one room
a day: the fixed fair rotation visited 9 distinct rooms and saw **19 of 19**
asked-about objects. Complete coverage. That is an artefact of a one-room budget
matching a nine-room house, not a result about choosing observations, and any
coverage number would say the rota is as good as or better than anything.

**The replacement measure, pre-registered here: timeliness.** For each household,
the number of days from the first disrupted day (day 14) until the robot's notes
first assert something CORRECT about a moved object's new place. Reported per
household, paired within household, with a standard error and n; never pooled and
never per question. Households where an arm never noticed at all are listed rather
than scored, because "never" is not a number of days. Implemented in
`measure_timeliness.py`; the cells now log the notes as they read at the end of
every night, because a single overwritten notes file cannot say *when* the notes
first became right.

**The selection bias this measure cannot avoid, and its placebo.** Timeliness
conditions on "the objects the disruption moved", and that set is chosen by
comparing two windows - the bias the gate's author measured at a 16-point false
break on a scenario that should show none. Timeliness cannot avoid the conditioning,
because an object that did not move cannot be noticed to have moved. So every
timeliness number is reported beside a **placebo**: the identical measure applied to
a pretend disruption beginning on day 7, inside the ordinary fortnight, with
"moved" objects picked by comparing days 0-6 against 7-13. Nothing changed there, so
the placebo is the measure's own noise floor and a real result must clear it. No
moved-object slice goes anywhere near a headline accuracy number.

**The prediction, written down before the runs land.** A chooser worth having
notices on the first or second day; under a fair rotation the disrupted room comes
up on about the fifth day of ten and which day is luck. **We also write down the
possibility that the rota still wins on timeliness, in which case the looking half
of this paper is a negative result and we will say so plainly.**

**Why the chooser collapsed, and the fix.** All four variants tried visited ONE
room ten times out of ten, saw 7 of 19 objects, and none ever reached the room the
change had moved into. The cause was the candidate list: candidates were generated
by scanning the notes for disagreements, so **a room the notes never mention could
not enter the list** — and that is exactly the room a new disruption has moved
things into. At day 13 on that household the notes said nothing at all about three
of nine rooms, one of which was the living room where the change lands.

The repaired chooser therefore enumerates **every room**, each annotated with what
the notes currently predict would be found there, explicitly including "your notes
say nothing about this room", and is asked which single room's contents its notes
are least able to predict. This keeps faith with the hypothesis rather than
weakening it: finding an object in room Y refutes a claim placing it in room Z, so
every room is a possible site of disagreement. The old version could only see
disagreements it had already written down.

Of the two earlier repairs: requiring the two competing claims to be about the
**same object** stays — it took the share of looks that actually settled which
claim held from **0% to 80%**. Telling it **how long since it last looked in each
room** is withdrawn as a fix, because it changed nothing whatsoever; the
information stays available, since a real robot has it.

## Fourth amendment: the first timeliness numbers, and what they say about which
## factor is doing the work

One household (s3), both arms on a **byte-identical look stream** (both the fixed
fair rotation), so the looking is held exactly constant and only the notes differ:

| | days until the notes first got a moved thing right | moved things ever noticed |
| --- | --- | --- |
| wholesale rewrite | **7** | 2 of 9 |
| incremental edits | **0** (the first disrupted day) | 7 of 9 |

So on this household timeliness is dominated by **how the notes are written, not by
where the robot looks**. The mechanism is visible and follows from the read budget:
the rewrite has 8 lines and must drop something, and what it drops is the moved
objects' new places; the claim store accumulates and keeps them.

One caveat on method, stated because it is an asymmetry: the rewrite number comes
from its actual per-night summaries, while the incremental number is reconstructed
from when each claim first appeared. The cells launched after this amendment log the
per-night text for both formats, so subsequent numbers are exact for both.

## Why 41% of the incremental arm's edits re-worded rather than revised

Asked whether the re-wordings cluster on nights that saw nothing relevant. **They do
not.** The nine nights that saw nothing produced zero edits — the forced-edit rule
correctly never fired on them — and all 97 edits came from the 20 nights that did
see something. So the honest fix that was proposed (stop forcing an edit on a blind
night) is already the behaviour.

The actual cause is visible in the breakdown of those 97 edits: **38 adds, 59
revises, and 0 attachments of evidence to an existing claim.** The arm never once
used the "record evidence" action, so every re-confirmation of a claim it already
held became a duplicate claim. That is a property of the arm, reported as such. The
prompt has not been touched to improve the number.

## Fifth amendment: why the memory answers below the trivial rule, and it is not
## the read window

**The result that prompted this.** At the control freeze point, one household, the
claim store scored **33% correct against a floor of 48%** — fifteen points *below*
the trivial rule of "each object's commonest settled place" — with a clean sanity
assay (8 distinct spots named, 30% on the commonest, nothing unparsed, no concerns).
So not a degenerate arm.

**Why that is close to self-contradictory, and so worth diagnosing rather than
accepting.** At the control point the notes were written from thirteen ordinary days
of looking, and the floor is very nearly what thirteen ordinary days should have
taught. A memory built from exactly that evidence landing under it is more easily
explained by the read path than by the claims being wrong.

**The diagnostic, which cost no GPU at all**, because the full store and the lines
actually read are both on disk and the window is recomputed deterministically. Every
wrong answer falls in exactly one bucket (`diagnose_the_read_path.py`):

| of 20 wrong answers | share |
| --- | --- |
| the selection rule — the right claim was in the store but not in the window | **0%** |
| the point of use — the right claim WAS shown and the model answered against it | 45% |
| write time — no claim named the true place | 15% |
| write time, unavoidable here — the thing moved after these notes were frozen | 40% |

Of the **12 that were avoidable at all**: **75% point of use**, 25% write time, **0%
selection**.

**Three conclusions.**

1. **The read window is innocent and a bigger budget would buy nothing.** Not
   because eight lines is generous, but because the selection is *relevance-first*,
   not recency-first: `claims_in_reading_order` puts claims naming the object being
   asked about ahead of everything else, then orders the rest by recency. So the
   claim that matters is in the window whenever it exists at all. An unbounded-budget
   run is going ahead anyway as a **clearly-labelled diagnostic, never an arm**
   (`this_is_a_diagnostic_not_an_arm`, `LOCKED` unmodified), precisely because the
   partition makes a falsifiable prediction: it should buy nothing.
2. **The dominant fault is at the point of use.** The model is shown a claim naming
   the true place and answers something else. That is a finding about reading, not a
   bug in the memory, and it is the same read-time failure a previous study measured
   at 807 of 890 questions.
3. **40% of the control point's errors are unavoidable by its own design** — the
   notes stop at day 13 and the questions come from days 14-23, so for every object
   the disruption moved, no claim could have named the true place. Counting those
   against the memory would be blaming it for not being clairvoyant, so they are
   split out and reported separately.

## The room available at each freeze point, and where we expect to detect nothing

To be stated prominently rather than in a footnote: **the room available is 10 to 20
points on illness_v1, not the 46 the code asserted**, because that figure came from
the superseded scenario. Reporting against 46 would have made every effect look like
a third of its true size relative to the room.

Two consequences carried forward in advance:

- the **day-16 looking point has the widest room, 20 points**, now measured on this
  scenario rather than assumed. That is where the looking factor is reported.
- the **"did it keep the old routine" point has only 10 points of room**, the
  narrowest of the four, because by the return most things are back where a
  never-updated memory already had them. **It is therefore the freeze point where we
  are least likely to detect anything, and we say so here in advance rather than
  discovering it as a null.**

## A specific limitation of evidence-linked revision, as we implemented it

Of 97 edits the claim store made across a month: **38 adds, 59 revises, and zero
attachments of a sighting to a claim already held.** The arm never once used the
action that exists for confirming something. So it has no way to *confirm*: every
re-observation of a place it already believes has to become a new claim or a
re-wording of an old one, which is exactly why 41% of its edits carried nothing the
notes did not already say.

That is a real and specific limitation of evidence-linked revision as built here,
and it is more interesting than the 59% figure it explains. The prompt has not been
touched to improve either number.

## Sixth amendment: the primary result needs no baseline at all

**The comparison.** Two freeze points ask **the same questions, days 14-23**. The only
difference between them is whether the notes were written through day 13 or through
day 23. Same household, same arm, same questions, same reading budget, same prompt -
only ten days of nightly note-writing over the disruption separates them. So their
difference *is* the answer to "did it learn the new routine", and no floor, ceiling,
oracle or baseline appears in it. Every argument about which baseline is fair becomes
irrelevant for the headline number. Implemented in `did_it_learn_the_new_routine.py`.

**Where it stands** (notes through day 23 minus notes through day 13):

| arm | level | mean | spread | n | verdict |
| --- | --- | --- | --- | --- | --- |
| claim store | the right room | **-1.3 pts** | 7.3 | 5 | smaller than the spread, not detected |
| claim store | the exact shelf | **+4.0 pts** | 6.4 | 5 | smaller than the spread, not detected |
| wholesale rewrite | the right room | **+0.0 pts** | 4.7 | 2 | not detected |
| wholesale rewrite | the exact shelf | **+3.3 pts** | 4.7 | 2 | not detected |

Ten days of watching the disrupted household, with nightly evidence-linked revision,
buys about four points at shelf level and nothing at room level. **Notes that watched
the entire disruption answer its questions no better than notes frozen the day before
it began.** Both ways of writing notes land in the same place, so on this measure the
memory factor is a null as well.

Below six households we use the stricter bar - the effect must exceed the spread
across households, not merely its standard error - and at n=5 it does not. At n=10 an
effect of this size would clear the two-standard-error bar, so finishing all ten
households on both arms is the whole game.

## The three reference points, and which is a bar

The floor we were judging against gave the baseline **strictly more information than
the robot ever had**: "each object's commonest settled place" was computed from the
true answers to every settled question, i.e. complete ground-truth observation of the
whole house every day, while **the robot looked in one room a day** and gathered
roughly 100 to 190 sightings. It was not unbeatable by accident but by construction.

So three reference points are reported at every freeze point, named so they cannot be
confused (`score_at_both_levels.py`):

- **a frequency rule with the robot's own sightings** - the fair bar, computed **per
  arm from that arm's own look stream**, because the looking arms see different rooms
  and a shared baseline would hide the entire looking factor;
- **a frequency rule with complete observation** - kept only as an upper *reference*;
- **the per-object oracle with complete observation** - the ceiling.

Against the fair bar, at the control point: shelf level 33% against 34%, level; room
level 67% against 59%, ahead by about 8 points and level with the oracle that saw
everything. That is a secondary claim and a useful one, but it does not carry the
headline, because it invites an argument about which baseline is fair and the
freeze-point difference above does not.

**Scoring at two levels, with the room level primary.** The hypothesis is about a
memory being useful for later object search, and a robot that walks into the right
room has found the thing. Naming the exact shelf is a precision we never asked for.
The shelf number stays visible as the strict secondary; nothing is renamed away.

## Seventh amendment: the naive chooser is a BUG, not a finding. Retracted.

Earlier amendments described the naive chooser's collapse onto one room as "the honest
consequence of the hypothesis taken literally", with a mechanism: a room the notes
never mention cannot be the site of a disagreement. **That claim is retracted. The
collapse is a serial-position artefact.**

**The test.** Same household, same notes, same days, naive chooser. Only the order the
rooms are presented in differs.

| | rooms chosen | positions chosen |
| --- | --- | --- |
| the order they always come in | bathroom, 8 of 8 | **1, 1, 1, 1, 1, 1, 1, 1** |
| the order shuffled each night | bathroom, living, kitchen, bathroom, kitchen | 1, 1, 6, 1, 6 |

The chosen room **changes when the presentation order changes**, and every choice is at
position 1 or position 6 - the first or last item. It was never reasoning about the
house. The tell was there to be seen without any run: `household.rooms` sorts
alphabetically, and the bathroom sat at position 1 or 2 in all three households where
the collapse was observed.

**Consequences.** The naive chooser must be fixed and rerun before it is reported at
all; it cannot appear as an arm whose failure means anything. No sentence about "the
hypothesis read literally fails for an intrinsic reason" may be written in either
direction. The chooser now logs, per night, the candidate list in presented order, the
room chosen, its position in that list, and the model's stated reason, so this is
checkable from the log rather than by a special run.

**On the repaired chooser I first argued badly and then tested it.** The original
argument here was that storage sits *last* in that household's order, "so position does
not explain it". That was wrong, and wrong in the same way as the claim it was defending:
the naive chooser's positions were **1, 1, 6, 1, 6** - first *or* last, never the middle -
which is the classic serial-position pattern, so "it fixates on the last item" is a
description of the artefact rather than evidence against it.

So the identical shuffle test was run on the repaired chooser, and it passes:

| repaired chooser, same household and notes | rooms chosen | positions |
| --- | --- | --- |
| the order they always come in | living, 8 of 8 | **5, 5, 5, 5, 5, 5, 5, 5** |
| the order shuffled each night | storage, living, living, living | **4, 1, 2, 3** |

Position 5 under the fixed order - neither first nor last - and under shuffling it
stayed on **living** while that room's position moved through 1, 2 and 3. So the
repaired chooser is choosing on content, not on position. And `living` is the room this
household's disruption moves things into, so it is choosing the right room.

The "a permanently empty room is perfectly unpredictable and perfectly uninformative"
reading of the objective is therefore **not supported by this test and is withdrawn as
a claim.** The storage concentration seen earlier came from the fixed-order cells, which
are confounded and have been moved to `superseded_looking_factor_fixed_order/`.

All chooser arms now shuffle the candidate order every night from a recorded seed, so
no chooser result can be position-driven again.

**The mechanism behind both fixations, logged rather than guessed.** The chooser now
records, per night, what its notes predicted for every candidate room and how many claims
it held about each. At the moment of choosing in `hh_s6_t03`:

| room | claims the notes hold |
| --- | --- |
| kitchen | 6 |
| bathroom | 3 |
| bedroom_1 | 3 |
| entry | 2 |
| **living** | **0** |
| **storage** | **0** |

The two rooms it fixated on across all runs are exactly the two it held **no claims
about**. So the objective rewards whatever room the notes predict worst, and how badly the
notes predict a room has little to do with whether looking there would settle anything:
**least evidence looks like least certainty.** That covers both fixations with one
mechanism and does not require the room to be empty, which the withdrawn "permanently
empty room" sentence did.

## What the looking result actually shows, and it is not what the hypothesis proposed

**The hypothesis has two halves and only one of them is doing the work.** We proposed that
a robot remembers a home better when it looks where its own guesses disagree. The
repaired chooser does beat the fixed rotation - 3.00 moved objects per look against the
rota's coverage, and 1.00 for the naive version - but the claim-count log says it is not
winning by discriminating between competing claims. It is winning by going to the rooms it
holds **no claims about at all**: living and storage, 0 claims each, against 2 to 6 for
every other room.

That is **exploration, not discrimination**. Least evidence reads as least certainty. The
half of the hypothesis about settling disagreements between competing routine claims is
not what produces the gain, and the structured two-claim action - which we built, logged
and checked for diagnosticity - is decoration on top of a policy whose real content is
"visit what you have not written about".

This is worth stating plainly rather than softening, because it is a sharper contribution
than a confirmation would have been: **choosing where to observe does beat a fixed
schedule, and it does so for a reason our hypothesis did not propose.** It also tells the
next person what to build - an explicit novelty or coverage term, not a disagreement-
scoring one.

**Was the room worth visiting? On the measure appropriate to a looking policy, yes.**

| hh_s6_t03 | room chosen most | moved things per look | best room available |
| --- | --- | --- | --- |
| naive chooser, fixed order | bathroom 8/8 | **1.00** | bedroom_1, 4 |
| naive chooser, shuffled | kitchen 4/8 | 1.50 | bedroom_1, 4 |
| repaired chooser, fixed order | living 8/8 | **3.00** | bedroom_1, 4 |
| repaired chooser, shuffled | living 7/8 | **2.62** | bedroom_1, 4 |

**A disagreement about this number, reconciled, and it is the same fork as the s4
exclusion rule.** Measured over the daytime hours a look could happen, `hh_s6_t03` has 9
moved objects and they land bedroom_1 4, **living 3**, kitchen 1, bathroom 1 - so `living`
is the second-best room in the house. Measured at question times only, it has 6 moved
objects landing bedroom_1 3, kitchen 1, entry 1, **living 1** - on which `living` looks
like a poor choice. Both are reproduced exactly; they are the same two methods that
disagreed over whether to exclude household s4, and that was settled in favour of daytime
hours because question times select on the outcome measure.

The same reasoning applies with more force here: the thing being judged is a **look**, and
a look happens at 13:00. So the daytime measure is the right one for a looking policy, and
on it the repaired chooser takes 3.00 moved things per look against a ceiling of 4, while
the naive chooser takes 1.00. The repair works.

## Eighth amendment: the write-side difference, measured semantically

Byte-identical repetition is brittle - near-verbatim rewording slips past it - so the
same question was asked semantically, with one extractor shared by both arms: **a night
is vacuous if the (thing, place) pairs it asserts contain nothing the memory had not
already asserted.**

| share of nights recording no fact the memory did not already hold | paired difference |
| --- | --- |
| all nights | **+18.5 pts, se 4.5, n=10, detected, 9 of 10 same direction** |
| nights that saw something asked about | **+31.3 pts, se 6.9, n=10, detected, 9 of 10 same direction** |

Comparable to the byte-identity figure of +23.7 and immune to the rewording objection:
two measures built on different principles agreeing in direction and rough size, which
is the reassurance this claim needed.

**The number moved by 18 points as extractor faults were fixed, so the audit matters
more than the figure.** The informative-nights difference read **+49.6** with a faulty
extractor, **+35.3** once possessive forms were understood, and **+31.3** after the
hand-check fixes. Every fault penalised the rewrite arm alone, because only it writes
prose.

**Why the audit matters more than the value, and what must appear in the paper beside
it.** All four extractor faults penalised the **rewrite arm alone**, because only it writes
prose: matching bare identifiers recovered nothing from three of ten households, and those
three then scored 100% vacuous as pure measurement. A one-sided measurement error on the
arm we already expected to look worse is exactly the error that survives peer review, and
the last two faults were caught only by hand-checking ten nights per arm. So the recovery
rates go in the paper next to the +31.3, because they are what licenses the comparison at
all.

**Even-handedness, which is the check that makes the number usable:** a fact is now
recovered on 99% of the rewrite arm's nights (worst household 97%) against 100% for the
claim store, at 10.6 facts a night against 13.4. The residual gap is plausibly real
rather than instrumental - the rewrite arm has eight lines and must drop facts, which is
the read budget working as designed.

**Four extractor faults, each of which gave a confidently wrong answer, and two found
only by hand-checking ten nights per arm.** Matching a place by the article-prefixed form
`plain_place_name` produces ("the cupboard") against prose that writes "Kitchen
cupboard" recovered pairs on **8 nights of 29**; matching bare words recovers 24 of 29.
Pairing every thing with every place named in a line emits a cross-product - one line
about three nightstands and three books asserts nine pairs, most false, and a rewording
reshuffles them and counts as new information - so each thing is paired with the nearest
place mentioned.

Matching only the object identifier recovered **nothing at all** from three of the ten
households' summaries, because the rewrite arm names things as people's possessions -
"Aisha glass", "Felix's book", "Hana, Ines and Yuki mugs". Those three households then
scored as 100% vacuous, which was pure measurement. A class word alone is still not a
match, since "the mug" cannot be attributed to anyone without inventing a fact.

**Found by hand-check, and only in the rewrite arm's text:** plain substring matching
credited "Aisha glasses" to both `glasses_aisha` and `glass_aisha`, so matching is now on
whole words; and a place written `KITCHEN_TABLE` or `BATHROOM_TOWEL_RACK` matched nothing,
losing every fact on those lines, so the text is also searched with underscores
flattened to spaces. Of ten nights hand-checked per arm, the claim store's lines were
read correctly throughout, while the rewrite arm's had two total misses and one invented
pair before these fixes and none after.

**And one methodological trap that reversed the result.** Reconstructing the claim
store's nightly wording from `first_written_day` and the current statement misses every
revision, so a claim that moved an object on night 16 looks as though it always said
the new place, or never did. Measured that way the difference was **+10.7, se 8.5, not
detected** - and reporting it would have said the antecedent had collapsed. The wording
in force on a night is the `was` snapshot of the earliest revision made after it, which
is what `statement_as_of` now computes. The rewrite arm's per-night text is exact and
recorded, so getting the claim store wrong biased the comparison in one direction only.

## Ninth amendment: the error partition reverses. The loss is at WRITING, not reading.

The fifth amendment reported 70% of avoidable errors at the point of use and concluded that
the notes contain the right answer and the reading step loses it. **That is retracted.**
Recomputed with the audited extractor across **357 wrong answers in all 20 cells** at the
decisive freeze point, against 120 across six before:

| of 357 wrong answers, strict shelf matching | pooled | claim store | wholesale rewrite |
| --- | --- | --- | --- |
| the selection rule | **0%** | 0% | 0% |
| the point of use | **2%** | 2% | 1% |
| write time - no line named the true shelf | **98%** | 98% | 99% |

A clean room-level partition - answers that named the wrong *room*, asking whether any line
placed the object in the right room - gives **9% point of use, 91% write time, 0%
selection** across 211 wrong answers, with an asymmetry worth noting: 18% for the claim
store against 2% for the wholesale arm.

**Two faults produced the 70%, and the hand check caught the one that mattered.**

The partition never used the audited extractor. It called `the_notes_assert`, which carried
the same article-prefix, underscore and possessive-form faults that had already been found
and fixed for the vacuity measure - fixed in one place, left in place in this caller.

Worse, `the_notes_assert` had a **room fallback**: a line naming the right room and no other
room counted as asserting the place. So notes saying "kitchen sink" were credited with
asserting "kitchen table", and `BATHROOM_TOWEL_RACK` with asserting the bathroom shelf. Same
room, different shelf. In a partition about whether the notes held the true *place*, that
converts a write-time error into a point-of-use error - inflating the single bucket the
contribution rested on. It is the right rule for timeliness, where noticing a move into the
living room counts, so it is now a parameter and the partition passes it off.

Neither fault was visible in the aggregate. Ten errors per arm read by eye found the room
fallback in the first five.

**What this does to the story.** The three-part account becomes: the two formats build
measurably different memories (+31.3 on vacuity), neither is read better than the other
(the outcome null), and **the loss is at writing - the notes do not hold the right shelf in
98% of wrong answers.** That is a different contribution from the one we had, and a simpler
one.

**What survives untouched: 0% from the selection rule, at both levels.** That bucket
compares what was in the store against what was in the window, both the same text, so it
does not depend on prose recovery at all. A larger reading budget cannot help.

## Tenth amendment: every capped figure measured two days, not ten

`run_frozen_memory_test` took `questions[:max_questions]` from a time-ordered list, so a
30-question cell asked **2 of the available days**, with 24 of 30 questions from the first:

| freeze point | window | what the first 30 covered |
| --- | --- | --- |
| before anything changed | days 14-23 | day 14 x24, day 15 x6 |
| did it learn the new routine | days 14-23 | day 14 x24, day 15 x6 |
| did the looking arm find it sooner | days 17-19 | day 17 x24, day 18 x6 |
| did it keep the old routine | days 29-31 | day 29 x24, day 30 x6 |

Day 14 is the transition day and the hardest in the window, so the capped numbers are biased
low - by about **8 points at shelf level and 4 at room level**, measured across seven
full-window cells. (An early reading of one household suggested 25 points and a factor of
four; that was `hh_s6` being an outlier on that one day, and it is struck.)

The **paired differences were never invalidated**, because both freeze points were asked the
identical question set. What narrows is their scope: they measure whether ten days of
revision helps answer questions about the first two disrupted days. The paper quotes the
full-window versions and labels the capped ones **"the first two disrupted days"**.

`spread_across_the_days` now replaces the slice: a cap of 30 takes 3 questions from each of
10 days. No capped run can repeat this.

## Eleventh amendment: the noise floor, on the quantity the paper quotes

Both freeze points rerun unchanged **against a fresh cache directory**, because the client
keys its cache on a hash of the prompt and an unchanged rerun would otherwise replay every
answer and report a floor of exactly zero, fast, looking like a clean result.

Measured: **1.1% of individual answers differ** between run and rerun, and the floor on the
day-23-minus-day-13 difference is **1.1 points mean absolute move, largest 3.3, n=3 cells**
so far. So the +7.0 and +5.0 shelf gains sit clear of it.

Not a general property of this server, which costs 3-5% of answers elsewhere: a property of
this task, where the prompt is eight lines and the answer is one item from a short list. The
model's reasoning text and stated confidence wander between reruns while the place it names
does not - worth recording because a previous paper's subject was whether a confidence
signal is usable.

## Twelfth amendment: the bottleneck is OBSERVATION, not memory maintenance

The write-time errors - 98% of all wrong answers - split three ways by asking that arm's own
`looks.jsonl` whether it ever saw the object at its true place on or before the freeze day.
351 write-time errors across all 20 day-23 cells:

| | pooled | claim store | wholesale rewrite |
| --- | --- | --- | --- |
| **a sensing failure: never saw it there at all** | **65%** (229) | 67% | 64% |
| a note-taking failure: seen once, no line names it | 17% (60) | 17% | 17% |
| a note-taking failure: seen more than once, no line names it | 18% (62) | 16% | 19% |
| | **65% observation, 35% note-taking** | 67/33 | 64/36 |

**This is the paper's thesis.** Two thirds of the memory's failures are about things the robot
never saw in their new place. No note-writing policy of any kind could have recorded them, so
the limiting factor sits upstream of the memory entirely, at one room a day.

**It unifies three findings that were separate.** The two formats differ enormously in what
they write (+31.3 points of vacuity) and are indistinguishable in what they answer (within
3.4 points at room level) - because the majority of what they get wrong is neither's fault.
And the looking factor is the only place anything helped, which is exactly what an
observation bottleneck predicts. Three results, one mechanism.

The split is **near-identical across the two arms** (67/33 against 64/36), which is the
strongest form of this argument: if the bottleneck were maintenance, two policies this
different would not fail in the same proportions.

**What the minority says, and it should not be dropped.** 35% of write-time errors are things
the robot did see and the notes do not carry, and **18% were seen more than once**. So
note-taking is not blameless - it is the smaller cause. A claim it saw twice and never wrote
down is the strongest form of the failure and it is a fifth of the write-time errors.

## Null risks, stated in advance

0. **The two ways of writing notes may not differ at all.** Measured above: given
   the same evidence, the rewrite arm converges on a copy-forward per-object
   table, which preserves the past as well as a claim store does. What still
   differs is whether the notes can name the condition a place holds under. If
   that turns out not to differ either, the memory factor is not separable in this
   setup and should be reported as such rather than run four ways.
1. **The disruption may still be one sentence long.** Even here, 4 of 10
   households send 83-100% of their movers to the same destination. The memory
   factor is strongest in s1, s3 and s4 (5 destinations each) and close to
   unfalsifiable in s2 and s9 (1 destination each). We will report the memory
   factor against the number of distinct destinations per household.
2. **The control freeze point is a null by construction** — a useful check, not a
   place an effect can live.
3. **Only 8 to 18 objects are asked about per household.** 644 to 744 questions
   are not that many independent facts; the effective sample is about 48 moved
   objects across ten households. A per-question binomial interval would be about
   four times too narrow, so intervals cluster on the household, and on the
   object within the household.
4. **The choosing arm's advantage is close to a step function per household.**
   The disruption concentrates into one room, so an arm that finds it once has
   found all of it. With ten households that means high variance on the paired
   difference.
5. **The return is not clean.** Of the objects that move, only 20% to 100% per
   household (mean 61%) go back to where they were; the rest stay put or end up
   somewhere third, and some objects that never moved have a different commonest
   place in the return window from ordinary drift anyway. "Did the memory revert
   correctly" is contaminated at roughly the 40% level, worse than the 20%
   assumed. It is measured and reported, never treated as binary.
6. **The first household will flatter.** Effects in this project have shrunk by
   half or more every time households were added. No result will be reported from
   fewer than all the included households.
7. **A cache hit is not agreement.** Generation on this server is not
   deterministic: the same notes rerun on the same data change 3 to 5% of their
   answers. Two arms whose outputs match because one was served from the
   prompt-hash cache have not been shown to agree. Differences below 5% are noise.

## How results will be reported

Per household, then combined: paired differences with standard errors and n,
clustered on the household and on the object within the household, never on the
question. Never a pooled number mixing household sets. We say what we measured
before we say what it means.


## The third way of writing notes: told whether it was right

Written 2026-09-24, before the arm has produced a single number. Code:
`src/self_improve/write_the_notes_told_if_right.py`. It is the claim store plus
exactly two things, both taken from arxiv 2510.04618: each night it is shown how the
day's questions went and says which of its claims helped and which misled, and it may
join two claims into one line. Everything else - the same day description, the same
prompt settings, the same read window with no limit - is the claim store's.

**What it is being asked.** Does a memory that finds out whether it was right notice a
routine change sooner, and does it keep the old routine's claim while doing so? The
claim store has never had this. Both of its two things are separate, and their sizes
in the paper are known: in the paper's own ablation, itemised edits plus the
joining step buy 12.7 points of average and the reflection step buys a further 4.3 on
top. So the reflection step is the smaller half even where it works, and this write-up
will not lean on it producing a large effect on its own.

**What would count as an effect.** On the movers, paired within household across all
ten homes, first-room-correct in the disrupted window and in the first four days after
the return, against the plain claim store: a difference of at least twice its standard
error, computed clustered on the household. Below that bar it is reported as no effect
found, with what the interval excludes stated.

**What would be an interesting null.** That being told the outcome changes nothing
measurable on accuracy while visibly changing what gets written - fewer repeated
claims, more set-asides, the ordinary claim kept more often. That is a result about
where the bottleneck is, not a failure, and it is the direction this project's
evidence already points: the robot is mostly limited by what it has looked at.

**What would make the arm uninterpretable, and is guarded.**
1. *Telling it the answer.* The first version of the reflection prompt printed the
   true room whenever the first room was wrong, and the true spot on every question
   including searches that never found the object. That is the answer key, which no
   other arm gets, and it would have made every accuracy comparison meaningless. It
   now names a place only when the search actually found the object there. The
   rule-based fallback tally was rebuilt the same way and reads no ground truth at
   all. A six-day run made under the leaking version is at
   `results/self_improve/superseded_told_if_right_smoke_LEAKED_THE_TRUE_ROOM_2026-09-24/`
   and is not evidence about anything.
2. *Joining the two claims the study is about.* The code's joining backstop picks by
   shared words, which pointed straight at the pair of claims for one object under two
   routines - the pair the pre-registered prediction is about. It now refuses to join
   two claims unless they hold under the same routine and name a common object, and
   never joins a claim that has been set aside. When nothing may be joined the notes
   simply stay over their line.
3. *An unexplained line count.* It is three lines per object the robot is asked
   about, because 24 of the 75 movers in these ten homes do not end the month in the
   spot they started in and so need a third claim, not two. Counted by
   `results/self_improve/check_how_many_states_a_mover_has.py`.

**What must be reported before any outcome.** How often the judging step named a claim
that does not exist; how many nights fell back to the rule instead of the model; how
many joins were the model's and how many the code's; and the two calls a night this
arm costs, against one for the other two.
