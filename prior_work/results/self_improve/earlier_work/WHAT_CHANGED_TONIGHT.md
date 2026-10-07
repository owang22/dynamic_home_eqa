# What changed tonight, and what it cost

Written for Oliver's 11:00 read on 2026-09-24 by the coordinating session. Plain names throughout.
Every number here was computed from the data at the time of writing, not recalled.

---

## The hypothesis has not changed

> Choosing which observations to make, and then revising memory in small evidence-linked pieces,
> produces a more useful memory for later object search than observing on a fixed schedule and
> rewriting memory wholesale.

Everything below is about how that gets tested, not about what is being claimed.

---

## Four things went wrong and were fixed before they cost a night

### 1. The scenario we were about to spend the night on fails a check we built tonight

You asked that simple non-language-model methods show the expected shape before a scenario earns
any GPU time: learn the settled fortnight, break when the disruption lands, re-learn during it,
break again when ordinary life resumes. That gate now exists, runs in about two seconds for ten
households, and is wired into the scenario checker so one command covers all seven checks.

It immediately failed the scenario we had just built. A forgetting learner loses only **1.6 points**
on the first two days back to normal, against a 5-point bar and with a household-clustered error of
4.2 — so in that scenario the return is not a change at all, and no arm could be measured on it.

The scenario we had been calling the failed one passes everything and beats it on every leg:

| leg, measured on a timetable with a three-day memory | illness_v1 | illness_v2 |
|---|---|---|
| learn the settled fortnight | +14.2 | +14.2 |
| break when the disruption lands | **−13.3** | −10.2 |
| re-learn during the disruption | **+13.5** | +7.4 |
| break again on the return | **−8.9** | −1.6 → fails |
| households showing all four legs | **5 of 10** | 4 of 10 |

**A correction to the record.** "illness_v1 failed seven ways" is no longer true of the directory
now sitting at `results/self_improve/runs/illness_v1/`. That claim was about an earlier build. The
current contents pass all seven checks, with 40 to 42 points of headroom in every window, 58 moved
objects across ten households landing on 13 different receptacles, and the commonest destination
taking only 29% of movers. Whatever we regenerated along the way fixed it, and v2's entire reason
for existing evaporated. The gate tables are saved beside each run as `seven_check_gate.txt`.

The night's compute moved to illness_v1. The superseded runs are under
`results/self_improve/superseded/`, moved rather than deleted.

### 2. The two arms of the study were freezing memory on different days

`frozen_memory_test.py` is the study's primary measurement — freeze the notes, stop all looking,
put the same held-out questions to every arm — and it refuses to run unless the notes are written
through exactly the day its freeze point asks for: **13, 16, 23 or 28**. The script that writes the
notes was saving them at **13, 18 and 28**. Day 18 is not a freeze point at all, and 16 and 23 were
never saved. Every sweep before this one produced notes usable at one freeze point out of four.

Fixed by setting the peek days from the launcher, so the file the builder owns did not have to be
edited mid-flight. All ten households now have notes frozen at all four days for the
wholesale-rewrite arm, with the incremental arm following.

### 3a. The dependent variable was being scored on a precision we never asked for

The answering step finally ran, and its first numbers said the memory answers **worse than the
trivial rule** of "each object's commonest settled place" — 33% correct against a floor of 48%. That
would have inverted the paper.

It is largely an artefact of scoring. Re-scoring the same six answer files on whether the named place
is in the **same room** as the true place:

| | mean across households |
|---|---|
| names the exact shelf | **33%** (standard error 5.9, n = 6) |
| names the right room | **67%** (standard error 4.3) |

Between a fifth and three-quarters of what was counted as an error is the robot naming the right room
and the wrong shelf — bathroom shelf instead of towel rack, counter instead of sink, bed instead of
desk. The hypothesis is about a memory being *useful for later object search*, and a robot that walks
into the right room and looks around has found the object. Shelf-level precision is a stricter thing
than usefulness.

Both are now reported, room level as the primary and shelf level as the strict secondary.

