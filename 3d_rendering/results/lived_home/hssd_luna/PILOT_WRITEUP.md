# Luna week in an HSSD home: Mara and Julian

Run: `3d_rendering/results/lived_home/hssd_luna/`. All 7 days ran on one code version (commit
`f2771d685`, in `code_version.txt`). Viewer: https://claude.ai/artifact/Pn2PshvAzh9uYAGeEdRpNh
(floor plan drawn to scale from the scene). Full tables are in `report.md`, and every action in
order is in `replay.md`. The skeptic's notes are in `3d_rendering/critic/notes_2026-10-07_2222.md`.

## What is new since the Mara and Daniel week

- **The home is a real 3D scene.** It is HSSD scene `105515337_173104347`: 9 rooms and 193 spots.
  `hssd_layout.py` reads them from the scene files: receptacle meshes split by height,
  surfaces read from each object's own mesh where HSSD gives none, real drawers, sink and tub
  basins, and one floor spot per room. The model only names the furniture and spots
  (`hssd_home.py`: one call for the whole home, one per room). Ids are built in code, and each
  spot keeps its scene geometry.
- **Exactly four relations:** inside, on_top, under and next_to. A position is relative to the
  spot or to an object at that spot. Hidden means under something, or inside a closed spot or
  a closed container. `day_XX/positions.json` gives every object's room, spot, relation,
  reference and hidden flag, plus each spot's furniture template, instance and pose.
- **Clothing:**
  - residents change into sleepwear at night and must take it off before day clothes go on;
  - clothes worn during a day count as dirty until washed;
  - leaving home reminds them of phone, keys and wallet.

## 1. Cost, calls, rejected actions

- Household creation: 29 calls, $0.11, and no answer was refused by a check.
- The week: 509 calls and $1.46. A normal day cost about $0.11; a sick day or the weekend cost
  $0.22–0.29, because both residents were home and talking.
- The residents asked for 4,165 actions, of which 140 were rejected (3.3%). The main reasons:
  - hands full: 20;
  - "you are not holding X", 31 in all; most come from a fault in the recap, now fixed (item 6
    below);
  - Mara naming herself as the listener: 13, now fixed.
- There were 159 interruptions, and 59 long activities were cut short.
- The whole session, including the earlier work and stopped starts, has spent $4.99 of the $6 cap.

## 2. Objects

101 of 276 objects moved at least once. Examples:
- **Tableware:** cupboard → table → sink basin → drying, every day. All 4 forks, knives and plates
  were used.
- **Keys:**
  - Julian's keys go from the hallway tray to the dining table.
  - Mara's keys go from her tote to the bedroom floor (in trouser pockets) to her nightstand.
- **The pocket chain:** Julian's phone and wallet went into the hamper inside his trousers. On day 3
  he fetched the phone back from there; the wallet stayed for days.

## 3. Response habits (self-reported, as before)

| habit | trigger said true | followed | days |
|---|---|---|---|
| Mara: tea, painkillers, temperature when Julian is unwell | 73 of 267 answers | 56 (50 with trigger) | 3, 4, 5 |
| Julian: rearrange the table, drinks, music when friends come | 8 of 232 | 5 | 6 |
| Julian: order food and shower after a late setup | 4 | 4 | 3, 5 |
| Mara: walk and a list after a rushed client request | 3 | 2 | 1 |
| Julian: fix things at once when something breaks | 0 | 0 | the power cut was not counted as "broken" |

## 4. Sick days (Julian, days 3 to 5) against normal days

- **Julian:**
  - 0 minutes out against about 630 on workdays;
  - health about 1.1 (3.0 on workdays), tiredness 2.7–2.8, mood 1.0–1.1;
  - his actions moved from the kitchen and hallway to the living-room sofa, his bedroom and the
    toilet room;
  - objects used only on sick days: cold medicine, a pill bottle, the first-aid kit, tea bags
    and a striped mug.
- **Mara:**
  - kitchen actions roughly doubled (85–100 against 30–55), and her mood fell from 2.4–2.8 to
    2.0;
  - things only she moved on sick days: thermometer, painkillers, first-aid kit, a tray.
