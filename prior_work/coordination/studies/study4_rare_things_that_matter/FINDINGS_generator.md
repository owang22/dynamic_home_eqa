# How the ten-home banks are generated, and where a rare mover can be added

Written 2026-10-02 by sim-builder-rare-things, before changing any code. Every path is under
`/home/oliver/robot/dynamic_home_eqa/`.

## The pipeline, file by file

1. **Scenario config**: `results/self_improve/varied_homes/scenario/varied_v2.yaml`. Names the
   events file (`events_varied.yaml`), the activities file (`activities_varied.yaml`), the
   calendar (lead 0-13, sick 14-23 with `unwell_spell` forced on `resident_1`, return 24-31;
   every day `day_kind: weekday`, all random events off), the asked-about class list
   (`book, water_bottle, tablet, mug, charger, glasses, glass, razor, medication, towel,
   notebook`), 24 questions a day, `question_moment: during`, 30-minute same-object gap,
   found-it feedback 10 minutes after each question. `all_generated_v2/config.yaml` is this
   file dumped back out; `all_generated_v2_twice` adds two more calendar blocks (days 32-49).
2. **Build script**: `results/self_improve/earlier_work/make_scenario.py` (moved there on
   2026-09-26 as "a one-off tool for a finished study"; nothing else builds banks). Its
   `simulate()` is `situation_sim.run.generate` with the scenario's own events and activities
   files; its `bank()` calls `baselines.patrol.bank.build_bank` with the activity list
   monkey-patched to the scenario's file. Simulations land in
   `data/situation_sim/self_improve/varied_v2/hh_s<seed>/` (`events.jsonl`, `hidden_state.json`,
   `trace.json`, `trace.md`); banks in `<out>/banks/hh_s<seed>_t03.jsonl`.
3. **Household sampler**: `src/situation_sim/household.py:sample_household(seed, acts)`. One
   seeded `random.Random(f"household:{seed}")` draws residents (2-3, roles, bedrooms, traits,
   hobbies), rooms, receptacles (fixed kinds per room kind, `ROOM_SPOTS`), and objects from
   `src/situation_sim/objects.yaml` (per-resident or shared, with a probability, a list of home
   spots, size class, pocket/outdoor flags). Object ids are `<class>_<owner name>` or
   `<class>_shared`; `src/self_improve/who_lives_here.py` relies on that suffix.
4. **Day situations**: `src/situation_sim/situation.py:sample_situations`. Per day: event rolls
   (all zero here), the calendar stage's forced causes (`unwell_spell:resident_1` on days
   14-23), internal states, episodes. `DaySituation.stage` is the calendar block name.
5. **Schedule**: `src/situation_sim/schedule.py:build_day`. Role templates from the activities
   file, habit-filled slots, event edits (the illness removes work, meals, trips; adds
   `dose_medicine` 08:15 at the nightstand, `nap_bed`, `rest_coffee`, `doze_couch`, ...),
   jitter, fragmentation. Output: a list of `Bout(resident, activity, start, end, room, surface,
   uses, ...)`; `room == ELSEWHERE` is a trip out.
6. **Simulation**: `src/situation_sim/simulate.py:Simulator.run`. Every object starts at
   `home[0]` at t=0. When a bout starts, the objects its `uses` list names are brought to the
   bout's surface (pocket items go ON_PERSON; trips take pocket/outdoor/bag items
   OUT_OF_HOUSE). When a bout ends, each used object goes through
   `placement.decide()` (event rule, tidy, dump at the door, leave where used, after-use sink,
   put back home, then capacity fallback and a small whim). Residents' rooms are recorded as
   `resident` rows at every bout start (`resident_at`), and on arrival home a resident
   "settles" in the living room if the next activity is more than five minutes away.
   The run is deterministic: re-simulating hh_s2 today reproduced `events.jsonl`,
   `hidden_state.json`, `trace.json` and `trace.md` byte for byte.
7. **Bank builder**: `src/baselines/patrol/bank.py:build_bank` -> `activity_question_rows`.
   Questions are drawn from the trace's activity start lines: pick a start, pick one of the
   objects that activity `uses` (owned by that resident or shared, class in the config list),
   a minute inside the activity, drop it if the truth is ON_PERSON/OUT_OF_HOUSE, enforce the
   30-minute gap, keep 24 a day. Question rows carry `question_id d{day}q{nn}`, `object_id`,
   `t_query`, `day_index`, `object_class`, `moment` (the activity) and `stage`. The bank also
   holds the truth rows, resident rows, a 03:00 patrol snapshot and feedback observations;
   the search harness (`src/self_improve/frozen_household.py`) reads only the header, truth,
   question and resident rows. The harness takes `--questions-per-day` evenly spaced
   questions from each day's list (`search_driven.questions_spread_across_the_day`); a value
   above the day's count takes them all.

## Why there are no rare movers today

An object moves only when an activity uses it (step 6), and the activities that use the
asked-about classes run daily (breakfast uses the medication, every trip takes the keys, the
desk and bed use the glasses). So every non-static object is either a fixture or a daily
mover, which is exactly what the count in `RESULTS_count.md` found. The illness is the only
calendar event; "arrivals home" happen several times a day but nothing is placed by them
except through the ordinary put-back/dump rule.

## What the robot can see

`src/self_improve/looking.py:TheHouseAsSeen.look` lists every object in every place of the
opened room and every resident in that room at that moment
(`FrozenHousehold.residents_in_room`, from the `resident` rows). So a cause is visible to the
robot if the resident is in the room at the times the robot opens it: the ill resident is in
the bedroom and the living room through the day on days 14-23; a resident who has just come
home is in the living room (settled) or at the surface of their next activity.

## Where the new option goes

A post-pass after the base simulation, in a new module `src/situation_sim/rare_movers.py`,
called by a new build script. It leaves the base run untouched (same rng streams, so every
existing object's trajectory is byte-identical to the ten-home banks) and adds:

* `pill_box_<ill resident>` (class `pill_box`): at a kitchen counter or bathroom cabinet (one
  seeded draw per home); on the first day with an `unwell_spell` cause it moves to the ill
  resident's nightstand at the start of that resident's first bedroom bout; on the first day
  after the spell it goes back at the start of that resident's first bout outside the bedroom.
* `car_keys_shared` (class `car_keys`): on the entry table. One to three times a week (seeded
  draw per week) a resident's trip out is a car trip: the keys leave with them and, on
  arrival, land where that person first sits: the living-room coffee table if they settle
  there before the next activity, otherwise the surface of the next activity (kitchen table,
  desk, dining table, ...). They stay there until the next car trip.
* reading glasses (c): the generator can express "nightstand at night, desk on working days",
  but this calendar makes every day a weekday, so the only non-working days are the ill
  resident's sick days. That makes the glasses either a daily mover (two moves a day) or a
  copy of the illness movers already in the bank, not a rare mover. Not built; said so in
  the report.

New classes rather than `medication`/`keys` so the base question draw (which picks from the
classes each activity uses) is unchanged; the base 24 questions a day are then byte-identical
to the ten-home banks, and the rare-mover questions are appended with their own ids
(`d{day}r{nn}`) and a `within_24h_of_rare_move` field on every question row. (Rebuilt the same
day on the coordinator's instruction: five questions in the first hour after each move and two
over the rest of the day, and a second bank set with the ordinary questions thinned to 8 a day.)
