# Under desks and chairs: the live view's blind spot, and a fix (10-25, nav-planner)

Offline only. Nothing in ~/oliver or the console was touched. Diffs against the live files of 10-25 06:15
(go2_nav f33b1ec6, go2_agent b44f8267, go2_dashboard a6cc3db6) are in `deploy/`, built by `build_deploy.sh`.

## Findings

1. **The 10-23 incident is not confirmed.** There is no pose log before 14:29:11 and no lidar before 14:31.
   The only candidate drive, 13:30:42–13:31:30, matches a straight `go_to desk_gaofeng` on the 10-19 map. That
   looks like an arrival facing the desk, not a shortcut. The 10-19 map is about 24.5° rotated from today's
   (`register.py`, fit 0.68 vs 0.38).
2. **With the saved map alone, no route goes under a solid desk top.** That holds for the era-1 planner on the
   10-19 map (182 pairs) and for today's planner on today's map (240 pairs): 0 m in the middle of routes. The
   saved map holds legs, drawers and chairs at 0.2–0.6 m.
3. **The live view drops every cell whose highest point is 0.6–1.0 m.** `on_cloud` keeps each cell's highest
   point, so a chair with a back, or anything under a desk top, is invisible to the planner. In the 14:31 bag
   (`chairs.py`, 84 moments):
   - about 370 dropped cells within 3 m at each moment, 54% of them chair-like and 46% under desks;
   - 0.4–1.2 m from the dog, where new live obstacles count, and shown open on the saved map: 13.8 chair-like
     and 5.8 desk cells per moment;
   - today's route from that moment to each place drives over a hidden one in **7 of 1291** routes, all
     chair-like (2 of them start at desk_pragya, 1 in the desk aisle to B).

## Fix (deploy/)

- `go2_dashboard.on_cloud`: for a cell whose top is 0.6–1.0 m, it also checks whether any point sits at bump
  height (0.18–0.6 m).
  - If one does, the cell goes in `under_obs`.
  - If not, it goes in `under`.
  - The cost is +0.1 ms per cloud (3.7 → 3.8 ms for the cell code, `test_oncloud.py`). The output matches the
    simulator on 68/68 clouds.
  - Both lists are left out of the `/state.json` and `/events` snapshot (they would add 18%).
- `go2_agent._update_live`:
  - `under_obs` cells become ordinary live obstacles (the saved-map / ≤1.2 m rule) and are also passed as
    `hard`. `under` cells become a cost.
  - The dead `OVERHEAD_MAX` branch is replaced by `UNDER_TOP_MAX = 1.0`.
  - `go_to` replies now carry `fallback` when any plan in the drive used a fallback tier.
- `go2_nav`:
  - `set_live(..., under=, hard=)`.
  - `hard` cells are left out of the tiers' relaxable set (`new_m`), agreed with loc-research. `test_tiers.py`:
    0 of 14,167 hard cells are relaxable, even with the thin tier switched on.
  - `under_cost` is added to `cost_near`: `UNDER_COST` 3 per live under-top cell, plus `MID_COST` 3 on the saved
    map's solid desk-top layer (`MID_FILL` ≥ 60% fill, cached per map version). Both are grown by 0.15 m.
  - It is never an obstacle. The live `over` set stays empty.

## Numbers (rebased code with fallback tiers, `plan()`)

| test | current | band + cost + solid layer (deploy) | hard block (OVERHEAD 1.0-like) |
|---|---|---|---|
| 240 pairs, clean / live / live + stall block: routes changed | – | **0 / 0 / 0** | 0 / 57 / 63 |
| 240 pairs: routes lost | – | 0 | 0 / 5 / 5 |
| 240 pairs: fallback tier used (live + block) | 99 | 99 | 97 |
| bag replay (1291 plans): routes lost | – | 1 | 77 |
| bag replay: routes changed (>0.3 m / >1 m) | – | 271 (28 / 16) | 804 |
| bag replay: drives over a hidden obstacle | 7 | **0** | – |
| bag replay: body under a desk top, m | 0.3 | 0.2 | 6.6 |
| stale map (under-desk obstacles erased): body under a desk top, m | 15.5 | **1.5** | 105 |
| CPU per plan, median clean / live / live + block | 7.7 / 9.2 / 17.0 ms | 8.2 / 9.8 / 17.6 ms (+4–7%) | – |

- **Live-only band rule on the stale map.** Without the layer cost, the band rule alone (cost 3 or 10) makes
  the stale map worse: 26.7–34.4 m under desks. Chairs it now sees close the normal-clearance route, and the
  `tight` route crosses the erased desk underside beyond the 3 m live range. The saved desk-layer cost fixes
  this. Note that the stale test's truth is that same layer, so `MID_COST` is graded against its own input.
- **Changes in the bag replay.** The 271 changed routes come from the chairs that are now visible. `tight`
  routes rise from 161 to 233, because chairs really are there. Layer cost alone (`midsolid3`) changes only 3
  of 1291 routes and fixes the stale case (0.3 m). It's the minimal under-desk fix, but it leaves the chair
  blind spot.
- **Lost route, open question.** The 1 lost route is bag moment 700 at (1.64, −1.13), in the desk aisle, to
  door_outside (marker B). Today it plans only at `tight` clearance (2.66 m). The band rule's newly visible
  chair cells close it, and the fallback tiers don't relax them (bonus 0, and hard). On 10-23 the dog drove
  this aisle (13:22 and 13:37 trail), but with a chair at a desk edge, so whether it truly fits is unverified.
  It needs a look before deploy.
- **Console page.** The `live` overlay will show about twice as many `new` cells (19 → 40 median), because
  chairs are now visible.

## Files

`livesim.py` (exact on_cloud + _update_live replay of the bag), `eval_bag.py`, `eval_pairs.py`, `chairs.py`,
`blind.py`, `test_tiers.py`, `test_oncloud.py`, `payload.py`, `make_stale.py`, `register.py`, `results/`.

## What to watch on the first drive (deployed 10-25 06:25)

1. The console's live overlay shows about twice as many red "new" cells near the dog. These are office chairs and things under desks, which the planner couldn't see before.
2. Routes avoid passing under desks and tables (a cost, not a block), so a few routes swing wider around desk rows.
3. A desk aisle that used to work may now give `no_route` when a chair sits at its edge. On the 14:31 replay the aisle to marker B, at (1.6, −1.1) towards door_outside, closes when the black chair at the left desk is out: about 0.3 m of gap against the dog's 0.31 m width. Push the chair in.
4. More routes are planned with `tight` (0.20 m) clearance next to chairs: 161 → 233 of 1291 in the replay.
5. go_to replies now carry `fallback` when a plan had to ignore the 2-minute stall blocks. That should be rare in open areas.
6. If the dog seems to avoid open floor for no reason, look for a chair back or a table edge there in the frame.
7. To undo the under-desk cost only: UNDER_COST = 0 and MID_COST = 0 in go2_nav.py. To undo chair visibility too, revert go2_agent/go2_dashboard (deploy/*.diff).
