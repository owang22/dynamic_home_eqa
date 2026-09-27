# What happens to the sentence "somebody is unwell", 2026-09-26

Two arms are handed one sentence on one night: the resident is unwell and is staying at home. Told
the night before the routine changes, or told on the first changed day. Three households, 24
questions a day, reason-first schemas. This file is about what the memory does with it, read out of
the claim stores rather than inferred from accuracy.

## It is written down, and then it is written out again within a night or two

Live claims naming the illness, three households pooled, by day:

| arm | night it is told | +1 | +2 | +3 | day 31 |
|---|---|---|---|---|---|
| told the night BEFORE (night 13) | **2** | 2 | 2 | 2 | 1 |
| told on the FIRST CHANGED DAY (night 14) | **8** | 2 | 1 | 1 | 1 |

Told on the first changed day, eight claims name it on the night it arrives and **seven of those
eight are reworded so that the illness is gone**. Same direction in 3 of 3 households: 2→1, 5→0,
1→0 over three nights.

Told the night before, it is barely taken up at all - one claim in two households, none in the
third - because there is no changed sighting yet for the sentence to explain.

## What the rewording does, in the model's own words

The three that matter most were CONDITIONAL claims, which is the only shape that can survive a
return to normal, and each was narrowed to a flat statement of where the thing was that day:

    night 14: Leo's water bottle is in the office during the day. When unwell, it may be on the
              bedroom_1 nightstand in the afternoon and return to the office desk in the evening.
    day 31  : Leo's water bottle is on the office desk during work hours. In the evening, it is on
              the kitchen table.

    night 14: Leo sleeps in bedroom_1. ... His workspace is the office, but when unwell, he may
              move his charger to the bedroom.
    day 31  : Leo sleeps in bedroom_1. His book, journal, and tablet are on the bedroom_1
              nightstand. His workspace is the office.

    night 14: Leo is unwell and staying home. He spends the day in the office or bedroom_1. In the
              evening, he moves to the living room couch with his book, bowl, mug, and tablet.
    day 31  : Leo spends the day in the office. He is seen in the office from morning to evening.

The pressure is obvious once it is named: every night the writer is shown that day's sightings and
asked what its notes should say. A claim of the form "usually A, but when unwell B" reads as half
wrong against any single night, so the model narrows it to whichever half tonight supports. The
conditional structure is not rejected - it is eroded, one night at a time.

## The field that exists for exactly this is used for something else

Our claim store has a `holds_under` field, offered on every claim, for the condition a claim holds
under. Across all six told cells:

**361 of 361 claims fill it in. One of them names being unwell.**

The rest say `Always` (77 claims), a person being at home, a time of day (`Evening`), or a literal
date (`Day 31 after 20:18`, `Day 25`, `Day 15`). The field is filled because it is offered, with
the easiest thing that fits, which is a time of day. Related: the same shape as the display teaching
the format.

## The one claim that did the right thing

One of the 361 put the state in the condition field and then set the claim aside when the state
ended:

    statement : Tomas is unwell and staying home on Day 14. He was seen in the kitchen (11:43) and
                bedroom (13:08) during the day, which is unusual as he is typically in the office.
    holds_under: Tomas is unwell.
    standing   : set aside for now      (on day 31, a week after he recovered)

That is the behaviour the whole study is looking for, and it happened once in 361 claims.

## What this means for the question the project started from

Telling the model is not the intervention. The sentence is received, believed and recorded - and
then destroyed by the ordinary nightly pressure to make every claim match today. So more telling,
or telling it louder, is not expected to help, and the accuracy already says it does not: on day
14 the told arms are worse than the same arm untold.

What follows is a design change with a name: **the household's state has to be a thing the memory
holds, separate from the claims, and a claim conditioned on a state must not be narrowed by
evidence gathered in a different state.** Two cheap versions to test:

1. Ask the nightly writer, as its FIRST field, which state the household is in tonight and whether
   it changed - so the state is written before any claim is touched.
2. Refuse the rewording rather than the claim: when a claim's condition names a state and tonight
   is a different state, the model may add a sibling claim but not rewrite that one.

This is also the honest answer to "why would a language model beat remembering the last place you
saw it". A last-seen rule cannot represent a state at all. Our arm can, once in 361 claims, by
accident. The paper's contribution is making that deliberate - and the measurement that shows it is
needed is the erosion above, which is a count, not a difference of means.

## What is not in this file

These six cells read no sighting log, for the reason in
`wave_reasons_first/THE_FIVE_VARIANTS_READ_NO_LOG.md`, so their accuracy is not comparable with our
method as published. The reruns with the log are queued. Nothing above depends on accuracy: it is a
count of what the claims say and when they stopped saying it.

## Written before the profile arm runs: what would make it a dud

Two days of it on hh_s2, before the three real cells started. The profiles fill out fast - 90
characters on night 0, 400 by night 1 - and they do read like profiles of people:

    Tomas: Works from home. Day: office (08:58-15:55). Evenings: living (18:26), office (22:59).
           Items: laptop/mouse/notebook/pen on office desk. Charger/water bottle/mug move to
           bedroom/kitchen in evening. Gym bag on bedroom floor.

But look at the second half of it. The prompt says in as many words that **a profile is not a list
of where things are**, and by night 1 half of Tomas's profile is a list of where things are. So the
prediction, written now rather than after the numbers:

**If the profile becomes a second copy of the notes, this arm is our arm with a longer prompt and
it will measure nothing.** The test is not accuracy. It is whether any profile ever names a state
that is not a placement - somebody being unwell, away, busy - and whether it stops naming it when
it stops being true. That is the one behaviour a claim store did once in 361 claims by accident.

This is the third time the same thing has happened in this project: a field is offered, it gets
filled, and it gets filled with the easiest thing that fits rather than the thing it was for. The
note limit was spent on places, `holds_under` was spent on times of day, and the profile is being
spent on placements. If it happens again here, the finding is about the format teaching the model
what to write, and no amount of clearer instruction is the answer - the memory has to make the
cheap thing impossible, not merely discouraged.
