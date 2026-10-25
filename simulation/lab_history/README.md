# lab_history: synthetic lab histories for memory tests

The plan and the model of the lab are in `../README.md` ("Lab history generator"). This folder holds the code and ready-made
runs.

```
python -m simulation.lab_history.generate --days 60 --seed 0 --out /data/oliver/simulation_out/lab_history/d60_s0
python -m simulation.lab_history.check /data/oliver/simulation_out/lab_history/d60_s0
```

Run from the repo root. Standard library only. 60 days take under a second.

| file | does |
|---|---|
| `world.py` | the hidden lab: places, people (desks, hours, work-from-home days, absences), objects and their routines, routine shifts |
| `generate.py` | the dog's patrols and what the camera reports (misses, wrong names, invented objects), truth intervals, questions |
| `check.py` | checks one output against its world: truth covers every minute, event texts match the truth, routines hold |
| `runs/d{30,60,90}_s{0,1,2}/` | ready-made runs: 30, 60 and 90 days, seeds 0-2, default settings, 300 questions each (7.8 MB in all) |
| `runs_preshift/` | the same 9 histories, questions from day 3 on (`--questions-from 3`), so about 30% fall before the first shift |

**Output files:**
- `events.jsonl`: one per place the dog looked at, in the event format of `go2/memory_lab/data.py`: `id, t,
  real_t` (equal), `kind` ("picture"), `source` ("sim_patrol"), `x, y, yaw_deg` (facing the place's target),
  `place, place_m, path` (null), `seen` (a describe dict: `summary, objects [{name, colour, on, across}], people,
  people_notes, states`), `describer` ("sim"), `text` (`data.line(seen)`). `t` is epoch seconds.
- `events_truth.jsonl`: per event, what was really there, and what the camera missed, misnamed or invented.
- `truth.jsonl`: where every person and object was, as intervals.
- `routines.json`: every routine and shift in words.
- `questions.jsonl`: each has its own `t`, the "now"; use only events up to it. Kinds: `where_now` (with the dog's
  last correct sighting, and `stale` when that no longer holds), `last_in_lab`, `desk_now`, `usual_place`.

**Places:** the 16 real lab places from `go2/memory_lab/places_2026-10-25.json` (default). Desks are `desk_*`. The
conference table is the meeting place, the water cooler is where cups go back, the sofa is the lunch spot, and the
two doors are never used for objects. `--places standin` uses the made-up list in `world.py`. The simulated people
are fictional (Alice, Bob, ...) and are given desks at random. A desk's name says whose it really is, not who sits
there in the simulation.

**Defaults:** 5 people, 20 objects. Shifts on evenly spaced days, each moving one person's desk and changing two
objects' routines. Per object and workday: 5% put somewhere else, 2% taken out. Camera: 12% of objects missed, 15%
misnamed, 3% of looks invent an object. Patrols at 09:30, 13:30 and 17:30 on workdays (dock + 6 places each),
noon on weekends, and an extra 2-place look on 30% of workdays.
