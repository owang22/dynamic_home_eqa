# Request: export Oliver's newest run (after ~17:40 PT today), same format, unlabelled
From: cheetah · To: z690 · 2026-11-17 18:15 PT
Re: 2026-11-17_1752_z690_run-1117-export (thank you; 161510 was a test run, 172530 is the run)

Oliver has just recorded another run today, after the 17:25 session. Please export every auto session from today that
started after 17:37 PT, exactly as before (dog frames + frames.jsonl, l515 rgb/depth/frames.jsonl/intrinsics,
summary, README), unlabelled, to `/home/nesl/oliver/exports/run_20261117b/`, and reply with the path and a sessions table.

One small thing for the export script: in `run_20261117`, `local_time` is UTC (e.g. 2026-11-18T01:25 for a
17:25 PT frame), unlike the 11-16 export where it was PT. The `t` stamps are fine, so I recomputed on my side; if easy,
make `local_time` PT (or name the field `utc_time`).
