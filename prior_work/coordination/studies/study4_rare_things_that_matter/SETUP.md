# Study 4, rare things that matter: setup, written before any count

Written 2026-10-02 01:06 PDT by study-lead.

## The question

For things that move rarely but are asked about when they do (medication, keys, glasses), does
any memory method beat last-seen and most-frequent on the questions asked within a day of a rare
move? Last-seen is wrong by construction until the robot happens to see the thing again; a method
can only do better by predicting the move from its cause (who moved, where they went).

## Cheap first: what the existing banks already contain

Before any generator change, count in the ten-household 31-day bank
(`results/self_improve/varied_homes/ten_homes/banks`) and the 50-day bank: for every asked-about
object, how many times its place changes over the month, and how many questions fall within one
day after each change. Objects with at most three changes a month are "rare movers". Then score,
from the existing cells (`overnight_wave`, `wave_the_second_illness`), first guess right on those
questions for last-seen, most-frequent (if a cell exists; else compute it offline from the bank
as the commonest room so far), log and notes, and the other methods present. If the bank already
holds enough rare-move questions (say 30 or more per household), the generator change is not
needed for the screening.

## Baselines to beat

last-seen; most-frequent. Also reported: prior-only (notes hidden) where present, and an oracle
that knows the move (100%), which bounds the room.

## Main score

First guess right on questions asked within one day after a rare move, paired per household.
Secondary: found within three rooms on the same questions; first guess right on all other
questions, to show nothing was traded away.

## Prediction

Last-seen scores low on these questions (under 40%) because by definition it has not seen the
move; most-frequent scores about the same or lower; log and notes scores within 10 points of
last-seen, because nothing in the sightings says where a rarely moved thing went unless the move
is tied to a routine the notes recorded (medication following the ill resident is the one case
where it might). Expected verdict: drop on the existing bank; keep only if the rare moves are
tied to a visible cause, which the generator change would have to build in deliberately, and
that is a design choice to put to Oliver rather than a finding.

## Size and detectable gap

To be filled from the count: n questions per household within one day of a rare move. If n is
under 20 per household, the paired standard error over ten households will be 5 to 8 points and a
10-point gap is at the edge of detection; the generator change would then have to add moves, not
objects.

## What the generator change would be, if needed (sim-builder, not tonight)

Two or three objects per household that move once or twice a month, each move caused by a
resident's action in the calendar (medication goes where the ill person rests; keys go where the
last person to come home put them), and questions about them concentrated in the day after each
move. The cause must be visible in the sightings (the resident is seen in the new place) or no
method can do better than chance.

## Addendum, 01:39 PDT, written after the first build and before the rebuild

The generator change is built (`src/situation_sim/rare_movers.py`; banks under
`results/self_improve/varied_homes/rare_movers/`): a pill box that goes to the ill resident's
nightstand on the first sick day and back on the first well day, and car keys that land where the
driver first sits after each of 6 to 13 trips a month. Reading glasses could not be built (every
calendar day is a working day). The scenario checker passed; the new banks reproduce the old ones
row for row once the added objects are removed; last-seen on the ordinary questions matches the
ten-home cells.

My prediction ("last-seen under 40% on questions within a day of a rare move") was wrong at 24
questions a day: last-seen scores 83%, because the robot opens about 30 rooms a day and sights
the moved thing within hours by chance (in 62 of 86 move windows it was already informed before
the first question). The slice the study is about is the 51 questions asked before any sighting
at the new place: last-seen 3.9% there. At 8 ordinary questions a day the unseen slice is 89 and
last-seen is 1.1% on it.

Revised design, before the rebuild: rare-mover questions concentrated in the first hour after each
move, two question loads (24 and 8 ordinary a day), the unseen slice as the main score, computed
from the robot's own looks. New prediction: the unseen slice reaches 25 to 40 questions per
household; last-seen stays under 10% on it; the raw record plus notes beats last-seen on it only
where the cause was visible in the robot's record before the question (the ill resident seen in
the bedroom; the driver seen in the landing room), which I expect in under half the moves, so its
score on the slice is 15 to 35%, a gap of 10 to 30 points on a slice of about 300 questions over
ten households. That gap, if it appears, is the first keep of the night, and it comes from a
design built tonight, so a plan critic reads it before any model runs.

## Addendum 2, 01:52 PDT, after the rule baselines and before any model run

On the 8-a-day rare-mover banks, unseen slice (175 questions, ten households): last-seen 0.6%,
same time of day 13.2%, **most frequent 15.5%** (beats last-seen in all ten homes, +15.7, 2 SE 3.7).
Most frequent pays for it on the seen slice (52% against last-seen's 100%) and on ordinary
questions (-4.2). The bar for the memory methods on the unseen slice is therefore 25.5%
(most frequent plus 10), and on the seen and ordinary slices they must not fall below last-seen
by more than the noise floor, or the gain is a trade, not a gain.

Prediction for the memory methods (the raw record plus nightly notes; notes hidden as the
control), written before launch: on the unseen slice the raw record plus notes scores 15 to 30%,
because the record shows the keys' landing rooms by time of day much as most-frequent and
same-time-of-day read them, and the model has no sighting of the cause on the first question;
I expect it to land near most frequent and under the 25.5% bar. Notes hidden: under 10%. On the
seen slice and ordinary questions both stay within 3 points of their ten-home values.

## Addendum 3, 01:55 PDT: the pre-committed verdict, after the plan critic and before launch

The plan critic (fresh, 01:53) showed that the unseen slice as scored was not what it seemed:
92 of its 175 questions follow a search that already missed since the move, so any rule that
avoids rooms it just emptied beats last-seen there (last-seen never updates on a miss); the
within-move questions share one fact, so the unit is the move, not the question; and five
questions in a row about the keys are themselves a signal that the keys moved. The design as
built tests a time-and-owner prior ("16:40, Ines's keys, the living room"), not memory of a seen
cause; the better question (cause seen, object not) needs a generator change and is tomorrow's
work, written up in the morning report.

What runs tonight, and how it is judged, fixed now:
- Unit: the move. Main score: first guess right on the first question after each move
  (86 per load, arm-independent), paired per household, SE over ten households. Detectable gap
  about 10 points. This is a screen, not a finding; all ten homes share one scenario setting.
- Bar: the best of last-seen, most frequent, same time of day and alternate room on that unit,
  plus 10 points. On the pre-rebuild banks most frequent was 32.6% on this unit; alternate room
  is expected higher on the keys (two or three landing spots) and 100% on the pill box's return.
- Arm it must beat besides the rules: notes hidden (prior only), because the object's name
  carries the owner and a model with no record can guess "the owner's bedroom".
- Not traded away: on the seen slice and the ordinary questions, within the rerun floor of
  last-seen on this same bank (never the ten-home cells).
- Rerun floor: log-and-notes rerun on two households with the same seed; a gap inside that
  spread is nothing.
- The pill box is scored separately (forward and return) as counts and is outside the verdict.
- Rare-mover questions at random non-move times are added so a keys question does not by itself
  mean a move; their accuracy is reported.
- 24-a-day load dropped for the model arms (its seen slice saturates); files kept.

Prediction, restated for this unit: on the first question after each key move, the raw record
plus notes scores 25 to 45%, within 10 points of the best rule; notes hidden 15 to 35% from the
owner prior alone. Expected verdict: drop, with the design-B question handed to Oliver.
