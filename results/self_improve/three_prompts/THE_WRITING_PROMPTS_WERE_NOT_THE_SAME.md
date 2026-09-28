# The two memory formats were never given the same instruction at writing time

Written 2026-09-24, before any outcome from this directory. Produced by building both
formats' nightly prompts on the same household (`hh_s2_t03`, 11 asked objects, 9 rooms)
on the same night (day 14, one look) from the **pre-patch** `write_the_notes.py` — the
module as it stood under the old defaults, so this is what every earlier memory-format
number was measured with. The module copy used is
`/tmp/.../scratchpad/wtn_before.py`, taken before any edit of mine.

**The shared preamble is byte-identical between the formats.** Verified, not assumed: the
day, the room list, the quiz list, and the whole rendering of what the robot saw are the
same lines in the same order. Everything below is what differs, which begins at the line
that shows the model its own notes.

## What the WHOLESALE writer was told, verbatim

```
Your notes as they stand:

Kitchen table holds mug_ines.

Write the notes again from scratch. Produce one summary of where this
household keeps the things above, as you now believe it to be. It
replaces what is there: whatever you do not write down is gone.
Say which routine or condition each part of it holds under. A household
can be in more than one routine over a month.

Your notes must fit in 8 lines, one fact to a line, and
this home has 11 things you are asked about. So
you cannot keep one line per thing: decide what is worth the space. A line
that covers several things, or says when a place holds rather than just
where, is worth more than a line naming one spot.
```

## What the CLAIM STORE writer was told, verbatim

```
Your notes as they stand. Each one is a separate claim with its own id:

[claim_0001] Kitchen table holds mug_ines. (holds under: ordinary weekdays; provisional; 0 sighting(s) for, 0 against; last revised on day 13)

Write the edits today's looks call for: anything you saw today that no claim covers yet needs a claim, and anything a claim got wrong needs that claim revised.

An edit either adds a new claim, revises an existing claim by its id, or attaches today's observation ids to an existing claim by its id as supporting or contradicting evidence.

Revising a claim keeps its previous wording in its history, so a claim is never lost. Set a claim's standing to "set aside for now" when the evidence now goes against it: that keeps the claim and records that it is not holding at the moment. A claim about one routine does not have to be undone to write a claim about another. A household can be in more than one routine over a month and your notes can hold claims for each.

Cite the observation ids in square brackets above for anything you assert. If today's looks only confirm what a claim already says, attach the evidence to it rather than writing the claim again.
```

## Everything that differed, enumerated

Not only the budget sentence and the object count. There are **six** differences, and
four of them push the wholesale arm toward compression and loss while the claim store is
pushed the other way.

| # | What | Wholesale | Claim store | Which way it pushes |
|---|---|---|---|---|
| 1 | **the line budget** | "Your notes must fit in **8 lines**, one fact to a line" | nothing | compress |
| 2 | **the object count, in the same sentence** | "this home has **11** things you are asked about. So you cannot keep one line per thing" | nothing | compress, and it makes the shortfall explicit |
| 3 | **a value ranking over kinds of line** | "A line that covers several things, or says when a place holds rather than just where, **is worth more** than a line naming one spot" | nothing | away from per-object facts |
| 4 | **what happens to what you leave out** | "It replaces what is there: **whatever you do not write down is gone**" | "Revising a claim keeps its previous wording in its history, so **a claim is never lost**" | **opposite directions** |
| 5 | **an anti-repetition instruction** | nothing | "If today's looks only confirm what a claim already says, attach the evidence to it rather than writing the claim again" | only the claim store is told not to restate |
| 6 | **evidence citation** | nothing | "Cite the observation ids in square brackets above for anything you assert" | only the claim store must ground a claim |

## And a seventh, which is not in the prompt at all

The output schemas are not comparable, and this is the **larger** half of the limit
because it caps the wholesale arm's entire memory rather than one night's writing:

| | Wholesale | Claim store |
|---|---|---|
| shape | one string | up to 8 edits a night |
| hard ceiling | `maxLength: 2400` characters — **on the whole memory, for the whole month** | `maxLength: 240` per statement, 8 statements a night, and **claims accumulate** |
| ceiling over 32 nights | 2,400 characters, ever | of the order of 60,000 characters |
| `max_tokens` | 900 | 1,400 |

So the wholesale arm's memory could never exceed about twenty lines no matter what any
prompt said, while the claim store's could grow without bound. **Removing the budget
sentence alone would not have produced a no-length-limit wholesale arm** — it would have
produced one capped at 2400 characters with nothing in the prompt to say so, which is the
worst of the two worlds because the constraint becomes invisible.

## What this costs the earlier results

Every difference measured between the two memory styles — the repetition rate, the
vacuity gap, the facts held, the reachability, the accuracy — is **partly a comparison
between a writer instructed to compress and warned that omissions are lost, and a writer
instructed that nothing is ever lost and told to cite its evidence.** That is not a
difference between representations. It is a difference between instructions, and it is
confounded with the representation in every number taken before today.

It also gives a simpler explanation for the finding we thought most damning about the
rewrite arm — that it dropped facts it had written **while they were still true**. A
writer told to fit eight lines in a house with fifteen objects, told that a line covering
several things is worth more than a line naming one spot, and warned that whatever it
leaves out is gone, is doing what it was told. Under the pre-2026-09-24 prompts that is
not a failure of wholesale summarising; it is compliance.

## What is true of the new wave

Confirmed for **every** arm, and asserted in the runner rather than hoped for:

- **Neither format is told to compress.** The budget sentence, the object count and the
  value ranking are removed together (`say_the_notes_must_fit_a_budget=False`). For the
  five incremental arms this changes nothing, because their writing prompt never said it
  — which is precisely the asymmetry above.
- **No read-time cap.** `what_the_robot_can_read(read_budget_lines=None)`, so every line
  the notes hold reaches the prompt, for both formats.
- **The schema ceiling is lifted** for the wholesale arm, from 2400 to 24000 characters
  with `max_tokens` from 900 to 6000 — ten times more than any summary has come near, so
  a removal in practice.
- `run_one_arm` **refuses to write a cell** if any night was still told to fit a budget,
  or if the read budget bit on any question. A silently-capped cell cannot be reported.

## What is STILL not symmetric, stated rather than fixed

Differences 4, 5 and 6 above remain, and so does the claim store's limit of 8 edits a
night. Those are not length limits, so they are outside the correction, and changing them
would alter the arms in more than one way at once. **So the uncapped wave is the first
comparison of the two styles in which neither is told to compress — it is not yet a
comparison in which they are told the same thing.** Any memory-style claim from it has to
carry that sentence.
