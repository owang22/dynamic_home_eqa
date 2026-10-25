# Ablation of the deploy package (10-25)

Run with `ablate.py` from `route_planning/` → `ablation.json` and `ablation_summary.txt`. It covers the same 30
non-lost records since 10-23 19:00 and the 480 normal plans: 240 place pairs × (clean, live view consistent with
the map). The base is the patched live files, with live-new cells injected as lidar obstacles, the 5-min pose-log
trail, and lost not set.

| variant | tiers after tier 0 | fixes / 30 | records fixed | tier that fixed them | normal plans changed / 480 | closest any route gets to a live cell (route→cell centre) |
|---|---|---|---|---|---|---|
| A: trail squeeze only | – | 6 | 60–65 | tier 0 + trail: 6 | 0 | 0.55 m |
| B: A + ignore blocks (live cells at full clearance) | `live_noblocks` | **21** | 48–65, 87–89 | trail: 6; `live_noblocks`: 15 | 0 | 0.14 m (#51); others ≥ 0.21 m |
| C: B + live cells at 0.20 m (fixed, any radius) | `live_noblocks`, `live20`, `live20_noblocks` | 21 | same as B | same as B; `live20` adds nothing | 0 | as B |
| D: full package as first proposed (thin = squeeze distance) | `thin_live`, `thin_live_noblocks` | 26 | B + 45, 68, 84, 85, 86 | trail: 6; `thin_live`: 2; `thin_live_noblocks`: 18 | 0 | 0.07 m |

**The coordinator's bet is right.** B gets 15 of D's 18 `thin_live_noblocks` fixes (#48–59, #87–89) with live
cells at full clearance. The blocks were the trap. The remaining 3 (#84–86) plus D's 2 `thin_live` fixes (#45, #68)
need live cells passed at squeeze distance.

But "live cells were smear" isn't supported. In #84–86 the camera shows a real wooden panel with cables where the
cell is (`frames.md`), and the cells near the B fixes include the mop bucket and cardboard boxes. **No checked frame
showed a cell to be smear.** C's 0.20 m clearance fixes nothing beyond B.

**The agent stall rule** ("block only if the lidar sees something ahead"):
* It changes nothing in any variant in the replay: A 6/6, B 21/21, C 21/21, D 26/26 with and without it. **It isn't
  needed for any fix.** The `live_noblocks` tier is what fixes the block traps.
* The model is weak. A logged block is kept if a logged live cell or a mapped obstacle lies within 0.30 m of it.
  The lidar view at stall time wasn't logged.
* Under that model the rule keeps 38 of 45 blocks: the lab is cluttered and most stall spots are near something.
  The blocks it drops (#60–65's) weren't on those routes.
* The rule still changes behaviour on the robot (fewer phantom blocks), but nothing here measures that. Keep it or
  drop it on its own merits.

**Recommendation:** deploy B. It's now the default `FALLBACK_TIERS` in `deploy/patched/go2_nav.py` and
`deploy/go2_nav.diff`. Leave the thin tiers out. They're still selectable, but in 3 of the 5 cases only they fix,
they'd brush a real panel.