**And the room-level rescoring does not rescue the result.** I computed the floor and ceiling at room
level across all ten households, and it went against my own suggestion:

| freeze point: before anything changed, n = 10 | floor | ceiling | room available |
|---|---|---|---|
| exact shelf | 55% | 71% | 16 points |
| room only | **67%** | 79% | 12 points |

Measured room-level accuracy is 67%. The room-level floor is 67%. So the memory lands **exactly on
the floor and captures none of the 12 points available** — "catastrophically below the trivial rule"
becomes "indistinguishable from the trivial rule", which is not good news, only less bad news.

What the two levels together say is sharper than either alone: the notes carry room information about
as well as a simple frequency rule does, and their shelf-level assertions are **22 points worse** than
one. The memory is adding noise at the shelf level rather than information.

**The framing correction that matters most, and I helped get this wrong.** At the freeze point
"before anything changed" the floor is **not a bar to beat — it is the predicted value.** The notes
have seen only the ordinary fortnight, the questions come from the disrupted days, so the best any
memory built from that evidence can do is reproduce the settled routine, which is exactly how the
floor is defined. Landing on the floor there is the design working. The alarm should never have been
raised at the control point.

The hypothesis can only win or lose at **"did it learn the new routine"** — notes through day 23,
questions from the disrupted days, where the notes have seen the whole disruption and ought to clear
the floor. That freeze point is now the priority across all ten households and both arms.

### 3b. The floor itself was an oracle, and there is a comparison that needs no floor at all

The floor — "each object's commonest settled place" — is computed from **the true answers to every
settled question**, which is complete ground-truth observation of the whole house for thirteen days.
**The robot looked in one room per day.** So the baseline had strictly more information than the
robot, and was unbeatable by construction rather than by accident. Rebuilding the identical rule from
each arm's own sightings:

| baseline, n = 10 households | exact shelf | room only |
|---|---|---|
| with complete ground truth (what we were using) | 55% | 67% |
| **with only the robot's own sightings** | **34%** | **59%** |

Against the fair version, at the decisive freeze point, the memory is **+4.7 points** at shelf level
and **+6.6** at room level (standard errors 4.5 and 4.6, n = 5) — both positive, neither detected yet
at the stricter bar we use below six households. At room level the memory sits level with the oracle
that saw everything, which is worth one sentence.

**But the cleanest test in the study needs no baseline at all, and it is the one to lead with.** Both
freeze points ask *the same questions, from days 14 to 23*. The only difference is whether the notes
were written through day 13 or through day 23. Same household, same arm, same questions, same reading
budget, same prompt — ten days of nightly revision over the disruption is the only thing separating
them. So the difference between them *is* the answer to "did it learn the new routine", with no floor,
no ceiling and no oracle to argue about.

On the five households that have both:

| household | naming the exact shelf | naming only the room |
|---|---|---|
| hh_s0 | +7 | −3 |
| hh_s1 | +1 | +2 |
| hh_s2 | +13 | +10 |
| hh_s4 | −4 | −10 |
| hh_s5 | +3 | −3 |
| **mean** | **+4.0** | **−0.8** |

**Ten days of watching the disrupted household, and nightly evidence-linked revision, buys about four
points at shelf level and nothing at all at room level.** Notes that watched the entire disruption
answer its questions no better than notes frozen the day before it began.

That is very likely the paper's core result, and it is a negative one with a mechanism rather than a
shrug. It also matches the earlier study's shape: there, language memories gained about ten points
across the spell where counting methods gained thirty-one. Here the gain is smaller still.

Two honest caveats. **n = 5**, and the spread is wider than the mean, so nothing is detected yet; at
ten households the same effect size would clear the bar, and all ten are running. And the day-23 notes
hold more claims than the day-13 notes, so the eight-line reading window bites harder on them — a
confound that **understates** what the notes learned. A diagnostic with the window removed, run at both
freeze points on one household, separates "the notes did not learn" from "the window did not deliver
what they learned", and is the single most informative cell left.

