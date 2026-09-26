# What we can say, as of the evening of 2026-09-25

Written because the headline we had been carrying is not what the data says. Each claim names the
population it rests on and the bar it clears. Where a claim does not clear its bar, it says so.

The two waves are NOT two samples of one thing and are never pooled. At 8 questions a day the
robot makes **9.0 to 10.7 looks a day**; at 24 it makes **25.6 to 30.5**. Three times the
questions is three times the looking, so the question count is the observation budget and the
difference between the waves is a treatment, not a resolution setting.

  * the ten-household wave, 8 questions a day, all arms complete - every number with a standard
    error comes from here
  * the three-household wave, 24 a day - curves inside one home, and the only place the two
    published methods exist

---

## 1. No memory design anticipates a latent shift, and all of them recover in about four days

Movers only, first room right, ten households, paired within household. Settled is days 8-13.

| arm | settled | day 14 | day 15 | day 16 | day 17 | day 18 | points lost per day, 14-23 |
|---|---|---|---|---|---|---|---|
| ours | **82.8%** | 34.0% | 65% | 66% | 91% | 132% | 13.4 |
| LastSeen, no model | 79.1% | 33.5% | 48% | 50% | 58% | 104% | 16.6 |
| the plain claim store | 64.5% | 36.0% | 20% | 116% | 115% | 144% | 13.1 |
| our first ACE | 66.1% | 31.5% | 17% | 104% | 119% | 120% | 12.9 |
| our first MemGPT | 63.1% | 36.8% | 44% | 116% | 61% | 89% | 20.7 |

Day 15 onward is the share of that arm's OWN lost ground recovered, so 100% is back to its own
settled level. Every arm falls to between 31.5% and 36.8% on the first changed day. None could do
better: the new routine is unobserved until it is observed.

**The claim we had been making is wrong.** "Existing methods adjust but not as fast as ours" is
not supported. Relative to their own baselines the weaker arms recover FASTER - the plain claim
store is back past its settled level by day 16 while ours takes until day 18 - because they had
less to lose. Our advantage is a LEVEL advantage, the same before, during and after.

The one speed claim that holds is against LastSeen: 48% against our 65% on day 15, 58% against
91% on day 17, 16.6 points lost a day against 13.4. A rule that only remembers where a thing was
has to see each thing again; a memory that has worked out why things moved can generalise from
the first few sightings. That is the mechanism worth writing about, and it shows against the
honest baseline rather than against the published designs.

## 2. A rule with no language model beats all three published memory designs

Ten households, 2,456 questions, identical question sets in every arm, 8 a day.

| arm | first room right | found within 3 rooms |
|---|---|---|
| ours | **85.5%** | **96.6%** |
| **LastSeen, no model anywhere** | **82.0%** | **95.0%** |
| the plain claim store | 76.8% | 86.8% |
| our first ACE | 75.9% | 85.3% |
| our first MemGPT | 70.9% | 82.0% |
| notes hidden at choice time | 53.4% | 65.8% |

Paired within household, against 2 standard errors and the rerun noise floor (1.9 points on first
room, 2.2 on found-in-budget):

  LastSeen - plain claim store   +5.1 / +8.2   both clear
  LastSeen - our first ACE       +6.1 / +9.7   both clear
  LastSeen - our first MemGPT   +11.1 / +12.9  both clear
  ours - LastSeen                +3.5 / +1.5   NEITHER clears; +1.5 is under the 2.2 floor

LastSeen also does not sag during the shift: 81.1, 81.8, 84.1 across the three windows.

**This is the strongest and least comfortable thing we have.** It only became true today: the
comparator used to keep ONE sighting per object, so it followed its own rule on its first guess
and picked at random after that - 13.4% of second guesses right against 13-15% for a blind pick.
Keeping the whole trail gained it 13.1 points of found-in-budget at 8 a day and 9.5 at 24.

