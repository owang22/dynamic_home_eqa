# Search-driven sensing: what is measured, and what it does not support

Every number here is from `results/self_improve/search_driven/`, three households
(hh_s0, hh_s1, hh_s2), 8 questions a day sampled evenly across the day, days 0-31,
k = 3 rooms per question, paired within household and clustered on **household,
never on question**. n = 3 means a 2 SE bar with two degrees of freedom: wide.

**The design.** No patrol and no day-0 walkthrough. Every observation comes from a
search the robot made because it was asked a question. It opens up to three rooms
one at a time, stops early on a find, answers with the true place if it found the
object and otherwise from an 8-line window of its notes plus the rooms the failed
search just ruled out. Every search step is described to the nightly note-writer by
`describe_look_for_the_model(look, only_these_objects=None)` - every sighting, every
resident, every absence, no filtering to the quizzed objects, for every arm.

## The measure this strand changed to, and why

**First-room-correct is primary. Find-rate-within-budget is not a robustness check;
on the mover slice it is actively misleading and must never appear without
first-room beside it.**

At k = 3 of about 7 rooms, chance alone finds the object 42.9% of the time, so
find-rate compresses the signal. First-room-correct has a chance baseline of about
1 in 7 and does not hand out the free credit of two more guesses. On the objects the
disruption moved, the two measures disagree about the direction of the effect:

| memory-guided / wholesale, movers | settled | transition 14-16 | spell 17-23 |
|---|---|---|---|
| first-room-correct | 63.2% | 45.5% | 47.4% |
| found within k=3 | 86.0% | 84.3% | 92.0% |
| rooms opened per question | 1.55 | 1.87 | 1.78 |

Paired, settled to transition: first-room **-17.7 pts (2 SE 11.4)**, clears; found
**-1.7 (2 SE 6.6)**, inside. Transition to spell: first-room **+3.5 (2 SE 3.5)**,
inside - **no recovery**; found **+8.8 (2 SE 3.6)**, clears. Settled to spell:
first-room **-14.2 (2 SE 13.7)**, clears. Non-movers are flat on every contrast.

So find-rate reports no disruption and then an improvement, where first-room reports
a collapse that does not recover inside ten days. They are reconciled by search
cost: the robot buys the outcome back by searching harder.

## The warning that governs every accuracy number here

**Accuracy inside a live search-driven cell is not a memory measurement.** Every cell
answers by looking: each opens 114 to 220 rooms to answer its questions and finds the
object on a large share of them, and an object you have physically found hands you its
shelf for free. The diagnostic is **shelf accuracy exactly equalling room accuracy** -
hh_s2's memory-guided wholesale cell reads 90.6% room and 90.6% shelf - which a memory
can never produce. Only legs can.

So the accuracy rows are largely find-rate in different units. It is visible in the
figures themselves: the shelf-answer gain on spell movers is +23.9 and the find-rate
gain is +22.8. Those are one result, not two.

**What survives untouched, because none of it depends on answer accuracy:**
first-room-correct (which room it opens first - a pure policy measure), rooms opened
per question (cost), found within budget (search outcome), the never-saw split and the
written-and-gone analysis (properties of observation and of the artifact).

**The correct gloss: what a memory buys here is a better SEARCH, not a better answer.**
Accuracy rows are reported only with rooms-opened beside them, and never tabled beside
a frozen arm's accuracy. The genuine memory measurement is the frozen-memory pass -
notes frozen, all looking stopped, answers from the notes alone - in
`results/self_improve/search_driven/frozen/`.


## What is claimed