### 3c. Where the failure sits — and this is the paper's thesis, after being overturned once

**The first version of this was wrong and said close to the opposite.** It reported 70% of avoidable
errors at the point of use, concluded "the notes contain the right answer and the reading step loses
it", and I wrote that up as the paper's contribution. The matcher behind it had a **room fallback**: a
line naming the right room and no other room was credited with asserting the place, so notes saying
"kitchen sink" counted as asserting "kitchen table". Correct for a timeliness measure, exactly wrong
for a partition whose whole purpose is separating shelf-level failures. A twenty-judgement hand check
found it; no amount of extra data would have.

Recomputed with the audited matcher, on **1,305 errors** instead of 120:

| naming the exact shelf | share |
|---|---|
| the reading rule picked the wrong lines | **0%** |
| the point of use — the right shelf was written down and another answered | **4%** |
| write time — no line named the true shelf | **96%** |

**So the loss is at writing, not reading.** And the next question splits that 96% into the two things
it could mean. Using the **structured sighting records**, so no text matcher is involved at all:

| of the write-time errors | share |
|---|---|
| **a sensing failure — the robot never saw the object there at all** | **75%** |
| a note-taking failure — seen once, no line names it | 10% |
| a note-taking failure — seen more than once, no line names it | 15% |

**Three quarters of the memory's failures concern objects the robot never saw in their new place.** At
one room a day, no note-writing policy of any kind could have recorded them. Computed independently
twice at the capped scale — 63.9% by this session and 65% by the builder, agreeing within a point
before either saw the other's number — and rising to 75% across all ten days.

**The strongest form of the argument is that the two arms fail in the same proportions** — 67/33
against 64/36 — despite differing by 31 points in what they write. Policies that different could not
fail alike if the bottleneck were maintenance.

The note-taking residue stays: **15% are objects the robot saw more than once** and the notes still do
not carry. The sentence is "predominantly observation, with a real note-taking residue", never
"memory maintenance is irrelevant".

**One thing from the original version survives intact: 0% from the reading rule**, at both levels. My
hypothesis that the eight-line window was hiding the relevant claim was wrong, and wrong for a reason
worth keeping — the selection is not recency-based, it puts claims naming the asked-about object ahead
of everything else, so the claim that matters is in the window whenever it exists at all. A bigger
reading budget cannot help.

### 3. Nothing in the repository was calling the primary measurement

`frozen_memory_test.py` has no caller anywhere in the codebase. Its docstring calls it "the primary
measurement". So every number the study had produced was about what the notes *contain*, not about
whether the notes *help* — which is the gap between our hypothesis and our evidence. The answering
step is now assigned and will run against the frozen notes as they land.

### 4. The GPU was running two requests at a time when it could run twenty

The language-model client is fully synchronous: one request per process, blocking. Both jobs were
running one household each, so the server was carrying **2 concurrent requests with nothing
queued**. Measured throughput at two streams was **28 generated tokens per second**. At ten streams
it was **1,160 — a 41-fold speed-up**, still with nothing queued, and it has since carried 22
streams without queueing. The serial loop was the entire bottleneck.

The fan-out now sweeps by household rather than by cell, so that at any point we stop we have a
complete balanced design on however many households finished, rather than two cells on ten
households and nothing on the rest.

---

## The looking half of the study is in trouble, and honestly so

The chooser was specified to look where its own notes disagree. Measured on one household over ten
days at one room a day, against a starting memory of sixteen self-written claims:

| arm | distinct rooms visited | asked-about objects seen | reached the room the change moved into |
|---|---|---|---|
| the fixed fair rotation | 9 | 19 of 19 | yes |
| the naive chooser | 1 (ten times) | 7 of 19 | no |
| plus its own look history | 1 | 7 of 19 | no |
| plus same-object disagreements | 1 | 7 of 19 | no |
| both changes together | 1 | 7 of 19 | no |

