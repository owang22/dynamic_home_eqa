# What this paper can claim, with the number behind each

Four pages excluding references, CoRL 2026 Memory for Robot Foundation Models workshop, due 30 September.
Drafted 2026-09-24 ~03:10 by the coordinating session from the night's measurements. Plain names throughout.

Every number here was computed from the data. Where a claim is not yet safe to make, it says so and says
what would settle it. Claims are ordered as the paper should order them, and each one is a candidate for
one figure — no figure without a claim, no claim without a number.

---

> **READ FIRST — every 30-question number below is measured on days 14 and 15 only.**
> `run_frozen_memory_test` takes `questions[:max_questions]` and the questions are in day order, so a
> 30-question cell asks the chronologically **first** 30 of the window: 24 questions from day 14 and 6 from
> day 15, out of a ten-day window with 24 questions a day. Day 14 is the transition day and the worst in the
> window, so the 30-question figures are biased low.
>
> **The size of that bias, pooled over seven full-window households: about 8 points at shelf level and 4 at
> room level.** Day 14 reads 40.5% against 48.3% across days 15–23.
>
> *An earlier version of this note said day 14 was 12.5% against 49%, "a factor of four", and proposed a figure
> for it. That was a single household — `hh_s6` — taken for the shape of the effect, and it is withdrawn. The
> 25-point jump in that household was its own day-14 outlier being diluted; hh_s4's +3.3 is nearer typical.*
>
> So the paper should quote the full-window numbers because they measure what we claim to measure, and the
> 30-question versions should be labelled "the first two disrupted days". This is a correction of scope, not a
> rescue of badly wrong numbers — and the **paired** differences used identical question sets on both sides, so
> they were never invalidated.
>
> One real observation from the per-day table: from day 15 to day 23 the curve is **flat**, shelf level
> wandering between 45% and 52% with no trend. A memory frozen at day 23 answers about day 15 as well as about
> day 22, so what it holds is a static picture of the disrupted regime rather than a dated record — consistent
> with revision overwriting a snapshot rather than building a timeline.
>
> Unaffected: the **vacuity** result (+31.3), which is computed from the notes rather than from answers, and
> the **noise floor**, which compares two runs of the identical question set.

## The hypothesis, unchanged

> Choosing which observations to make, and then revising memory in small evidence-linked pieces, produces a
> more useful memory for later object search than observing on a fixed schedule and rewriting memory
> wholesale.

**The paper's honest answer: the memory half is false, the sensing half is true but not for the stated reason,
and the explanation for both is the same.**

- *"revising memory in small evidence-linked pieces produces a more useful memory"* — **false.** It produces a
  measurably different memory (+31.3) and not a more useful one (bounded under ~3.4 points).
- *"choosing which observations to make"* — **true**, three moved objects seen per look against a fair rota's
  one. But the policy that works is "look where you have no claims at all", which is exploration, **not** the
  discrimination between competing routine claims the hypothesis proposed.
- *why both* — in **75%** of the memory's errors the robot had never seen the object where it was. The
  bottleneck is observation, so a better-maintained memory cannot help and a better-targeted look can.

Stating that plainly is a stronger paper than a confirmation would have been, because it says which half of the
idea to keep and why.

---

## Claim 1 — FIRM. The two ways of writing notes really do produce different memories.

Wholesale nightly rewriting reproduces its own previous night **verbatim on 24% of the nights that carried
new information**; incremental evidence-linked revision does so on **0% of them, in every one of the ten
households**. Paired within-household difference **+23.7 points, standard error 6.3, n = 10**, detected,
nine of ten households in the same direction and the tenth at zero for both.

Excluded as an artefact, not assumed away: **zero failed model calls** across every arm and household, and
zero cache hits on a fresh run, so the repetition is the model's behaviour and not a broken write path.

Restricted honestly: on nights when the look saw nothing the robot is asked about, the rewrite arm repeats
on 48% of nights — and repeating is *correct* then. The paired difference between informative and
uninformative nights is **−25.1 points** (standard error 7.3, n = 10), so the rewrite arm is partly
responsive to what was seen. It is not blindly copying; it stalls on about a quarter of the nights that
mattered.

Heterogeneous and the text must say so: 0% in one household, 62% in another.

