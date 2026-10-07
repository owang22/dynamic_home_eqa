# night_shift_v1 — a late shift for ten days, built as a negative control

**FAILS six checks, which is what it was built to do, and it fails cleanly.** Table:
`check.txt`, numbers: `check.json`.

## What changes in the household

One resident moves onto a late shift for ten days: home in the morning, out from early
afternoon until eleven at night. Nothing is told to go anywhere new — there is no event,
no new activity and no rule about where anything is put down. The only change is the
resident's timetable, swapped by the simulator's own calendar override, and every
activity keeps the room and the surface it always had.

## What a memory would have to notice

Nothing, if we are right about it. The objects still end up in the same places — the same
bathroom shelf, the same kitchen table, the same nightstand — only at different hours,
and the robot is asked its questions between seven in the morning and eleven at night
either way.

## What actually happened

Exactly that, and more cleanly than the old night-shift scenario the gate's thresholds
were calibrated against. A counting method's accuracy does not fall at the shift at all:
it goes **up** by 0.1 and 2.5 points, where the old `results/regime_search/nightshift`
fell by a weak but real 6.0 and 4.1. Even on the "objects that moved" slice — the
selection-biased one that the coordinator measured a 16-point false break on for the old
version — this one reads **−0.2 points**. And the overnight visibility of the change is
**4%**, against 38% for the illness scenario and 70% for the bathroom refit. As a floor
for the study, this is a better calibrated zero than the one we had.

Which legs it fails, and by how much: no break (+0.1 needed −8.0 for the never-forgetting
learner, +2.5 for the forgetting one), the settled floor by 0.8 (69.2 against 70), the
settled climb by 2.3 (+7.7 against +10), the re-learning by 1.0 (+4.0 against +5), and
the visibility check. One household out of ten shows the full four-phase shape, against
five for illness_v1.

## THE THING THE VALIDATOR SHOULD KNOW ABOUT ITSELF

**This scenario passes the "break again" leg, at −7.6 points against a −5 bar, while
having no first break at all.** The forgetting learner's accuracy rises straight through
the whole disruption — 61.5%, 69.2%, 71.7%, 75.7% — and then drops 7.6 points on the
first two days back to normal. The objects that never moved drop 7.0 points at the same
moment, so it is not the moved ones carrying it. The explanation is that a shift worker's
weekday is *simpler* than an ordinary one — no cooking, no dinner, fewer free slots — so
the learner does better during the shift and worse when the ordinary week comes back.

The consequence for the gate: **the fourth leg on its own does not show that a scenario
contains a learnable disruption.** It can be produced by a spell that is merely easier to
predict. That matters directly, because illness_v2 was rejected on that one leg and
nothing else, and it is the one leg a scenario with no disruption in it can pass. The
gate as a whole is not fooled — it rejects this scenario six ways — so the answer is not
to change the bar but to stop reading the fourth leg in isolation: it should be reported
alongside the stayed-put slice, which is what reveals the artefact here.