**Both repairs failed on room diversity and one succeeded elsewhere.** Telling it how long since it
last visited each room changed nothing whatsoever. Requiring the two competing claims to be about
the same object took the share of looks that actually *settle* which claim held from **0% to 80%**,
which is a real improvement in the quality of a look — it just does not make the robot go anywhere
new.

The cause is intrinsic rather than a prompt fault: a room the notes never mention cannot be the site
of a disagreement, and that is exactly the room a new disruption has moved things into. This
household's claims never mentioned the living room, where its disruption lives.

**The proposed fix** is to build the candidate list from every room in the house, each labelled with
what the notes predict would be found there — including "the notes say nothing about this room" —
rather than from pairs of claims already written down. That keeps faith with the hypothesis, because
finding an object in one room refutes a claim placing it in another, which makes every room a
possible site of disagreement.

**And a ceiling that was already handled.** A fair rotation at one room a day achieves complete
coverage of a nine-room house within the ten-day disruption — 19 of 19 objects — so there is nothing
left to win on coverage at any late freeze point. The builder had already seen this and built the
day-16 freeze point for exactly that reason, with the note that a fixed rotation has found 92% of
moved objects by about day 4.4. I raised it as a new problem; it was not. The looking factor is
reported early, the memory factor late.

**RETRACTED, and I was the one who wrote it.** I argued that the naive chooser's collapse should stay in
the paper as an arm, because its failure was "the honest consequence of the hypothesis read literally".
It was not a consequence of anything. A shuffle test — same household, same notes, same days, only the
order the rooms are listed in changed — settles it:

| candidate order | rooms chosen | position chosen |
|---|---|---|
| the order they always come in | bathroom, 8 of 8 | 1, 1, 1, 1, 1, 1, 1, 1 |
| shuffled each night | bathroom, living, kitchen, bathroom, kitchen | 1, 1, 6, 1, 6 |

The room **follows the presentation order**, and every choice is at the first or the last position. It was
never reasoning about the house. `household.rooms` sorts alphabetically, which put the bathroom at position
one or two in all three households where the collapse appeared. A finding that moves when you shuffle the
menu was never a finding, and it is struck from here and from the pre-registration.

**And the repaired chooser is not yet cleared of the same fault.** It concentrates on a storage room, 20 to
24 looks of 32. The appealing reading is that the instruction is being satisfied too well — we ask for the
room whose contents the notes can least predict, and a permanently empty room is perfectly unpredictable
and perfectly uninformative. That would be a genuine finding about the objective. But the positions the
naive chooser selected were first *or last*, which is the ordinary serial-position pattern, and the storage
room is **last** in that household's order. So "it is last, therefore position does not explain it" has it
backwards. The same shuffle test is now running on the repaired chooser, and until it lands **the looking
factor has no reportable arm.**

---

## The memory half has a real result already

Both formats, same model, same household, same look stream, same words describing what was seen.
Only the instruction about how to write differs.

All ten households are complete, all four freeze days, both arms.

**Nightly wholesale rewriting reproduces its own previous night verbatim on 35% of nights**
(standard error 6.2 points, n = 10 households, range 0 to 68%), with mean night-to-night text
overlap of 0.789. The incremental arm was identical to its previous night on **0 of 29 nights in
every one of the ten households** — not a mean of nearly zero, but exactly zero everywhere.

**The obvious bug hypothesis is excluded, not assumed away.** Across every arm and household there
were **zero failed model calls** and zero cache hits on a fresh run, so the repetition is the
model's behaviour and not a silently broken write path.

**The obvious objection, tested, and it shrinks the number.** Repeating a summary is *correct* if
nothing happened that night, so the finding only counts on nights when the look actually saw an
object the robot is asked about. Conditioned that way:

| nights, n = 10 households | wholesale rewriting | incremental revision |
|---|---|---|
| the look saw an object the robot is asked about | **24%** (standard error 6.3, range 0–62%) | **0%** |
| the look saw nothing relevant | 48% pooled | 0% |

