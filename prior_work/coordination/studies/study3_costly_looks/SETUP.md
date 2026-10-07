# Study 3, costly looks: setup, written before any run

Written 2026-10-02 01:05 PDT by study-lead.

## The question

When every look costs walking distance and looking into an occupied room costs extra, does a
method that reasons about where to look next beat the plain rule (last-seen, then the nearest
place not yet tried) on things found within a budget and on cost per question?

## Where it runs

Not in the household simulator. The rendered search benchmark
(`src/rendered_look/searchbench/bench.py`, data in
`results/rendered_look/hh_s151/searchbench/go2/` and `raised/`) already has: 164 camera positions
in one home with walking metres between every pair (habitat shortest paths), 248 question times
over a month (8 a day) with a stored picture for every position at every time, residents in the
pictures, a "cannot be found" answer, and the policies random / last-seen / most-frequent / mix
/ chance-over-cost / oracle with four fallbacks. Perfect perception = the "in view" rule (at least
200 pixels, not cut by the edge). This is the brief's "existing simulator" for this study; building
costs into the household simulator would take the night and reproduce what exists.

What has to be added (sim-builder):
1. A per-look penalty when a resident is in the room looked into (the pictures already record who
   is in frame; the moments file records where each resident is).
2. A cost budget per question (metres plus looks plus penalties) and the score "found within
   budget", at three budget levels.
3. A model-driven policy: given the robot's own past sightings of the asked thing, the map of
   places with distances from where it stands, which places were looked at already in this
   search and what was seen, it names the next position (or "cannot be found"). Same prompt for
   Qwen and for Opus; structured output with a reasoning field first. It must be handed only what
   the rule policies get (`Known` and `Memory`), never the truth object.
4. A dry run of the whole loop with a fake model that always answers "nearest untried", which
   must reproduce the rule policy's numbers exactly before any real model call.

## Baselines to beat

- last-seen, then nearest untried place (the brief's first baseline); on this data it finds 80%
  of findable things under "in view" (Go2 rig, five starts).
- every place in order of distance from where the robot stands (the brief's second baseline).
- also reported: the mix of last-seen and most-frequent (79%), chance over cost (70%), and the
  oracle (100%), which bounds any method.

## Main score

Found within budget, of findable, at three budgets; and total cost per question (metres + looks
+ penalties) among found. Split by towels (43% of questions, never move) and other things, as the
benchmark page already does, because the towels dominate.

## Prediction

The oracle is at 100% and last-seen with nearest-untried at 80%, so a model has at most 20 points
of room on all things and about 50 on other things (last-seen finds 51% of those). Prediction: a
Qwen chooser lands within 5 points of last-seen on all things and within 10 on other things, at
higher cost per question, because the places are few and the rule already uses the two facts
that matter (where it was, what is near). The occupied-room penalty hurts the rule and the model
equally. Expected verdict: drop; the gap stays under 10 at every budget.

## Size and detectable gap

One household, 248 questions, five starting positions pooled: per-start spread on the pooled
score was 1 to 8 points for the rules, so differences under about 5 points are not separated, and
there is no household spread at all. A keep verdict would need the benchmark rendered for more
households (the binding of places to furniture is hand-written for this one home); a drop does
not.

## Opus

Blocked by the usage file. If it is unblocked: 1 start, 40 questions (5 days), one subagent per
question with the same prompt, zero tool calls allowed, transcript checked.
