# Narrative outline for the uncertainty workshop submission

Drafted 2026-09-23 ~03:00 by the coordinating session, revising Oliver's outline of 2026-09-22 with what
the overnight work established. Plain names throughout.

---

## The argument in one paragraph

A home robot answers "where is X?" from a memory of what it has seen. In a settled household every method
we tested does this well and knows roughly how well it is doing. When the household's routine changes
temporarily — one resident is off sick for ten days, then returns — every method breaks, and the useful
question is not whether it breaks but whether it can tell that it has. It cannot. At the moment the routine
changes, the confidence these methods report stops predicting their own correctness, so a robot deciding
when to answer and when to ask for help is deciding on a signal that has gone dead exactly when it is
needed. The failure is not calibration and cannot be fixed by tuning a threshold: the ordering of questions
by confidence carries no information at that moment, and a threshold chosen with hindsight does no better.
One method escapes — the one whose confidence models how long a fact stays true rather than how regular the
past was — and it is the least accurate of the three. Being right and knowing when you are wrong come apart.

## Why this setting, not another

No benchmark in the memory literature tests a change that **reverts**. A 2026 survey of the area lists
reverting facts as future work in so many words. That is the gap: real households change temporarily and
change back, and a memory that adapts is punished on the return exactly as a memory that does not is
punished on the way in.

---

## Section 1 — Setting and methods (short)

The household, the question stream, the ten-minute feedback, the frozen regime. The eight methods, named
plainly. One paragraph on why the feedback is deliberately generous: the robot is told the truth after every
question regardless of where it looked, which makes every failure below a lower bound on the failure a
deployed robot would suffer.

## Section 2 — Everything learns, everything breaks, and forgetting is a straight trade
*Figure 1 (learn, break, re-learn) and Figure 2 (who re-learns).*

Accuracy climbs to ~80% over a fortnight, falls 15–47 points on the first sick day, and — the non-obvious
half — falls again when normal life returns. How much a method forgets decides which of the two breaks
hurts it: the timetable that never forgets is the only method the return does not hurt (+2.6 where the
adaptive ones lose 24–34), because the routine that came back is the one it never stopped believing.

Within the spell, the counting methods re-learn the new routine two to three times faster than any language
memory. **New tonight:** what looks like re-learning is mostly repetition of the exact object at the exact
hour. On a question about an object-and-hour it has already been corrected on, the three-day timetable is
94% right; on one it has not, 34%. Every language memory is *better* than it on the uncorrected cell
(44–53%) and worse on the corrected one (67–88%). Nothing here infers a rule; the counter simply memorises
faster.

## Section 3 — A sentence does what a week of evidence cannot, and then it goes stale
*Figure 3 (the three message arms).*

Told on the first sick morning, the whole-log memory gains 10.4 points immediately and 26.9 on first-of-day
questions, sustained through the spell — where ten days of daily corrections gained it about 10. So the
failure is not an inability to represent the new regime; it is an inability to detect that the old one
expired.

The same sentence, never retracted, costs 8.6 points on the first days back and 6.8 a week later. Retract
it and the arm becomes indistinguishable from never being told. All four windows clear on ten matched
households.

**New tonight, and this is the section's strongest material:** the same shape appears three more times, from
three different mechanisms.
- **A written routine in the prompt.** Every prompt carries a description of the resident's day that is
  never updated when she falls ill. Remove it and accuracy rises 9.7 points on the first sick days and 18.8
  later in the spell, while the lead-up — where the description is still true — shows nothing measurable.
- **Pinning the right evidence.** Moving the most recent same-hour sighting to the top of the prompt gains
  16.8 points on first-of-day questions in the spell, and nothing on the first sick days, because on day 14
  the most recent same-hour sighting is still a lead-up one — pinning makes the *stale* record prominent.
- **Telling it twice.** Already above.

One mechanism, four surfaces: *whatever the prompt asserts, the model keeps following after it stops being
true* — whether the assertion came from us, from a message, or from a line it pinned.

## Section 4 — Where the failure lives: reading, not writing
*No figure; a table.*

