# hssd_a2: household A re-run under the placement rules of 2026-10-13

Run on 2026-10-13, 16:55 to 19:51 (2 h 56 min). 14 of 14 days completed. Nothing committed.

## What was run

- **Household:** household A's created household, the same file the original A run used
  (`hssd_a/household_created.json`). Same residents (Mara and Julian), objects, HSSD scene
  107734254_176000121 and layout. No creation calls.
- **Flags:** the same as the original A run (recovered from the session that launched it on
  2026-10-09): `--days 14 --sick 7:3 --seed 1`, default model `gpt-5.6-luna`, effort medium.
  `--sick 7:3` means a 3-day illness starting on day 8; the seed picks Mara, as in A.
  No `--pilot_layout`.
- **Command** (from the repo root):

  ```
  HOSTED_SPEND_CAP=17.83 HOSTED_SPEND_LEDGER=$PWD/3d_rendering/results/lived_home/spend_ledger.json \
  PYTHONPATH=$PWD/3d_rendering/results/lived_home/hssd_a2/code_frozen \
  nohup python -u -m lived_home.run_pilot --household 3d_rendering/results/lived_home/hssd_a/household_created.json \
    --days 14 --sick 7:3 --seed 1 --out 3d_rendering/results/lived_home/hssd_a2 > .../hssd_a2/run.log 2>&1 &
  ```

- **Code:** the generator changes of 2026-10-13 are not committed. So the run used a frozen copy:
  `code_frozen/lived_home` and `code_frozen/dynamic_home_eqa`, copied from the working tree just
  before launch, with `code_frozen/VERSION.txt` listing the changed files. Edits to `src/` made
  during the run could not reach it. `code_version.txt` says `4d71d3825`; that is HEAD, which
  does not include these uncommitted changes.
- **Cheap check first:** a 2-day `--fake` run (scripted residents, no model) on the same
  household ran end to end: 0 holding problems and 0 floor or basin problems.
- **What differs from the original A run, apart from the placement rules:**
  - **At the start,** 6 things were moved off places the rules forbid:
    - a mug, a water bottle, a paperback and a phone charger, off the hall floor;
    - the newspaper, off the entryway floor;
    - a paperback, off a water glass.
  - **The "usually kept in X" reminder is on.** It is the default since 2026-10-10. The
    original A run predates it, so A ran without it.
  - **No restarts.** A was restarted three times after network drops and code fixes, with
    some days run twice. This run went through in one go.

## Cost and time

- **Spend:** $2.35 of the $5 allowed (ledger $12.83 → $15.17; the hard cap was set at $17.83).
  The spend guard read both environment variables; this was checked before launch.
  For comparison, the original A run cost $3.04 including its creation and repeated days.
- **Model calls:** 874, none answered from the cache. That is about $0.17 per day.
- **Time:** about 12.5 minutes per simulated day.

## Placement checks against hssd_a

`python -m lived_home.check_placement <run>` checks each run against its own snapshots: 112 of
them, every 2 hours from 08:00 to 22:00 over 14 days. The numbers for hssd_a are the "before"
numbers in `../FIXES_2026-10-13.md`. Full output is in `check_placement.json`.

| | hssd_a | hssd_a2 |
|---|---|---|
| Things on or in a thing that cannot hold them (the holding rule) | 304 (2.7 per snapshot) | **0** |
| Things on a floor or in a basin where they do not belong | 833 (7.4 per snapshot) | **0** |
| Snapshots with a spot over its measured room | 100 of 112 (123 spot-snapshots) | **9 of 112** (9) |
| Things on or in another thing, per snapshot (allowed ones included) | 24.2 | 23.9 |

- **The 9 over-full snapshots in hssd_a2** are all the small bedroom table's top shelf, from day
  1 08:00 to day 2 08:00. A sweater and a mug start there on 0.038 m². This is the known gap
  "start positions are not checked for room". It cleared once a resident moved them.
- **The checker uses the same rules the run enforced, so I also checked by hand.**
  - I listed every thing lying on a floor or in a basin or bathtub, by type, across all 112
    snapshots. The only phones and keys on a floor were ones in someone's hand or pocket. The
    things in basins were dishes, cutlery, toiletries, a toothbrush in the bathroom sink, and
    some fruit and yogurt in the kitchen sink. The kitchen sink is allowed food.
  - I also listed every "on top of / inside another thing" pair by type. All look like what the
    rules allow: things in bags, the first-aid kit, the laundry basket and pockets; a pen on a
    book; carrots on the cutting board; fruit in a bowl; clothes on clothes.

