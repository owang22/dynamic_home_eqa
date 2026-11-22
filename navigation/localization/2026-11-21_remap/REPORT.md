# Lab remap from the 11-16 to 11-21 recordings, with a tag survey (offline, 2026-11-21)

Candidate only. Nothing live was touched: no writes to `~/oliver`, no POST, no container or GPU use.
Everything is under `~/go2_overnight/remap_1121/`.

**Ready-to-swap set:** `final/` holds `lab.grid.npz`, `lab.places.json`, `lab_objects.json`, `lab_keepout.json`,
`lab_markers_survey/`, `moves_old_to_candidate.tsv` and `old_vs_candidate.png`. Internal name: `maps/cand_r2_recent`.

## Method
1. **Extract** (`extract_sqlite.py`): plain Python over rosbag2 sqlite with zstd.
   - 29 sessions have lidar. Five 4-minute stands from today have 0 clouds.
   - 8 sessions recorded after 18:05 were held out as unseen.
2. **Graph** (`graph_1121.py`): October gates.
   - Metric odometry with K = 1/0.864.
   - Nodes every 0.3 m / 10° / 10 s.
   - Scans use fresh wall-band voxels (≤ 20 s old, 60 s fallback); first-cloud voxels are excluded.
3. **Initial poses** (`track.py`): offline scan-to-old-map tracking, seeded by the console pose log.
   Its fit beats the live poses in every session.
   - The first solve misplaced six sessions: 132441, 171906, 175716, 115804, 161344 and 155228. Their scans fit the
     others' map at only 0.39–0.72, and in three of them tag A appeared 1.4–1.8 m from where every other session
     puts it.
   - `fix_bad.py` re-localised them on the map of the 23 good sessions, using their own tag-A sightings, the live
     pose or a global search. They now fit at 0.87–0.93.
4. **Solve** (`solve_1121.py`, wrapping `../remap/solve.py`): KD-tree pairs; no marker factors; per-session
   odometry scale free.
   - Run r2: 23.4k scan edges, 7.6k of them across sessions; final node move p50 0.03 m, max 0.14 m.
   - Odometry scale median 1.009 × K, so odom ≈ 0.856 × true. The tape says 0.864.
5. **Grid** (`rebuild_1121.py`): votes come only from fresh voxels placed at the solved pose at their birth. Each
   session votes into its own ±5 score.
   - **Combine rule "recent":** within a day, scores are summed and clipped. Each cell then takes the value of the
     newest day with |score| ≥ 2; otherwise it keeps the overall sum.
   - Furniture follows the newest look, and no single session can erase a wall. On unseen sessions this rule scores
     0.900, against 0.883 for a plain sum.
6. **Frame** (`align.py`, `pin_frame.py`): a similarity fit of stable walls (occupied on ≥ 2 days) gives
   old = 0.896 × candidate.
   - The candidate stays metric. It uses the similarity rotation and is pinned at the centroid of the saved places.
   - The old map is internally bent: dominant wall direction 51.5° in most of it, 37.5–38.5° for x > 2 and y < 0.
     The candidate is 45.5° throughout.
   - Wall residual, candidate to old (p50 / p90 by distance from the places centroid):

     | distance from centroid | p50 | p90 |
     |---|---|---|
     | < 2 m | 0.05 m | 0.11 m |
     | 2–4 m | 0.05 m | 0.21 m |
     | 4–6 m | 0.07 m | 0.35 m |
     | 6–9 m | 0.28 m | 0.53 m |

7. **Moves** (`moves.py`): places, objects and keep-outs move by the local node correction (old → candidate), as in
   `rebuild_v2`. Places move 0.27–0.81 m.

## Scale vs tape
- **room_A** (nav-planner `tape_checks_1030` rule): 9.894 m vs tape 9.925 m, ratio **0.997** (p10–p90
  9.86–10.52). The old map gives 9.30 (0.937).
- **Tag A face runs** (facing −131.6°):
  - far cabinet end 2.28 m vs 2.235 m;
  - water-cooler end 1.04 m vs 0.94 m.
- **A→cabinet is not usable:** the ray hits clutter in the aisle, giving 2.2 / 4.06 / 3.48 m depending on the facing.
- No extra scale correction was applied.

## Tag survey (model cal_f788; `out/survey_cand_r2_recent.json`)

Gates: view ≤ 30°, range ≤ 3 m, ambiguity < 0.5, reprojection ≤ 2 px, edge ≤ 0.85, side ≥ 30 px, turning ≤ 10°/s.
The lens is taken 0.30 m ahead of the solved pose.

| tag (id) | x | y | facing used | IPPE / wall | n (sessions) | spread p50 / p90 |
|---|---|---|---|---|---|---|
| A (0) | 1.345 | 0.395 | −131.6 | −131.6 / −145.5 | 26216 (20) | 0.030 / 0.067 |
| B (1) | −0.654 | −4.395 | 38.3 | 54.9 / 38.3 | 5280 (12) | 0.033 / 0.076 |
| C (2) | −6.858 | 1.331 | 46.2 | 46.2 / 50.1 | 1191 (4) | 0.017 / 0.060 |
| D (3) | 0.535 | 2.890 | 48.1 | 48.1 / 68.8 | 1642 (7) | 0.034 / 0.050 |

