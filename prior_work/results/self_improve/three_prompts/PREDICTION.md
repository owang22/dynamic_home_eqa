# Three prompts: predictions, written before anything ran

Written 2026-09-24 at 19:43, before the first cell was launched. NOT committed: this
project's rule is that commits happen when Oliver asks, so the timestamp rests on the
file's own mtime and on the fact that its contents were reported to the coordinator
before any cell had finished. **A commit would make the pre-registration materially
stronger and can be made on request.** Nothing above the addendum line may be edited
after a number exists; the scoring goes in `PREDICTION_SCORED.md` beside it.

## What is being run

Five arms, all on `incremental edits` (the claim store) with `memory-guided search`,
on the ten pilot homes at `results/self_improve/varied_homes/ten_homes/banks/`:

| arm | what changes |
|---|---|
| `control` | nothing. The nightly note-writing prompt exactly as it stands. |
| `rival_beliefs` | the writer is told to ADD a claim for the new state and set the old one aside rather than rewriting it, and that a superseded belief is worth keeping because routines come back. |
| `describe_the_person` | the writer is asked to record the household's routine and what the people are doing, in the same line budget, so routine lines compete with object lines. |
| `told_unwell` | one sentence on the night of day 14 ("resident_1 is unwell and staying at home") and one on the night of day 24 ("resident_1 is better and back to their usual routine"). Nothing on any other night. |
| `rival_and_describe` | variants 1 and 2 together. |

Only the nightly note-writing prompt differs. The homes, the searches (3 rooms, 8
questions a day), the read budget (8 lines), the answer step and the question sets are
identical across arms.

The primary outcome is measured with the notes FROZEN and all looking switched off
(`frozen_memory_test.run_frozen_memory_test`), at day 13 and day 23, on the full
question window (days 14-23, 240 questions a home) with no cap.

## The three pre-registered predictions

**P1. `rival_beliefs` will raise reachability** — the share of questions where the
asked-about object's true place is named inside the eight lines the robot reads —
because a set-aside claim is still readable and the return makes it correct again.
Direction: reachability(rival_beliefs) > reachability(control), paired within home.

**P2. `describe_the_person` will LOWER shelf-level accuracy and may RAISE room-level
accuracy**, because routine lines cost space that object lines were using.
Direction: shelf(describe) < shelf(control); room(describe) >= room(control).

**P3. `told_unwell` will produce the largest single effect of the three**, and it will
appear as a sharp improvement on the FIRST disrupted days rather than a gradual one.
Direction: |effect(told_unwell)| > |effect(rival_beliefs)| and |effect(describe)|; and
the day-by-day curve for `told_unwell` separates from `control` at day 14-15, not at
day 19-23.

## What counts as the effect being real

Two standard errors of the paired within-home difference, clustered on home (n = 10
homes, never on question). A difference smaller than that is reported as a null
together with what the null excludes.

## Negatives that are publishable and must not be softened

- **If the rival-belief instruction is COMPLIED WITH — the share of set-aside moves —
  and reachability does not improve, that is the strong result of the night.** It would
  say the readable memory is not the binding constraint: the right place is already in
  the window as often as it is going to be, and what fails is the answer step or the
  writing, not the read.
- If `told_unwell` does nothing, then being told the world changed is worth nothing to
  this memory, which is a harder negative than any of the format results.
- If `describe_the_person` costs nothing at shelf level, then the line budget was not
  binding and every "curation is zero-sum" claim in this project needs re-reading.

## Compliance comes before any outcome

An arm that was asked for something and did not do it is not an arm. Before any
accuracy or reachability number is read:

- `rival_beliefs`: count claims added-and-set-aside against claims overwritten, per
  home. Today's control baseline is 81 overwrites to 37 never-written with set-aside
  almost unused. **If the share of set-aside does not move, the variant failed and no
  outcome number from it means anything.**
- `describe_the_person`: count lines that mention a person, a time of day or a routine
  rather than an object-and-place, and count how many object-and-place facts were
  displaced. Both are reported; the trade is the point.
- `told_unwell`: the message appeared on exactly nights 14 and 24 and nowhere else.

## A fourth thing being measured, which is not one of the three

A third of answers in the earlier runs hit the 600-character ceiling on the
`reasoning` field of `CONF_SCHEMA`, and those answers were 13 points less accurate
(measured 2026-09-24 over 15,560 existing frozen answers: 34.3% at the ceiling, 36.4%
correct against 49.4%). That is correlational — a hard question produces long
reasoning — so the cap is raised as its own contrast on the control arm and the
answer is reported either way. **Prediction: raising the cap moves accuracy by more
than any of the three prompt variants does.**

---

# ADDENDUM, 2026-09-24 20:05, before any outcome number existed