So **24% is the honest headline, not 35%**, and the paired within-household difference on those
informative nights is **+23.7 points** (standard error 6.3, n = 10), detected at the
two-standard-error bar, with **9 of 10 households in the same direction** and the tenth at exactly
zero for both arms.

The gap between the two rows of the rewrite column is a second result: the paired difference between
informative and uninformative nights is **−25.1 points** (standard error 7.3, n = 10), detected, with
8 of 10 households repeating less often when there was something to record. So wholesale rewriting is
*partly* responsive to what the robot saw — it is not blindly copying — but it still stalls on
roughly a quarter of the nights that carried new information, where incremental revision stalls on
none of them in any household.

**The spread is large and belongs in the text.** One household repeats on 0% of informative nights
and another on 62%. The mean is real but the mechanism is plainly not uniform, and that heterogeneity
should not hide behind a standard error.

One honest concern the runs raised about themselves: only **59%** of the incremental arm's edits
carried anything the notes did not already say, below our 60% threshold, which means the rule
forcing an edit every night is partly producing re-wordings. This is deliberately **not** being
tuned away, because tuning a prompt against our own test produces a number that means nothing. If
the re-wordings turn out to cluster on nights where the look saw nothing relevant, the honest fix is
to stop forcing an edit on those nights — a design correction rather than a tuning.

---

## The likely shape of the paper: the write side is a null and the read side is the bottleneck

The two ways of writing notes produce **visibly different notes**. Wholesale rewriting repeats its
previous night verbatim on 24% of the nights that carried new information; incremental revision does so
on 0% of them, in every one of the ten households. That is a paired difference of +23.7 points,
standard error 6.3, n = 10, detected.

And on the dependent variable it makes **no difference at all**. At the freeze point where the
hypothesis has to win, paired within-household, incremental minus wholesale:

**All ten households, both arms, are now in.**

| at n = 10 households, 30 questions each | paired difference | what the null excludes |
|---|---|---|
| naming the exact shelf | +1.8 points (standard error 3.4) | nothing larger than about 7 points |
| naming only the room | +2.9 points (standard error 1.7) | nothing larger than about 3.4 points |

Neither clears two standard errors. And the room-level figure moved around as households were added —
+2.0 at n = 5, +3.4 at n = 8, +2.6 at n = 9, +2.9 at n = 10 — never once crossing the bar. Three findings
in the previous paper reversed or halved exactly this way, so nothing here is reported as detected on the
strength of one more household. The exclusion is what makes this null useful: **whatever incremental
evidence-linked revision buys over nightly wholesale rewriting, it is smaller than about three and a half
points of room-level accuracy.**

Measured against the oracle floor, both arms sit essentially on it at room level — incremental −0.6 points
(standard error 2.5), wholesale −3.5 (standard error 2.6) — and both well below it at shelf level,
incremental −13.8 and wholesale −15.6.

To settle it rather than leave it on a knife edge, all ten households are being rerun at the **full
question window** instead of thirty questions each. With all ten households in hand the limiting noise is
no longer how many households there are but how noisily each one's accuracy is measured — and at thirty
questions that sampling error is about the same size as the effect being chased. Widening the questions
tightens every paired difference without touching the design, the clustering or the unit of evidence, and
it will make the answer unambiguous in whichever direction it falls.

Put beside the corrected error partition — **96% of errors because no line ever named the true shelf,
0% from the reading rule, and 75% of those write-time errors concerning objects the robot never saw
there at all** — the account is coherent and it is the paper:

> A large, measured change in **what the memory contains** produces no change in **what the memory
> answers**, because the bottleneck is upstream of the memory entirely. Three quarters of the time the
> robot never observed the fact, so no way of writing it down could have helped.

That is worth more than a strained win. The memory literature's current effort goes into what gets
stored — graph memories, manager agents, better write policies — and this is a direct test showing that
a substantial improvement in the store buys nothing when the robot never saw the thing. For a home
robot on a sensing budget, **what to look at is the binding constraint**, and memory maintenance is the
wrong place to spend.