In 807 of 890 questions where the recent-sightings memory is wrong during the spell, its prompt already
contains a sighting of that object at that hour naming the true location. When it follows that record it is
88% right; when it overrides it, 32%. It overrides *more* at the shift (follow rate down 9–12 points) and
those extra overrides are far worse (the penalty roughly doubles).

And the record it is overriding is **better** during the spell, not staler: the most recent same-hour
sighting is correct 83% of the time then, against 76% settled — a resident who is home sick leaves things
in one place all day. Decomposed: of its overrides, the share that were warranted falls from 61% to 31%,
while its ability to repair a record it has correctly judged stale barely moves. It can fix a stale record;
the shift destroys its ability to tell which record is stale.

Independent corroboration: a 2026 paper measuring the same thing on text dialogue found new evidence
retrieved 77.5% of the time and old entries judged stale 3.3% of the time; published memory systems score
5–18% there.

## Section 5 — Uncertainty: the signal dies at the moment it is needed
*Figures 4–7 (handing the question over, confidence against accuracy, the inversion, the sets).*

Under a rule that declines when confidence is low, aiming to be wrong at most one time in ten: every method
keeps that promise while the household is settled and breaks it at the change, by 2.4 to 6.3 times. They do
react — every one at least doubles how often it declines — but reacting is not recovering.

**The mechanism, new tonight.** How well a method's confidence predicts its own correctness, measured
within households: all three counting methods are about equally good while settled (+0.28 to +0.37). At the
shift both timetables stop predicting entirely; the survival-time model's is unchanged at +0.43. And a
method's confidence stops predicting at the disruption that breaks *it* — the timetable that never forgets
is fine on the return, where the three-day one is not.

The honest sets tell the same story with different machinery: the truth falls out of the offered list on
the first sick day (69% against a promised 90%) while the list gets *smaller*, not larger. It fails by being
confidently wrong rather than by becoming uselessly vague — which is the worse failure for a robot deciding
where to look.

## Section 6 — What a decision is worth, and a small theorem
*Figures 8–10 (score per day, what the confidence adds).*

Score +1 for a right answer, −1 for a wrong one, 0 for declining. Then the value of being allowed to decline
splits exactly in two: what you get from declining *everything* when your accuracy is below half, which
needs no signal at all, plus what the ordering of your confidence adds.

- The value of declining is **exactly invariant** to any monotone relabelling of the confidence. Calibrating
  a signal in level buys nothing; only the ordering can. (Verified numerically: unchanged to three decimals
  under two relabellings while a calibration error metric moved threefold.)
- At the shift the timetables' *ordering* term is negative — worse than declining at random — and their
  apparent gain is entirely the level effect of being wrong more often than not. The survival-time model's
  ordering term is +1.05 and the whole-log memory's +0.48.
- Against a shuffled-label floor, the timetables' gains are not distinguishable from noise; the survival-time
  model's and the whole-log memory's are.

So **a flat confidence signal is not necessarily a bad one.** The survival-time model's confidence barely
moves at the aggregate level, and it is the only counting method whose confidence is worth acting on. That
is the paper's sharpest point for a workshop on uncertainty: the community's default diagnostic — does
confidence track accuracy in aggregate — is not the quantity a decision depends on.

## Section 7 — What to do about it

Not a method contribution; a direction with evidence behind it. What distinguishes the one method whose
uncertainty survives is that it models how long a fact stays true. Nothing else we tested — including five
language-model memories — represents the validity of what it knows, neither for a sighting nor for a
sentence it was told. The field's current answers are aimed elsewhere: graph and manager memories improve
what gets *stored*, and our measurements say the failure is at the point of *use*.

---

## What we deliberately do not claim

- That a robot acting on its own wrong beliefs cannot recover. Our feedback is clean by construction; the
  closed-loop version of this question is scoped and not run.
- That language memories cannot represent a new regime. Told explicitly, they adapt at once.
- That the survival-time model is a better belief model. It is the least accurate of the three counters.
- That any method's uncertainty is deployable here. None keeps its promise at the change.
- That confidence is highest on the objects that moved. Tested and refuted — it is slightly lower.

## Figure budget

If four: 1 (learn/break/relearn), 3 (the three message arms), 10 (what the confidence adds, per day), and
either 4 (handing the question over) or 6 (the inversion). Sections 4 and 6's theorem carry as text.