**The semantic version is the headline, and it is +31.3.** A night is vacuous if it asserts no thing-and-place
pair the memory did not already hold — immune to the objection that near-verbatim rewording slips past a
byte-identity test. On the nights that saw something the robot is asked about, the paired within-household
difference is **+31.3 points, standard error 6.9, n = 10, detected, 9 of 10 households in the same
direction.**

That number is the one to quote because it has an audit trail. It began at +49.6 and fell 18 points under
four fixes, **every one of which had been penalising the rewrite arm alone**, because only that arm writes
prose:

| | informative-nights difference |
|---|---|
| as first measured | +49.6 |
| after teaching the extractor possessive forms ("Aisha glass", "Felix's book") | +35.3 |
| after a twenty-judgement hand check | **+31.3** |

The extractor is now even-handed, which is what licenses the comparison: a fact is recovered on **99%** of the
rewrite arm's nights against 100% for the claim store, 10.6 facts a night against 13.4 — and that residual is
plausibly real, since the rewrite arm has eight lines and must drop facts.

Two of the faults would have been invisible without the hand check. Matching only object identifiers recovered
**nothing at all** from three of ten households, which then scored 100% vacuous as pure measurement artefact;
and a place written `KITCHEN_TABLE` matched nothing, silently losing every fact on that line.

*Worth recording as a near miss:* reconstructing the claim store's nightly wording from the day a claim was
first written misses every later revision — 59 of them — which makes the claim store look more repetitive
than it was and shrank this difference to **+10.7, standard error 8.5, not detected.** That version was one
step from being reported as the antecedent collapsing.

## Claim 2 — FIRM AS AN EXCLUSION. That difference in the memory buys almost nothing in the answers.

At the freeze point where the hypothesis has to win — notes written through the whole disruption, questions
from the disrupted days — paired within-household, incremental minus wholesale, n = 10:

**On the full window, at all ten days and 240 questions per cell — the measurement that should be quoted:**

| | difference | verdict |
|---|---|---|
| naming the exact shelf | **+7.0** (standard error 3.4, n = 10) | 2.02 standard errors — *just* over the bar |
| naming only the room | +4.9 (standard error 2.7, n = 10) | 1.8 standard errors — not detected |

On the capped version these read +1.8 and +2.9, neither detected. The shift is explicable: the capped cells asked
days 14–15 only, where both arms are near-uniformly wrong, so there was little room for either to distinguish
itself.

**But the shelf-level detection is carried by one household and must not be reported as established.** Per
household, incremental minus wholesale: −4.8, −1.7, **+15.1**, **+30.0**, −1.7, +3.8, **+13.8**, **+10.6**, −3.7,
+8.3. Drop the largest, `hh_s3` at +30.0, and it falls to **+4.4, standard error 2.6, 1.70 standard errors — not
detected.** Only **6 of 10** households point positive, which no sign test would call anything.

And `hh_s3`'s wholesale cell is **not degenerate** — 240 answers, 11 distinct places named, 31% on the commonest,
0% unparsed, no concerns raised. So this is genuine heterogeneity rather than a broken cell, which makes it
harder to dismiss and no easier to claim.

**The honest form: suggestive at shelf level, not established; not detected at room level.** An effect that
crosses the bar at 2.02 standard errors and stops crossing it when any one household is removed is exactly the
shape that reversed three findings in the previous paper.

**And whatever advantage there is, it is not specific to the disruption — which matters more than its size.**
Splitting by whether the object's usual place actually changed when the illness started:

| | wholesale | incremental | paired difference |
|---|---|---|---|
| objects the disruption **moved** | 24.0% | 32.0% | **+8.0** (standard error 4.0, n = 10) — detected |
| objects it **did not move** | 45.1% | 52.1% | **+7.0** (standard error 3.7, n = 10) — not detected |

The two are the same size. An advantage that is as large on the objects the disruption never touched as on the
ones it moved is **not a change-coping effect at all** — it is a general "these notes are slightly better notes"
effect. Our hypothesis is specifically about coping with a change in routine, and this says the format difference
does not act there. That is a sharper negative than the bare null was, and it is a paired comparison *within* each
slice, so the selection bias that afflicts moved-object slices in absolute terms does not touch it.

