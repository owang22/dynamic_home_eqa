# Overnight 2026-10-23 (no dog)

## Morning summary (lead, 02:10)

| area | result | where |
|---|---|---|
| Localization, lidar | Root cause is odom yaw drift while still (+0.3 to +4.7 deg/min, CCW). The console rarely jumps (2 in 370 min) but is often slightly off: 49% revisit-consistent. A map learned across days tracks 57% vs the console's 33% and relocalizes from scratch 53% vs 21%. The lidar stream has nothing above about 1.4 m. | `localization/REPORT.md` |
| Localization, camera | No tilted photo exists (look springs back). The upper part of a level frame survives furniture changes better than the lower part, not better than the full frame. Matching across days: 63% of queries posed at 93% precision, or 86% with a spin. Effective field of view about 79 deg, not 73. | `localization/visual/REPORT.md` |
| Memory | 167 missing descriptions filled in. SigLIP picture search combined with words (modest honest gain). 478 objects with P(still there). New `where_is`. Date bug fixed. | `lab_agent/memory_notes/` |
| Hierarchy for Khang | 8B watch loop: 20/20 hits, 0/114 false at 25-57 ms per frame. 8B alone on memory questions 0.43 vs Opus 0.83. Router 0.73 at 53% Opus. `watch_go_to` and `scan_for` added to `server.py` after two safety fixes; `web.py` router not enabled. | `lab_agent/hierarchy/REPORT.md` |
| Explorer page | Private page with layers, map, search traces, search comparison, and Ask (Claude with in-page memory tools). | https://claude.ai/artifact/XEuuRRjX64xHaLGAunsob9 |
| Board | #25: publish hand placements, jumps and drift corrections to agents. #26: yaw-bias removal, jump gate, consensus map, relocalize routine, tilt bug, focal length. | Lab Guide doc, Agent chat tab |

**Needs Oliver:**
- Both of our vLLM servers got SIGTERM at 01:50; user gaofeng now holds the GPU. Restart with
  `lab_agent/serve_vlm_shared.sh` and `lab_agent/hierarchy/serve_8b.sh` when the GPU is free.
- Decide on the `web.py` router.
- Nothing is committed; `go2/lab_agent/` is untracked.

**With the dog:**
- A 10 min still test.
- Taped floor marks, with a 360 deg turn at 3 of them.
- A survey walk with no hand placement.
- Check that tilt is captured.
- A checkerboard calibration.
- Test `watch_go_to` with Oliver walking past.
- Move a few objects on purpose to test P(still there).

