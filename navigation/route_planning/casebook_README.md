# casebook.json: go_to failure cases for log-diagnosis tests

Built offline on Z690 by `casebook.py` (in this folder) on 2026-10-25. It covers 10-23 13:34 to 10-24 16:49.

## Contents
* **46 cases of kind `nav_failure`**: one per episode of `lab_nav_failures.jsonl`. The 90 records are merged into
  episodes when they have the same goal (within 0.3 m), a start within 0.5 m, and less than 120 s since the
  episode's previous record.
* **24 cases of kind `localization_event`**: 23 from the 5 Hz pose log, plus one "lost period" from cheetah's
  inbox note.

## Schema (one entry in `cases`)

| field | meaning |
|---|---|
| `id` | `E##` for an episode, `L##` for a localization event |
| `kind` | `nav_failure` or `localization_event` (`subkind` for events) |
| `t_start`, `t_end` | `{iso (local, with offset), epoch}` of the first and last record |
| `client`, `call` | always **null**. The failure log doesn't record them. Any failed `planner.plan()` with a live view writes a record, whether from `go_to` or a `GET /nav/plan` preview. |
| `args` | `goal_xy` as logged. `place_guess`: the saved place within 0.4 m in the *current* places file (inferred). |
| `result` | **null**. A failed plan makes `go_to` return `no_route`, or `blocked` after a replan; which one isn't logged. `planner_error` is the logged planner error. |
| `why` | the logged fields of the first record: `saved_map_has_route`, `cause`, `live_cleared_n`, `blocks`, `live_robot`, plus `live_new_n`. The full live cell lists are in the source log. |
| `n_records`, `record_ids` | the source records: 0-based line numbers in `lab_nav_failures.jsonl` |
| `sensor` | `map_pose_logged` (the planner's start). `poselog`: the nearest pose-log row within 5 s (map, odom, T, mapping). `loc_fit`, `track_fit`, `lost_flag`, `obstacle_ranges`: **null**, not logged on Z690. Live-new, cleared and block counts. Saved-map clearance at the start and goal. Which saved map and which planner version were live. |
| `true_cause`, `mechanism`, `evidence` | my diagnosis. `evidence` names files, fields and replay results. |
| `confidence`, `confidence_why` | high, medium or low, with the reason |
| `fixed_by` | `planner change 10-23 19:00`, `prototype C (proposed)`, `none…`, or `n/a` (map replaced) |
| `replay` | offline replay: `as_logged_fails`, `current_plans`, `proto_C_plans`, `in_lost_window` |
| `figure` | `figs/episodes/E##.png`, one per episode (first record) |
| `detail_figure` | a hand-picked example from `figs/`, when there is one |

Figure colours:
* black: mapped obstacle; tan: < 0.20 m from one; grey: unmapped;
* red: live cells not on the map; blue rings: blocks;
* green: saved-map route; magenta: proto C route; teal: the dog's trail over the last 5 min;
* cyan: the dog and a 1.2 m ring; orange ×: goal.

## Sources
* `~/oliver/go2_maps/lab_nav_failures.jsonl`: the failure records.
* `~/oliver/go2_maps/lab_poselog/2026102{3,4,5}.jsonl`: map pose, odom, T and the mapping flag at 5 Hz.
* Saved maps: `lab.grid.npz` (loaded 10-23 15:15:52), `history/lab_20261023_144422`, `history/lab_20261019_165417`.
* `~/oliver/go2_nav.py` (mtime 10-23 19:00:21) and the replay (`harness.py`, `diag.py`, `evaluate.py`), which
  establish which planner version and map each record ran on.
* `~/dynamic_home_eqa/coordination/inbox/z690/2026-10-24_1632_cheetah_agent-relocalize.md`: the 10-24 16:23 drop
  in track fit.
* Board archive #24, #28, #42: context for the blocks, the map history and old-map line-up errors.

## Caveats
* **Diagnoses come from an offline replay, not ground truth.** The replay injects the logged live-new cells and
  blocks. Cleared cells were logged only as a count, so none are cleared. The replay reproduces the logged failure
  for 88 of 90 records; records 1 and 2 don't reproduce.
* **Real objects and phantoms can't be told apart.** Whether live-new cells were real objects (chairs, people,
  the mop bucket) or lidar smear isn't determinable from these logs. Trail camera frames weren't checked, so those
  cases are at most medium confidence.
* **"Blocks are stall marks" is inferred from the code:** avoidance is always on, so `obstacle()` returns None
  ahead. It isn't a logged field.
* **Lost windows:**
  * 16:23:00–16:34:25 comes from cheetah's track-fit log plus the 3.19 m / −55° jump.
  * 16:44:00–16:45:36 is inferred only from the 0.7–1.0 m corrections right after.
* **Localization events:**
  * A `pose jump` is a single-step change of more than 0.3 m or 5° in the logged T.
  * `first map pose after none` means a pose reappeared: a session start, console restart or line-up. Its cause
    isn't logged.
  * Event kinds (`hand_placement`, `auto_align`, …) aren't in the pose log. Only 16:34:25 is labelled, as a
    probable hand placement, from the inbox note.
* **`place_guess` uses the current places file.** Places were moved on 10-23 15:49–15:54, so guesses for earlier
  records may name the wrong place.
* Times are Z690 local time (PDT).
