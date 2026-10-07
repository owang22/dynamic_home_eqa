# Study 4: the rare-mover banks and the no-model baseline on them

Written 2026-10-02 by sim-builder-rare-things; rebuilt the same day on the coordinator's
instruction (questions concentrated in the first hour after each move; two question loads). What
the generator does and why is in `FINDINGS_generator.md`; what changed in the banks is in
`results/self_improve/varied_homes/rare_movers/README.md`; the commands for the memory methods
are in `LAUNCH_COMMANDS.md`. No model was called.

## What was added

* `src/situation_sim/rare_movers.py` (new, the only change under `src/`): `add_rare_movers`
  (a post-pass over a finished simulation) and `rare_mover_questions`. Existing generator files
  unchanged.
* `results/self_improve/varied_homes/rare_movers/`: `rare_movers_v1.yaml`, `make_rare_movers.py`,
  `banks/` (ordinary 24 a day) and `banks_8_a_day/` (ordinary 8 a day, the ten-home 8-a-day
  cells' ids), a `*_rare_moves.json` side file beside each bank, `README.md`,
  `check_scenario_output.txt`, `check_scenario.json`, `build_summary.json`.
* `results/self_improve/wave_rare_movers/` (24 a day) and `results/self_improve/wave_rare_movers_8_a_day/`
  (8 a day): `cells/last_seen_no_model/<home>/` for all ten homes (every question asked), `logs/`;
  the 24 folder also has `check_same_household.py` and its output; the 8 folder has the prepared
  `launch_memory_methods.sh`, `run_no_model_rules.py` and the cells of the two extra no-model rules
  (`most_frequent_no_model`, `same_time_of_day_no_model`).
* here: `score_rare_movers.py`, `visible_cause_check.py`, `RESULTS_rare_movers_last_seen_24.json`,
  `RESULTS_rare_movers_no_model_rules_8.json` (all four rules on the rebuilt 8-a-day set; the earlier per-arm
  8-a-day JSONs were superseded by the rebuild and removed), `RESULTS_visible_cause_24.txt`,
  `RESULTS_visible_cause_8.txt`, `PROMPTS_seen_by_the_arm.md`, `LAUNCH_COMMANDS.md`.

Built: the pill box (medication) and the car keys. Not built: the reading glasses, because every
calendar day is a weekday, so the only non-working days are the sick days and the glasses would be
either a daily mover or a copy of the illness movers.

## Questions, per home

| home | place changes (pill box + keys) | added q | within 24 h | in the first hour | ordinary q, 24 set | ordinary q, 8 set |
|---|---|---|---|---|---|---|
| hh_s2 | 2 + 8 | 86 | 69 | 49 | 744 | 248 |
| hh_s19 | 2 + 7 | 76 | 63 | 45 | 744 | 248 |
| hh_s20 | 2 + 8 | 87 | 70 | 50 | 744 | 248 |
| hh_s32 | 2 + 4 | 71 | 42 | 30 | 744 | 248 |
| hh_s48 | 2 + 8 | 84 | 66 | 47 | 744 | 248 |
| hh_s63 | 2 + 5 | 65 | 49 | 35 | 744 | 248 |
| hh_s93 | 2 + 5 | 56 | 42 | 30 | 743 | 248 |
| hh_s109 | 2 + 7 | 88 | 63 | 45 | 744 | 248 |
| hh_s123 | 2 + 6 | 79 | 53 | 37 | 744 | 248 |
| hh_s151 | 2 + 8 | 86 | 66 | 46 | 744 | 248 |

## Checks made on the way

* The base simulation reproduces the stored varied_v2 run row for row, and the ordinary questions
  are the ten-home bank's field for field, on all ten homes (the build stops otherwise).
* Each rare mover's place over the month was printed beside the events that moved it: every move
  is one minute after the resident's own row puts them in the room where the object lands.
* Scenario checker: WORTH RUNNING, every check passed; one warning, the standing one the ten-home
  banks also carry (verdict one class deep on `glass`). Nothing to fix.
* Same household: last-seen replayed on the 24 set with the added questions removed is identical
  to the ten-home 24-a-day last-seen cell on every search of every home (744 of 744; hh_s93 743).
* The unseen flag: `asked_before_any_sighting_at_new_place` is computed from the cell's
  `looks.jsonl` (no sighting of the object at its new place between the move and the question).
  The search row's `times_seen_there_before` was tried first and is wrong for these objects: it
  counts sightings at that place over the whole month, and the keys go back and forth between the
  same two or three spots (the pill box returns to its usual place), so it called a question
  "seen" when the robot had last seen the keys on that table a week earlier. With the looks-based
  flag the seen slice is 100% for last-seen at both loads, as it must be.

## Last-seen, first guess right (found_at_step == 1), every question asked

(The 8-a-day table in this section is from the banks BEFORE the random background questions were added; the
final 8-a-day numbers are in the last section.)

Ordinary load 24 a day (`wave_rare_movers`):

| home | rare-move q | unseen | 1st right | seen | 1st right | 1st after move | 1st right | ordinary q | 1st right | ten-home 24/day, same ids | this cell, same ids |
|---|---|---|---|---|---|---|---|---|---|---|---|
| hh_s2 | 69 | 19 | 0.0 | 50 | 100 | 10 | 0.0 | 744 | 85.9 | 89.0 | 85.9 |
| hh_s19 | 63 | 12 | 16.7 | 51 | 100 | 9 | 22.2 | 744 | 88.0 | 88.0 | 88.0 |
| hh_s20 | 70 | 17 | 0.0 | 53 | 100 | 10 | 10.0 | 744 | 86.3 | 85.2 | 86.3 |
| hh_s32 | 42 | 15 | 0.0 | 27 | 100 | 6 | 0.0 | 744 | 91.3 | 90.3 | 91.3 |
| hh_s48 | 66 | 12 | 8.3 | 54 | 100 | 10 | 20.0 | 744 | 86.3 | 81.9 | 86.3 |
| hh_s63 | 49 | 10 | 0.0 | 39 | 100 | 7 | 0.0 | 744 | 77.2 | 76.6 | 77.2 |
| hh_s93 | 42 | 6 | 0.0 | 36 | 100 | 7 | 28.6 | 743 | 93.5 | 93.4 | 93.5 |
| hh_s109 | 63 | 11 | 0.0 | 52 | 100 | 9 | 11.1 | 744 | 86.3 | 85.9 | 86.3 |
| hh_s123 | 53 | 7 | 0.0 | 46 | 100 | 8 | 12.5 | 744 | 91.5 | 91.0 | 91.5 |
| hh_s151 | 66 | 9 | 22.2 | 57 | 100 | 10 | 30.0 | 744 | 83.6 | 81.9 | 83.6 |
| pooled | 583 | 118 | 4.2 | 465 | 100 | 86 | 14.0 | 7439 | 87.0 | 86.3 | 87.0 |

Unseen slice: 118 questions (76 of the 86 first-after-move questions are unseen); mean of
households 4.7, SE 2.6; pill box 0/20, car keys 5/98; 30.3 room visits a day.

Ordinary load 8 a day (`wave_rare_movers_8_a_day`):

| home | rare-move q | unseen | 1st right | seen | 1st right | 1st after move | 1st right | ordinary q | 1st right | ten-home 8/day, same ids | this cell, same ids |
|---|---|---|---|---|---|---|---|---|---|---|---|
| hh_s2 | 69 | 15 | 0.0 | 54 | 100 | 10 | 0.0 | 248 | 82.3 | 83.1 | 82.3 |
| hh_s19 | 63 | 21 | 4.8 | 42 | 100 | 9 | 11.1 | 248 | 79.0 | 78.2 | 79.0 |
| hh_s20 | 70 | 23 | 0.0 | 47 | 100 | 10 | 0.0 | 248 | 81.0 | 77.4 | 81.0 |
| hh_s32 | 42 | 11 | 0.0 | 31 | 100 | 6 | 0.0 | 248 | 87.9 | 84.7 | 87.9 |
| hh_s48 | 66 | 26 | 0.0 | 40 | 100 | 10 | 0.0 | 248 | 81.0 | 80.6 | 81.0 |
| hh_s63 | 49 | 18 | 0.0 | 31 | 100 | 7 | 0.0 | 248 | 73.0 | 91.9 | 73.0 |
| hh_s93 | 42 | 11 | 0.0 | 31 | 100 | 7 | 14.3 | 248 | 88.3 | 87.1 | 88.3 |
| hh_s109 | 63 | 25 | 0.0 | 38 | 100 | 9 | 0.0 | 248 | 78.2 | 78.6 | 78.2 |
| hh_s123 | 53 | 10 | 0.0 | 43 | 100 | 8 | 12.5 | 248 | 86.3 | 85.1 | 86.3 |
| hh_s151 | 66 | 15 | 0.0 | 51 | 100 | 10 | 0.0 | 248 | 74.6 | 74.2 | 74.6 |
| pooled | 583 | 175 | 0.6 | 408 | 100 | 86 | 3.5 | 2480 | 81.2 | 82.1 | 81.2 |

Unseen slice: 175 questions (83 of the 86 first-after-move questions are unseen); mean of
households 0.5, SE 0.5; pill box 0/32, car keys 1/143; 13.0 room visits a day.

Reading the ordinary columns: the household is the same (exact replay above), but the added
searches change when last-seen looks, and its rule depends on that. hh_s63 at 8 a day drops 19
points on the same ids because its searches for the keys open the kitchen at off-moments and
leave stale kitchen sightings of mugs and glasses that are asked about at the dining table.
Pooled the effect is +0.7 (24) and -0.9 (8).

Why the unseen slice is only 1.4 to 2 questions per move even with five questions in the first
hour: last-seen's first search after a move finds the object within its three rooms about nine
times in ten, and every later question is then "seen". A bigger unseen slice needs more moves,
not more questions per move (the bank's `arrivals_per_week` setting), or a wider first window
(`first_window_minutes`) so some first questions come after the robot has been elsewhere.

## Is the cause in the robot's record before it is asked? (`visible_cause_check.py`)

For every place change: the first unseen question, the looks between the move and that question,
and whether any of them shows the cause. Detail for hh_s2 and hh_s63 is in
`RESULTS_visible_cause_8.txt` / `_24.txt`; the counts over all ten homes:

| load | place changes | with an unseen question | looks between move and first unseen q (mean) | cause seen strictly (resident in the cause room) | resident seen anywhere at home | resident seen in the cause room in the 24 h before the move |
|---|---|---|---|---|---|---|
| 8 a day | 86 | 83 | 0.1 | 1 (pill box 1, keys 0) | 1 | 21 (pill box 1, keys 20) |
| 24 a day | 86 | 76 | 0.2 | 0 | 0 | 25 (pill box 3, keys 22) |

Over every unseen question, not just the first after each move (8 a day): 159 in the first hour,
3.5 looks since the move on average, cause seen strictly 1, resident seen anywhere 10; 16 later
than the first hour, 18.8 looks since the move, strictly 0, resident seen anywhere 12. At 24 a
day: 114 first-hour (strictly 0, anywhere 1), 4 later (strictly 0, anywhere 2).

What the hh_s2 detail shows: the pill box moves at 08:06 on day 14, one minute after Tomas starts
his dose in the bedroom; the first unseen question is at 08:09, with no look in between; the
robot had not seen Tomas resting on any sick day yet because there had been none. The keys land
at 16:35 on day 1 one minute after Ines sits down in the living room; the first unseen question
is at 16:41, no look in between. The same for every move printed.

So on the first question after a move the cause is not in the robot's record: the question comes
one to eleven minutes after the move and the robot has not looked anywhere. A method can beat
last-seen on that question only by predicting the move from the routine (that Ines is back from
the gym around 16:30 and sits in the living room; that the ill resident keeps the pill box by the
bed), not from having seen the cause. The questions where the cause is in the record and the
object is not (the resident seen somewhere else at home after the move) are the later unseen
ones, and there are 12 to 16 of them in the whole ten-home set at 8 a day, because once the robot
opens the cause room it sees the object too. Two levers if the study wants that slice larger:
`first_window_minutes` (push the first questions to, say, 30-120 minutes after the move) and
`arrivals_per_week` (more key moves). Both are settings in `rare_movers_v1.yaml`; the base
simulation and the ordinary questions do not change.

## Two more no-model rules on the 8-a-day set (the bar for the memory methods)

Added 2026-10-02 on the coordinator's instruction. Both run the last-seen search loop (three rooms,
answer with the newest sighting, no notes, no model) and differ only in the FIRST room they open;
later rooms on the same search follow last-seen's order. Patched onto the module in-process by
`results/self_improve/wave_rare_movers_8_a_day/run_no_model_rules.py` (the route
`paper/scripts/last_seen_without_the_first_illness.py` used), so each has its own `looks.jsonl`;
cells under `results/self_improve/wave_rare_movers_8_a_day/cells/most_frequent_no_model/` and
`.../same_time_of_day_no_model/` (a `RULE.txt` in each cell says what ran). A sighting is one look
that found the object in a room.

* **most frequent**: the room where this robot's own earlier sightings of the asked object are most
  numerous, ties by the most recent sighting; nothing seen yet, last-seen's order (fired on 325 of
  334 searches in hh_s2).