Oliver's brief (2026-10-23 ~00:10): no access to the dog overnight; do any changes that don't need the dog.
Directions from the 2026-10-22 discussion: Roomba-style relocalization robust to moved furniture, embodied memory,
small/large model hierarchy (Khang's Qwen3-VL-8B). Surveys: `lab_agent/research_2026-10-22/`.

## Rules for everyone tonight
- The dog is still connected to the control PC console (172.17.40.64:8080). Read-only GETs only
  (`/state.json`, `/map.png`, `/trail/*`, `/frame.jpg`). Never call `/agent/*` (claim, go_to, stop, ...), never post.
- `go2/lab_agent/` is not in git. Backup: `go2/data/lab_agent_code_backup_2026-10-23_pre_overnight.tgz`.
  Never delete outputs; move to `*_v1` / `.bak`. No commits.
- vLLM (Qwen3.8-27B, :8300) runs in tmux `vlm` (started 00:13, evidence_memory/serve_vlm.sh, util 0.85).
- Areas are file-disjoint: localization -> `go2/localization/`; memory -> `go2/lab_agent/` memory files + server.py;
  hierarchy -> `go2/lab_agent/hierarchy/` (does not edit server.py; integration by the lead session).

## Status log (one line per change)
- 00:13 vLLM started for the picture-description backfill (205 undescribed records, 38 duplicate ids).
- 00:13 lab_agent backed up.
- 00:21 backfill done: 167/167 described in 301 s, +2 new trail frames; 1109 pictures, 0 undescribed. Duplicate ids are by design (placeholder then described record; load() keeps the last). Backup: data/lab_agent/index.jsonl.bak_2026-10-23_pre_backfill
- 00:22 27B restarted at util 0.66 (lab_agent/serve_vlm_shared.sh) to make room for Qwen3-VL-8B-FP8 on :8301 (hierarchy agent, tmux vlm8b)
- 00:26 Qwen3-VL-8B-Instruct-FP8 up on :8301 (tmux vlm8b, lab_agent/hierarchy/serve_8b.sh, util 0.20; needs VLLM_USE_DEEP_GEMM=0)
- 00:45 Board message #25 posted (Lab Guide doc, Agent chat tab): asks the control PC console to publish hand placements / jumps / drift corrections as `map.events` + a `localization_notice` on /agent/* replies. Cheetah side (lab agent passes the notice on; memory marks uncertain poses) waits for those fields.
- 00:45 Finding: the 0.12-0.17 m stationary twitches match the console's own drift correction (board #12, ±20 cm / ±2°); map.track is not in /events, so it can't be confirmed from logs.
- 00:47 Fourth agent: camera relocalization from the upper part of frames (ceiling / upper walls), go2/localization/visual/. Oliver has no AprilTags.
- 01:07 Hierarchy agent done: report saved as lab_agent/hierarchy/REPORT.md. The lead re-ran the tests: test_hierarchy 10/10, test_integration 5/5. watch_go_to/scan_for are not yet registered in server.py; waiting for the memory agent to finish its edits there.
- 01:25 memory (agent): SigLIP embeddings + fused search_memory (mode=words keeps the old search), synonym map, memory_instances.py + where_is tool in server.py, SYSTEM.md/README lines. Backups *.bak_2026-10-23. Notes: lab_agent/memory_notes/.
- 01:20 Lidar localization agent done: localization/REPORT.md (saved by the lead). Root cause: odom yaw creeps +0.3-4.7 deg/min while still, CCW (the lead re-measured it independently); a consensus map learned across days tracks 57% vs the console's 33% and relocalizes from scratch 53% vs 21%; the lidar stream has almost nothing above 1.2 m, so the ceiling idea needs the camera. Board post with the proposal waits for the camera results.
- 01:23 Memory agent done (notes in lab_agent/memory_notes/): SigLIP picture search fused with word search (recall@5 0.67 -> 0.70 with the weight fixed in advance on 20 held-out queries; 0.79 tuned, optimistic), 478 object instances, new `where_is` tool, `search_memory(mode=fused|words|images)`, `when()` date bug fixed. Lead checked: memory self-test passes, calls.jsonl untouched.
- 01:23 Lead wired `watch_go_to` and `scan_for` into server.py (16 tools) plus one SYSTEM.md rule. Fixed two hierarchy bugs first: (1) server.py crashed at import if the 8B was down (LLM() queried /models eagerly) -> lazy connect; (2) with the 8B down the dog would walk the whole route unwatched while reporting frames as "checked" -> tools refuse before moving if :8301 doesn't answer, and report frame_errors. Re-ran all tests: hierarchy 10/10, integration 5/5, memory self-test OK. Router in web.py NOT enabled (Oliver's call). Backups: *.bak_2026-10-23_lead*.
- 01:33 Memory explorer page published (private): https://claude.ai/artifact/XEuuRRjX64xHaLGAunsob9. Source lab_agent/memory_viz/ (build.py -> data/lab_agent/memory_viz/, memory_explorer.html). Views: layers + map + inspector, search traces of the 17 logged turns, search comparison on 40 labelled queries, and Ask (Claude via the page's sample capability, with 6 in-page memory tools and an optional picture check).
- 01:55 Camera relocalization agent done; report saved by the lead as localization/visual/REPORT.md, and section 7 of localization/REPORT.md filled in. Lead verified P1: the look +16 / -5 photos have zero vertical shift against the level photos, so tilt was never captured. Both of our vLLM servers received SIGTERM at 01:50:14; user gaofeng (logged in 01:39) now holds 78 GB of the GPU with their own vLLM. Not restarted (shared machine; Oliver's call).
