# In-person trial: evidence memory on the Go2 (script for the lab)

Based on the simulation (RESULTS.md). One person stays next to the dog whenever it moves; obstacle avoidance on.

## The method to run (the strongest one in the simulation)

1. **Visit the same places on a schedule.** 5-6 places the 0.4 m camera sees well: floor under a desk with a
   bag, a low shelf or bench with tools, the water cooler (tilt up), the door, an open floor area, a second desk.
   Not desk tops or counters: from its 0.4 m stands the simulated dog saw 6-26% of the counter, table and desk
   tops on the patrol (render/spot_views_0p4.json).
   Same stand and angle every time (patrol positions, or mark the floor with tape if driving by hand). One round
   every 45-60 minutes; 5 rounds.
2. **Keep every picture.** A day is a few MB. In the simulation, keeping only the pictures marked important lost
   16 points against keeping all (Opus, questions a fixed answer sheet cannot get, 2 SE 11), mostly on look-back:
   the detail asked later is usually in a picture nobody marked. The importance marks are still worth writing:
   with Qwen answering, at the same budget they beat random before/after pairs on the "when" and "what was going
   on" questions (+25, 2 SE 15, one random draw).
3. **After each round, write a change note per place** against the previous picture of that place: what changed,
   importance 0-3, a guess at what happened. The local Qwen writes these (`lab.py update`); a "usually here"
   note per place is rewritten each round.
4. **Answer with the strongest model reading all the notes and opening up to 6 pictures** (`lab.py ask`, Opus by
   default). On the questions a fixed answer sheet cannot get, Opus answering from the same Qwen-written memory
   scored 47 points above Qwen (2 SE 13), and 30 above Qwen shown exactly the right picture (2 SE 15). With Qwen
   answering, memory beat a fixed answer sheet by 12-26 points on those questions, and at 0.4 m not at all.
5. **Every answer gives the two visits that bracket the change, the pictures used, and "cannot tell" when no
   picture covers it.**

## Commands

```
# pictures: go2/data/patrols/2026-10-20/<HHMM>/<place>.jpg  (patrol output, or hand-driven snapshots saved the same way)
nohup go2/evidence_memory/serve_vlm.sh > go2/evidence_memory/logs/vlm_server.log 2>&1 &     # local Qwen, ~2 min
edit go2/evidence_memory/lab/people.txt        # who sits where, what their things look like (keys, bag, mug ...)
python go2/evidence_memory/lab.py update go2/data/patrols/2026-10-20     # after each round
python go2/evidence_memory/lab.py ask "Did anyone leave without something they usually take?"
python go2/evidence_memory/lab.py ask "..." --memory captions --answerer qwen     # the plain baseline, for comparison
```

## Staging (a second person stages; the truth sheet stays hidden until the end)

| between | change | what it tests |
|---|---|---|
| round 1 | nothing staged: the lab as it is | the "usually here" baseline |
| 1 -> 2 | A's bag and jacket leave from under desk A; A's keys stay on the floor or low shelf by the desk. The water cooler's empty light comes on. | left behind (keys); a second clue that may explain it (gone to refill water) |
| 2 -> 3 | Screwdrivers, a handful of screws and a half-opened device appear on the low shelf / bench. The door is propped open. | the screws case (a detail asked later); when did the door open |
| 3 -> 4 | A's bag returns; the keys are picked up; the cooler light goes off (bottle replaced). A box appears on the floor. | returns; whether the robot links them to round 2 |
| 4 -> 5 | The device is put back together and taken away; one screw is left behind. The door is closed. | something still out of place; a small thing a caption may skip |

Write on the hidden sheet the real clock time of every change.

## Questions (ask after round 5; do not tune them on the answers)

1. Did anyone leave without something they usually take? What, where, and between which visits? (keys, rounds 1-2)
   The simulation could not test this one (its left-behind questions were not valid); this is its first real test.
2. Looking back at round 3: were there screws next to the screwdrivers? (yes)
3. What was going on at the bench between rounds 2 and 3? (taking a device apart)
4. When did the water cooler's light come on, and what might the person have done? (rounds 1-2; refilling water)
5. When was the door propped open, and when was it closed? (2-3; 4-5)
6. Is anything still out of place now? (the screw)
7. Who does the bag under desk A belong to, and when was it away? (from people.txt; rounds 2-3)
8. Was there a mug on the top of the tall cabinet at round 2? (a place the robot never sees: "cannot tell")
9. Two questions written by the stager after seeing nothing but the truth sheet (unplanned questions).

## What to compare and how to score

- Same pictures, three memories: (a) captions only, Qwen answering; (b) change notes + every picture, Qwen
  answering; (c) change notes + every picture, Opus answering (the method above). Also write down, before
  asking, what a person would answer with no memory at all ("no", "cannot tell", "cooking" at the kitchen):
  in the simulation that fixed sheet scored as well as every Qwen memory.
- Each answer: right / wrong on the main fact; time bracket right or not; the cited picture really shows it;
  says "cannot tell" for question 8.
- Expect from the simulation: (c) clearly best; (a) and (b) close to each other and not far above the fixed
  sheet; all weak on "who" (people are never in the pictures; the people sheet is the only link).
- The trial is small (about 10 questions), so it shows whether the method works on real pictures, case by case,
  not a precise score. Record every answer in `lab/asked.jsonl`.
