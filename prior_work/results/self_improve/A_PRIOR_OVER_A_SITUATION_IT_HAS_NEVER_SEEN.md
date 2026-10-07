# The model predicted an unobserved situation correctly, and its memory deleted the prediction

2026-09-27, hh_s2, the arm that is told the night before and made to commit before it has seen
anything. One household, one night: an existence proof, not a replicated finding. The five-household
run is queued.

## What it wrote on night 13, having seen nothing of the change

> Tomas is unwell and staying home. **Expect him in bedroom_1 or living room during day/evening, not
> office.** His laptop/mug/charger **likely in bedroom_1 or living, not office desk.**

It had one sentence - a named person is unwell and is staying at home instead of going out - and no
sighting of any changed placement. It named two rooms and ruled out a third.

## Where his moving things actually were

Read from the bank, not from anything the robot saw:

| | office | bedroom_1 | living | kitchen | dining |
|---|---|---|---|---|---|
| days 8-13, the settled routine | **39%** | 15% | 0% | 35% | 9% |
| day 14, the first changed day | **0%** | **57%** | **29%** | 14% | 0% |

**86% of the placements fell in the two rooms it named, and none at all in the room it ruled out** -
against the office having been the commonest room of the previous week.

This is not "a language model knows a mug belongs in a kitchen". It is a model of what a person does:
somebody unwell and staying home has their work things where they are resting rather than at the desk
they are not sitting at. No rule over past sightings can attempt this, because the situation has never
been observed. It is the one thing in this study that an LLM can do and the comparator provably
cannot.

## And then the memory threw it away

On night 14 that claim was reworded to:

> Tomas works from the office during the day (seen 14:08). He moves to the living room in the evening.
> **The 'unwell' hypothesis from Day 13 is not supported by Day 14 activity.**

On the strength of one office sighting at 14:08. On the same night, in a different claim, the same
model wrote **"Tomas's glass is on the bedroom nightstand during the day (seen 08:07-15:12)"** - it
had the confirming evidence in front of it, recorded it, and still declared the hypothesis
unsupported.

So the failure is not that the model cannot form the prior. It forms it, specifically and correctly.
The failure is that **a nightly update that rewrites each claim to match the latest sighting destroys
a correct prediction on partial counter-evidence**, and it does so within one night. A claim store has
no way to hold "mostly the bedroom, sometimes the office" as a hypothesis under test; it holds only
what it last saw.

## What to do about it, and what is ours rather than theirs

The obvious next arm keeps a prediction from being reworded at all: it may be confirmed, or set aside
when the thing it was conditioned on stops, but not narrowed by a day's sightings. That is a guard WE
would impose, so any gain has to be reported as our design choice and not as a property of the model
- the same discipline that caught the four earlier faults where a limit of ours was read as a finding
about somebody else's method.

The measurement that does not depend on any of that, and the one to replicate first: on the first
changed day, before the robot has looked, **what share of the questions does the told-and-committed arm
get right in the first room, against the same arm untold and against the rule with no model?** The
slice is defined from the bank - the objects whose true place on day 14 differs from their settled
place - so it is the same set of questions for every arm and does not depend on where any arm chose to
look.
