# What the reasoning traces show — prompt and data failure modes

Read from the elicitation traces of hh_001 tl0/bank0 (tour 15:08 Mon, 8 objects
not seen), hh_001 tl1/bank0 (tour 11:26 Tue, 10 not seen), and the day-3
revision trace of tl0/bank0. Every item below is quoted or paraphrased from
the model's own reasoning; the traces are in `logs/tour_named/<subdir>/hh_001.md`
and `tour_start/tl*/<run>/revisions/*.md`.

## Prompt problems (patched in `prompt.py`; the running spread used the OLD prompt)

1. **"NOT FOUND" burned ~40% of the reasoning.** The model looped on whether
   an unseen object was out of the house, on a person, "in a closed bag on the
   desk", "in a nightstand drawer", "in a closet", "under the bed", "on a high
   shelf" — places that do not exist — and only concluded "NOT FOUND =
   OUT_OF_HOUSE or ON_PERSON, period" after ~300 lines. It also invented a
   fridge ("lunchbox at fridge... wait, no fridge"). *Patch:* the receptacle
   list now states it is complete ("no closets, drawers, bags or shelves
   beyond these"); the observation model is stated once ("the robot sees every
   object in any receptacle above; not seen = out of the house or on a
   person").
2. **Two object lists (vocabulary + NOT FOUND) invited the confusion above.**
   *Patch:* one object table, each row carrying its tour status (`seen at X` /
   `NOT SEEN`).
3. **The tour instant became the subject.** With the time named and the
   missing list given, three of five hypotheses were built to explain the
   snapshot ("at 15:08 she has just returned from an errand", "items are
   ON_PERSON because she is about to go out", "getting ready for evening
   yoga") rather than to describe a weekly routine. *Patch:* "Describe the
   routine, not the tour instant — do not write hypotheses whose point is to
   explain what was happening at 15:08."
4. **The length guide's "1–6 moves per activity" dropped carry-out objects.**
   tl1: "*Wait, that's 9 moves. Max is 6 per activity... I'll just pick the 6
   most important carry items.*" This is the direct cause of the scorecard's
   carry-out coverage of 0–6 of 15. *Patch:* "An activity lists every object
   it moves — an outing that takes ten objects out of the house lists ten
   moves."
5. **Distinguishing checks at ON_PERSON / OUT_OF_HOUSE are unverifiable**
   (three of five in tl0), and the day-3 report duly said "not yet tested".
   *Patch:* the check's `at` must be an observable receptacle; the example was
   fixed to match (keys back on the shelf at 19:00 rather than "keys
   OUT_OF_HOUSE at 13:00").
6. **`_shared_` read as a second resident.** Both traces spend a paragraph on
   "shared items suggest a partner or family" and tl1's hyp2 is built on a
   partner who owns the shared items. *Stopgap patch:* a naming note in the
   table ("`_shared_N` is a household item with no owner; suffixes are ids,
   not evidence of how many people live here"). The real fix is the renaming
   you are doing.
7. **The revision report said every hypothesis had weight 0.00** with no
   explanation — because the statistical particle held 1.00 and was not
   listed. *Patch:* the report now shows the statistical model's weight and
   says what it is.

## Data problems the model noticed (your generator edits)

- **Keys at the entry table while every other carry item was out** (tl0,
  15:08 Monday): the `forget_p` draw. The model built an entire hypothesis
  around it (hyp3: "part-time afternoon worker who leaves her keys, uses a key
  fob") and used it as the check that "came true".
- **Jacket and notebook seen at the dish rack, lunchbox in the sink** (day-3
  stats): misplacement draws to implausible receptacles. The model wrote
  "*jacket at dish_rack? weird*" and then, in the revision, set rests from
  those stats.
- **Bowl at the entry table, remote in the cupboard, vacuum on the bedroom
  floor, watering can in the sink**: read by the model as "unusual"; the
  vacuum/yoga-mat/suitcase placements pulled it toward "messy homebody"
  stories.

## Model limits not fixable by prompt

- Rests for objects it never saw (all ten carry items in tl1) are pure
  priors, and the priors are generic: work items → `desk_b1`, wallet →
  `desk_b1`, phone → `nightstand_b1`. In this home everything work-related
  rests on the kitchen table. A wrong rest is 3 pseudo-sightings against a
  72 h-decayed steady state of ~3 real ones, i.e. permanent.
- It wants per-weekday schedules ("WFH on Wednesdays") that the
  weekday/weekend/both vocabulary cannot express, and says so.

## Added after re-reading: ON_PERSON vs OUT_OF_HOUSE

The old prompt listed `ON_PERSON` as a receptacle with no definition; the only
hint was "not found = out of the house or on a person". In tl0/bank0 (tour at
15:08 with 8 objects unseen and the keys at home) the model made `ON_PERSON` a
routine state — "afternoon_errand: items ON_PERSON → OUT_OF_HOUSE → back",
"wearing the jacket in the house", "carrying the laptop around while WFH" —
13 of the 18 ON_PERSON moves across all eleven elicitations are in that one
run, and three of its five checks were at ON_PERSON (unverifiable). In the
truth ON_PERSON is 7% of away time (138 vs 1,745 object-hours) and scoring
already merges the two. *Patch:* ON_PERSON is marked not a valid destination
or rest; rule 5 now says anything taken out of the home goes to
OUT_OF_HOUSE with `after: returned` if it comes back. *For the generator:*
the 12 true ON_PERSON stints average 11.5 h each.