* **same time of day**: the room where its earlier-day sightings of the object within one hour of
  the current clock time are most numerous, ties by recency; none, last-seen's order (fired on 297
  of 334 in hh_s2).

First guess right, %, ordinary load 8 a day, every question asked; the unseen flag is each cell's own
(computed from its looks), so the unseen counts differ slightly between arms.

**most frequent**

| home | rare-move q | unseen | 1st right | seen | 1st right | 1st after move | 1st right | ordinary q | 1st right | ten-home 8/day, same ids | this cell, same ids |
|---|---|---|---|---|---|---|---|---|---|---|---|
| hh_s2 | 69 | 15 | 13.3 | 54 | 51.9 | 10 | 20.0 | 248 | 77.0 | 83.1 | 77.0 |
| hh_s19 | 63 | 21 | 19.0 | 42 | 52.4 | 9 | 33.3 | 248 | 78.6 | 78.2 | 78.6 |
| hh_s20 | 70 | 23 | 13.0 | 47 | 46.8 | 10 | 30.0 | 248 | 76.6 | 77.4 | 76.6 |
| hh_s32 | 42 | 11 | 18.2 | 31 | 58.1 | 6 | 33.3 | 248 | 83.9 | 84.7 | 83.9 |
| hh_s48 | 66 | 26 | 15.4 | 40 | 52.5 | 10 | 40.0 | 248 | 68.5 | 80.6 | 68.5 |
| hh_s63 | 49 | 18 | 16.7 | 31 | 58.1 | 7 | 42.9 | 248 | 79.8 | 91.9 | 79.8 |
| hh_s93 | 42 | 11 | 9.1 | 31 | 51.6 | 7 | 28.6 | 248 | 76.6 | 87.1 | 76.6 |
| hh_s109 | 63 | 25 | 8.0 | 38 | 44.7 | 9 | 22.2 | 248 | 81.9 | 78.6 | 81.9 |
| hh_s123 | 53 | 10 | 20.0 | 43 | 48.8 | 8 | 37.5 | 248 | 82.3 | 85.1 | 82.3 |
| hh_s151 | 66 | 14 | 28.6 | 52 | 55.8 | 10 | 40.0 | 248 | 64.5 | 74.2 | 64.5 |
| pooled | 583 | 174 | 15.5 | 409 | 51.8 | 86 | 32.6 | 2480 | 77.0 | 82.1 | 77.0 |