## Other numbers, hssd_a against hssd_a2

| | hssd_a | hssd_a2 |
|---|---|---|
| Actions carried out | 8,103 | 8,577 |
| Actions rejected | 236 (2.8%) | 235 (2.7%) |
| ... of which "no room" at the spot | 68 | 89 |
| ... of which "that thing cannot hold it, and there is no room next to it" | 0 (rule absent) | 9 |
| Put-downs redirected by the rules | 0 (rule absent) | 35 |
| Things that ever moved | 159 | 153 |
| Things in the kitchen sink, mean per snapshot (max) | 6.7 (17) | 7.3 (14) |
| Things on the counter beside the kitchen sink, mean (max) | 5.7 (10) | 5.6 (11) |
| Things on the main nightstand, mean (max) | 7.5 (13) | 6.6 (14) |
| Things on the kitchen island, mean (max) | 15.8 (30) | 17.5 (37) |
| "Lying about": clean things off their usual place on a floor, seat, bed, basin or stove; days 2-4 → days 12-14 | 24.8 → 30.4 | 18.7 → 28.9 |
| Share of things at their usual place, days 12-14 | 55% | 56% |

The "lying about" row comes from `python -m lived_home.drift` (`drift.json`). hssd_a2 fails the
drift check (growth +10.2 against a limit of 9.4). It does so because it starts lower, not
because it ends higher. Its end level is about the same as A's.

**Redirects (35):**
- **20 were off a floor or out of a basin:**
  - 12 times, Mara put the house keys on the entryway floor. Each time they went to a kitchen
    counter in another room.
  - Twice, a bath towel put into the bathtub went to the vanity top.
  - 4 times, a water bottle, a glass or a banana put on the bedroom floor went to the bed's
    shelves.
  - Twice, a ceramic tray, put once in the kitchen sink and once on the entryway floor, went to
    a kitchen counter.
- **15 were things put on top of something that cannot hold them** (a laptop, a wallet,
  tissues, a phone charger). Each went next to that thing instead.

## Task scoring (search task and simple predictors)

These were run the same way as for hssd_a in FIXES section 4: same code, same patrol seed (0).
- `python -m lived_home.play hssd_a2` built a 30-question session, `hssd_a2-s0`.
- `python -m lived_home.play_baselines hssd_a2/play/play_data.json` scored the 30 questions
  (`play/baselines.json`).
- `python -m lived_home.play_baselines hssd_a2` scored every question
  (`play/baselines_all_questions.json`).
- `python -m lived_home.baselines hssd_a2` and `--truth` wrote `baselines_notes.md` and
  `baselines.md`.

The 30 questions are a different sample in each run, so compare the "all questions" columns.

Right / partly right / wrong:

| | A, 30 | A, all 4,755 | A2, 30 | A2, all 4,318 |
|---|---|---|---|---|
| nearest (no memory) | 2 / 28 / 0 | 623 / 4132 / 0 | 2 / 28 / 0 | 572 / 3746 / 0 |
| last seen | 9 / 8 / 13 | 3827 / 338 / 590 | 10 / 5 / 15 | 3344 / 303 / 671 |
| most often | 13 / 8 / 9 | 4003 / 338 / 414 | 16 / 5 / 9 | 3537 / 305 / 476 |

Over all questions, "last seen" is right on 80% in A and 77% in A2, and "most often" on 84% and
82%.

Simple predictors, share with the right furniture (right room in brackets). Questions are asked
about every object that moves, at 10, 14, 18 and 22 h, from day 2 on:

| | questions | no history | last known | usual place | usual at this hour | mix |
|---|---|---|---|---|---|---|
| A, patrol notes | 7,540 | 16% | 65% (71%) | 48% (59%) | 47% (58%) | 57% (65%) |
| A2, patrol notes | 7,592 | 13% | 62% (69%) | 47% (59%) | 48% (59%) | 55% (64%) |
| A, true positions | 7,540 | 0% | 90% (92%) | 58% (72%) | 52% (68%) | 68% (79%) |
| A2, true positions | 7,592 | 0% | 89% (91%) | 57% (73%) | 54% (71%) | 69% (80%) |