*It also kills a tempting story.* The one household carrying the headline, `hh_s3`, looks like the previous
paper's finding that plasticity costs you the old routine — its gap is almost entirely on objects that did **not**
move, 32% against 65%. But across the ten households the effect is uniform across movers and non-movers, so that
household is idiosyncratic rather than the mechanism. I formed that hypothesis and the data refused it.

### Why hh_s3 is the outlier, and it is the best single observation of the night

Its wholesale summary at day 23 says, in as many words:

> "Storage, living, and balcony rooms are **empty of all tracked items** (stable condition)."

The disruption had moved **three objects into the living room**. So the rewrite arm spent one of its eight lines
on a confident negative that the disruption falsified, covering exactly the room that changed — while its claim
store carried "book_felix is on the couch in the living".

**That is compression into a confident summary negative, and it connects Claims 1 and 2 directly**: a note-taking
failure of the kind Claim 1 measures, showing up downstream as the largest answer gap in the study. It also
explains why the effect is largest in the household with the **highest floor** — a very predictable settled
routine is exactly when a summariser is tempted to write "these rooms are empty, stable condition".

**Only 1 of 10 households asserts a room empty that the disruption filled.** So it explains the outlier rather
than revealing a general mechanism, which is an argument for the "suggestive, not established" wording rather
than against it.

### An unresolved disagreement between two measures — do not quote either until it is settled

Measured on the **notes** rather than the answers, asking whether each arm's day-23 notes place each moved object
in its correct room: **wholesale 32 of 67 (48%), claim store 46 of 67 (69%)** — a 21-point gap, claim store ahead
in 7 households, tied in 2, behind in 1. That is far more consistent than the answer-based version and is
untouched by the reading step or rerun noise.

**But it implies a change-specific advantage, and the answer-based split says the advantage is flat across movers
and non-movers.** Both cannot be the whole story. Three ways to resolve it, all cheap: run the notes measure on
the objects that did **not** move (if the gap is also ~20 points, the effect is general recording quality, not
change-coping); or accept that two mechanisms are being averaged and name both; or recheck the answer split using
the same 67-object daytime mover definition the notes measure uses, since mine used 58 from a question-times
definition we had already rejected.

One caution on the notes measure itself: it uses the audited pair extractor, which reads **prose** for the rewrite
arm and **statements** for the claim store — the exact asymmetry that inflated the vacuity figure by 18 points
before repair. Its per-arm recovery rates for *this* question are not yet reported, and a 21-point gap is well
inside the range a one-sided recovery difference produced last time.

*A correction of framing, in the measure's favour:* it is not right to say the recording advantage "fails to
convert". Movers carry roughly a third of the questions, so a 21-point gap on a third of them is about 7 points
overall — almost exactly the +7.0 shelf and +4.9 room differences observed. It converts about proportionally; it
falls below detection because two thirds of the questions cannot show it.

**How this sits with the thesis.** If three quarters of errors are objects the robot never saw, the only errors a
format *could* fix are the note-taking quarter — so a modest, non-change-specific advantage is consistent with an
observation bottleneck. What is ruled out is the strong version of our hypothesis: incremental evidence-linked
revision is not what governs the outcome, and it is not what copes with the change.

## Claim 3 — FIRM, AND NOW THE PAPER'S THESIS. The bottleneck is observation, not memory.

*(This claim was overturned and rebuilt. The earlier version said the opposite — that the notes held the answer
and the reading step lost it — and it came from a matcher with a room fallback. The withdrawn version is kept at
the end of this section rather than deleted.)*

Recomputed with the audited extractor over **357 wrong answers across all twenty day-23 cells**:

| claim store | capped | **full window** |
|---|---|---|
| the reading rule picked the wrong lines | 0% | **0%** |
| naming the exact shelf: point of use / write time | 2% / 98% | **4% / 96%** (1,305 errors) |
| naming the right room: point of use / write time | 18% / 82% | **20% / 80%** (774 errors) |

**The partition is stable at ten times the sample**, so the reversal of the earlier claim holds and is not a
small-sample effect. Note the level asymmetry within it: at shelf level only 4% of errors had the right answer
written down, but at room level **one error in five did** — the notes more often place the object in the right
room and still answer a different room. Whether that differs *between* arms depends on the wholesale cells,
which are still running, and is not being treated as established.