**same time of day**

| home | rare-move q | unseen | 1st right | seen | 1st right | 1st after move | 1st right | ordinary q | 1st right | ten-home 8/day, same ids | this cell, same ids |
|---|---|---|---|---|---|---|---|---|---|---|---|
| hh_s2 | 69 | 11 | 27.3 | 58 | 43.1 | 10 | 30.0 | 248 | 85.1 | 83.1 | 85.1 |
| hh_s19 | 63 | 20 | 15.0 | 43 | 48.8 | 9 | 22.2 | 248 | 89.9 | 78.2 | 89.9 |
| hh_s20 | 70 | 27 | 11.1 | 43 | 48.8 | 10 | 30.0 | 248 | 81.5 | 77.4 | 81.5 |
| hh_s32 | 42 | 11 | 9.1 | 31 | 45.2 | 6 | 16.7 | 248 | 85.5 | 84.7 | 85.5 |
| hh_s48 | 66 | 26 | 11.5 | 40 | 50.0 | 10 | 30.0 | 248 | 83.1 | 80.6 | 83.1 |
| hh_s63 | 49 | 18 | 11.1 | 31 | 45.2 | 7 | 28.6 | 248 | 91.1 | 91.9 | 91.1 |
| hh_s93 | 42 | 11 | 9.1 | 31 | 51.6 | 7 | 28.6 | 248 | 82.7 | 87.1 | 82.7 |
| hh_s109 | 63 | 25 | 12.0 | 38 | 34.2 | 9 | 33.3 | 248 | 83.9 | 78.6 | 83.9 |
| hh_s123 | 53 | 10 | 10.0 | 43 | 51.2 | 8 | 25.0 | 248 | 89.5 | 85.1 | 89.5 |
| hh_s151 | 66 | 15 | 20.0 | 51 | 51.0 | 10 | 30.0 | 248 | 84.7 | 74.2 | 84.7 |
| pooled | 583 | 174 | 13.2 | 409 | 46.9 | 86 | 27.9 | 2480 | 85.7 | 82.1 | 85.7 |