## 3. None of these memories represents the shift. They record its consequences

Day 31, a week after recovery. A note counts when it names an object and the plain words of the
place that object went to DURING the illness, both read from the bank, not from text.

| arm | live notes | describing an illness place | set aside | mentioning the illness |
|---|---|---|---|---|
| the plain claim store | 595 | 156 | **0** | **0** |
| our first ACE | 334 | 103 | **0** | **0** |
| ours | 471 | 131 | **0** | **0** |
| our first MemGPT | 101 | 38 | **0** | **0** |

**428 notes describe where things went while somebody was ill and none of them mentions that
anybody was ill.** The condition attached is a time of day - 74 say the placement holds `always`,
the rest say `evening`, `afternoon`, `general observation`, `Felix is at home`. None is set aside,
so all are offered as current belief a week after they stopped being true.

Read alongside the reasoning traces, the mechanism is visible: faithful ACE tracks the shift by
moving a time threshold, night after night, from 20:00 to 13:00 to 11:47, until its note says the
charger is on the bed "in the evening (11:47+)". It has redefined late morning as the evening
rather than concluding that somebody is at home during the day.

So a memory here cannot transfer what it learned to a second spell, because it never encoded a
spell. This is the claim closest to the question the project started from.

## 4. Two mechanism results about the published methods, from their own records

**MemGPT as published freezes.** Its 20,000-character block fills to about 19,900 and then
refuses writes - on two of three households **every night from 19 or 20 through to 31**, the whole
recovery window. Its archive held **0 passages at every point in every cell**: the overflow
mechanism fires constantly and the model never once evicts. It also quoted a piece of its own
block that was not there 3, 7 and 9 times, and it is the only arm in the study that ever emitted
malformed output - 2 of 96 nights against 0 of 1,920 for every other arm that writes at night.
Our 1,200-character version refused twice in 320 nights, so the tight variant never tested the
mechanism at all.

**ACE as published merges beliefs about different objects.** 16 of its 26 folds (62%) joined
claims with no object in common - a mug into a water bottle, that into a glass, with the model
noting the objects differed and arguing past it. The surviving claim inherits the absorbed one's
"this helped" tallies, so 11 to 20% of its live claims hold 22 to 62% of all the credit, and those
tallies are what its reflection step reads the next night. Our own claim store does this too on
the model's path (7 of 85 folds); our three guards exist only on the deterministic backstop, whose
own record is clean at 22 of 22. So the guard works where it is applied and is not applied where
the model acts - a bug in our code, found through their method.

## 5. Limits we state rather than discover later

**The movers are not independent.** Day by day, the objects that move agree strongly, and the
agreeing set is always one household's ill resident - in one home six of eight movers are one
person's things, all switching on days 14 and 15. The effective number of independent movers per
household is **2.4 to 2.9**, so an object-level standard error over movers is about 1.7 times too
narrow. Cluster by household, which is the right unit because the correlated set is one
household's resident. Widening the object list does not fix this (2.65 to 2.89 with twice the
kinds): the cause is one event, one day, one person. What clustering does not absorb is that the
destinations live in one event file, so a per-kind effect is a sample of one however many homes run.

**Our arm's note limit binds.** A flat 16 notes a night was reached on 27% of nights at 24
questions a day and a third of the disrupted ones, while the control's limit is counted from what
the night saw and ran 21 to 97. On those nights our arm could not do what the control did. The
test - our arm on the counted limit, nothing else changed - is running on three households now.

**The questions are narrow.** Eleven object kinds of the 143 the generator knows, 40-55% of them
drinkware, decided by one line in a scenario file inherited from earlier work. The robot sees 57
objects a month and is quizzed on 11; a snack bowl seen in eight places and a blanket that moves
between couch, armchair and bed are in the record and never scored. A wider version exists and
passes every gate (drinkware 42.1% to 22.9%, asked objects nearly doubled) and has not been run.
