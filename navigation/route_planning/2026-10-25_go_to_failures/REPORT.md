# go_to route failures: offline analysis and planner prototypes (night of 10-24 to 10-25)

Everything here ran offline on Z690. I sent nothing to the dog and used only read-only GETs on the console
(one `GET /state.json` to confirm the loaded map: `saved_at 2026-10-23 15:15:52`). I didn't edit `~/oliver`.
The prototypes are copies in `proto/` on Z690 (`~/go2_overnight/route_planning/`); their diffs are in `proposed/` here. **Proposed, not deployed.**

## TL;DR

* The log has **90 records but only 46 episodes**. Agents retry every ~2 s, and batches of goals are tried 0.05 s
  apart (previews or candidate viewpoints).
* **Half the log (45 records, 10-23 13:34–18:55) predates the 10-23 19:00 planner change** (speck filter and
  `squeeze`). Replaying those records with the old planner reproduces 43 of the 45 failures. The current planner
  plans 41 of the 45. The 36 "narrow aisle on the saved map" failures are **already fixed**. The 4 it still fails
  are on maps that are no longer loaded.
* **The current planner fails all 45 records logged since 10-23 19:00. The replay reproduces 45 of 45.** Root causes,
  by record:

  | cause (since 10-23 19:00) | records | episodes |
  |---|---|---|
  | localization lost (10-24 16:23–16:34 and just before the 16:45 correction) | 15 | 8 |
  | start pocket: the dog stands where the only exit is under 0.20 m, and the squeeze retry isn't allowed within 1.5 m of the dog (`door_outside`) | 11 | 5 |
  | temporary blocks (stall marks, 0.15 m discs) close an aisle the saved map has open | 11 | 3 |
  | live cells and blocks: each alone closes the route | 5 | 3 |
  | live-lidar cells alone close the route (2 wall-hugging, 1 free-standing) | 3 | 2 |

