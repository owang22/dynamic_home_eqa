# Go2 localization in a cluttered lab: survey + staged plan (2026-10-22)

[U] = not verified from a primary source. All arXiv IDs below were checked against the arXiv API.

## 0. What the current stack actually feeds slam_toolbox (read from the go2-lab image, nesl/Go2Controller f7898ac)

- **Which dog:** `go2/README.md` says "the lab's Go2 **Pro**", connected over **WebRTC**. That matters: the Pro has no DDS/ethernet SDK, so the raw L1 stream (`/utlidar/cloud`, `/utlidar/imu`) that every Go2 FAST-LIO/Point-LIO recipe uses is **not available**. Those recipes all need the EDU (e.g. jizhang-cmu/autonomy_stack_go2 says "make sure to use the Go2 EDU"). Check this before planning around raw-cloud LIO.
- **The "lidar" is not a scan.** The driver subscribes to `rt/utlidar/voxel_map_compressed`, decodes it with `libvoxel.wasm`, and publishes `point_cloud2` in frame **`odom`**, stamped with the time it arrived (`now()`), not the sensor time (`ros2_publisher.py`). So it is the dog's own **accumulated, voxelized local map**, already registered by the dog's onboard odometry. It keeps "ghost" voxels where people and chairs used to be, and it has no per-scan structure.
- **Odometry:** odom->base_link comes from `rt/utlidar/robot_pose`, Unitree's onboard estimate (lidar/IMU/leg fused [U]). A Go2-EDU user measured the related `/utlidar/robot_odom` as stable: under 1 mm xy drift in 12 s while standing still ([mybotshop forum](https://forum.mybotshop.de/t/unitree-go2-l1-saved-map-localization-only-no-slam/1789)). Adding robot_localization EKF+IMU on top would mostly double-count IMU that is already fused, so expect little from it.
- **Flattening:** `pointcloud_to_laserscan` with `target_frame: base_link`, `max_height: 0.1`, and `min_height` at the default (about 0). The band is therefore **0-10 cm above the body**, roughly 0.3-0.45 m above the floor [U for body height]. That is chair-seat, bag, case, and desk-leg height: almost exactly the movable clutter.
- **slam_toolbox localization params** (`mapper_params_online_async.yaml`): `minimum_travel_heading: 0.5` rad and `minimum_travel_distance: 0.5` m mean a scan is only processed after about 29 deg of turn or 0.5 m of travel. So during a turn in place the correction lands in a few large steps. Other settings: `correlation_search_space_dimension 0.5`, `do_loop_closing: true`, `loop_search_maximum_distance 3.0`, `loop_match_minimum_response_fine 0.45`. In clutter-band scans, loop closure can snap to a wrong but similar-looking spot. That is a plausible mechanism for the ~1 m jumps.
- **L1 specs (Unitree manual / retailers):** 360x90 deg FOV, 21,600 effective pts/s (43,200 sampled), 0.05-30 m range at 90% reflectivity, about ±2 cm. Density is highest at the centre of the FOV. On the Go2 it sits on the head, which leaves a blind region near the body [U].
- **Caveat:** the control PC (`~/oliver/go2_*.py`) owns the live stack, and its parameters may differ from the nesl defaults above. Check them on the board.

### Likely causes of the reported symptoms, in order
1. **Map pose jumps ~1 m when turning in place.** slam_toolbox corrects map->odom in big steps (29 deg gating) and matches a clutter-height pseudo-scan built from a ghost-filled voxel map. It may also be closing a loop to an aliased spot. Leg slip during turns hurts much less here, because the onboard odometry is lidar-aided.
   - **First diagnostic:** bag `/tf`, `/odom`, `/scan`, and `/point_cloud2` while turning 360 deg on the spot, then plot odom->base_link and map->odom separately.
   - If odom->base_link is smooth and map->odom jumps, the problem is in the localizer. That is the likely outcome.
