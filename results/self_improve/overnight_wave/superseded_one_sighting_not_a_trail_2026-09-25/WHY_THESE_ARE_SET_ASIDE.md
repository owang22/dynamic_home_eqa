# The old `newest sighting, no model` cells: set aside on 2026-09-25, not deleted

These ten cells ran an arm called "newest sighting, no model" that kept **one** sighting per
object, overwritten every time the object was seen again. Its first guess was the room the
object was last seen in. From the second guess on it had nothing left: that room had just been
opened and removed, so it fell through to the room where things of the same class were last
seen, and then to a random room.

Measured over 7,439 searches at 24 questions a day in ten homes of 8 or 9 rooms:

| | found | share of the guesses made |
|---|---|---|
| room 1 | 6,107 | 82.1% of searches |
| room 2 | 178 | 13.4% of 1,332 |
| room 3 | 172 | 14.9% of 1,154 |

With seven or eight rooms left a blind pick is right about 13%, and with six or seven about
15%. So the second and third guesses were chance. The arm named "last seen" was one good guess
followed by a random walk, and every arm compared against it on *found within the budget* was
being compared against something weaker than the name says.

The replacement, `last seen, no model`, keeps the whole trail: every room the object has been
seen in, newest first, one entry per room, and guess k is the k-th most recent room not yet
opened. On hh_s2_t03 at 24 questions a day, on the identical question set:

| | one sighting only | the whole trail |
|---|---|---|
| first room right | 86.6% | 89.0% |
| second guess right | 12 of 100 (12.0%) | 44 of 82 (53.7%) |
| never found in 3 rooms | 71 (9.5%) | 31 (4.2%) |
| exact place right | 90.5% | 95.8% |

The first room improves as well, which is not a mistake: finding the object more often means
the record of where it has been seen is better, so later first guesses are better too.

**Nothing here is wrong as a record of what that rule does.** It is set aside because the name
promised a rule that the code only followed on the first guess, and because the new arm is the
fair opponent for a memory - the memory has to beat remembering, not beat remembering once.
The directory name is not reused: no folder under `cells/` holds two different rules under one
name. Read `search_driven.LAST_SEEN` for the rule that replaced it.
