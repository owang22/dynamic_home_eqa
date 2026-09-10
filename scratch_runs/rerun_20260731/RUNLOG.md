# Rerun 2026-07-31 — household-profile generation (Qwen3.6-35B-A3B)

Context: GPU had fallen off the bus previously; driver was upgraded to 580.173.02
and the box rebooted (verified: nvidia-smi OK, kernel+userspace matched, RTX PRO
6000 Blackwell idle at 27C, 47MiB used). Rerunning the intensive gen_dataset
household-profile jobs against the local vLLM endpoint.

Plan:
1. Serve Qwen/Qwen3.6-35B-A3B on :8300 (vllm_q env, sm_120 recipe flags).
2. Smoke test: 1 scene x 1 day, default profile.
3. Full set: the 4-profile daybudget batch (retired_couple,
   single_parent_young_kids, roommates_shared_house, family_with_kids).

## Timeline
- 12:20 nvidia-smi verified healthy post-reboot; model snapshot present at
  /mnt/nvme/oliver/robot/models/hub/models--Qwen--Qwen3.6-35B-A3B (26 shards).
- 12:24 vLLM server launched (PID 2442286, recipe flags incl. --moe-backend
  triton, --compact-guided-json). UP after ~190s, /v1/models healthy.
- 12:28 smoke test started: gen_dataset --n 1 (scene 102343992), 1 day,
  profile family_with_kids, endpoint :8300, no-cache.
- 12:33 smoke attempt 1 FAILED: "No module named dynamic_home_eqa.trace_validate"
  — commit 2f2afa4c (archiving hssd) moved trace_validate.py to archive/ but
  pipeline.py:1033 still imports it. Restored the file (byte-identical to the
  pre-move git version) to src/dynamic_home_eqa/trace_validate.py. Import OK.
- 12:35 smoke attempt 2 started (same flags).
- 12:41 smoke attempt 2 PASSED: survival 100% (40/40), realism 0.78, 18 changes,
  trace gate on. Serving stack + pipeline healthy.
- 12:42 FULL BATCH started: 4 (scene, profile) pairs x 18 days, --calendar-days
  --enrich-context, fresh cache dir (true regeneration, resumable). Pairs run in
  parallel (vLLM batches concurrent requests; max-num-seqs 256).
- 13:51 FULL BATCH DONE (~70 min wall). Per pair (grounding survival / mean
  realism / days kept):
    102343992 single_parent_young_kids  100% (688/688)  0.773  18/18
    102344022 roommates_shared_house    100% (745/745)  0.748  17/18
    102344049 family_with_kids          100% (682/682)  0.754  14/18
    102344049 retired_couple            100% (798/798)  0.766  18/18
  Missing days = trace_validate hard-gate rejections, all "unattended" (1-2
  events with no occupant in source/dest room at event time); zero chain
  breaks / re-inserts / no-ops. Same failure mode as the old daybudget runs
  (their registries also had missing days). Dropped: roommates day7;
  family_with_kids days 2, 7, 10, 15.
  Outputs: scratch_runs/rerun_20260731/full_out/ (67 day dirs). Cache kept at
  scratch_runs/rerun_20260731/cache — rerunning just the failed days will
  reuse it (proposer resamples only where needed).
