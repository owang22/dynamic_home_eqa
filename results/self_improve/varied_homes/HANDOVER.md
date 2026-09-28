# varied_v2: which homes to run the arms on, and what is known about them

Written 2026-09-24. Everything named here is under `results/self_improve/varied_homes/`.

## Run these

**Start on the pilot ten:** `ten_homes/banks/` — `hh_s2, hh_s19, hh_s20, hh_s32, hh_s48,
hh_s63, hh_s93, hh_s109, hh_s123, hh_s151`. These are the first ten of the selected 61
**in seed order**, not the ten with the sharpest step: picking by the size of the effect
would be selecting on the outcome.

**THE TEN IS A PILOT, NOT THE SAMPLE.** The claim that makes the return a memory result
rather than a general change in difficulty is *the return costs the objects the illness
moved and not the others* — the night-shift scenario died because the untouched objects
fell as far as the movers. That contrast needs the full set:

| the return (`break again`, three-day memory, household-clustered) | pilot ten | all 61 |
|---|---|---|
| on the objects the illness moved | −44.3 ± 8.01 (5.5 SE) | −44.3 ± 2.34 (19.0 SE) |
| pooled over every object | −16.9 ± 3.95 | −14.9 ± 1.45 |
| **on the objects that stayed put** | **−1.4 ± 2.85** | **−0.8 ± 1.19** |

At ten homes the control null only excludes a drift larger than about 5.7 points; at 61
it excludes anything larger than 2.4. **Run the pilot to get numbers moving, then run all
61 before the control contrast is claimed in the paper.** The other 51 are already
generated and gated: `selected_v2/banks/`.

## What was selected on, and why the gate is an independent test

Two stages, in `pick_the_seeds.py` (floor plan and residents, no simulation) and
`select_the_homes.py` + `which_lever_is_wrong.py` (the generated month). 1000 seeds looked
at, 127 simulated, **61 kept (6.1%)**. Every rejected home is in `rejected_v2/banks/` with
its reason in `SELECTION_v2.json`; `all_generated_v2/banks/` holds all 127 and nothing was
deleted.

Six bars, every one a property of the world — the floor plan, the residents' routines,
where and when the illness puts things. No learner, no counting method and no language
model is run in either stage:

1. at least 7 rooms (stage 1 requires 8);
2. at least 3 movers — an object the illness puts in a **different room** from its usual one;
3. at least half the movers land outside the three busiest rooms;
4. at most half the illness-window questions about movers answered by a busiest-three room;
5. every mover: **leak under 10%** (share of ordinary-fortnight questions already answered
   by its illness place) and **switch over 70%** (share of illness-window questions that
   are) — this is what makes the change a step instead of a slope;
6. the busiest three rooms hold at most 88% of all answers, and at least 3 controls.

**The asked-about object class list is unchanged from illness_v1 and predates every one of
these gates.** Nothing in it was chosen by trying mixes against a gate. That sentence is
worth stating in the paper, because it is exactly what could not be said about the earlier
bathroom scenario: here the gates are an independent test of the scenario rather than a
description of it.

## What the world looks like

`scenario/varied_v2.yaml`, built from `scenario/activities_varied.yaml` and
`scenario/events_varied.yaml`, which are **generated** by `make_the_activities.py` and
`make_the_events.py` — edit those scripts, not the YAML. Same calendar, protocol, class
list and per-day question count as illness_v1; ordinary life happens on the day-time
surfaces (bathroom shelf, the table, the desk in the study) and the illness happens on the
bed, the nightstand, the sofa and the chair by the window. For ten days the ill resident
does not come to the table, cook, wash up, take the evening's television slot or read in
bed: supper comes on a tray and the evening stays where the afternoon was.

The step, day by day, is in `gate_output/which_lever_is_wrong_*.txt`: **0% before day 14 in
every home**, 60–100% from it, median step +91 points over the pilot and +87 over the 61.
For contrast, illness_v1's hh_s1 went 37% → 48%.

**Keep the one-surface-per-moved-class check in `make_the_events.py`.** It enumerates every
bout an ill resident can still have and fails the build if any moved class is used on more
than one surface, or if the resting rule names a different surface from the one it is used
on. It caught a real fault: `sit_quietly` used the compound room token `balcony_or_living`,
so the tablet was used on the balcony table and rested on the living-room side table — two
rooms for one object, which would have quietly halved that object's switch in every home
with a balcony. That class of bug is invisible in the output and the check is the only
thing that finds it.

## Known limits, for the wording

- **The illness is a two-room step.** Destinations are the bedroom and the living room
  across all 61 homes (five distinct receptacles; heterogeneity and independence both
  pass). Sharper than illness_v1 but less varied. The route back to variety is more
  illness bouts in other rooms, each owning a class of its own — future work, not done.
- **hh_s131 is in the 61 but not in the pilot.** It passes all six world levers, and fails
  `check_the_lazy_robot.py` as that gate is written today (52%) only because that gate
  still counts a towel moving from the towel rail to the bathroom shelf as a mover. On
  room-changing movers its score is 0%. Bringing that gate's mover definition in line with
  this one is a one-line change to a shared file and was deliberately not made here.
- **Idiosyncrasy is global, not home-specific.** Cross-home agreement on where a class
  usually lives is 67% (illness_v1: 67%) — see `gate_output/is_it_the_same_in_every_home.txt`.
  The pill box is on the kitchen table in *every* home, so one sentence of common sense
  still covers it once known. Making a habit differ between homes needs
  `sample_household` in `src/situation_sim/household.py` to sample per-home variants; not
  attempted.
- `check_scenario.py` passes every check on both sets, with two standing warnings: the
  verdict is one class deep on `glass` (the *learn* floor), and the never-forgetting
  learner's return leg is a null inside two standard errors.
- A third of all questions are about towels, in this population and in illness_v1 alike, so
  the effective sample on the moved objects is much smaller than the question count
  suggests. Not fixed: fixing it means changing the class list, which would cost the
  independence claim above.