It also explains the one positive result rather than sitting beside it: the only intervention that
helped was choosing where to look, and it helped by going to rooms the notes had no claims about —
which is exactly what relieves an observation bottleneck.

**What would still qualify it:** the 25% note-taking residue is real, and **15% of write-time errors are
objects the robot saw more than once**. The eight-line window is not the explanation — 0% of errors came
from the reading rule — but the unbounded-window diagnostic at both freeze points is still queued as the
last check on whether the notes learned more than they could deliver.

## A methodological trap to keep out of the paper

Conditioning any of these curves on "the objects the disruption moved" makes every leg look two to
three times bigger, and it is tempting. It is selection-biased: the set is chosen by comparing the
two windows, so noise alone puts objects into it and they then break by construction. The measured
floor for that bias is a **16-point false break on a scenario that should show none at all**. Every
gate number therefore uses all questions, with the moved and stayed-put slices printed beside it and
labelled. No moved-object number goes in as a headline.

---

## The disruption is no longer only illness

Two of the four non-illness disruptions are generated and gated, and one of them is the best
scenario in the study.

All five are built and gated.

| scenario | verdict | break | re-learn | break again |
|---|---|---|---|---|
| **a bathroom out of action** (`room_shut_v1`) | **passes all seven** | **−19.9 / −16.9** | +11.9 / **+18.6** | −7.6 |
| **a resident off sick** (`illness_v1`) | **passes all seven** | −13.5 / −13.3 | +11.1 / +13.5 | −8.9 |
| a guest in the spare room (`guest_v1`) | fails 1, by 0.8 points | −11.0 / −11.0 | +6.2 / +11.7 | −8.4 |
| a resident off sick, second build (`illness_v2`) | fails the return leg | −10.1 / −10.2 | +5.0 / +7.4 | −1.6 |
| working from home (`wfh_v1`) | fails 3 | −9.0 / −6.1 | +14.4 / +11.8 | −3.7 |
| **a night shift** (`night_shift_v1`) — deliberate negative control | **fails 6, as designed** | **+0.1 / +2.5** | +5.6 / +4.0 | −7.6 |

(two numbers = a timetable that never forgets / a timetable with a three-day memory)

**The negative control is the most valuable row in that table.** The night-shift household was built to
be a disruption that changes *when* things happen without changing *where* they end up, and the gate
rejects it on six legs with a break of **+0.1 and +2.5 points — the wrong sign entirely**. So the
checker is discriminating rather than rubber-stamping, which is the only way to trust it when it says
a scenario passes. It also fails for the right stated reason: "even at its most visible hour the change
shows on only 20% of the objects that moved — a robot cannot learn what it cannot see."

Working from home fails four legs, including the same visibility check at 38%. It is a real change to
the household's day that barely moves any object, which is exactly the near-duplicate-of-illness risk
worth naming rather than shipping.

Three predictions were written down before these ran and all three held: the room-out-of-action case
strongest, working from home weakest, the night shift failing.

**What makes a disruption learnable, across all six.** Ordering the six by the share of moved objects a
look can actually see — 70, 62, 38, 32, 31, 4 — very nearly orders them by verdict, and both outright
failures fail that visibility check *before* any curve is computed. Working from home moves **more**
objects than the illness does, 60 against 58, and still fails. So it is not how many objects move; it is
how many move into places the robot can see. That is the generalisation worth printing.

The reason working from home fails is worth one sentence of its own: **a memory can only be broken about a
belief it actually holds, and while a commuter is commuting the robot is barely ever asked where their work
things are.** Of 1,010 settled-window questions about the ten classes that scenario moves, only **311 concern
a commuter's possessions** — a question whose true answer is "out of the house" never enters the bank, and
**131 of the 144 settled laptop questions belong to residents the disruption never touches.** The commuter's
share then *rises* from 311 to 537 during the spell, because the new at-home activities are what put their
things on an askable surface at all. It is a different mechanism, not a weaker copy of the illness.

