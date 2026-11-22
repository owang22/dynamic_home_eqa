# Patrol brain (cheetah side): first design, 2026-11-21 (draft, not built)

The patrol brain picks what the dog looks at next and why, compares each new view with past pictures, updates
memory, and writes a round report. Z690 owns safety, motion and geometry: the patrol envelope, `/agent/view`,
candidates and route costs (Z690 proposal, inbox 2026-11-21 16:10; reply draft `reply_to_z690_DRAFT.md`). The
brain never decides anything about safety. A refusal is final: the brain drops that candidate and logs the `why`.

## What the data says (why the design looks like this)
- **Coverage is the main gap, not detection.** In the 34 hand-labelled object tracks (33 runs each,
  `frontier_baseline/research/objsearch/tracks/*.json`), 33% of object-runs never viewed the object's spot at all
  (status `not_seen_spot_not_viewed`). The average place was out of view 68% of active time
  (`go2/data/memory_lab/grounded/visibility/REPORT.md`).
- **Natural change is sparse and tied to people.** There were 0 relocations over 9 weeks; changes are appear or
  disappear (Oliver's taxonomy, 11-20). Using the tracks, I counted seen-vs-viewed-absent flips per viewed run pair
  (11-21, quick count, biased sample: the `pm_*` tracks were picked as movers). Desks with personal things flip
  0.10-0.13 (desk_pragya 11/86, desk_oliver 13/134, desk_khang 3/27). Furniture spots, the sofa, the podium, the
  water cooler and the stairwell door flip 0/20-46.
- **Height matters.** Most of the planted 11-16 movers sat on tabletops, out of sight of the 0.4 m dog camera.
  Opus found 2-4 of the 11 logged changes per run (`days/planted_1116/RESULTS.md`). About 10% of described
  landmarks lie where the 2-D map says the view is blocked. The L515 at about 0.68 m saw the water bottle (#11).
- **Per-frame vision is not the frontier edge.** On identical 3-frame montages, Opus scored 0.85 balanced accuracy
  on absence and the 8B scored 0.83. Opus's edge on removals is choosing which views to compare across days
  (`research/objsearch/FINDINGS_1120.md`). In the 11-20 night eval, more looking without better targeting did not
  raise accuracy (27B with a 60-call budget, the 8B evidence gate; `night-1120-eval` notes). So view selection is
  the part to test, not assume.
- Poses wobble about 0.5 m / 9 deg within a patrol, and heading drifts +6 to +19 deg over a walk. A change note
  must compare views that overlap, not views with the same nominal pose.

## The loop (one round)
1. **Read.** `/patrol/views` + `/patrol/check` (Z690), plus cheetah memory: every past frame with its pose
   (`deep_sandbox/frames.json` format: id, t, run, x, y, heading_deg), L515 frames (`rs_depth_index.json`), the
   SigLIP crop/tile index (`research/objsearch/crops_emb.npy` + `crops_meta.jsonl`), the change log (below) and the
   map grid with height layers.
2. **Candidates.** Z690's set (places, dwell spots, sampled cells), plus cheetah's own:
   - target-centred views of spots memory is unsure about: P(still there) falling, or "possibly gone" after a miss.
     The code is `go2/console/view_plan.py` (rings around a target; fix its HFOV from 73 to 79 deg) and
     `go2/lab_agent/memory_instances.py`.
   - the stalest cells.
   All candidates go through `/patrol/check` before scoring.
3. **Score** (computed in code from data, one unit, so no hand-set weights between terms):
   `value(c) = Σ_cells p_detect(c, cell) · q_cell / t(c)`, which is the expected number of so-far-unnoticed
   changes the view would show, per second.
   - `q_cell` = P(the cell changed since the memory last effectively saw it). It grows with time,
     `q ← 1 − (1 − q)·exp(−λ_cell·Δt)`, and shrinks after a view, `q ← q·(1 − p_detect)`. This one quantity
     covers both staleness and change rate. Nothing is ever "fully seen", because p_detect < 1.
   - `p_detect(c, cell)` comes from the fitted visibility model (`go2/memory_lab/grounded/visibility.py`: 90 deg gate
     = 79 deg lens + heading error, 6 m range, map occlusion with a self-mask; F1 0.65 against the 35B's yes/no). Its
     detection rate falls with distance (measured: 56% at 1-2 m, 31% at 3-4 m, 16% at 5-6 m). Extend it to 2.5-D
     with the height layers: whether a point at height h is visible from a camera at 0.4 m or 0.68 m.
   - `λ_cell` = change events in that cell per occupied hour, from the memory's **own** change log, pooled with a
     lab-wide Gamma prior (empirical Bayes). Every cell keeps a non-zero rate. The hand tracks are evaluation data,
     never features.
   - Evidence for unplanned questions: people cause most change, so person activity per cell (person detections
     already in `owl_dets.jsonl`, captions) is a covariate of λ, not a separate weighted term. Add a separate term
     only if the replay shows unknown windows stay large under this score.
   - `t(c)` = Z690's estimated walk + face + settle + photo seconds. Per-view timings from `/agent/view` replace
     the estimates as they accumulate.
   - Plan a short tour greedily on value/time, re-scoring after each view. Stop on the time budget or when Z690
     says stop.
4. **View** → `/agent/view` (dog camera + L515). Copy the frame, depth and metadata into cheetah memory at once:
   agent photos live in a 60-photo RAM buffer, and trail frames expire after 14 days.
5. **Change note vs past pictures.** Pick the past frames whose view footprints overlap this view's, using the
   visibility model and SigLIP tile similarity, not the nominal pose. Take the latest overlapping frame plus one
   from an earlier day. Write a note in the evidence_memory shape (`go2/evidence_memory/lab.py`: changes, importance,
   guess), restricted to `appear | disappear | unclear`. Each entry has: the thing (owner + look, never a place
   name), map xy, the frame ids compared, and whether the pose overlap was good enough to say "absent" rather than
   "not visible from here". People are described by desk, clothing or activity, never matched by face.
6. **Memory update.** Append the frames to the frame store, embed the new crops and tiles (`rs_index.py` path),
   update `q` and λ for each cell, and rebuild instances for `where_is` (`instances.json` is stale since 10-23).
7. **Round report.** List the changes with before/after pictures and times. List what was **not** checked
   (highest remaining `q`), and the refusals with their `why`. Keep "absent" (spot viewed, thing not there) separate
   from "not viewed".

## Offline test first: replay recorded runs
Data, all on cheetah: 13,743 posed frames across 50 runs (`frontier_baseline/deep_sandbox/frames.json`), 7,707 L515
frames, the map grid (`deep_sandbox/map_grid.json`) and regions.
- **Keys (author-only, never in a sandbox).**
  - `days/planted_1116/changes.json`: 11 logged changes between patrol 1 (`2026-11-16_patrol1_part{1,2}`) and
    patrol 2 (`..._patrol2_part{1,2}`). The isopropyl bottle, brown marker, tape measure and water bottle have map
    xy in the tracks. The other seven need placing once, with Oliver confirming.
  - The natural appear/disappear flips in `research/objsearch/tracks/*.json`, plus the removals Oliver confirmed in
    the Lab Memory Study flags (water jug, paper carton at 11-17).
  - `days/run_111{7,8}/GROUND_TRUTH*.md`, for the people and transient events (11-18 jug swap).
- **Protocol.** Take runs in date order. Memory = runs before r. Candidates = the frames run r actually took (with
  L515 where present). The brain picks a tour of K views under a time budget, with walk cost from A* on the map grid
  at Oliver's speed from `/patrol/prior`.
  - **Stage 1, targeting:** did the chosen views cover the keyed changes (2.5-D visibility)? This uses oracle
    perception, so targeting is isolated from perception.
  - **Stage 2, perception:** run the change note on the chosen views against past views and judge blind with the
    key. Report found, false claims, and "absent" vs "not viewed".
- **Baselines.** All frames of the run (ceiling), random K, staleness only (λ equal everywhere), the fixed 17-place
  tour, and Oliver's dwell prior alone. Dev split: runs up to 11-12. Test: 11-16 to 11-19, including the planted
  pair. Nothing is tuned on test.
- **Limits.** This is off-policy: the replay can only choose among views someone already took. There are few keyed
  changes (11 planted plus about 20 natural flips). Before or alongside the first watched runs, ask Oliver for
  **staged floor-level removals with a log** (FINDINGS_1120 next step 1). That is the real test, and it is visible to
  the 0.4 m camera.

## Capability test before harness parts (Oliver's rule)
1. **Raw prompt test, before any scoring code.** Give Opus (`claude -p`) and the Qwen 27B (only if a GPU is free;
   no waiting for GPUs) the stage-1 replay task with standard tools only: the map, the candidate list with poses,
   the past frames and captions, and search. Ask "pick the next K views and why". Pilot: about 10 rounds × 2 models
   = about 20 calls. Read the traces at runs 1, 3, 5 and 10.
2. **Minimal nudge.** If it fails, change only the prompt: "consider what you have not seen recently, and what tends
   to change". Re-run the same rounds.
3. **Read the traces for the mechanism** (for example: it cannot compute staleness from raw timestamps, it
   confuses not-viewed with absent, it ignores walk cost, it re-views the same spot). Build only the part that fixes
   an observed mechanism: a staleness/q tool, a coverage tool (`seen_by` exists), a route-cost tool, or the full
   scorer above. Each part must be general: no object vocabulary from the keys, no thresholds fitted on test
   rounds, no fixed tile grids. Ablate one part at a time on one base model.
4. **Same for change notes.** On the planted 11-16 pair, test the raw model on the overlapping before/after views
   first. On record: Opus is precise (1 false of 13 claims) but misses many (2-4 of 11), at 150-300k tokens per sweep.
   The 8B on pose-matched pairs is unusable (4-11% precision). The 27B has not been measured on change notes.
   Unattended rounds need a cheaper note writer, so that is the measurement to make.
5. Live runs come only after a replay result is written up and Oliver has seen it. They are watched, short and
   slow, as Z690 proposed. State the call count before going over 30 calls.

## Reuse map
`go2/console/{view_plan.py, lab_round.py (--plan-only)}`, `go2/memory_lab/grounded/{visibility.py, coverage.py}`,
`go2/lab_agent/{memory_instances.py, server.py where_is}`, `go2/evidence_memory/lab.py` (note format),
`frontier_baseline/research/objsearch/{absence_bench.py, rs_index.py, objtool.py}`.