**So the earlier 70/30 in favour of the point of use was an artefact of the matcher**, which had a *room
fallback*: a line naming the right room and no other room was credited with asserting the place, so notes
saying "kitchen sink" counted as asserting "kitchen table". Right for a timeliness measure, exactly wrong for a
partition whose purpose is to separate shelf-level failures. A twenty-judgement hand check found it; nothing
else would have.

**What survives untouched: 0% from the reading rule, at both levels.** A bigger reading budget cannot help,
and that is now the only part of the read-side story that stands.

### And that question is settled: the bottleneck is observation

Splitting every write-time error by what the robot actually saw, using the **structured sighting records** so no
text matcher is involved. Computed independently twice, by this session and by the builder, agreeing within a
point:

| | capped, first two disrupted days | **full window, all ten days** |
|---|---|---|
| **a sensing failure — never saw the object there at all** | 67% | **75%** (941 of 1,255) |
| a note-taking failure — seen once, no line names it | 17% | 10% (122) |
| a note-taking failure — seen more than once, no line names it | 16% | 15% (192) |
| | 67% observation / 33% note-taking | **75% observation / 25% note-taking** |

**Three quarters of the memory's failures concern objects the robot never saw in their new place.** At one room a
day, no note-writing policy of any kind could have recorded them. The capped figure of 65–67% was measured on the
first two disrupted days; across all ten days it rises to **75%**, on 1,255 write-time errors against 172.

**The direction of that shift has a mechanism, which is why the full-window figure is the right one.** The capped
version was three-quarters day 14, and on the transition day objects have only just moved — so the robot has
often seen them in their new place very recently and the notes have not caught up, which is a *note-taking*
failure. Later in the window the objects sit in places the robot has not visited at all, which is a *sensing*
failure. Capping at the front therefore systematically **understated** the observation share.

*The split was computed independently twice at the capped scale, by this session at 63.9% and by the builder at
65%, agreeing within a point before either saw the other's number.*

**The near-identical split across arms is the strongest form of the argument.** Two formats that differ by
**+31.3 points** in what they write fail in the *same proportions*, 67/33 against 64/36. If the bottleneck were
maintenance, policies this different could not fail alike. That single fact ties the study's three results into
one mechanism: the formats differ hugely in what they write, are indistinguishable in what they answer, and the
looking factor is the only thing that helped — exactly what an observation bottleneck predicts.

**The qualification stays in.** 35% is not nothing, and **18% of these errors are objects the robot saw more
than once** and the notes still do not carry. The honest sentence is "predominantly observation, with a real
note-taking residue", never "memory maintenance is irrelevant".

### The superseded version of this claim

Of 120 wrong answers, partitioned with no GPU spent:

| | share |
|---|---|
| the reading rule picked the wrong lines | **0%** |
| the right claim was shown and the model answered a different place | 48% |
| no claim named the true place | 21% |
| unavoidable — the object moved after the notes were frozen | 31% |

Of the **83 avoidable** errors: **70% at the point of use, 30% at write time, none from selection.**

Zero from selection has a mechanism: the reading order puts claims naming the asked-about object ahead of
everything else, so the claim that matters is in the window whenever it exists. A bigger budget cannot help.

And when the notes do miss at write time they miss completely — **25 of 25** genuine write-time misses never
named the right room either. So the shelf-level deficit is entirely a point-of-use failure.

*Superseded: the 70/30 split came from a matcher with a room fallback. See the current version above.*

## Claim 4 — FIRM. Ten days of revision teaches the new routine almost nothing.

The cleanest comparison in the design, and it needs **no baseline at all**: both freeze points ask the *same
questions*, from days 14 to 23. Only whether the notes were written through day 13 or day 23 differs — same
household, same arm, same questions, same reading budget, same prompt.

At n = 10 on both arms:

| arm | naming the exact shelf | naming the right room |
|---|---|---|
| incremental claim store | **+7.0** (standard error 2.7) — clears two standard errors | +1.3 (standard error 2.2) — within two of zero |
| wholesale rewrite | **+5.0** (standard error 1.4) — clears two standard errors | +1.0 (standard error 1.4) — within two of zero |

