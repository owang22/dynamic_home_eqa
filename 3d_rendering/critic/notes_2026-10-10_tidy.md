# Critic notes 2026-10-10 03:21: the "usually kept" cue

Scope: world.py `homes()` and the kept label, run_pilot.py `is_tidying`, drift.py, against hssd_a and hssd_b. Scripts: `critic/scratch/tidy/`. No model calls; nothing written under results/.

1. **(C) Half the "drift" is resettling, not clutter.** On days 12-14, of homed objects away from their start spot (A 111, B 102), 61 and 53 sit on another shelf or surface. 42 of A's 61 are at that one spot in at least 70% of snapshots (`settle.py`): laptop from tote bag to desk, receipts from island to desk, toothbrush to the other bathroom. The cue would push these back, erasing what "most often seen" should learn. *Suggestion:* treat only floor/seat/sink/hamper growth as clutter.

2. **(B) A start spot is often where a thing is in use, not where it is kept.** In A, 15 of 35 dishes get a home on a surface outside the kitchen (mug_blue_speckled on the guest nightstand; plates on the dining table). Daniel's phone (B) gets the bar cart. Receipts, a banana and a yogurt cup get countertops. Cause: the prompts ask for "right now in the early morning" (prompts.py:264, 277) and for "clothes they leave lying around" (prompts.py:81). Mara's 13 inferred clothes inherit a small-table shelf by an armchair (world.py:196); Daniel's blazer inherits a drawer. *Suggestion:* add a `kept_at` field at creation, separate from where the thing is now, before more households are made.

3. **(B, bug) Drawers in a "sink cabinet" count as wet basins.** WET is tested on the furniture's words (world.py:133). B: 15 spots, including every `kitchen_kitchen_sink_counter` drawer, so 36 objects get no home (all the cutlery, utensils, trash bags). A: 6 spots, 3 objects; hssd_luna: 11 spots. *Suggestion:* test only the spot's own name. Add a test with B's ids.

4. **(A) The cue fires where little clutter grows.** A: 58 of 78 cued activities are in the kitchen; bedtime calls are all in bedroom_1. The clutter that grew (laundryroom floor 13, bathroom_2 floor 8 in A; sofa 12, bathroom_1 floor 11 in B) got 0-3 cued calls in 14 days, and about half of it is dirty clothes, which the cue skips (world.py:399). Expect a kitchen reset four times a day and floors unchanged. *Suggestion:* fix floors through the laundry flow, not this label.

5. **(A/D) The label reads as a long to-do list.** Days 10-14: median 37 labels per kitchen view in A (maximum 44), 20 in B (`label_load.py`). Dishes have no dirty state, so a plate in the sink reads "(usually kept on dining_room_dining_table_tabletop)". *Suggestion:* label only what is held or listed in `uses`, at most about 5 per view.

6. **(C) drift.py grades the fix on the very quantity the cue displays.** A run where nothing moves passes; the resettled household of finding 1 fails. *Suggestion:* gate on baselines.md's "usual place" accuracy (learned from data; A falls 80%→36%) on the moved-since-last-question rows, plus a floor on moves per day.

7. **(C) The floors/beds/seats column measures the starting clutter.** It is 44 (A) and 40 (B) at day 1 08:00, of which only 11 and 15 are at their own home; it ends at 49 and 47. Pillows on mattresses count (SEATS includes bed, mattress). It does not support "clothes pile up". *Suggestion:* count only things not at their home, as a change from day 1 08:00.

8. **(C) Old numbers shift when the rules change.** For runs without homes.json, drift.py recomputes homes with the current code, so fixing finding 3 changes this morning's 85→55. *Suggestion:* freeze homes and a rules version in household.json.

9. **(C) Keyword match.** "fold" matches "folder" (8 of A's 78); "dishes" and "rinse" catch meals. The cue rate depends on how the plans are worded. *Suggestion:* match whole words; report the count of `kept_shown` calls per run.

10. **(C) Test design.** n=2, and other fixes landed after hssd_a/b. *Suggestion:* run both arms from one day-7 checkpoint at one commit for 2-3 days. Measure compliance: the share of labelled items moved to the label within the call. Above about 80% means the label is an order.

## Questions I could not answer
- Should a return to the start spot count as "moved" in play questions? Daily returns make "usual place" win by construction.
- Does capacity stop 13 clothes from fitting on Mara's table shelf?

## What looks sound
- The cue is off for dirty clothes, and the `run_config.json`/`kept_shown` logging and the `--no_kept_cue` arm make the comparison possible.
- Carrier homes, and leaving out carriers things only pass through, are sensible.
- No hidden position leaks: residents plausibly know where things are kept.
