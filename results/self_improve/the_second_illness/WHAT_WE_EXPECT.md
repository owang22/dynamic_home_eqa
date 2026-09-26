# The second illness: written before it runs

Oliver's question is whether a memory that has already lived through one illness handles the
second one better. This file says what we expect, so that whatever happens cannot be read as
whatever we wanted.

## What we already know, and it makes this a prediction rather than a fishing trip

Measured on the complete ten-household wave at 8 questions a day, on day 31 — a week after the
resident recovered. A note counts here when it names an object and the plain words of the place
that object went to **during** the illness, both taken from the bank rather than from any text:

| arm | live notes on day 31 | describing an illness place | of those, set aside | mentioning the illness |
|---|---|---|---|---|
| the plain claim store | 595 | 156 | **0** | **0** |
| our first ACE | 334 | 103 | **0** | **0** |
| ours, record + notes on the routine | 471 | 131 | **0** | **0** |
| our first MemGPT | 101 | 38 | **0** | **0** |

**428 notes describe where things went while somebody was ill, and not one of them mentions that
anybody was ill.** The condition each note carries, where it carries one, is a time of day:
`always` (74 notes across the arms), `evening`, `afternoon`, `general observation`,
`Felix is at home`. Thirty notes in the plain claim store say the illness placement holds
**always**. None is set aside, so every one of them is offered to the reader as current belief a
week after it stopped being true.

The matcher was tested before these counts were believed. Its first version read zero everywhere,
because it looked for `place_id` and `day` on rows that carry `receptacle_id` and `t` - a check
with no power, reporting the cleanest possible result. Fixed, it fires on a sentence built from
an object's illness place and does not fire on the same sentence built from its ordinary place.

## So the prediction

**The second illness will look like the first.** Same fall to roughly a third of settled accuracy
on its first day, same recovery over about four days, no arm materially faster than it was the
first time. Nothing in any memory says "this is what happens when Tomas is ill", so there is
nothing for the second spell to match against, and the only route back is relearning from
sightings.

What would refute it: any arm recovering materially faster on the second spell than on the first,
paired within household. "Materially" is at least 2 standard errors on the paired difference and
above the rerun noise floor for the measure quoted, which is 1.9 points on first-room-right and
2.2 on found-within-budget.

## What each outcome means, decided now

- **The prediction holds for every arm.** Then no current memory design represents a temporary
  regime, only its consequences, and none can transfer. That is the paper's central negative
  result and it is worth more than a small win on accuracy.
- **One arm recovers faster.** Then whatever that arm writes differently is the mechanism, and the
  next thing to run is the smallest change that gives another arm the same property.
- **Every arm recovers faster.** Then the notes carry the regime in some form our matcher cannot
  see, and the matcher is wrong rather than the methods. In that case the claim to check is
  whether the improvement survives asking the same questions of a memory frozen at day 31.

## The third step, only if the second illness shows transfer

A DIFFERENT resident falls ill, days 50-59. If an arm transferred from Tomas-ill to Tomas-ill
again, the question is whether it transfers to Ines-ill, which needs the note to be about illness
rather than about Tomas. We do not run this until the second illness has been read.

## How it is built, and why it is nearly free

The episode is the current month with 18 days added, not a new month with two illnesses in it, so
the first 32 days are byte-identical and every model call for them comes back from the response
cache. Checked on three households: truth rows, questions, resident rows, walkthrough
observations, room visits and day names all identical before day 32, while seven header fields
that must differ do differ. A replay-only run of one arm over two days served 94 of 94 prompts
from the cache on the new bank and 2 of 172 on a different household's bank, so the 100% is a
measurement and not an artefact of a test that cannot fail.

About 37% of the work is new: roughly 596 new calls of 1,622 for the heaviest arm.
