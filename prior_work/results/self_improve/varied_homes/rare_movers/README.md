# rare_movers_v1: the ten pilot homes with two rare movers that have a visible cause

Built 2026-10-02 by `make_rare_movers.py` in this folder from `rare_movers_v1.yaml`; the new
generator option is `src/situation_sim/rare_movers.py`. For study 4
(`coordination/studies/study4_rare_things_that_matter/`).

## What is the same as `ten_homes/banks`

Everything the base generator does. The ten households (hh_s2, s19, s20, s32, s48, s63, s93,
s109, s123, s151; seeds, residents, rooms, objects), the calendar (lead 0-13, sick 14-23 with
`unwell_spell` on resident_1, return 24-31), the activities and events files, every existing
object's trajectory, every resident row, and the ordinary 24 questions a day. The build stops
if any of this differs: it compares the base truth and resident rows with the stored varied_v2
simulation row for row, and the base question rows with the ten-home bank field for field.
Replaying last-seen on these banks with the added questions removed reproduces the ten-home
24-a-day last-seen cell search for search on all ten homes
(`results/self_improve/wave_rare_movers/check_same_household.txt`).

## What was added

Two objects per home, appended after the base simulation finished (they never go through the
placement rule, so nothing else moves differently):

* `pill_box_<ill resident>` (class `pill_box`), owned by the resident who falls ill. Usual place:
  the kitchen counter or the bathroom medicine cabinet (one seeded draw per home). On day 14 it
  moves to that resident's nightstand one minute after they start their first bedroom activity
  of the day (the morning dose); on day 24 it goes back one minute after their first activity
  outside the bedroom (up and about again). Two moves a month.
* `car_keys_shared` (class `car_keys`). Starts on the entry table. One to three times a week
  (seeded draw per 7-day week) one resident's trip out (errands, groceries, gym, lunch out,
  work, classes, a shift, or a visit) is a car trip: the keys go OUT_OF_HOUSE with them and,
  one minute after the resident is recorded back in a room, land where that person first sits:
  the living-room coffee table if they settle there before their next activity, otherwise the
  surface of that next activity (kitchen counter or table, desk, dining table; never a floor).
  They stay there until the next car trip. 6 to 13 car trips a month, 4 to 8 of which change
  the keys' place (the rest bring them back to the same spot).
* Reading glasses were asked for and NOT built: every calendar day is a weekday, so the only
  non-working days are the sick days; the glasses would be a daily mover or a copy of the
  illness movers, not a rare mover.

The cause of every move is visible to the robot in the way the harness already shows people:
when it opens the room it lists the residents there (`FrozenHousehold.residents_in_room`), and
each move is placed one minute after the resident's own row puts them in that room.

## Questions

The ordinary questions are unchanged (ids `d{day}q{nn}`). Two bank sets differ only in how many
of them a day they carry:

* `banks/`: the ten-home bank's 24 a day (744 per home).
* `banks_8_a_day/`: 8 a day, picked from those 24 with the harness's own even spacing
  (`search_driven.questions_spread_across_the_day`), so the ids are exactly the ones the ten-home
  8-a-day cells (`overnight_wave`) asked (248 per home).

The added rows (ids `d{day}r{nn}`, `moment: rare_mover`) are the same in both sets: after each
place change, five stratified over the first hour (10-minute minimum spacing) and two over the
rest of the 24 hours, plus background questions at random waking times when the object has NOT
moved in the last 24 hours, as many per home as the first-hour questions (flag
`rare_mover_background_random`), so that a question about a rare mover does not by itself say it
just moved. In the 8-a-day set (rebuilt 2026-10-02 with these): 72-120 added rows per home,
42-70 within 24 hours of a move, 30-50 in the first hour, 30-50 random background.

**The 24-a-day set is kept as built earlier in the day (thin background, no
`rare_mover_background_random` flag) and is dropped for the model arms: at 24 ordinary questions
a day the robot opens about 30 rooms a day and sights a mover at its new place within hours, so
the seen slice saturates (last-seen 100% on it) and the unseen slice is a few questions per home.
The model arms run on `banks_8_a_day/` only.** Every question row carries `rare_mover` and `within_24h_of_rare_move`; the
added rows also `rare_mover_background_random`, `in_first_hour_after_rare_move`, `rare_move_t`, `hours_since_rare_move`,
`rare_move_rank` (1 = the first question after that move) and `rare_move_cause`. The first
window is a setting (`first_window_minutes`, default `[0, 60]`) so the questions can be pushed
later without a code change.

Whether the robot had already sighted the object at its new place when asked depends on the
robot's own looks, so that flag (`asked_before_any_sighting_at_new_place`) is computed at scoring
time by `coordination/studies/study4_rare_things_that_matter/score_rare_movers.py` from the
cell's `looks.jsonl` (no sighting of the object at its new place between the move and the
question). The search row's `times_seen_there_before` is not that flag: it counts sightings at
that place over the whole month, and the keys go back and forth between the same spots.

## Files

* `banks/hh_s<seed>_t03.jsonl` and `banks_8_a_day/hh_s<seed>_t03.jsonl`: the banks. Header field
  `rare_movers` holds the objects, the counts and the settings; `ordinary_questions_per_day` says
  which set it is.
* `*_rare_moves.json` beside each bank: every move (object, day, time, from, to, cause words, the
  resident and the room they are seen in) and the added questions with their flags.
* `config.yaml`, `build_summary.json`, `check_scenario_output.txt`, `check_scenario.json`.
* simulations: `data/situation_sim/self_improve/rare_movers_v1/hh_s<seed>/` (with a
  `rare_movers.json` manifest beside the usual four files).

## Scenario checker

`python3 results/self_improve/check_scenario.py results/self_improve/varied_homes/rare_movers`:
WORTH RUNNING, every check passed; the one warning (the verdict is one class deep on `glass`)
is the same standing warning the ten-home banks carry (`varied_homes/HANDOVER.md`).

## Running an arm on them

    PYTHONPATH=src python3 -m self_improve.overnight_wave --arm "<arm>" --household hh_s2_t03 \
        --banks results/self_improve/varied_homes/rare_movers/banks --last-day 31 \
        --questions-per-day 99 --out results/self_improve/wave_rare_movers

`--questions-per-day 99` asks every question in the bank (the harness takes evenly spaced
questions per day otherwise, which would thin the rare-mover questions along with the rest).
For the 8-a-day set use `--banks .../banks_8_a_day --out results/self_improve/wave_rare_movers_8_a_day`;
the prepared launcher for the memory methods is
`results/self_improve/wave_rare_movers_8_a_day/launch_memory_methods.sh`. Score with
`coordination/studies/study4_rare_things_that_matter/score_rare_movers.py --load 24|8`.
