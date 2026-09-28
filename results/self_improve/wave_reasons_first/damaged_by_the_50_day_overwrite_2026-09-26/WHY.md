# Two completed cells were overwritten by their own second-illness run, 2026-09-26

`cell_dir` is built from the ARM NAME, and the second-illness run uses the same arm on the same
household with a different bank and 50 days instead of 32. So it resolved to the same directory
and `searches.jsonl`, `notes.json` and `looks.jsonl` are all opened `"w"` - the 50-day run
truncated the finished 32-day reason-first cells for `the log and notes about the routine` and
`ACE as published` on hh_s2_t03.

Nothing was lost: `cell.json` is written once at the end and still held all 744 searches to day
31 for both. These directories are that state, kept rather than deleted. The two cells were rerun
from the response cache, which replays them for nothing because every prompt is identical.

The agent warned about exactly this two hours earlier - that the old launchers pass no `--banks`,
that household names are identical across bank sets, and that `take_the_lock` only refuses a LIVE
second writer, so a run with a colliding `--out` overwrites completed cells in place. I queued the
collision anyway. The fix is that a run on a different bank or a different length gets its own
`--out`, never the same one.