Two corrections arrived from Oliver via the coordinator after the first wave was
launched and before any cell finished. The first wave was stopped at 19:59 and moved to
`superseded_8_line_budget_2026-09-24/`; no number from it is used anywhere. The
predictions above stand as written and are scored as written. These are added, not
substituted.

## Correction 1: the memory has no length limit, in writing or in reading

The eight-line budget was applied in two places, and changing one tests nothing:
`memory_notes.what_the_robot_can_read` cut the notes down before they reached an answer
prompt, and the **wholesale writing prompt told the model its notes must fit in eight
lines** and in the same sentence how many objects it would be asked about. Eight is fewer
lines than there are asked-about objects in nine of the ten homes. It is a limit we
imposed, cannot justify, and which shapes every number measured under it, so removing it
is a correction rather than an extra condition. There is no line-count sweep and no
variable-budget arm.

**What this does to prediction P2.** P2 said describing the person would lower shelf
accuracy *because routine lines cost space that object lines were using*. With no length
limit there is no space to compete for, so **the stated mechanism is removed**. P2 is
scored as written and, if it holds anyway, the mechanism it names is wrong and something
else is doing the work; if it fails, the reason may simply be that the budget is gone.
Either way the compliance measure still reports the trade, because the writer can still
choose to write routine lines instead of object lines even when nothing forces it to.

## Correction 2: the end-to-end measurement is the headline

In this design the robot searches in order to answer, and a search that finds the object
is an observation that enters memory with certainty, so memory quality shows up in the
search. The headline outcomes are now, for each arm against the unchanged control, paired
within home and clustered on home: **was the first room it opened the right one; rooms
opened per question; did it find the object within its budget; was the final answer
right, at shelf and at room level.** The frozen-notes pass is kept and reported as a
diagnostic answering one narrow question - what do the notes alone contain - and is
labelled as such. It is not an arm's result.

**A prediction on the new headline, written now.** The three variants will move
*reachability* and *what the notes contain* more than they move the *first room opened*,
because the chooser was already shown all of the notes and already finds the object in
one to two rooms. If that holds, the honest reading is that this design's search loop is
near its ceiling and the prompt is not the binding constraint.

## An added condition, and a prediction about it

`control_wholesale`: the unchanged prompt under the wholesale-rewrite style, with the
budget sentence removed. **Prediction: with nothing forcing it to drop anything, the
rewrite will stop being a rewrite** - its notes will grow close to monotonically and the
two memory styles will converge on "keep everything". If they do, the distinction
between the two styles was never about the style: it was about being made to choose what
to lose. That is an answer to the memory-style question, not a failed experiment.

---

# SECOND ADDENDUM, 2026-09-24 22:15, still before any outcome number existed

## The settled period no longer contains a coverage ramp

The nightly edit allowance replaced a flat cap of eight edits a night. Measured on a real
cell: night 1 saw **47 distinct objects**, was allowed **63** edits, and wrote **58 claims**
— so the claim store now opens with a near-complete description of the house, where under
the eight-edit cap it took about four nights to reach one claim per asked-about object.

**This is the better experiment and it is not being changed.** With no coverage ramp in the
settled fortnight, a change at day 14 is a change in the ROUTINE rather than a mixture of
learning the house and learning the routine. But it removes a premise that more than one
prediction above rested on, and that has to be said rather than quietly enjoyed:

- **Reachability in the settled period may not be able to discriminate at all.** If coverage
  at day 13 is near 100% in every arm, there is no room for an arm to be better there, and
  only the disrupted window can separate them. Any reachability comparison against an earlier
  wave is not like-for-like with this one.
- **Prediction P1 said rival beliefs would raise reachability "because a set-aside claim is
  still readable".** That reasoning assumed the notes were not already carrying nearly
  everything. It may now be right for a smaller reason, or right for no reason. It is still
  scored as written.
- **Duplication is no longer evidence of keeping a rival belief on its own.** 58 claims for
  47 objects means some objects had two claims on night 1, before any routine had changed. So
  the rival-beliefs reading must be a **change** in duplication between day 13 and day 23,
  never its level at day 23. The compliance report now reports both days and the paired
  change.

Three measures are added to the reports because of this, and they are diagnostics of the
design rather than outcomes: coverage of asked-about objects at day 13, objects carrying
more than one live claim at day 13 and day 23, and the growth curve per arm as a figure with
a CSV table beside it.

## A constraint that shapes the run rather than the result

The model client's socket timeout is `min(600, DEADLINE_S)`, so **600 seconds is the hard
limit on one generation**, and night 1 generates about 16,000 tokens. At 42 concurrent that
one call would take roughly 1,870 seconds and be killed, retried, killed again, and return
nothing. So the expensive first night runs at 12 concurrent and the cheap nights after it at
42. The shared client is deliberately not modified: that watchdog exists because a request
the server lost once blocked a thread for an hour, and other work depends on it.