**Paired per-household difference against last-seen (same homes, each arm's own unseen slice), points:**

| rule | unseen slice: mean | SE | 2 SE | first question after each move: mean (SE) | ordinary questions: mean (SE) |
|---|---|---|---|---|---|
| most frequent | +15.7 | 1.9 | 3.7 | +29.0 (3.1) | -4.2 (2.0) |
| same time of day | +13.1 | 1.9 | 3.7 | +23.6 (2.8) | +4.5 (2.2) |

Both beat last-seen on the unseen slice in every one of the ten homes (most frequent +8 to +29,
same time of day +9 to +27). They pay for it on the seen slice (about 50% against last-seen's
100%, because they do not open the room of the newest sighting first) and most-frequent pays on
the ordinary questions too (-4.2); same-time-of-day is the only one of the three above last-seen
on the ordinary questions (+4.5, 2 SE 4.4, at the edge).

**On the unseen slice the best of the three rules is most frequent, 15.5% pooled (last-seen 0.6%,
same time of day 13.2%); that is the bar the memory methods must beat there.**

## Final no-model bars on the rebuilt 8-a-day set (plan critic's batch, 2026-10-02)

The 8-a-day banks were rebuilt with background questions at random times when the object had not
moved in 24 h, as many per home as the first-hour burst (flag `rare_mover_background_random`,
30-50 per home), so a question about a rare mover no longer means it just moved. The 24-a-day set
is kept but dropped for the model arms (its seen slice saturates). All four no-model rules were
rerun on the rebuilt set; a fourth rule, **alternate room** (first room = the room where the
object was sighted most often this month excluding the room it was last seen in; then last-seen's
order), was added in `run_no_model_rules.py`.

`score_rare_movers.py` now scores every arm in one table. **Main score** (arm-independent unit):
first guess right on the first question after each place change, one row per move, 86 per load,
unseen for last-seen on 83 of 86; paired per household against last-seen, SE over households.
Secondary, per question and per arm: unseen, after a miss (unseen questions that follow a failed
search since the move), seen, background, ordinary. A cell without its completion marker
(cell.json with a per_day row for every day) is refused by name.

First guess right, %, pooled over ten homes:

| rule | first after move (86) | unseen | after a miss | seen | background (414) | ordinary (2480) | ten-home 8/day same ids |
|---|---|---|---|---|---|---|---|
| last-seen | 3.5 | 0.5 (190) | 0.9 (107) | 100.0 (393) | 97.8 | 81.0 | 82.1 |
| alternate room | 44.2 | 21.0 (186) | 1.0 (103) | 2.5 (397) | 31.9 | 63.7 | 82.1 |
| most frequent | 33.7 | 14.8 (189) | 0.9 (106) | 50.0 (394) | 72.7 | 75.3 | 82.1 |
| same time of day | 32.6 | 13.6 (191) | 0.9 (109) | 45.2 (392) | 70.5 | 85.1 | 82.1 |

Main score, paired per household against last-seen (points; last-seen per home 0, 11, 0, 0, 0, 0,
14, 0, 12, 0):

| rule | mean diff | SE | 2 SE | per-home % |
|---|---|---|---|---|
| alternate room | +40.0 | 5.7 | 11.5 | 50 33 60 50 40 57 14 33 50 50 |
| most frequent | +29.6 | 2.8 | 5.6 | 40 33 30 33 40 29 29 22 38 40 |
| same time of day | +28.1 | 4.1 | 8.2 | 30 22 40 17 40 43 29 33 25 40 |

Pill box, first question after the move, right / moves: forward (to the bedside) 0/10 for every
rule; return 2/10 last-seen, 8/10 alternate room, 10/10 most frequent, 9/10 same time of day.
Car keys first-after-move: 1/66, 30/66, 19/66, 19/66.

**The bars (best rule, and best + 10):** first after move: alternate room 44.2, bar 54.2. Unseen:
alternate room 21.0, bar 31.0. After a miss: alternate room 1.0, bar 11.0. Seen: last-seen 100
(cannot be beaten). Background: last-seen 97.8 (bar 100). Ordinary: same time of day 85.1, bar
95.1.

Two things to say when the memory arms are read against these: alternate room wins the main score
by exploiting a property of the bank (the keys go back and forth between two or three landing
spots per home, so "the other room" is right often) and pays with 2.5% on the seen slice and 63.7%
on the ordinary questions; and no rule does anything after a miss (about 1%), because the rooms
left after a failed three-room search are the ones nothing points at.

## Prompt leak check

`PROMPTS_seen_by_the_arm.md` (from `dump_prompts_seen_by_the_arm.py`, a dry run of the
log-and-notes arm on hh_s2 with the client in replay-only mode, no server): the day-1 and day-14
nightly prompts and a day-1 and day-14 room-choice and answer prompt. Given but not derived from
looks: the map of rooms and spots, the resident count and names (resolved from the seed; the same
names are on the object ids), the day index and clock. Nothing from the calendar, the stages, the
illness, the schedules, roles, resident cards, hint messages or the asked-object list.

## Could not do

* Reading glasses (see above).
* Any model arm (no vLLM, by instruction). The commands are prepared in `LAUNCH_COMMANDS.md`.