* **Scoring (rescored 10-25 at the coordinator's request, `rescore.py`, `results/rescore.md`).** A planner change
  can't fix a failure caused by a wrong pose. In the 15 lost-window records, any route returned was planned from a
  wrong map position, so it counts as a **harm**; the correct outcome there is no route or a lost report.
* **Prototype C** (planner fallback tiers plus a "walked-trail" squeeze exit):
  * **fixes 26 of the 30 non-lost failures**;
  * **harms 13 of the 15 lost-window records**: it returns a route from the wrong pose;
  * changes **no normal route** (0 changes over all 240 place-pair plans in the clean and live scenarios).
* C may only ship together with a lost gate: skip the fallback tiers and the trail, and report "localization lost",
  whenever `mapper.lost_since` is set. With the gate the harms would be 0, *if* the lost flag fires. That flag was
  added 10-25 01:20, after these events, and track fit isn't in the Z690 logs, so this is untested. Cheetah's logger
  shows fit 0.44–0.59 from 16:23, below `LOST_FIT` 0.65, so it would probably have fired for 69–81. Unknown for
  82–83.
* C also fixes a systematic asymmetry. It also fixes a systematic asymmetry: every
  place can drive *to* `door_outside` with a squeeze route, but nothing can be planned *from* `door_outside`.
  That's 15 of the 240 place pairs, and it is the cause of the 10-24 15:28 failures.
* **Main risk:** a fallback route may pass about 0.1 m from unconfirmed live obstacles. Its last tier ignores the
  2-minute stall blocks, so when an object really blocks the only way, the dog walks up to it again. On a wrong pose
  it plans confidently (13 harms above). The dog's
  avoidance and the stall → replan loop (max 3) then end it with `blocked` instead of an instant `no_route`.
  Pair it with the agent-side changes below: don't place blocks for stalls with nothing in front, and say "lost"
  instead of `no_route`.

## 1. Data and how the replay works

* `harness.py`: a `FakeMapper` (score, seen, mid, origin) and `load_planner()`. `set_situation()` rebuilds a
  record's planner state:
  * the logged `live_new` cells are injected exactly (through `live_over`, which bypasses the saved/1.2 m test, so
    the same cells get added);
  * the logged blocks are re-added with r = 0.15;
  * the 0.35 m footprint around `live_robot` is cleared.

  The live **cleared** cells were logged only as a count, so the replay clears nothing. That reproduces the logged
  failure in 88 of 90 records, so the injected state is what closed the route. (Upper bound with every saved
  obstacle within 3 m cleared: 44 of 45 era-2 records would pass. Not a realistic scenario.)
* **Which map:** `map_for_time()` picks the map the console had loaded at the record's time:
  * before 10-23 14:44:22: `history/lab_20261019_165417`;
  * until 15:15:52: `history/lab_20261023_144422`;
  * after that: `lab.grid.npz`, which is byte-identical to `lab_straightened` and is still loaded. `lab_clean` was
    never loaded.
* **Which code:** `variants_check.py` shows which planner version matches the logged
  `saved_map_has_route` verdicts.
  * Records 0–44 (before the `go2_nav.py` mtime, 10-23 19:00:21) match a planner **without** the speck filter: 43
    of 45 agree. With the speck filter only 4 of 45 agree.
  * Records 45–89 match the current file: 45 of 45.
  * The replay also implies no squeeze retry before 19:00.
  * So era 1 = old planner (`SPECK_CELLS=0`, no squeeze) and era 2 = the current planner.
* **Localization:** I found jumps of the map←odom T in the 5 Hz pose log (`tjumps.py`). That gives the 10-24
  16:34:25 hand placement (3.19 m, −55°) and the 16:45:17–35 corrections (0.7–1.0 m, −48°). Cheetah's 10-24 16:32
  inbox note says the track fit fell to 0.44–0.59 at 16:23. Records in those windows count as "lost".
* `diag.py` computes, per record:
  * clearance at the start and goal;
  * the widest-path bottleneck on the saved map and with live cells;
  * the saved-map route and which live cells sit on it;
  * whether live alone or blocks alone close the route;
  * the fraction of live cells hugging a mapped wall (≤ 0.1 m), which is the signature of a pose offset or smear.

  Output: `diag.jsonl`.

## 2. Failure breakdown (all 90 records)

Full table: `results/categories.md`. Per record: `results/categories.json`, with cause, mechanism, episode and
whether current or proto plan it.

| cause | mechanism | records | episodes | current plans | proto C plans |
|---|---|---|---|---|---|
| narrow aisle on saved map (era 1) | smear specks pinch aisles to a 0.14 m bottleneck < 0.20 m `tight`. **Fixed 10-23 19:00** (speck filter + squeeze) | 36 | 16 | 36 | 36 |
| start pocket | exit < 0.20 m within 1.5 m of the dog: squeeze isn't allowed there | 11 | 5 | 0 | 9 |
| temporary blocks close the aisle | the stall marks (0.15 m + 0.20–0.28 m clearance) close an aisle open on the saved map; live cells alone don't | 11 | 3 | 0 | 11 |
| localization lost | live cells and blocks seen from a wrong pose | 10 | 6 | 0 | 9 (on a wrong pose!) |
| obsolete map (14:44 unstraightened save) | batch of plans 40 s after saving the drifted mapping-drive map; superseded at 15:15 | 8 | 8 | 5 | 5 |
| live cells + blocks | each alone closes the route; free-standing live cells | 4 | 2 | 0 | 4 |
| localization lost | the dog's pose is inside a mapped obstacle (clearance 0) | 4 | 1 | 0 | 4 (on a wrong pose!) |
| live cells close the route | wall-hugging cells (95% within 0.1 m of mapped walls) narrow the door corridor | 2 | 1 | 0 | 0 |
| obsolete map + localization (10-19 map) | 251 live cells, 77% hugging walls: map/pose mismatch | 1 | 1 | 0 | 1 |
| live cells close the route | free-standing cluster about 1 m ahead | 1 | 1 | 0 | 1 |
| live cells + blocks | wall-hugging | 1 | 1 | 0 | 1 |
| localization lost | goal (−6.5, −5.0) is off the map | 1 | 1 | 0 | 0 |

Contributing factor: in 9 records the goal itself is on a mapped obstacle, with clearance 0. Snapping handles
that today; none fails for that reason alone. No record failed because the start cell was blocked: the 0.8 m
step-out works. The "start in an obstacle" cases are all mislocalized.

### Example records (figures in `figs/`)

Figure key:
* black: mapped obstacle; tan: < 0.20 m from one; grey: unmapped;
* red: live cells not on the map, pink their 0.20 m band; blue rings: blocks;
* green: saved-map route; magenta: proto C route; teal: the dog's map trail over the last 5 min;
* cyan: the dog with a 1.2 m ring; orange ×: goal.

* **Narrow aisle (era 1).** `figs/09_*`, `figs/20_*`.
  * #9, 10-23 15:59:14, (0.89, −0.28) → `desk_joseph`. The saved map's bottleneck is 0.14 m.
  * #20, 18:39:06, (1.87, −0.25) → `desk_joseph`, same bottleneck.
  * The old planner fails both. Current and proto plan them at 0.28 m once the specks are filtered.
* **Start pocket.** `figs/60_*`, `figs/46_*`.
  * #60, 10-24 15:27:57: the dog stands at `door_outside` (0.15, −2.95), aiming for `door_stairwell`.
  * The pose log shows it had just walked 4.3 m into the pocket, so it got in on a squeeze route. Leaving needs
    the same 0.14 m pinch, which is within 1.5 m of the dog, so only 0.20 m is allowed there.
  * The same happens for all 15 `door_outside → *` pairs on the clean saved map (see 4).
  * #46 (10-23 19:36, (1.43, −1.69) → `door_outside`) is **not** fixed: the dog stands in a pocket that the map
    shows closed on all sides. That is a pose or map inconsistency.
* **Blocks close the aisle.** `figs/52_*`, `figs/87_*`.
  * #52, 10-23 19:39:12, (2.18, −0.30) → `water_cooler`. The blocks at (1.75, −0.49) and (1.72, −0.06) are
    0.5 m ahead, the "not making progress" placement. Together they close a 0.9 m aisle.
  * #87, 10-24 16:49:49 → `conference_table`: one block plus a few live cells.
  * Avoidance is always on, so `obstacle()` never reports anything ahead. **Every block is a stall mark**, and the
    known right-front-foot drag causes stalls with nothing in front.
* **Live cells + blocks.** `figs/85_*`: #85, 10-24 16:49:45, (−0.05, 3.24) → `podium`. Free-standing live
  clusters 0.6–1.1 m away and one block. Either alone closes the route.
* **Wall-hugging live cells.** `figs/66_*`: #66, 10-24 15:28:42, (0.70, −2.50) in the door corridor →
  `door_stairwell`. 95% of the new cells lie along mapped walls, so the corridor's walls appear shifted inward.
  That is heading drift or smear.
* **Lost.** `figs/72_*`, `figs/78_*`.
  * #72, 10-24 16:24:44: the dog's map pose is *inside* mapped furniture, with 77 live-new cells and 3 blocks.
  * A hand placement 10 minutes later moved it 3.2 m and −55°.
  * Planning "succeeds" here only on a wrong pose. The right answer is "relocalize".
* `figs/00_*`: #0, 10-23 13:34, on the old 10-19 map: 251 live cells hugging walls (map/pose mismatch).

### Other observations
* **`go2_agent.py`: the overhead (desk-top) live layer is always empty.** `_update_live` assigns `over` only when
  `BUMP_H[1] (0.6) <= h < OVERHEAD_MAX (0.6)`, which never happens. Desk tops at about 0.75 m don't block routes,
  despite the comment. If that's intended, delete the branch. If not, set `OVERHEAD_MAX` to about 0.9. Not tested.
* **`_why_failed` tests the saved map at 0.28/0.20 only, not squeeze.** A saved map whose only route is a squeeze
  is logged as `cause: "saved map"` even though the planner could use it.
* **The log can't separate previews from `go_to`.** It has no `source` field (`go_to` / `/nav/plan`) and no client,
  and both repetition patterns above are visible. Neither can be told apart.
* **Systematic pessimism (idea, not tested).** Occupancy is pooled with "any of 4" from 5 cm to 10 cm, and
  clearance is measured centre to centre. Together these make aisles look up to about 5 cm narrower per side.
  Computing `dist` on the 5 cm grid would widen every aisle by a few cm.

## 3. Replay harness

* `evaluate.py` re-runs every record on:
  * the planner as logged (era-appropriate);
  * the current planner;
  * prototype variants.

  It writes `results/replay_results.jsonl` (routes included) and `results/replay_summary.txt`.
* For each route it also measures how close it passes to the logged live cells and blocks.
* `diag.py` gives the per-record mechanism, `categorize.py` the categories, `figures.py` the PNGs.
* `allpairs.py` and `arrival_trail.py` are the regression checks.

Run them with `~/miniconda3/envs/go2/bin/python <script>`. Order: `diag.py` → `evaluate.py` → `categorize.py` →
`figures.py`, then `allpairs.py`.

## 4. Prototypes and results

`proto/go2_nav.py`, as `proto.diff`, about 100 changed lines in the planner. Three independent pieces:

1. **Fallback tiers (`FALLBACK_TIERS`).** These run only when the normal plan (tier 0, all three radii) fails, and
   only when there are live cells or blocks. Tier 0 is unchanged. The live overlay is kept in parts (saved and
   cleared, live-new, blocks, footprint), so the tiers can rebuild the grid without re-reading the map.
   * Tier `thin_live`: live obstacles not on the saved map still block, but the route may pass them at squeeze
     distance. In code: `dist = min(dist_mapped, dist_live + 0.16)`, with live cells themselves at 0.
   * Tier `thin_live_noblocks`: the same, with the temporary blocks ignored.
   * A route from a tier is marked `"fallback": <tier>`.
2. **Trail squeeze (`set_trail`, `TRAIL_R` 0.20 m).** On the squeeze retry, cells within 0.20 m of where the dog
   walked recently are exempt from the "≥ 0.20 m within 1.5 m of the dog" rule. The 0.12 m minimum still holds.
   The replay feeds the last 5 min of pose-log map poses.
3. `SNAP_REACHABLE` (off by default). When everything fails, drive to the reachable cell nearest the goal, within
   1.2 m, at 0.20 m clearance, and mark the route `goal_cut_off`.

### On the 45 records since 10-23 19:00 (`results/rescore.md`, `results/replay_summary.txt`)

Fixes count only among the 30 non-lost records. A route returned in the 15 lost-window records is a harm.

| variant | fixes (of 30 non-lost) | harms (of 15 lost) | routes entering a logged live cell | routes entering a logged block disc |
|---|---|---|---|---|
| current | 0 | 0 | – | – |
| A: trail only | 6 | 0 | 0 | 0 |
| B: tiers only | 16 | 13 | 0 | 16 |
| **C: tiers + trail (recommended, with the lost gate)** | **26** | 13 (0 with a working lost gate) | **0** | 19 |
| **C gated** (`fallback=False` while lost, replayed) | **26** | **0** | 0 | 19 |
| C2: like C but blocks "thin" instead of dropped | 20 | 10 | 0 | 6 |
| D: C + reachable-goal snap | 28 | 14 | 0 | 19 |
| E: drop live cells beyond 0.6 m (instead of thin) | 27 | 13 | **16** | 17 |

The trail alone (A) causes no harm: in the lost windows the dog had no trail into a squeeze pocket. All the harms
come from the fallback tiers.

`tier_grid.py` has more tier designs. The pattern:
* blocks are the main closer: removing blocks helps more than anything done to the live cells;
* "thin" live cells get almost the same success as dropping them, without ever routing through one.

C's 4 remaining non-lost failures:
* #46/47: the pose sits in a pocket the map shows closed.
* #66/67: wall-hugging cells narrow the door corridor below squeeze. Only dropping live cells (E) passes.

In the lost windows C still returns no route only for #71 and #81. That is correct, but by luck.

Era 1 under C: 42 of 45, against 41 for current.

### Normal routes, all 240 ordered pairs of the 16 saved places on `lab.grid.npz` (`results/allpairs_summary.txt`)

| scenario | current: ok | proto C: ok | differences | notes |
|---|---|---|---|---|
| clean (no live view) | 225 | 225 | **0** | same paths; mean length 5.34 m; min clearance median 0.22 m, p10 0.22 m |
| live view consistent with the map | 225 | 225 | **0** | identical |
| + 12 phantom cells 0.4–1.2 m from the start | 217 | 225 | 8 (all fallback) | lengths and clearance of the common routes unchanged |
| + a real 0.4 × 0.4 m object 1 m along the route | 121 / 209 | 148 / 209 | 27 (all fallback) | routes within 0.15 m of the object: 7 → **34** (the risk) |
| arrived at the start along a planned route (trail), clean map | 225 | **240** | 15 | all 15 are `door_outside → *` |

* The 15 clean failures are all `door_outside → *`, while every `* → door_outside` succeeds by squeeze. That is
  the asymmetry the trail fixes.
* With D's snap as a last resort, the clean and live results are also identical.
* Plan time on the failure situations: median 19 → 23 ms, worst 68 → 155 ms (3 extra tiers × 3 radii).

## 5. Recommendation

**Deploy (planner):** `proto.diff` with `FALLBACK_TIERS` as in the file (C) and `SNAP_REACHABLE = False`. Deploy it
**only together with agent item 3 as a gate**: no fallback tiers and no trail while `mapper.lost_since` is set.
Without the gate it would have produced 13 wrong-pose routes on 10-24.
* Lowest risk: tier 0 is untouched, so nothing changes unless today's planner would have said `no_route`. That's
  verified: 0 differing routes in the clean and live all-pairs runs.
* The trail only acts on the squeeze retry and needs `set_trail`. Without it, the change is inert.

**Deploy together (agent, `proto_agent.diff`, written but NOT run; it needs ROS):**
1. Record map poses in `update_live` (5 min). Clear them when a line-up moves the dog more than 0.3 m. Pass them
   with `planner.set_trail()`.
2. On a stall, block only if the lidar sees something in the front box, via `obstacle(1, force=True)`, which
   ignores the avoidance flag. Otherwise retry without a block. With avoidance always on, today every block is a
   stall mark, and 16 of the 45 failures involve them.
3. When a plan fails while `mapper.lost_since` is set, say so: `reason: "localization lost: relocalize first …"`
   and `loc_lost: true`. 15 of the 45 recent failures were planning on a wrong pose, and the fallbacks would
   happily plan there too. **Required for C, and implemented:** `planner.plan(..., fallback=False)` skips the tiers, the trail and the snap.
`proto_agent.diff` passes `fallback=self.mapper.lost_since is None`. Replay with the gate set on the lost-window
records: 26 of 30 fixes, **0 of 15 harms**. That assumes the flag is set in those windows.

**Risk notes:**
* A fallback route can pass about 0.1 m from a live obstacle that may be real (a chair, a person, the mop
  bucket). The dog's avoidance has to handle it. In the real-object test this happened in 27 of 209 pairs, where
  today the dog would refuse.
* Tier 3 ignores the 2-minute blocks. If the thing is real, `go_to` walks up to it again. The replan loop caps
  that at 3 more attempts before `blocked`. Item 2 above makes blocks real obstacles, which makes dropping them
  rarer and more justified. With item 2 deployed, consider removing the `noblocks` tier (C2 numbers).
* Trail squeeze lets the dog leave a pocket at 0.12 m clearance near itself. It will turn in place in a tight
  spot (right-front-foot drag), and backing up remains avoided. It's only as good as the pose that wrote the
  trail; that's why the trail is cleared on line-up jumps.
* Consider a slower speed on `fallback` and `squeeze` legs. Not implemented.
* `SNAP_REACHABLE` (D) adds 3 more successes, but they end up to 1.1 m from the goal. Off by default; use it only
  if arrival checks (vision) confirm the view.

**Logging to add** (makes future replays exact):
* `live_cleared` cells, not just the count;
* the live obs and free sets (capped);
* `source` (`go_to` / `/nav/plan`) and the client;
* `loc` fit and lost;
* the tier and radius tried;
* the trail;
* a planner version (file mtime or hash).

Also include squeeze in `_why_failed`'s saved-map check.

## 6. What I tested and what I didn't

**Tested, offline only:**
* the planner and prototypes on all 90 logged situations as far as the log allows;
* reproduction of the logged failures: 88 of 90;
* all-pairs regression on the saved map in 5 scenarios;
* the arrival-trail scenario;
* timing;
* `py_compile` of both prototype files.

**Not tested:**
* anything on the dog, or the `go_to` loop dynamics: following, replans, avoidance behaviour on fallback routes;
* the agent patch (needs ROS and the console) and the `OVERHEAD_MAX` observation;
* the live cleared cells, which weren't logged (the replay assumes none);
* whether the live cells in each record were real objects or phantoms. Only the geometry hints at it; the trail
  camera frames could settle it and weren't examined;
* whether the "pocket" situations (#46/47) were map errors or pose errors;
* the 5 cm-grid clearance idea.

## Files
* `REPORT.md` (this file)
* `proto.diff` and `proto/go2_nav.py`: planner prototype, recommended configuration C
* `proto_agent.diff` and `proto/go2_agent.py`: suggested agent changes, untested
* `harness.py`, `diag.py`, `evaluate.py`, `categorize.py`, `figures.py`, `render.py`, `allpairs.py`,
  `arrival_trail.py`, `tier_grid.py`, `variants_check.py`, `tjumps.py`, `replay.py`: harness and analysis scripts
* `results/`: categories, replay results, all-pairs results, timing; `results/rescore.md` (fixes vs. harms, `rescore.py`)
* `casebook.json`, `casebook_README.md`, `figs/episodes/`: one case per failure episode plus localization events (`casebook.py`)
* `figs/`: rendered example situations
* `orig/`: the untouched copies used as the baseline