2. **"No route" near furniture.** This is mainly planner geometry: a 10 cm grid with 28 cm clearance, against a map where chairs were baked in as obstacles. Localization error makes it worse by putting the robot or goal into inflated cells. Re-making the map with clutter removed (below) helps both. `nav_proto.py`'s graded cost is the right fix for the planning side.

## 1. Lidar-side fixes and tools

**Cheap fixes on the current stack**
- **Raise the scan band** to roughly 1.3-1.9 m above the floor (above desks and chair backs, below the ceiling), i.e. `min_height`/`max_height` relative to base_link of about +0.9/+1.5 m. Walls, tall cabinets, door frames, and whiteboards dominate there.
  - Rebuild the map with the same band. Keep a separate low band (or the dog's own avoidance) for obstacles only.
  - Check L1 coverage at that height; the vertical FOV may make the high band sparse near the robot [U].
  - Robust-indoor-localization work does the same thing: rely on the high, permanent structure. See the Area Graph paper, arXiv 2308.05593.
- **Map with clutter removed:** build the map when the lab is tidy, then hand-erase movable objects in the PGM (chairs, cases, tripods). Clear the "unknown" status of furniture footprints for planning.
- **slam_toolbox localization:**
  - Set `minimum_travel_heading` to about 0.1-0.15 rad and `minimum_travel_distance` to about 0.1-0.2 m.
  - Set `do_loop_closing: false` in localization, or raise `loop_match_minimum_response_*` to about 0.6.
  - Increase `angle_variance_penalty` and `distance_variance_penalty` so the matcher trusts odometry more.
  - Alternatively swap to **Nav2 AMCL** (likelihood_field, `laser_max_beams` 60-120, low `alpha*` because odometry is good, `update_min_a` about 0.1). AMCL's corrections are smooth particle drift rather than graph snaps [U: community reports].
- **Jump gate:** reject any map->odom update that moves more than 0.3 m or 10 deg in one step while the robot moves less than that. Log it as an event.

**3D LIO and 3D map localization** (needs the raw cloud and IMU, i.e. EDU over DDS, or an external lidar)
- **Odometry:**
  - FAST-LIO2: arXiv 2107.06829, github.com/hku-mars/FAST_LIO.
  - Point-LIO: Adv. Intell. Syst. 2023, github.com/hku-mars/Point-LIO. Unitree's own L1 adaptation is github.com/unitreerobotics/point_lio_unilidar (ROS1 Noetic).
  - KISS-ICP: arXiv 2209.15397. Lidar-only.
  - DLIO: arXiv 2203.03749.
  - GLIM: arXiv 2407.10344, github.com/koide3/glim. GPU; can add camera constraints.
- **Localization on a saved 3D map:**
  - hdl_localization: github.com/koide3/hdl_localization (UKF+NDT).
  - FAST_LIO_LOCALIZATION: github.com/HViktorTsoi/FAST_LIO_LOCALIZATION, ROS1; ROS2 forks exist [U].
  - lidar_localization_ros2: github.com/rsasaki0109/lidar_localization_ros2. NDT/GICP/small_gicp backends, PCD map. Its global relocalization is experimental.
  - small_gicp (Koide 2024) + LIO publishing map->odom.
- **What is known to work on a Go2:**
  - CMU autonomy_stack_go2 (github.com/jizhang-cmu/autonomy_stack_go2): Point-LIO on the built-in L1 + IMU, Go2 EDU only. It does SLAM; no prior-map localization mode is described. It warns the L1 is "low-cost, high-noise", that obstacles should be >0.3 m tall, and that SLAM drift can make the robot stuck.
  - A Go2-EDU+L1 user ran Point-LIO mapping (fine, with occasional skewed walls) plus NDT scan-to-PCD localization. It drifted and jittered even when stationary; the user blames the L1's non-repetitive pattern. Accumulating 5 deskewed scans helped about 10x. No accepted fix ([forum](https://forum.mybotshop.de/t/unitree-go2-l1-saved-map-localization-only-no-slam/1789)).
  - Go2-W (arXiv 2606.21387) **removed the L1** and used a **Livox MID-360 + Jetson Orin NX**, with FAST-LIO2 at 10 Hz plus small_gicp GICP against the prior map at about 1 Hz. This is the most reliable pattern reported.
- **Takeaway:** L1-based 3D localization on Go2 is fragile in practice. The robust route is MID-360-class lidar + FAST-LIO2 + scan-to-map GICP (with deskewed multi-scan accumulation).
- **Cleaning dynamic objects out of a 3D map** (to build a static prior map):
  - ERASOR: arXiv 2103.04316.
  - Removert: IROS 2020, github.com/irapkaist/removert.
  - Dynablox: arXiv 2304.10049.
  - DUFOMap: arXiv 2403.01449.
  - LMNet moving-object segmentation: arXiv 2105.08971.
  - SuMa++ (semantics used to drop movable classes): arXiv 2105.11320.

## 2. Visual / visual-inertial relocalization

- **hloc** (Sarlin et al., "From Coarse to Fine", arXiv 1812.03506; github.com/cvg/Hierarchical-Localization). It chains:
  - retrieval: NetVLAD 1511.07247, or newer VPR models;
  - local features: SuperPoint 1712.07629 + LightGlue 2306.13643;
  - PnP against an SfM model.
  - Indoors, a good SfM model gives cm-to-dm accuracy [U for our setting].
  - Requirement: the reference images need accurate poses, e.g. COLMAP/GLOMAP SfM on a dedicated mapping walk, aligned to the 2D map. Trail frames posed by the current (bad) localization are not good enough.
- **VPR backbones for retrieval:** AnyLoc (DINOv2, 2308.00688), MixVPR (2303.02190), SALAD (2311.15937), BoQ (2405.07364), MegaLoc (2502.17237, a strong general retriever).
- **Map-free / foundation relocalization:**
  - The Map-free benchmark (2210.05494) shows metric pose from a single reference image is feasible but coarse.
  - DUSt3R 2312.14132, MASt3R 2406.09756, VGGT 2503.11651: relative pose and metric-ish depth from 2+ images.
  - Reloc3r (2412.08376): relative pose regression, fast.
  - These are good for "pose relative to the stored photo of place X", which is exactly the existing trail store. Recover metric scale from the lidar or from two reference frames.
- **Full SLAM with camera + lidar:**
  - RTAB-Map (arXiv 2403.06341) supports 2D/3D lidar + RGB, visual loop closure, localization mode, and a ROS2 Humble package. It is the lowest-effort way to add visual loop closures to a lidar-odometry graph.
  - ORB-SLAM3 (2007.11898) is mono/VI. Monocular at 73 deg HFOV without depth is weak for metric localization; use it only as a loop-closure source.
- **Fusion pattern:** keep the lidar/onboard odometry as the backbone. Add visual place matches as (a) global pose priors into AMCL (inject particles or reset), or (b) loop-closure factors in a pose graph (RTAB-Map, GTSAM). Gate them by geometric verification (PnP inliers) and odometric consistency.
  - CROSS (arXiv 2605.02227, NeurIPS 2026, real quadruped) shows how: each retrieval becomes a candidate pose, and a Gaussian-mixture filter keeps only branches consistent with odometry before accepting them.

## 3. Semantic / object-level localization and static-vs-movable reasoning

**Direct answer: yes, the VLM-labels-permanence idea has been done, on a quadruped in a lab.**
- **VLM-GLoc** (Agrawal & Hayes, CU Boulder, arXiv **2605.30506**, May 2026):
  - **Setup:** Go1 + RealSense D455 + VLP-16 in a 3,700 sq ft lab, on a slam_toolbox 2D map.
  - **Mapping:** Gemini annotates each frame with boxes, a rich label ("yellow JUSTRITE flammables cabinet"), and **permanence [Static]/[Quasi-Static]/[Dynamic]** plus a confidence. Dynamic and low-confidence items are dropped.
  - **Semantic map:** per pose cell (0.5 m, 24 headings), raycast the FOV and embed the concatenated descriptions with a LoRA-tuned MiniLM. Training uses "quasi-static dropout" augmentation that removes jackets, bags, and movable chairs.
  - **Online:** retrieve top-K pose cells to seed MCL particles, weight by semantic similarity, then add lidar weight once particles converge (or use lidar for reranking).
  - **Results, one month after mapping:** global localization 74% vs AMCL 4% and a fixed-class semantic PF 10%. Error at convergence about 0.5 m; tracking ATE about 0.41 m / 0.13 rad; tracking success 46%. Ablations: removing permanence tags -8%; no augmentation -18.75%.
  - **Cost:** cloud VLM latency 23 s per frame, so about 0.2 Hz.
  - **Read-out:** the VLM is a **global relocalization / disambiguation prior**, not a precise tracker. The lidar has to supply the cm-level part.
  - Their ceiling AprilTag ground truth had **0.75 m disagreement** between tags and was abandoned. Keep that in mind when designing ground truth (see section 4).
- **ShelfAware** (2512.09065, same group): semantic particle filter for quasi-static spaces; 97% global success in a mock store.
- **OMCL** (2512.15557, Bonn, RA-L): open-vocabulary features in MCL; can start from a language description.
- **VLG-Loc** (2512.12793): VLM global localization against a labelled footprint map.
- **SignLoc** (2508.18606): navigation signs + floor plans.
- **Zimmerman et al.:** text spotting for localization (2203.12647); semantic cues in floor-plan maps (2210.01456). Both are classic semantic MCL in changing indoor spaces. Room numbers and door signs are exactly the stable cues in a university lab.
- **Object-level SLAM and long-term object maps:**
  - QuadricSLAM 1804.04011.
  - Probabilistic Object Maps for long-term localization (Adkins, Chen, Biswas, 2110.00128): models object existence and position variance over time, i.e. semi-static reasoning.
  - ObVi-SLAM 2309.15268: long-term object-visual SLAM, multi-session.
- **Dynamic masking in visual SLAM:** DynaSLAM 1806.05620 masks people and other a-priori movable classes with Mask R-CNN plus multi-view geometry. Same idea as masking classes out of the lidar scan.
- **Persistence / long-term map maintenance:**
  - Krajník FreMEn (T-RO 2017; frequency models of cell or feature persistence) [U for exact venue/year].
  - Panoptic Multi-TSDFs (2109.10165).
  - Khronos (2402.13817): spatio-temporal metric-semantic SLAM.
  - Recent change detection: FOCUS 2610.05639, OASIS-Map 2607.14899.
- **Scene graphs:** Hydra (2201.13360), S-Graphs (2202.12197) / S-Graphs+ (2212.11770; walls, rooms, floors as landmarks for localization), ConceptGraphs (2309.16650). SG2Loc (2606.11880) does sequential visual localization on 3D scene graphs.
- **Language-to-map localization:** Text2Loc (2311.15977), VLM-Loc (2603.09826), Loc3R-VLM (2603.18002). These are meant for coarse localization from a description, not for robot tracking.
- **Can a VLM estimate pose directly?**
  - The one paper claiming 0.11 m from a fine-tuned Qwen2.5-VL regressor (arXiv 2607.01079, sim only) has been **withdrawn as irreproducible**.
  - "VLMs Can Describe, But Not Measure" (2609.28184) fits the broader picture.
  - Every working system uses the VLM for semantics and filtering and leaves geometry to registration.
- **VLM as a verifier:** "Breaking Déjà Vu" (2607.12818) puts a VLM after VPR retrieval to judge same place vs not, per match. It reports recall@1 +13.6%, false acceptance about 12%, and precision >95% at >75% coverage. This is the formal version of "compare the photo to the stored picture at this pose".

## 4. Staged plan for our stack

**Stage 0 - measure first (1 day)**
- **Ground truth:**
  - Tape 6-10 floor marks at surveyed map poses (tape measure from walls / laser distance meter), with known yaw.
  - Add 15-20 cm AprilTags on walls at 1-2 m from the stands, read by the calibrated 720p camera. Tag pose at short range is good to a few cm [U]. Avoid far or ceiling tags (see the VLM-GLoc caveat).
- **Metrics:**
  - (a) Error at marks: drive there, then compare the reported pose with the mark.
  - (b) Revisit consistency: same place visited N times, spread of the reported pose.
  - (c) Jump rate: number of map->odom steps >0.3 m or >10 deg per hour, and per 360 deg turn in place.
  - (d) Time-to-localize from an arbitrary start.
  - (e) Route success near furniture.
- **Bag the turn-in-place test** to locate the jump (see section 0). Log map->odom continuously in `log_events.py`.

**Stage 1 - cheap, high yield (days)**
1. Raise the scan band to walls-and-cabinets height. Rebuild the 2D map in a tidy lab and hand-erase movable items.
2. slam_toolbox localization: smaller travel thresholds, loop closing off, heavier odometry trust. Or switch to Nav2 AMCL with likelihood_field. A/B both on the Stage-0 metrics.
3. Add the jump gate. Keep "start at the defined spot" as an automatic initial-pose prior, not a requirement.
4. Planner: graded cost (`nav_proto.py`), and a stand choice that tolerates about 0.2 m of localization error.

**Stage 2 - visual relocalization from the existing trail (1-2 weeks)**
- Do one clean mapping walk and get accurate poses via SfM (hloc/COLMAP) aligned to the 2D map.
- Build a MegaLoc/SALAD index over the frames.
- On demand, and whenever jump/lost is detected:
  - retrieve top-k;
  - get the pose with SuperPoint+LightGlue PnP (or MASt3R/Reloc3r relative pose, with scale from the reference frames);
  - check odometric consistency, then publish `/initialpose` (AMCL) or a map->odom correction.
- Optionally use RTAB-Map (camera + lidar scan) in localization mode as an off-the-shelf alternative.

**Stage 3 - where the VLM adds value (research angle)**
- **(a) Recovery prior:** VLM-GLoc-style rich descriptions with permanence tags give top-K pose hypotheses to seed AMCL when lost. Latency of seconds is fine for recovery.
- **(b) Pose verification:** after reaching a place, compare the live photo with stored frames at that pose. Use VLM same-place judgement (2607.12818) plus a LightGlue inlier count, and trigger relocalization on disagreement. The agent already does this informally; formalize it with logged precision and recall.
- **(c) Static-landmark selection:**
  - Use the VLM or an open-vocabulary detector (cheap, every frame) to label movable objects in camera frames, project the masks onto the lidar points (calibrated camera, 73 deg FOV), and drop those points from the scan and the map. Only the front sector is covered, so treat it as best-effort.
  - Offline, label map cells or voxels as structural vs quasi-static, and down-weight quasi-static cells in the likelihood field.
- **(d) Static prior map:** keep only VLM-confirmed static structure (walls, cabinets, door frames, whiteboards) plus geometric persistence across sessions (FreMEn / POM-style).
- **Novelty check:** VLM-GLoc already covers permanence-tagged semantic MCL. Room left for a contribution:
  - per-point masking of lidar evidence by VLM permanence (VLM-GLoc only filters the semantic channel);
  - persistence learned across sessions and checked against VLM priors;
  - VLM-gated verification of pose-graph closures on a legged robot with a weak lidar.

**Stage 4 - if still unsatisfactory: hardware**
- Mount a Livox MID-360 + Jetson Orin NX: FAST-LIO2 + small_gicp scan-to-map localization at about 1 Hz (the Go2-W recipe).
- If the dog really is EDU, first try Point-LIO on `/utlidar/cloud` with multi-scan accumulation before buying hardware.