The task's difficulty is about the same as in A, within 3 points on every predictor.

## Bugs and rough edges seen (none corrupted data; the run was never stopped)

1. **The kitchen sink area is the main place the room limits bite.** The counter beside the
   sink measures 0.26 m² and always holds the sponge, dish soap, a thermos and the herbs. 44 of
   the 89 "no room" rejections were there, and 11 more in the sink itself. Residents retry the
   same full spot several times in a row: Julian tried the thermos 8 times on day 12 and 5 on
   day 13, and the stockpot 4 times on day 9. Nobody washes up and puts dishes away, so the
   sink stays full. hssd_a's sink was just as full; the difference is that now it refuses
   things. "No room" rejections per day rise from 0-6 on days 1-9 to 20 and 14 on days 13-14,
   and total rejections from about 2% to about 4-5% of actions. A dish rack or draining board
   spot, or a washing-up step, would relieve it.
2. **Bathroom 1 has nowhere obvious for a bath towel.** The upper shelf of the low table is
   0.067 m² and already holds a hand towel; the vanity top is full of toiletries. On day 1 Julian
   gave up and took the towel back to the laundry room. On day 13 Mara tried 8 times in two
   minutes. The lower shelf (0.27 m²) would take it, but residents rarely think of it. Towels may
   also go on the floor (counted as lying about).
3. **The residents are not told about a redirect when it happens.** The put-down simply
   succeeds; they see the new place only later, in what they remember. So Mara puts the keys on
   the entryway floor 12 times and each time they end up on a kitchen counter in another room,
   with a walk added for her. This is the open "redirect across rooms from a hall with only a
   floor" item in FIXES.
4. **A wording bug in the "no room" message for an empty spot.** It says "it already holds .".
   This happened 6 times, all on the piano's middle shelf. That shelf has 0.02 m² assumed, too
   small for a book or a backpack. It is not new in the rule, but the message misleads: Julian
   retried the identical action once.
5. **Clothes cannot always be piled.** "Sleep pants are too big to go on top of the sleep shirt"
   came up 8 times. This is the older stack-by-size check, and it ignores that a pile of clothes
   is allowed as a base.
6. **Grammar in redirect reasons:** "a keys does not go on the floor", "a market herbs does not
   go on a dish towel". These are seen only in logs and in the rejection text.
7. **Not new, still there:** "you are not holding X" when a resident puts down something they
   had already put down (Julian, 4 times in one minute on day 7); "you are still wearing your
   sleep clothes" before dressing (9 times).

## Residents' behaviour

- **They mostly adapt sensibly to "no room":** "The counter beside the sink is full, so I set
  the plate into the sink with the other dishes"; "The nightstand is full, so I carry the wallet
  to the dresser"; Julian set his phone on Mara's paperback when the nightstand was full.
- **They do not remember that a spot was full.** The next time they choose the same spot, it is
  refused again (see 1 and 2).
- **The sick days (8-10) work.** Mara knows she is ill from her day-8 plan: she stays home,
  makes ginger tea and rests. Julian plans to check on her between shifts.
- **Nothing suggests the rules left any thing unplaceable.**
  - 142 put-downs were rejected. Every one refused for room, or because the thing named could
    not hold it, was followed the same day by a successful put-down of that thing.
  - The 7 rejected put-downs with no later put-down that day were "you are not holding it"
    cases, where the thing had already been put down.
  - No one held anything at the end of any day.

## Files for rendering

- **Positions every 2 hours:**
  `results/lived_home/hssd_a2/day_01 … day_14/positions_HHMM.json`, HHMM = 0800, 1000, …,
  2200. That is 8 per day, 112 in all. There is also an end-of-day `positions.json` per day, as
  in hssd_a.
- **The format is unchanged from hssd_a.**
  - Same top-level keys: scene, day, time, relations, hidden_rule, people, places, objects.
  - Same per-object keys, the same 187 places and the same 251 object ids.
- **One addition, in the places' geometry:** each place now carries `area_assumed` and
  `area_from`, and `area` is the measured area where the scan was used. That is 80 of the 94
  scanned spots (the other 14 scans were doubtful and the assumed area is kept); for example the dining-room floor is 11.1 m², was 26.3. A renderer that ignores
  `area` sees no difference.
- **Start positions differ from hssd_a for the 6 things moved at the start.** The list is in
  `household.json` → `moved_at_start`.