- **His illness ran over** into day 6 ("under the weather", health 2.3), as in the last pilot.
- **A confound the skeptic found:** Mara works at Julian's desk in his bedroom 7–9 hours a day,
  because the household text made it "his office". On sick days he lies on the living-room sofa
  "to keep my distance while Mara works". So part of his sick-day room shift comes from his room
  being taken.

## 5. Ten excerpts

**Lifelike**

1. **Pockets have consequences** (day 3, 07:37, Julian): "My phone is still in the laundry hamper,
   so I will retrieve it first and avoid getting drawn into a full workday."
2. **Care, assembled once** (day 3, 07:30, Mara): "make the tea first, gather the thermometer,
   painkillers, and water, then bring everything to him together so he does not have to get up."
3. **Medicine with care** (day 4, 12:01, Julian): "check the thermometer, read the cold-medicine label
   before taking a normal dose, and refill my water bottle."
4. **The power cut** (day 6, 19:02, Julian): "check that the kettle and stovetop are off ... then fetch
   the flashlight and bring everyone into the living room for a calm candlelit pause". Later
   (20:33): he moves the perishable food into the fridge and leaves the dishes in the sink unwashed.
5. **Packing for an errand** (day 2, 17:25, Mara): "carrying my canvas tote with my wallet inside and
   my house keys in my pocket."

**Wrong-looking**

6. **Putting down what is already down** (day 4, 17:38–17:42, Mara): she tries to put the notebook
   down three times.
   - Cause: she put the pen "on top of the notebook" she was holding, so the engine set the
     notebook down first. Her "so far you have" recap listed only her own action.
   - Fixed: the recap is now built from the engine's log and marks such steps.
7. **Asleep undressed on the floor** (day 2, night, Julian): his last activity ended before he put
   on pajamas, and the engine left him where he stood.
   - Fixed: whoever is home walks to their own bed at day end.
8. **Talking to herself** (13 times, Mara): every one was meant for Julian.
   - Fixed: a resident's list of people to talk to no longer contains themselves.
9. **Things inside things that cannot hold anything**, since household creation: a table knife
   inside a fork, a spoon inside that knife, a paring knife in a chef knife, cheese inside a tomato.
   - When Mara took the fork for lunch, the knife and spoon came along with it.
   - The model uses "inside" to mean "kept together with". Not fixed; a decision is needed
     (question 1 below).
10. **Wearing dirty clothes again** (day 4, 07:10, Mara): she takes the trousers and blouse from
    the hamper and puts them back on.
    - This home has no washing machine, so the clean/dirty cycle can never close here.

## What the skeptic found (checked against the files)

- **Spots far too full:**
  - 14 things in the kitchen sink basin (0.12 m²) on day 3, including a frying pan, a saucepan
    and a cutting board;
  - 10 on Julian's nightstand (0.25 m²);
  - the scene's own lamp and alarm clock already sit on some of these spots.
  Placing these in 3D will fail, so the engine needs a capacity per spot (area against object
  size).
- **`positions.json` lacks some fields:**
  - whether an object can hold things, and which door hides a cupboard spot. Both are now added
    for the next run.
  - the outline of the 46 spots taken from meshes, and of the floor spots. Not yet added.
- **The hidden flag is for an adult standing in the room, not the robot.**
  - 18 visible objects sit 1.5 m or higher.
  - 8 drawers belong to a solid bathroom cabinet that cannot open in the simulator.

## Decisions for Oliver

1. **"Inside" an object that cannot hold things.** The engine could read it as next_to, the
   bookmark-in-a-book kind excepted. Or creation could mark which objects can hold flat things.
   The guard you dropped blocked bags in bags; this one would block only forks and tomatoes.
2. **Spot capacity.** Should the engine refuse a put-down when a spot is full by area? That
   changes behaviour, and the model would then look for another spot.
3. **No washer in this home.** Options: rank homes with a washer higher in the survey, or treat a
   trip out with laundry as washing it.
4. **For the robot:**
   - which camera height to use;
   - whether the rule against opening drawers and cupboards still holds;
   - whether questions come during the day or only at day end (positions are written only at
     day end).
5. **Guests as people.** On day 6 the friend is fed and seen out, but has no body: a plate is set
   for them and no one uses it.