**A correction, and it is mine to own because I praised the wrong version and repeated it.** I had written
that the laptop's usual place is "right only 51% of the time". That was a **pooled modal share across ten
households** — a fact about households having different desks — quoted as if it were a per-object accuracy.
**Per object the laptop sits at its own commonest place 100% of the time in the settled window**, so the
sentence said close to the opposite of the truth. The same category error produced two more figures: the towel
"right 88% of the time" is **89–94% per object**, and a 25% figure for glasses came from a build whose banks
contain no glasses questions. It recurred three times, so it is a systematic trap rather than a slip: a pooled
modal share and a per-object accuracy are different quantities, and every per-object accuracy in any file
needs checking against that distinction before it is quoted.

### One caveat that costs us a claim, and a fault in our own gate

**`room_shut_v1` and `guest_v1` had their object-class lists chosen by trying about a dozen mixes against
the gate and keeping the best.** That is selection on the outcome, and the measured trade shows the knob
moves exactly what the gate judges: a class that hardly ever moves buys about 5 points of settled level
and costs 6 to 9 points of break. So:

- **`illness_v1` is the primary scenario and its pass is not fitted** — it was built before the gate
  existed, so the gate tested it independently. Every claim rests on it.
- **`room_shut_v1` is a secondary replication whose classes were gate-informed.** Its −19.9 break does
  **not** go in as evidence that structural disruptions break memories harder than behavioural ones,
  because that is precisely the comparison the fitting could have manufactured.

**And the gate has a fault we found by using it.** The night-shift control **passes the fourth leg at
−7.6 while having no first break at all**, because a late shift's weekday is simply easier to predict —
no cooking, no dinner, fewer free slots — so the learner improves during it and drops when ordinary life
resumes. Decisively, the objects that never moved drop 7.0 at the same moment, so the movers are not
carrying it. Two fixes are with the gate's author: make the fourth leg **conditional on the first break
existing**, and print the **stayed-put slice beside it**. No threshold moves; the gate as a whole was not
fooled, six failures to one pass.

This does not reinstate `illness_v2`, whose failure was the opposite pathology — it failed the fourth leg
while having a genuine first break of −10.1, which is the case that leg is meant to catch.

So the paper can carry **two** independent disruptions rather than one run ten times, which was the
right concern. The room-out-of-action case is structural rather than a change of preference, and it
breaks a counting learner half again as hard as illness does.

**One caveat on it that must go in the paper rather than a footnote:** 49% of the objects that move
during a bathroom refit **never return** to where they were. Half the reversion in that scenario is
therefore the world, not the memory, and any claim about reuse of the old routine has to say so.

The guest scenario misses on a floor rather than on the disruption: a forgetting learner reaches only
**68.8%** by the end of the settled fortnight against the 70% needed, so the ordinary routine is not
learnable there and nothing can be lost at the upset either. Its disruption legs are all healthy.
It gets one attempt at a fix aimed at the *settled* routine, then it is reported as a near-miss.

## Still open at the time of writing

- The remaining two disruptions — working from home, and the night shift as a deliberate negative
  control we expect to fail the gate. The old night shift showed a weak but real 4-to-6 point break,
  so the control is expected to fail on several legs rather than to show nothing at all.
- The answering step at all four freeze points, which is the paper's dependent variable.
- **The shuffle test on the repaired chooser.** This is the one that decides whether the looking factor
  exists at all. If its chosen room follows the presentation order the way the naive chooser's did, the
  factor has to be rebuilt before it can be measured; if the room stays put while its position moves, then
  "look where your notes are least certain" being maximised by a permanently empty room is a real finding
  about the objective.
- **Whether the vacuity extractor is even-handed between the two arms**, since the arms write in different
  styles and one extractor scores both. *Resolved: after four fixes the even-handed answer is **+31.3**,
  standard error 6.9, n = 10 — neither the inflated +49.6 nor the conservative +23.7.*
- The conditional version of the 35% figure, restricted to nights the look saw something relevant.
