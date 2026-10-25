# Deploy package for review: trail squeeze + "ignore stall blocks" fallback (updated 10-25 after the ablation)

**Change since the first version of this file.** The default `FALLBACK_TIERS` is now variant **B**: trail squeeze
plus one tier that ignores the temporary blocks, with live obstacles at full clearance.
* The ablation (`ablation/ABLATION.md`) found that the thin-live tiers add only 5 fixes.
* In 3 of those 5 the live cell is a real wooden panel (`ablation/frames.md`).
* The thin tiers are still in the code (`LIVE_THIN_BONUS`) but are off.

**Overhead cells and nav-planner's `under_cost` design.** The tier split never adds an obstacle; this is new in
this version.
* Inside the tiers, `hard` and `new_m` are both subsets of tier-0 `occ` (nav `_grid`, lines ~144–158).
* A `live_over` cell that is already an obstacle in tier 0 is excluded from the relaxable set, so it stays hard
  in every tier. That is today's code, where overhead cells are obstacles.
* A `live_over` cell that is not an obstacle stays free in every tier, and its `under_cost` (in `cost_near`, owned
  by nav-planner) still applies. That is nav-planner's design.
* Tested in `overhead_rule_test.txt`, with a stand-in copy where overhead cells aren't obstacles: tiers 0–2 add 0
  obstacles in both designs. Overhead cells are 16/16 blocked in today's design, and in the stand-in only the 5
  that were obstacles anyway.

**Files**
* `go2_nav.diff` and `go2_agent.diff`: made against the live `~/oliver` files, which are still identical to the
  copies in `live/` at 03:xx (`go2_nav.py` mtime 10-23 19:00, `go2_agent.py` mtime 10-25 02:30).
* `patch -p1 --dry-run` passes on fresh copies, and so do the real apply and `import go2_nav, go2_agent`.
* `patched/` has the results.
* Edit boundary kept. Not changed: `_update_live`, `update_live`, `set_live`, the live-view block in `_grid()`
  (`live_over` handling), `MID_BLOCKS` / the mid layer, `cost_near`.
* `self.live_over` is only read, to decide which tier-0 obstacles are excluded from relaxation. Some hunk context
  lines sit next to the `MID_BLOCKS` and `live_over` lines; re-run `patch --dry-run` after nav-planner's diff.

## Lost gate: the live one, reused

Live since 02:16:
* `GO_TO_STOP_WHEN_LOST` (agent line 46) makes `tick()` (agent line 250) raise `lost` while a `go_to` runs and
  `mapper.lost_since` is set.
* `tick()` runs before the first motion command in `_follow` / `_turn`, so a `go_to` started while lost plans once,
  then stops without moving.

The patch adds no second agent gate. The planner reads the same flag (nav line 331). While it is set, `plan()` runs
tier 0 only, without the trail, which is exactly today's planner. That also covers `/nav/plan` previews.

## Tiers in order (`FALLBACK_TIERS` nav line 51, loop at nav line 334, grids from `_set_tier` at nav line 172)

All tiers try radii 0.28, then 0.20, then 0.12 (squeeze, only beyond 1.5 m from the dog). They share the same goal
snap, step-out, graded cost (`cost_near`, unchanged, including any `under_cost`) and shortcutting.

A later tier runs only if every radius of the earlier one found nothing, the dog isn't lost, and there is a live
view or a block. A route from a later tier is marked `"fallback": "<tier>"`.

| # | name | relaxes | never relaxes | what the dog would do differently |
|---|---|---|---|---|
| 0 | `live` | nothing: identical to today | – | the same routes as today; 0 of 480 normal plans changed |
| 1 | `live_noblocks` | **ignores the temporary blocks** (`block()`, 0.15 m discs, 120 s) | saved-map obstacles, all live lidar obstacles (full clearance), overhead obstacles, unknown cells | may **walk back to the spot where it stalled less than 2 minutes ago**. Live obstacles the lidar sees there keep full clearance. In the replays, routes stay ≥ 0.21 m (route to cell centre) from live cells, except #51 at 0.14 m. `go_to`'s replan cap (3) still ends a real blockage with `blocked` |

