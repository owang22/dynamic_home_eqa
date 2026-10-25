# lab_history: synthetic lab histories for memory tests

The plan and the model of the lab are in `../README.md` ("Lab history generator"). This folder holds the code and a
one-week example.

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
| `example_7d/` | one week, seed 0, one shift (day 4, a Friday), 30 questions |

**Output files:** `events.jsonl` (`id, t, place, x, y, text`; `t` is epoch seconds), `events_truth.jsonl`
(per event: what was really there, missed, misnamed, invented), `truth.jsonl` (where every person and object was,
as intervals), `routines.json` (every routine and shift in words), and `questions.jsonl`. Question kinds:
`where_now` (with the dog's last correct sighting and `stale` when it no longer holds), `last_in_lab`, `desk_now`,
`usual_place`.

**Not settled yet (waiting on cheetah):** the 16 real places (stand-in list in `world.py`; pass the real one with
`--places places.json`), the exact event fields of `go2/memory_lab/data.py`, and the style of `text`.

**Defaults:** 5 people, 20 objects. Shifts on evenly spaced days, each moving one person's desk and changing two
objects' routines. Per object and workday: 5% put somewhere else, 2% taken out. Camera: 12% of objects missed, 15%
misnamed, 3% of looks invent an object. Patrols at 09:30, 13:30 and 17:30 on workdays (dock + 6 places each),
noon on weekends, and an extra 2-place look on 30% of workdays.