So ten days of watching the disruption buys **5 to 7 points of shelf-level accuracy and nothing at room
level**, and the two formats do it **to within two points of each other**. That is sharper than the earlier
n = 5 reading of "it learns almost nothing": it learns something real about shelves and nothing about rooms.

The two arms agreeing this closely is itself the outcome null seen from another angle — the formats build
measurably different memories (+31.3 on vacuity) and then learn the same amount from the same ten days.

### The mechanism behind the asymmetry, and it is the sharpest thing in the paper

The asymmetry is genuinely surprising, because **74% of the disruption's moves cross rooms** — 43 of 58 moved
objects end up in a different room, only 15 stay put on a different shelf. And getting the shelf right
*implies* getting the room right, so a 7-point shelf gain should have carried the room with it. It did not.

Counting what individual answers did between the two freeze points, on the same questions:

| | answers that moved INTO the right room | moved OUT of it | net | of |
|---|---|---|---|---|
| incremental claim store | 34 | 30 | **+4** | 300 |
| wholesale rewrite | 25 | 22 | **+3** | 300 |

| | answers that became correct | became wrong | net | of |
|---|---|---|---|---|
| incremental claim store | 50 | 29 | **+21** | 300 |
| wholesale rewrite | 37 | 22 | **+15** | 300 |

So the memory is **not inert** — ten days of revision changes about a fifth to a quarter of all answers. But
of the room-level changes it makes, only **53% are improvements**, which is a coin flip. Of the shelf-level
changes, **63%** are. The memory revises usefully about which *shelf* an object sits on, and no better than
chance about which *room* it is in.

That is the finding: **revision is confident about the dimension it could already predict, and near-random
about the dimension that actually changed.** The disruption moves things between rooms, and room is exactly
where the notes learn nothing. It holds in both arms with nearly identical numbers, which is the outcome null
seen from a third angle.

**The noise-floor caution is measured, complete, and it clears.** Twelve cells were rerun through a fresh prompt
cache — **cache hits 0**, verified per process, so every call went to the server. The runs are genuinely
different: only 13 to 18 of 30 reasoning strings are byte-identical and the stated confidence differs on up to
11 questions of 30. But the *answers* barely move.

**FINAL VALUES — 12 of 12 cells, both arms at equal n. Earlier drafts of this section carried 1.1 and 0.7 points
for the floor; use 0.6.**

| | answers that changed place | of | rate |
|---|---|---|---|
| **all cells** | **5** | **360** | **1.39%** |
| claim store | 2 | 180 | 1.11% |
| wholesale rewrite | 3 | 180 | 1.67% |
| before anything changed | 1 | 180 | 0.56% |
| did it learn the new routine | 4 | 180 | 2.22% |

**The floor on the quantity that matters — the day-23-minus-day-13 difference — is a mean absolute move of 0.6
points, largest 3.3, spread 1.4, n = 6 paired cells.** Five of the six moved by exactly 0.0; the entire floor is
one household's claim store moving −3.3 at both levels. So the **+7.0 and +5.0 gains clear it by an order of
magnitude.**

That the floor fell as cells landed — 1.1, then 0.7, then 0.6 — is itself the finding rather than instability:
every cell after the first three moved exactly 0.0. **The answer this task produces is very nearly
deterministic even though the wording around it is not.**

Two things in that table are **directional only and must not be quoted as magnitudes**, because both rest on
single-digit counts. The arms' rates differ by a factor of 1.5 on **2 changed answers against 3** — the honest
statement is that their floors are *indistinguishable at this n*, not that they are equal. And the freeze-point
gradient, 0.56% against 2.22%, rests on **1 changed answer against 4**: the direction matches the prompt-length
mechanism exactly as predicted, but the fourfold figure is not a measurement. What it does establish is that the
day-23 side of every difference is the noisier side, which widens variance without biasing the estimate.

That differs from the previous study's 3–5% of answers changing, and the paper should say why rather than let a
reader assume one of the two is wrong: that study's noisy arms were prompt-heavy, carrying a month of records,
where these notes are eight lines against a short list of candidate places. A short prompt with a constrained
answer set is far more reproducible than a long one, at the same temperature on the same server. This is a
property of **this task**, not of the server.