**Trail squeeze** applies inside every tier, at the squeeze radius only (`_plan`, nav line 381; `TRAIL_R` 0.20 at
nav line 52). Cells within 0.20 m of where the dog walked in the last 5 min are exempt from the "≥ 0.20 m within
1.5 m of the dog" rule. The 0.12 m minimum stays.
* What the dog does differently: it **can leave a narrow pocket the way it came in, at 0.12 m from mapped
  obstacles near itself**.
* `door_outside → *`: 0 of 15 today, 15 of 15 after arriving along a planned route.
* Expect a turn in place in a tight spot (the right-front-foot issue). No reversing is planned.

Optional, off (`LIVE_THIN_BONUS`): the thin tiers `("thin_live", 0.16, True)` and `("thin_live_noblocks", 0.16,
False)`. They pass unconfirmed live obstacles at squeeze distance, about 0.07 m in the replays. Not recommended
(see the ablation).

**Agent changes** (`go2_agent.diff`, outside the live-view code):
* **Trail recording** in `map_pose_now()` → `_note_trail()`: at most every 0.2 s, kept 300 s, cleared on a line-up
  jump over 0.3 m. Passed to the planner before each `go_to` plan.
  * Only agent tools call `map_pose_now`, so console (human) driving leaves no trail.
  * The planner keeps the last trail it got, which previews also use.
* **Stall blocks:** `_follow` tags a stall `stall: True`. `go_to` marks a block only if `obstacle(1, force=True)`
  sees something in the front box, and places it there; otherwise it retries without a block.
  * **The ablation shows this rule isn't needed for any replay fix:** 0 change in A–D. The `live_noblocks` tier
    does the work.
  * It's still a behaviour change worth considering (fewer phantom blocks), but it's separable. Dropping it from
    the diff wouldn't change the numbers below.

## Results (`eval_deploy.json`, default tiers = B)

The replay model is the same as before:
* logged live-new cells injected as lidar obstacles;
* `mapper.lost_since` set in the 15 lost-window records. The live `tick()` gate stops motion; the planner gate is
  checked directly.

| | live planner | patched, lost flag set | patched, lost flag not set |
|---|---|---|---|
| fixes among 30 non-lost | 0 | **21** (48–65, 87–89) | 21 |
| routes returned in 15 lost-window records | 0 | **0** | 6 (69, 70, 77–80) |
| plan time on these situations, median / p95 | 24 / 66 ms | 22 / 53 ms | 21 / 97 ms |
| normal plans changed (240 pairs × clean/live) | – | **0 / 480** (re-checked after the overhead change) | – |
| all-pairs plan time, median / p95 | – | 10 / 50 ms | – |
| arrived along a route (trail), clean map | 225 / 240 | 240 / 240 (same tier-0 trail code as before) | – |

How the 21 fixes split: trail squeeze 6 (60–65), `live_noblocks` 15 (48–59, 87–89).

## The 9 non-lost failures it doesn't fix

* **#46/47** (pinch at (1.15, −2.15), 0.54 m from the dog, at its own earlier stall point; the trail doesn't cross
  it) and **#66/67** (wall-hugging live cells fill the corridor's only 0.14 m gap). Same as before; details in
  the previous section of the report.
  * No safe planner fix for #46/47.
  * #66/67: "trail clears live cells in fallback tiers" fixes both offline. It's untested on the robot and not in
    the diff.
* **#45, #68, #84, #85, #86** need live cells passed at squeeze distance (thin tiers).
  * #84–86: the camera shows a real wooden panel with cables at the cell. Not fixing them is correct.
  * #45, #68: unclear from the frames.

## Not tested
* Anything on the robot.
* nav-planner's real `under_cost` patch: only a stand-in, where overhead cells are not obstacles.
* `tick()`, read from the code.
* The stall rule on real clouds.