- **Facing choice:**
  - A: IPPE, because its face runs match the tape.
  - B: wall, which agrees with the 10-26 survey (42.3°).
  - C: the two estimates agree.
  - D: IPPE, because the tag sits 0.17 m in front of any wall line.
- Per-day medians are stable; no tag moved.
- **Range scale k (1 = consistent with the metric lidar map):**

  | model | A | B | C | D |
  |---|---|---|---|---|
  | pinhole79 | 1.03 | 1.04 | – | – |
  | calibrated | 0.925 | 0.94 | 0.905 | 0.895 |
  | cal_f788 | 0.98 | 1.02 | 0.92 | 1.09 |

- The **calibrated model (fx 864) reads 6–10% long**, which agrees with the tape (pinhole79 = 0.985 × tape).
- **Pinhole79 ignores the barrel distortion (k1 = −0.35).** Off-axis it reads tags long, with a wrong view angle.
- **cal_f788** combines the calibrated distortion with fx = fy = 788.4 (the 79° pinhole focal / 0.985 from the tape).
- Tag positions under the three models differ by only 1–8 cm.

## B / tag_B ids
**The physical tag at door_outside is id 1** (detected at −0.65, −4.40).
- id 2 is at the stairwell door (C), and id 3 is near desk_joseph (D). id 4 is never seen.
- The live hand entries are off by one: tag_B → 2, tag_C → 3, tag_D → 4. As a result, the live table puts id 2 (C) at
  B's spot and id 3 (D) at C's spot, about 7 m off.
- `final/lab_objects.json` corrects the ids (`aruco_id_was` keeps the old value).

## Validation
Unseen sessions:
- 174819 and 180548 were in the solve but excluded from voting in `cand_r2_ho`;
- 181107, 181651, 184015 and 184434 were recorded after the build.

### (a) Lidar fit
Console wall likelihood (σ 0.08) after a ±0.2 m / ±2° search.

| area | old | cand_ho (unseen) | candidate | candidate, sum rule |
|---|---|---|---|---|
| desk (617 views) | 0.859 | 0.901 | 0.896 | 0.881 |
| far desks (82) | 0.786 | 0.943 | 0.930 | 0.901 |
| all (700) | 0.850 | 0.906 | 0.900 | 0.883 |

In-sample (today: 155228, 172113, 174049):

| area | old | candidate |
|---|---|---|
| desk | 0.859 | 0.959 |
| sofa / conference | 0.783 | 0.933 |
| far desks | 0.791 | 0.915 |

The unseen sessions never went near the sofa.

### (b) Tag A vs lidar (unseen sessions, console gates, about 1500 sightings)

| detector model | old map + live table | candidate + survey |
|---|---|---|
| pinhole79 (deployed) | p50 0.37 m (96% ≥ 0.30) | p50 0.25 m (0.3% ≥ 0.30) |
| cal_f788 | 0.16 m | 0.066 m |

- The patrol stands see A at 0.68 of the half-frame, where pinhole79 is 0.25–0.29 m off and cal_f788 is 0.04–0.09 m
  off.
- The "old 1.6 m" figure in the in-sample json is the offline old-map track misplacing 155228. Ignore it.

### (c) Places
- All 17 are on free floor, with clearance 0.14–0.66 m. The tightest are desk_kang, desk_brian, desk_pragya and
  desk_joseph, at 0.14–0.15 m.
- The keep-out moves to (−6.70, 1.82) and still covers C.
- The route planner was not run.

### (d) Picture
`final/old_vs_candidate.png`. `out/recent_vs_sum.png` shows the cells the newest-day rule changed.

## Uncertain
- **The A→cabinet span is not reproducible**, so the scale rests on room_A, the face runs and the odometry-scale
  agreement.
- **The frame diverges from the old map by 0.3–0.5 m beyond 6 m** from the places centroid, because of the old map's
  scale and bend.
- **Today's lidar is thin:** five stands have no clouds.
- **Some survey numbers are weak:** B and D facing are uncertain by about ±10°. C has only 4 sessions. cal_f788 is
  constructed, not calibrated.
- **There may be other misplaced sessions:** six were caught. All sessions now average ≥ 0.83 fit.

## Recommendation
**Swap, as one deploy (safe procedure):**
1. grid;
2. places;
3. keep-out;
4. objects;
5. markers survey.

Also:
- Remove or rename `lab.session.json`; T and odom in the grid are old-frame. Line up fresh.
- Anything else storing map xy is stale: patrols, `lab_prior`, proposals.
- **Fix the tag ids now, even without the swap.**
- The remaining tag-A suspect gap is the camera model. Either gate fixes to edge ≤ 0.5, or move go2_markers to a
  distortion-aware model with the tape focal. That needs Oliver's OK.

## Rerun
`run_solve_r2.sh`, then `./finalize.sh r2`. `final/` was assembled inline from `cand_r2_recent` with the facing
choices above. `extract/` (39 GB) can be deleted.
