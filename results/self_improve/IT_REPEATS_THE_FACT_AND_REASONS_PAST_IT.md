# The told arm recalls the sentence and then reasons past it, 2026-09-27

Read out of the reasoning on day 14 of the told-with-the-log cell on hh_s2 - the first changed day,
the sentence delivered the night before, so the robot knew before it saw anything.

**It has the information and recalls it unprompted.** Of 24 questions on day 14, seven mention being
told or being unwell without being asked to. So it is not forgotten and it is not lost in the notes.

**And then it reasons straight past it.** Every one of those seven predicted the office or the
kitchen. The true room was the bedroom. In its own words, on three separate questions:

> My notes state Tomas works from the office during the day (09:35-15:48) **and is unwell/staying
> home**. However, since he is working in the office, he may have moved his drink there...

> My notes state Tomas works from the office during the day (09:35-15:48) **and is unwell/staying
> home**. His personal items are consistently found on the office desk during these hours.
> Although the glass was last seen in the kitchen, it is highly probable he has moved to his
> workspace...

> **since he is working from the office**, he likely keeps his drink there. The office is the most
> likely location for a work-from-home individual's personal item during the day.

"Unwell and staying home" has become a phrase attached to the routine rather than a premise that
replaces it. In the third quote it has been reversed outright: the sentence said he is staying home
instead of going out, and the model concludes he is at his desk because that is what someone who
works from home does.

**This is the same shape as two faults already found in other designs.** Faithful ACE slid its time
threshold from 20:00 to 13:00 to 11:47 so that late morning counted as "the evening" rather than
concluding somebody was at home during the day. Our own claim store reworded seven of eight
conditional claims to match the day in front of it. In all three the new information is bent to fit
the structure that already exists, rather than the structure being changed.

## What follows, and it is a design change rather than a louder sentence

Being told a fact puts the fact in the prompt. It does not make the model USE the fact, because
nothing asks it to commit to anything. So the next arm does ask: on the night it is told, and before
it has seen a single changed sighting, it must write down **what it expects to be different
tomorrow** - which person will be where, which of their things will move, and to which room.

That turns the sentence into a prediction the memory carries into the next day, and it is the thing
worth testing, because it is the one claim in this study that a rule over sightings cannot even
attempt: a prior over a situation nobody has observed yet, generated from one sentence about a
person. "A language model knows a mug lives in a kitchen" is not news. "A language model can say
what a household will look like tomorrow, having been told only that somebody is unwell, and be
right often enough to beat a sighting rule on the day of the change" would be.

## Confounds to hold onto while measuring it

1. **The sentence must carry no placement.** It says only that a named person is unwell and staying
   home, or is better and back to their usual routine. No room, no object, no shelf. Re-checked.
2. **The slice must not be defined by the arm's own behaviour.** "Objects not yet re-seen since the
   change" depends on where that arm chose to look, so it differs between arms. Define the slice
   from the bank instead: the objects whose true place on day 14 differs from their settled place.
   That is the same set of questions for every arm.
3. **Chance differs by household** - eight to nine rooms - so pair within household and never pool
   raw percentages across homes.
4. **Day 14 is one day**, about 24 questions a household. Five households, not three, and the
   single-day figure gets read with the number of homes printed beside it.
5. **The slice was chosen before the cells landed.** This file is the record of that, written while
   the told-with-the-log cells were still running on three homes and before any of them were read on
   the five wider homes.
