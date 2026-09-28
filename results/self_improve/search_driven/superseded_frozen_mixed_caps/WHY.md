# Superseded: the first frozen-memory pass, two runs at different question caps

Moved here, not deleted. Two things went wrong and both are visible in the artifact
rather than inferred:

1. The first launch used bare `nohup ... &` from a tool shell. Backgrounded children
   are killed with their process group when that shell exits, so the pass stopped
   after one cell with NO error in the log - a run that looked complete because
   everything it did do succeeded. The relaunch uses a wrapper script ending in
   `wait`, started with `setsid`.
2. The relaunch used `--max-questions 30` while a survivor of the first launch was
   still writing at `--max-questions 40`, into the SAME log files. The giveaway is a
   line reading "ASSAY: 87% of antold the asked list hh_s2_t03 ..." - two writers
   interleaved mid-line. So the per-cell question counts differ (30 and 40) within
   one household and the numbers must not be pooled or compared across cells.

Nothing here is a result. The pass is being rerun at a single cap.
