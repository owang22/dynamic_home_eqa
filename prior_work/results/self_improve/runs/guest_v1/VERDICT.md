# guest_v1 — a guest comes to stay for ten days

**NEAR MISS: six of seven checks pass. It fails the one check that is a floor rather
than a discriminator, by 0.8 of a point.** Table: `check.txt`, numbers: `check.json`.

## What changes in the household

A guest sleeps in the living room for ten days — the only room any of these ten homes
has spare, since a couple shares one bedroom and flatmates have one each. Every evening
the couch is made up as a bed and the coffee table becomes a bedside table, so the
things the household normally leaves there are carried out: the remote and the magazines
go onto a nightstand, the blanket into a wardrobe, the snack bowl onto the armchair, the
tablet onto a dresser, the mugs straight into the sink, and the guitar, the dog's toy
and the board games out of the living room altogether.

## What a memory would have to notice

That the displacement falls on **the hosts, not the guest**. Nothing the guest owns is
tracked, so a disruption that moved only a newcomer's possessions would teach a memory
nothing — the robot never had a belief about those things. What it has to notice here is
that a room it thought it understood has been given away, and that the household's own
possessions have been redistributed into bedrooms it had no reason to look in.

## Why it misses

A counting method with a three-day memory only reaches **69.2%** on the ordinary
fortnight, against a 70% floor: the guest households' settled routine is a shade too
unpredictable to be learnt, and the gate's position is that if the ordinary routine
cannot be learnt then nothing can be lost when it is disrupted. Everything that
discriminates between scenarios passes, and passes well: the break is −9.5 and −9.7
points against a −8 bar, the re-learning is +13.7, and the return costs −8.0, which is
better than the illness scenario we were about to run a fortnight ago.

## Is it fixable

Not by choosing object classes. About a dozen mixes were tried and they trade the floor
against the break one for one: every mix that clears 70% loses the break, and every mix
that keeps the break sits at 68 to 69.

One further attempt was made at the floor itself rather than at the disruption, and it
half-worked. **Asking the robot more often — 32 questions a day instead of 24, with a
20-minute rather than a 30-minute gap between two questions about the same object — gives
a forgetting learner more feedback to learn the ordinary fortnight from, and lifts the
settled level from 69.2% to 72.9%.** The break improves to −10.5 and −11.2 and the return
to −8.3. But the *never-forgetting* learner's re-learning leg then falls to **+4.6 against
a +5.0 bar**, because with more data it has already converged before the disruption starts
and has little left to gain during it. Six of seven either way, failing different legs.

So this scenario sits on the gate from both directions, which makes it a genuine near miss
rather than an unfixed one. The alternative build's full table is saved next to this file
as `check_alt_per32_gap20.txt`. It is **not** the committed run, because 24 questions a day
with a 30-minute gap is what illness_v1, illness_v2, room_shut_v1, wfh_v1 and
night_shift_v1 all use, and changing it for one scenario would make the cross-scenario
table not like for like. If the coordinator would rather have a third passing-shaped
scenario than a like-for-like table, that build is one command away.

## Two artefacts found and removed, worth remembering

The board game and the jigsaw got **zero** questions in the settled fortnight and 26 and
14 during the guest's stay, because the habits that use them only fire on weekend-shaped
days and this calendar has none. An object asked about only during the disruption shows
a break by construction and proves nothing, because the memory never held a belief to
revise. They are out of the question bank; the world still moves them. The knitting, the
guitar, the console and the yoga mat exist in one or two homes out of ten and were
dropped for the same kind of reason: four to eleven questions is noise with a number's
clothes on.