1. **The prior, not the memory, does the work in ordinary life.** On day 1, with the
   notes empty at the first question, the memory-guided arm already found 92% of
   objects in 1.25 rooms. Household s0 then ran 7,8,7,6,8,7,8,7,7,8,8,7 of 8 from
   day 1 to day 12: a flat line at ceiling, which is what a saturated prior looks
   like and not what learning looks like. **The settled-period search-cost
   separation (91% found against the controls' 40%) must not be quoted as a memory
   result.**

2. **The model earns its place exactly when the world stops matching the prior, and
   not otherwise.** Against a mechanical arm that calls no model at all - go to the
   room you last saw it in, answer with the shelf you last saw it on - paired within
   household, n = 3:

   | model minus mechanical | settled | spell | back to normal |
   |---|---|---|---|
   | first-room, all | -0.016 (2 SE 0.083) | **+0.042 (0.022) model** | +0.005 (0.038) |
   | first-room, movers | -0.087 (0.118) | **+0.100 (0.069) model** | +0.030 (0.062) |
   | found, movers | +0.019 (0.047) | **+0.206 (0.080) model** | +0.083 (0.096) |
   | rooms/q, movers | +0.058 (0.089) | **-0.247 (0.141) model cheaper** | -0.056 (0.191) |

   **A mechanical rule must be run as its own arm.** Scored on the model's look
   stream it reached 78.1% first-room against the model's 76.2% settled and 73.5%
   against 63.2% on movers - apparently beating the model. That is invalid: the
   stream is generated by the model's choices, so "where you last saw it" is a good
   signal there *because* the model chose well. Given its own stream the rule drops
   from 50.6% to 45.2% on spell movers.

3. **SET ASIDE, not a result.** It looked as though notes helped at shelf level and
   not at room level, contradicting a prediction that the reverse would hold. But
   shelf accuracy inside a live cell tracks find-rate (see the warning above), so
   that comparison was never a granularity test. **Neither the prediction nor its
   apparent refutation holds on this data.** Recorded so nobody re-derives it.

4. **The bottleneck has moved from sensing to note-taking.** Under the patrol, 75%
   of the memory's errors were objects never seen in their new place. Under search,
   movers during the spell: on wrong answers, 7.1% never saw it, 2.4% saw it once,
   **90.5% saw it repeatedly and still got it wrong**; on first-room failures for
   memory-guided/wholesale, 23.2% / 5.4% / **71.4%**. `glass_yuki` was on
   `kitchen_table_k1`, which that arm had seen at that exact shelf 5 times and in
   that room 37 times, and it walked into the entry. Every count is of sightings
   **strictly before** the question, so this is a curation failure and not a latency
   one.

   **The never-saw share is a composition of the failure set and inverts if quoted
   alone.** The memory-guided arm's 23.2% against the controls' 5% is not the arm
   doing worse: it fails on 56 of 126 mover-questions against the rotation's 115 of
   126. The share is never stored as a bare number in
   `where_the_bottleneck_moved.py`; the field carries both figures and the warning.

5. **Both of these are true and neither may be stated alone.** The memory is far
   from what its own evidence would allow - it fails on objects it saw repeatedly
   and does not recover inside ten days - *and* it is well ahead of the obvious
   mechanical alternative over the same window. The first alone says memory is
   useless; the second alone says it works.

6. **The wholesale rewrite is not a faithful transformation of its own input, in
   either direction.** Of 101 wrong answers on movers during the spell, on objects
   it had seen at that shelf at least twice: 13.9% never written, 51.5% written and
   gone, 30.7% in the notes but outside the read window, 4.0% in the read window and
   still wrong. At most 14% selection, at least 82% capacity.

   **The strong form of this covers about a quarter, not a half.** Of the 52
   "written and gone", 46.2% were true on a night they were written and 53.8% only
   became true later. So: half of its errors are facts it had written at some point
   and lost, and for about half of those the fact was true when written - roughly a
   **quarter of all its errors are facts it held while true and then dropped**. The
   weaker half still matters: a summary that said the mug was on the coffee table,
   dropped it, and was wrong when the mug returned there has lost reusable
   structure. It is just not "it forgot something it knew to be true".

7. **The incremental claim store, as the model actually drives it, is a wholesale
   rewrite one claim at a time. This explains why the two formats have been so hard
   to separate: the architectural difference exists in the data structure and the
   model does not exercise it.**

   Of the (mover, place) facts that were true during the spell: the store ever wrote
   111 of 148 (75%) and then lost 73 of them (**66%**); the rewriter ever wrote 162
   of 186 (87%) and lost 90 (**56%**). The store loses *more*. Consistent across all
   7 store cells, 57% to 78%.

   Mechanism, checked rather than assumed. Of 118 true spell facts absent from the
   store's live statements, **81 were lost by revising the claim in place** and 37
   were never written. `revise_claim` does retain the previous wording - in
   `revision_history` - but `what_the_robot_can_read()` reads `claims[].statement`
   and never touches history, so **the guarantee is over the audit trail, not the
   readable memory**, and a retained fact is unreachable. That is a design flaw of
   ours, stated plainly, not a bug.

   The format offered a non-destructive path and the prompt said so: add a claim for
   the new routine and set the old one's standing to "set aside", keeping both live.
   The model did not use it.

   **A named candidate cause, to be tested rather than assumed: the forced-edit rule
   plausibly pushes toward `revise`, because revising is the cheapest way to satisfy
   "say something tonight".** The experiment that settles it is a schema that cannot
   overwrite - revise may change standing and status, a new place requires a new
   claim - which distinguishes a model that *fails* to preserve from one that was
   *never made* to. Not run: it is a design change and would look like smuggling a
   fix into the arm.

## What these numbers do NOT support

- **No naive comparison with the patrol runs** at `results/self_improve/memory_factor_v1/`.
  The search runs differ in TWO ways at once - no priors and search-driven looking.
  Averaged over the six search cells, search opens far more rooms a day than the
  patrol's 1.26 and observes far more distinct objects than its 10.7. The three
  search arms share the k = 3 budget and are comparable with each other.
- **The 7.1% never-saw on wrong answers is 42 errors from 2 completed cells.** The
  first-room version is three households in every row; lead with that.
- **The fixed rotation is indistinguishable from random** - 38.9% found against
  40.5%, 2.56 rooms against 2.62 - so it was dropped from the primary configuration
  as redundant, not as inconvenient.
- **The households are typical by construction.** The generator puts towels on towel
  rails and mugs in kitchen cupboards, so a commonsense prior is nearly right before
  any observation. This is the regime **least favourable to finding a memory
  effect**, and any effect found here is a lower bound. A household with
  idiosyncratic placements would separate prior from memory in the settled period
  too - future work that follows directly from claim 1.
- **The absence de-duplication** states each (object, room) absence once with a
  count of how many looks confirmed it that night, rather than up to 24 times. Both
  sizes are logged per night; verbatim rendering is 0.36-0.51 of the compacted size's
  reciprocal, i.e. 124,000-161,000 characters against 45,000-72,000.
- **One measure here needs a text matcher** - whether a line of prose asserts a
  (object, place) pair, in claims 6 and 7. It uses the audited
  `facts_a_statement_asserts`. Its failure mode is to MISS an assertion, which
  inflates "never written", so that bucket is an upper bound and the capacity buckets
  are lower bounds. Everything else is from structured sighting records.
- **The forced-edit rule's quiz-set dependence is a no-op under search**: it fired on
  407 of 407 nights across all 33 cells, because a robot opening up to 24 rooms a day
  always sees something it will be quizzed on. It is NOT inert under the patrol
  design, where one room a day means many nights see nothing quizzed.
- **The no-asked-list change moves two sentences**, the enumeration and the count of
  quizzed objects in the read-budget sentence. That arm cannot attribute its effect
  to the enumeration alone.

## The memory's contribution at choice time, priced against the prior

The control that makes this interpretable: the identical chooser with the notes
withheld at choice time, notes still written every night and still used to answer.
Primary (no-asked-list) configuration, incremental edits, paired within household,
n = 3. **memory-guided minus prior-only:**

| | window | all | movers |
|---|---|---|---|
| first-room-correct | settled | **+0.061 (2 SE 0.046)** | +0.091 (0.092) |
| first-room-correct | spell 17-23 | +0.107 (0.109) | +0.123 (0.139) |
| first-room-correct | back to normal | **+0.133 (2 SE 0.117)** | +0.162 (0.186) |
| found within k=3 | spell 17-23 | **+0.071 (2 SE 0.041)** | **+0.128 (2 SE 0.079)** |
| rooms per question | transition 14-16 | **-0.153 (2 SE 0.100)** | **-0.199 (2 SE 0.117)** |

So the notes DO contribute beyond the prior, and the contribution is largest at and
after the disruption: about 0.2 fewer rooms opened per question at the transition and
about 13 points of find rate on the movers through the spell. It is modest and about
half the rows sit inside the bar at n = 3. **Two households show the effect and one
(hh_s2) shows 0.000 on nearly every first-room row**, which is the honest picture and
is why n = 3 is not enough to size it.

## The told-list wave, complete: 18 cells, paired within household

memory-guided minus fixed rotation, wholesale rewrite: rooms per question
**-1.195 (2 SE 0.075)**, found within budget **+0.522 (2 SE 0.011)**, room accuracy
+0.093 (0.051), shelf accuracy +0.228 (0.067) - the last two read with the warning
above. random minus fixed rotation: every measure inside 2 SE, confirming the two
question-blind controls are one control.

**The settled period is flat and HIGH, not flat and low.** Room accuracy runs 86-96%
across days 1-13 with slopes between -1.7 and +0.3 points per day. The night-shift
failure mode this check was built to detect is not present, but neither is a learning
curve - because the prior supplies the settled routine for free and there is nothing
left for the notes to learn there. The four-phase shape IS visible at room level for
the memory-guided arm: 95.8% settled, 81.2% at the transition, 94.8% through the
spell, 91.7% at the return, 97.9% back to normal.


## Still running / not done

- **all three waves are COMPLETE**: told-list 18 cells, no-asked-list 15 cells
  (including the prior-only control), mechanical 3 cells;
- the **frozen-memory pass** is running: notes frozen at days 13 and 23, all looking
  stopped, 30 questions a cell, into `frozen/`. This is the only number from this
  framework comparable with the patrol results. NOTE that unlike the patrol design the
  control point is NOT a null by construction here, because each arm has its own look
  stream and therefore genuinely different information;
- one sanity-assay concern to carry: hh_s2 memory-guided wholesale, 12% of answers did
  not parse;
- the **notes-alone ablation** (answer step not told what the search ruled out);
- the **non-destructive-schema variant** of claim 7;
- scaling past three households.