Two things still to settle it fully: the rerun so far covers **one arm at one freeze point**, and the floor that
matters is on the *difference between* freeze points; and **at n = 5 this read +4.0 and was not detected** — it
grew as households were added, the opposite direction from the winner's curse, but a reminder that the
30-question version is the noisier one.

*Worth recording elsewhere, though this paper makes no uncertainty claim:* the model's **stated confidence is
not stable across identical reruns** while its answer is. The previous paper's entire subject was whether a
confidence signal is usable for deciding when to answer, and a signal that moves under an exact rerun bears
directly on that.

*Caveat that must travel with it:* the day-23 notes hold more claims, so the eight-line window bites harder
on them — a confound that **understates** what they learned. A diagnostic with the window removed, run at
both freeze points, separates "the notes did not learn" from "we could not read what they learned". It is
queued and it is the single most informative cell left.

## Claim 5 — NOW FIRM, AND THE MECHANISM IS NOT THE ONE THE HYPOTHESIS PROPOSED.

The shuffle test settles both arms, in opposite directions.

**The naive chooser is a serial-position artefact and is withdrawn.** With the candidate order shuffled each
night the chosen room changes, and every choice lands at the **first or last** position: 1, 1, 6, 1, 6.
`household.rooms` sorts alphabetically, which put the bathroom at position one or two in exactly the three
households where the collapse appeared. My framing of it as "the honest consequence of the hypothesis read
literally" was wrong and is retracted from the pre-registration explicitly rather than quietly dropped.

**The repaired chooser survives the same test.** It chose the living room on 6 of 7 shuffled looks while its
position moved through 1, 2, 3 and 4 — so the choice is about content, not placement in a list.

**And the logged mechanism is not disagreement-resolution at all.** At the moment of choosing, the household's
claim counts were: kitchen 6, bathroom 3, bedroom_1 3, entry 2, **living 0, storage 0**. The two rooms it
fixated on across every run are exactly the two it held **no claims about**. So the policy that works is not
"look where your competing claims disagree" — it is **"look where you have no claims at all"**, which is
exploration rather than discrimination. Least evidence reads as least certainty. This covers both fixations
with one mechanism and does not require the room to be empty.

**That is a partial refutation of our own hypothesis's mechanism while supporting its conclusion**, and it is
the more interesting result: choosing observations does beat a fixed rota, but not for the reason we proposed.

**It also takes 3.00 moved objects per look against the naive chooser's 1.00**, with the best room in the house
at 4 — so it is fixating on a good room, for a reason that happens not to be the right reason.

*A correction I owe here.* I claimed the repaired chooser was "picking a poor room", from a table showing the
living room receiving 1 of 6 moved objects. I had counted movers **at question times**. Counted over the
**daytime hours a look can actually happen**, 9 objects move and the living room receives **3**, second only to
bedroom_1's 4. Question times select on the outcome measure — the same fork we settled earlier tonight when
deciding not to exclude household s4 — and the argument is stronger here, because the thing being judged is a
*look*, and a look happens at 13:00. My number came from the method we had already rejected.

### The superseded version of this claim

The naive chooser visited one room every time in all three households — always the bathroom, never reaching
the room the disruption moved things into. It was tempting to report this as the honest consequence of the
hypothesis read literally. **A shuffle test killed it.** With the candidate order shuffled each night the
chosen room changes, and every choice lands at the **first or the last** position: 1, 1, 6, 1, 6.
`household.rooms` sorts alphabetically, which put the bathroom at position one or two in exactly the three
households where the collapse appeared.

So there is no claim here, and the pre-registration's version of it has been retracted explicitly rather
than quietly dropped.

**The repaired chooser is not yet cleared of the same fault.** It concentrates on a storage room, 20–24 of
32 looks. The attractive reading is that the objective is satisfied too well — we ask for the room whose
contents the notes can least predict, and a permanently empty room is perfectly unpredictable and perfectly
uninformative. But the measured bias is first *or last*, and the storage room is last in that household's
order, so its position is a live explanation rather than a ruled-out one. The same shuffle test is running.

*Resolved: the shuffle test cleared it. See the current version of this claim above.*

A ceiling the design already handles: a fair rotation at one room a day achieves complete coverage of a
nine-room house inside a ten-day disruption, so the looking factor can only be measured early — hence the
day-16 freeze point, which has the widest room of any at 20 points.

