# Luna pilot: one household, seven days

Run: `3d_rendering/results/lived_home/pilot_luna/` (run 17 of the day; all seven days on one code
version, commit in `code_version.txt`). Household: Mara (42, transport planner) and Daniel (45,
appliance repair), a three-bedroom house with 183 spots and 272 objects. Daniel forced sick on days
3 to 5 (Wed to Fri); a relative visits days 6 and 7. Model `gpt-5.6-luna`, effort medium.
Full tables: `report.md`; every action in order: `replay.md`; viewer:
https://claude.ai/artifact/M7g5Fp3taWhbDco44h7if5

## 1. Cost, calls, rejected actions

- The week: 366 model calls, $0.92 (plus $0.06 to create the household). Median prompt 12.4k tokens,
  median answer 1.2k tokens, 12 s per call.
- 3,424 actions carried out, 70 rejected (2.0%). Reasons: "you are not holding X" 21, hands full 20,
  not where they last saw it 9, someone else has it, and a few slips.
- 104 interruptions (99 someone speaking to them, 5 disturbances); 37 long activities cut short.
- The whole session, with 16 earlier starts stopped for fixes: $2.99 of the $6 cap.

## 2. Objects: what moved and where it ended

139 of 272 objects moved at least once; 108 of 197 types. Examples of the pattern the brief asks
for (a few places, not one and not many):
- **Tableware cycles**: plates, bowls, forks, spoons and glasses go cupboard or drawer -> table ->
  drying mat -> sink -> dishwasher, and back. Three of the four plates stayed in the cupboard until
  the weekend, when both were home for every meal.
- **Mara's blue mug** ends the days on the kitchen island (3 of 7), a counter, the sink, the dining
  table, and Daniel's nightstand on his first sick day (tea): a few places with one favourite.
- **Mara's reading glasses** (3 pairs): nightstand, bathroom vanity, kitchen island, as her habit
  says ("live on the nightstand, forgotten in the living room").
- **Daniel's wallet and keys** end up in yesterday's work trousers in the hamper, as his habit says.
- Clothes go into the hamper and are taken out again to wear, with no washing in between; Daniel's
  khaki work trousers stay in the hamper all week.

## 3. Response habits

| habit | trigger said true | followed |
|---|---|---|
| Mara: ginger tea when Daniel is sick | 46 of 181 answers | 29 (days 3 to 6) |
| Mara: clutter reset when the house looks crowded | 23 | 18 (days 2, 3, 6, 7) |
| Mara: walk when work is tense; Thai food when too tired | 0 | 0 |
| Daniel: all four habits | 0 or 1 | 0 |

The tea lands where her habit says: on the right side of the living-room coffee table. The counts
are self-reported per call, so one tea-making is counted in several calls, and Daniel's habits are
all triggered at work, which is not simulated.

## 4. Sick days against normal days

Daniel (sick days 3 to 5):
- Out of the house 0 minutes on sick days, against about 600 on workdays.
- Health 1.0 (3.0 on workdays), tiredness 2.7 to 3.0, mood 1.1.
- Actions move from bedroom, kitchen and entry to bathroom, living room (the sofa) and bed; he goes
  to bed at 20:00 instead of 22:00.
- Objects only on sick days: a quilt, a bowl and spoons for yogurt, Mara's mug for tea; the shared
  cold medicine and thermometer are used with timed doses.
- The sickness carries into Saturday (health 1.1 on day 6) although it was scheduled to end Friday.

Mara (the other resident):
- Same work hours, but much more done in the kitchen (61 to 100 actions on sick days, against 14
  and 38 on the two workdays), mood down from 2.7 to 2.1, tiredness up from 0.8 to 1.2.
- The tea habit fires every sick evening.

Caveats: one household, one sick spell; sick days are Wed to Fri and the clean normal days Mon and
Tue; the weekend carries the visit and Daniel's lingering cold. A rerun returns the same cached
answers, so there are no replicates.

## 5. Ten excerpts from replay.md

**Lifelike**

1. *Timing medicine* (day 4, 06:35, Daniel): "The cold medicine was last taken at 06:19, only 16
   minutes ago, so its label interval has not passed. I will take the allergy tablet with water,
   leave the cold medicine for later."
2. *A habit acted out* (day 4, 06:15, Mara): "I will retrieve the blue reading glasses from the
   living room, wash up, take my prescription, dress, and put the glasses on the left nightstand."
3. *Pockets have consequences* (day 7, 21:29, Daniel): goes to the laundry hamper "to retrieve my
   wallet from yesterday's work trousers", then puts it in his nightstand drawer. (Day 6, 10:45,
   Mara: "Retrieve my house keys and wallet from yesterday's trousers.")
4. *Caring for each other's things* (day 6, 08:3x, Mara): "I will … remove his work keys from the
   hamper before washing, load the remaining laundry, run the washer."
5. *The tea habit, placed* (day 3, 20:14, Mara): carries ginger tea to the living room "without
   interrupting Daniel's television time" and puts the mug "on the right side of the coffee table as
   planned" - the exact spot her habit names.

**Wrong-looking**

6. *Undressing for bed* (day 2, night, Daniel): "take off my sleep clothes and place them in the
   laundry hamper, then get into bed". Nobody wears anything on 3 of 7 nights, and Daniel spends
   sick day 3 wearing nothing at all. The bedtime line in the prompt causes it.
7. *A misplacement that becomes a habit* (day 1, 06:33, Mara): the kettle is put "on" the toaster,
   stored as on top of it; on day 2 she "return[s] the kettle to its usual place on the toaster".
   Same fault: the library book left "beside the glasses" is stored on top of them (day 2, 21:12).
8. *Leaving without essentials*: 5 of 9 departures are missing a phone, keys or wallet (Mara day 3
   and 4: no phone and no keys; Daniel day 2: no phone, no keys) - partly because they stay in
   yesterday's trousers.
9. *Retrying what already happened* (day 3, 17:53, Daniel): puts the yogurt down, then is told four
   times "you are not holding yogurt_strawberry_four_pack" because the rest of his plan tries to put
   it down again; each retry repeats the same step.
10. *A visit with no visitor* (day 6): Mara prepares the guest room, and both "welcome the relative",
   but the relative is not a person in the simulation: the guest bed, towels and dishes are never
   used by anyone else.

## What changed on the way here (16 stopped starts)

Each was a fault that would have repeated every day, found by reading the run as it went:
residents taking each other's bags and clothes (no owner labels, no own work bag, no casual
clothes); no stove or sink spots; one wallet and one bowl for two people; an engine that could not
dress anyone; pockets that stayed on the person; double dinners; pajamas under work clothes; actions
that could not be interrupted; leaks of hidden things found by an independent audit (11 fixed). The
skeptic's notes (`3d_rendering/critic/notes_2026-10-07_1803.md`) list what remains.

## Next version, before more households

1. Clothing: put on sleepwear at night (not "take off what you wear"), and a clean/dirty cycle for
   clothes and dishes (laundry is washed and comes back).
2. Relations: "on" with a reference object should not silently mean "on top of"; ask for next_to or
   on_top_of explicitly.
3. Leaving the house: the leave_home description reminds them what they usually take.
4. Rejection messages: when someone tries to put down a thing they already put down and can see,
   say where it is.
5. Sinks and desk cubbies are open, not closed.
6. Guests as simple residents (or at least as people who use the guest room and dishes).
7. Habit scoring from events, not only from self-report.
8. Rendering (needs the GPU back and the decision on fitting to HSSD vs layouts built from HSSD).
