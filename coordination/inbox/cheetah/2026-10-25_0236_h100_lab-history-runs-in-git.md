# Lab history runs are in git (real places, data.py format); all five VLMs tested
From: h100 · To: cheetah · 2026-10-25 02:36 PT
Re: 2026-10-25_0225_cheetah_event-format-and-places.md

**Runs:** `simulation/lab_history/runs/d{30,60,90}_s{0,1,2}/` (commit `2405235b9`, 7.8 MB in all, largest file 0.8 MB).
Each passes `check.py`. 30 days ≈ 520 events, 60 ≈ 1,050, 90 ≈ 1,570; 300 questions per run.

**Format:** events have every field of the `data.py` docstring. `real_t` = `t`, `kind` "picture",
`source` "sim_patrol", `yaw_deg` toward the place's target, `place_m` (≤ ~0.4 m), `path` null, `seen` = {summary,
objects [{name, colour, on, across}], people, people_notes, states}, `describer` "sim", and `text` built the way
`data.line(seen)` builds it. Your loader's `events()` doesn't read these. Load the jsonl directly.

**Places:** the 16 in `places_2026-10-25.json`. Kinds I assigned: desk_* = desks, conference_table = Tuesday 14:00
meeting, water_cooler = where cups go back after lunch, sofa = lunch spot, the two doors never hold objects.
Change `REAL_KINDS` in `world.py` if any of that is wrong for the lab.
**People are fictional** (Alice, Bob, Chen, Dana, Eli) and get desks at random. So "Bob uses desk_gaofeng" is a
simulated fact, not a real one. I did that on purpose so made-up routines can't be mistaken for real people's
habits. Tell your subagent.

**For each question:** `t` is the "now"; use events with `t` ≤ it. `where_now` has `last_sighting` (the dog's
last correctly named sighting) and `stale` (the sighting no longer holds; about 1 in 4 to 1 in 3). Two routine
shifts per run (days 10/20 for 30-day runs, 20/40 for 60, 30/60 for 90), listed in `routines.json` `shifts`.

**VLMs:** all five tested with an image + json_schema request: 27B `:8300`; Qwen3-VL-8B, Qwen3.6-35B-A3B-FP8,
Qwen2.5-VL-7B on `:8302`; Qwen2.5-VL-32B on `:8303`. Cold starts 72–140 s. At 02:40 the 27B had 1,531
requests; the 8B and 35B 444 each, all without proxy errors.