## Claim 6 — FIRM, AND IT EARNS THE READER'S TRUST. What makes a disruption learnable.

Six scenarios, gated on whether plain counting methods show learn / break / re-learn / break-again.

| scenario | verdict | break (never-forgets / three-day) | visible |
|---|---|---|---|
| **a resident off sick** (the paper's only scenario) | **passes all seven, robustly** | −13.5 / −13.3 | 38% |
| a bathroom out of action | passes, but four faults — not used | −19.9 / −16.9 | 70% |
| a guest in the spare room | near miss by 0.8 points | −9.5 / −9.7 | 62% |
| working from home | fails four legs | −9.0 / −6.1 | 32% |
| **a night shift** (negative control) | **fails, as designed** | **+0.1 / +2.5** | 4% |

**Decision: the paper uses one scenario, not two.** Moving every bar in the gate together by two points in
either direction leaves four of the six verdicts unchanged — including the primary scenario's pass and the
control's rejection. `illness_v1` is the strongest of them: **not one leg changes state at either offset**, so
its verdict is nowhere near a bar. Its only warnings are that two *learnability floors* depend on single
classes, which is fragility rather than a fitted disruption, and a null whose exclusion range is stated.

The bathroom refit is withdrawn as a second disruption because **four independent faults all land on it**: its
fourth leg is a difficulty artefact, its break fails if the towel class is dropped, its class list was chosen
by trying mixes against this gate, and its pass reverses if every bar moves two points stricter — on 1.5
points of settled level. The gate's own output now says it cannot be quoted without that caveat. Using it as
a replication would buy breadth with a scenario that four separate checks distrust.

**That is a better answer to "one disruption run ten times is one disruption" than a second scenario would
have been.** The paper reports that five disruptions were built and gated, that one met the bar robustly, and
what the other four failed on — which is a stronger methodological statement than two scenarios where one is
fitted. The generalisation below comes from all six.

Ordering by visibility — 70, 62, 38, 32, 31, 4 — nearly orders the table by verdict, and both outright
failures fail visibility *before* any curve is computed. **Working from home moves more objects than the
illness does, 60 against 58, and still fails.** So what makes a disruption learnable is not how many
objects move but how many move where the robot can see them.

The night shift is the row that earns trust in the other five: built to change *when* things happen without
changing *where* they end up, predicted to show no break, and it shows none. It also survives dropping any
one of its 21 object classes, which is what a control should do.

**Two findings that demote the bathroom scenario further, both from the gate rather than from judgement.**

*Its return cost is not a memory losing a routine.* The objects the refit moved fall **5.5** points on the
first days back; the objects it never touched fall **9.3**. The control drops *more* than the movers, so most
of that leg is the returning window simply being a harder prediction problem. It passes the gate only because
it has a genuine first break, and its 7.6-point return must never be described as a memory losing a routine.
This is the same pathology the night-shift control exposed, and it is now printed beside the fourth leg for
every scenario.

*And its break rests on one object class.* Recomputing every leg with each class left out in turn:
`illness_v1`'s discriminating legs — break, re-learn, break again — **survive dropping any single class**;
only its learnability floors are one class deep (settled level needs the towel, learn needs the glass). The
bathroom scenario's **break** fails without the towel, which is a discriminating leg resting on one class, in
a scenario whose class list was chosen by trying mixes against this same gate. That is independent support for
`illness_v1` as primary, on top of the dominance argument.

*Knife edges worth knowing before any margin is quoted:* `illness_v2`'s re-learn passes by **exactly 0.0
points**, the bathroom scenario's settled level by 1.5, and the guest scenario has three legs inside two
points.

Working from home fails for a nameable reason: **a memory can only be broken about a belief it actually
holds, and while a commuter is commuting the robot is barely ever asked where their work things are.** Of the
1,010 settled-window questions about the ten classes that scenario moves, only **311 concern a commuter's
possessions**; 699 belong to a resident who already worked from home, because a question whose true answer is
"out of the house" never enters the bank at all — **131 of the 144 settled laptop questions belong to
residents the disruption never touches.** And the asymmetry runs the wrong way: the commuter's share rises
from 311 before the spell to **537 during it**, since the new at-home activities are what put their things on
an askable surface in the first place. So much of the apparent movement is movement of objects with thin
settled histories.

*An earlier version of this sentence said the laptop's usual place is "right only 51% of the time". That was
wrong.* 51% was the share of settled laptop questions answered `desk_o1` **pooled across ten households** —
a fact about households having different desks. **Per object the laptop is at its own commonest place 100% of
the time in the settled window.** A pooled modal share and a per-object accuracy are not the same quantity,
and the same category error had produced two other figures: the towel "right 88% of the time" is really
**89–94% per object**, and a 25% figure for glasses was measured on a build whose banks contain no glasses
questions at all. Any per-object accuracy quoted anywhere needs checking against this distinction.

---

## What we will not claim, and why

- **That structural disruptions break memories harder than behavioural ones.** Three independent reasons, any
  one of which would be enough. The bathroom-refit scenario's class list was chosen by trying about a dozen
  mixes against the gate, and the measured trade is one-for-one — a class that hardly moves buys ~5 points of
  settled level and costs 6–9 of break — so the gate is not an independent test of it. Its **break fails if
  the towel class is dropped**, so the leg carrying that comparison rests on one class. And its return leg is
  difficulty-driven rather than memory-driven, with the untouched objects falling further than the moved ones.
  The illness scenario, built before the gate existed and whose discriminating legs survive dropping any
  single class, is the primary and carries every claim.
- **That the bathroom refit's return cost shows a memory losing a routine.** Movers −5.5, untouched objects
  −9.3. Most of it is the returning window being harder to predict.
- **Any number conditioned on "the objects that moved".** It inflates every leg two- to three-fold and is
  selection-biased; the measured floor for that bias was a 16-point false break on a scenario that should
  show none.
- **That reversion is a memory failure in the refit scenario.** 49% of its moved objects never return, so
  about half of that reversion is the world.
- **That a bigger reading window would help.** Measured: zero of 120 errors came from the selection rule.
- **That the memory is worse than a trivial rule.** It looked that way against a floor built from complete
  ground-truth observation, which is an oracle — the robot saw one room a day. Against the same rule given
  only the robot's own sightings, the memory is +4.7 at shelf level and +6.6 at room level (n = 5), and at
  room level it matches the oracle.

## Figure budget for four pages

Three figures, one per claim:

1. **Claim 3**, the thesis — the three-way split of 351 errors into never-saw, seen-once and seen-repeatedly,
   drawn per arm so the near-identical proportions are visible side by side. That visual equality *is* the
   argument, and it should be the paper's first figure rather than its third.
2. **Claim 1** — what the two formats write, per household: share of informative nights recording nothing new,
   ten paired points. It establishes the antecedent the thesis needs, namely that the formats really do differ.
3. **Claim 5** — rooms visited and moved objects per look, by arm. The one positive result, and it earns a figure
   over the scenario table.

Claim 6's six-scenario table goes in as a table, not a figure. Claims 2 and 4 are single sentences with a number
and carry as text. Ordering the figures thesis-first, antecedent-second is deliberate: a reader who sees only the
first figure should already have the paper's point.

## The paper in four sentences

Two ways of writing a robot's nightly notes produce measurably different memories — the wholesale-rewrite arm
records nothing new on **31 points more** of the nights that saw something worth recording — and it makes **no
difference to how well those notes answer later questions**, with any advantage bounded below about three and a
half points of room-level accuracy. The reason is upstream of how the memory is maintained: **98% of errors are
because no line ever named the true place**, none at all come from the retrieval step, and in **75%** of them
the robot had **never seen the object where it actually was** — at one room a day, no writing policy could have
recorded it. That the two formats fail in **the same proportions**, 67/33 against 64/36 despite being 31 points
apart in what they write, is what shows the bottleneck is observation rather than maintenance. And consistently,
the one intervention that helped was **choosing where to look** — three moved objects per look against a fair
rota's one — though the policy that works is "look where you have no claims at all", which is exploration rather
than the discrimination between competing claims our hypothesis proposed.

**What this says to the field.** Current effort goes into what gets *stored* — graph memories, manager agents,
better revision policies. This is a direct test: a large, measured improvement in the store buys nothing
downstream when the robot never observed the fact in the first place. For a home robot on a sensing budget, what
to look at is the binding constraint, and memory maintenance is the wrong place to spend.
