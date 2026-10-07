# What was set aside, and where it went

Moved 2026-09-28 out of the run folders and into
`results/self_improve/archive/superseded_inside_the_run_folders_2026-09-28/`, which is not in
git. Nothing was deleted. The directory names there are the original paths with `/` written
as `~`, so `overnight_wave~superseded_dry_runs_2026-09-25` was
`results/self_improve/overnight_wave/superseded_dry_runs_2026-09-25`.

This index exists because each of those folders carried its own `WHY.md` explaining what was
wrong with it, and moving the folder took that explanation out of git with it. The reasons are
the part worth keeping in the repository; the streams are not.

Checked after moving: the artifact rebuilds to the same 141,126 questions and 252 cells, and
the page is byte-identical, so none of this was reaching it.

## `overnight_wave_24_questions/superseded_one_sighting_not_a_trail_2026-09-25`

665 MB, 10 finished cells. Its note is `WHY_THESE_ARE_SET_ASIDE.md`.

> These ten cells ran an arm called "newest sighting, no model" that kept **one** sighting per object, overwritten every time the object was seen again. Its first guess was the room the object was last seen in. From the second guess on it had nothing left: that room had just been opened and removed, so it fell through to the room where things of the same class were last

## `overnight_wave_24_questions/superseded_the_night_that_did_not_parse_2026-09-25`

0 MB, 0 finished cells. Its note is `WHY.md`.

> Moved aside 2026-09-25, not deleted, because the accuracy numbers for `MemGPT as published` at 24 questions a day come from **reruns** of these two cells, and a rerun reported without the original failure is selection on outcome. | cell | the night that did not parse |

## `overnight_wave/superseded_before_the_people_had_names_2026-09-25`

18 MB, 0 finished cells. Its note is `WHY.md`.

> Stopped 2026-09-25 at about 01:07, partial and unfinished, by decision rather than failure. **No number from these cells is usable.** Nothing deleted. The ten `newest sighting, no model` cells are NOT here: they call no model, see no prompt, and are unaffected. These cells were shown `resident_1` and `resident_2` in their look records while the objects

## `overnight_wave/superseded_before_the_prompts_were_evened_2026-09-25`

18 MB, 0 finished cells. It carried no note.

## `overnight_wave/superseded_dry_runs_2026-09-25`

2 MB, 0 finished cells. Its note is `WHY.md`.

> Both were run before the wave's five socket-bug reruns landed, and before the no-model comparator was replaced (`newest sighting` kept one sighting; `last seen` keeps the whole trail). They were run to shake crashes out of the report, not to be read: at the time they were written the headline silently dropped four of six arms and the no-model arm was absent from the

## `overnight_wave/superseded_one_sighting_not_a_trail_2026-09-25`

230 MB, 10 finished cells. Its note is `WHY_THESE_ARE_SET_ASIDE.md`.

> These ten cells ran an arm called "newest sighting, no model" that kept **one** sighting per object, overwritten every time the object was seen again. Its first guess was the room the object was last seen in. From the second guess on it had nothing left: that room had just been opened and removed, so it fell through to the room where things of the same class were last

## `overnight_wave/superseded_ran_under_the_600s_socket_2026-09-25`

114 MB, 5 finished cells. Its note is `WHY.md`.

> These five cells each lost at least one model call to the same bug, and nothing else. In `baselines/patrol/llm.py` the connection was built with `timeout=min(600.0, self.DEADLINE_S)` while `DEADLINE_S` is 900: two limits on one quantity, and the smaller one — which nobody chose — was the real one. Every lost call in this wave failed at **exactly 600 seconds on both

## `overnight_wave/superseded_standing_was_filled_while_rewording_2026-09-25`

145 MB, 0 finished cells. Its note is `WHY.md`.

> Stopped 2026-09-25 at about 02:35, partial, by decision rather than failure. **No set-aside number from these cells is usable.** Nothing deleted. The ten `newest sighting, no model` cells are not here: they write no notes. `standing` was an optional field on every edit, so the model filled it while doing something

## `search_driven/superseded_first_wave`

23 MB, 0 finished cells. Its note is `WHY_THIS_IS_SUPERSEDED.md`.

> Moved here, not deleted. Stopped 2026-09-24 about four minutes in, after the coordinator changed two things about the design: 1. the answer prompt must show the rooms the failed search just ruled out (this wave withheld them);

## `search_driven/superseded_frozen_mixed_caps`

1 MB, 0 finished cells. Its note is `WHY.md`.

> Moved here, not deleted. Two things went wrong and both are visible in the artifact rather than inferred: 1. The first launch used bare `nohup ... &` from a tool shell. Backgrounded children are killed with their process group when that shell exits, so the pass stopped

## `superseded_v1_five_bars`

1 MB, 0 finished cells. It carried no note.

## `superseded_v2_place_level_movers`

1 MB, 0 finished cells. It carried no note.

## `three_prompts/stopped_early_the_notes_were_a_place_table_2026-09-25`

74 MB, 25 finished cells. Its note is `WHY.md`.

> Stopped 2026-09-25 on Oliver's instruction, with phase 1 warming 25 of 70 cells and no full-month cell finished. **These cells are partial by DECISION, not by failure.** Nothing here failed a gate; the wave was cut because the comparison below made four more hours of GPU not worth spending. Nothing was deleted.

## `three_prompts/superseded_2400_char_summary_schema`

12 MB, 0 finished cells. Its note is `WHY.md`.

> These partial cells had the budget SENTENCE removed from the prompt but still carried `SUMMARY_SCHEMA`'s `maxLength: 2400` — a hard cap on the wholesale arm's entire memory for the whole month, with no equivalent on the claim store. A "no length limit" arm capped at about twenty lines with nothing in its prompt saying so is worse than an openly capped one,

## `three_prompts/superseded_8_line_budget_2026-09-24`

18 MB, 0 finished cells. Its note is `WHY.md`.

> These 14 cells were launched at 19:51 on 2026-09-24 and stopped by me at 19:59, after the coordinator's correction arrived: **remove the memory length limit entirely, in writing and in reading.** They were running with `read_budget_lines = 8` at answer time, which is the confound the correction removes, so every number they would have produced

## `three_prompts/superseded_two_writers_same_cell`

6 MB, 0 finished cells. Its note is `WHY.md`.

> My launcher wrapped each cell in `( ... ) &`, so `$!` recorded the SUBSHELL's pid and not python's. Killing the recorded pid therefore orphaned the python child instead of stopping it. When I relaunched the wholesale arm at 20:12 after lifting the schema ceiling, the four pre-patch processes from 20:03 were still alive and still writing - so five of these cells

## `told_if_right/superseded_flat_allowance_2026-09-24`

4 MB, 0 finished cells. It carried no note.

## `wave_reasons_first/damaged_by_the_50_day_overwrite_2026-09-26`

59 MB, 2 finished cells. Its note is `WHY.md`.

> `cell_dir` is built from the ARM NAME, and the second-illness run uses the same arm on the same household with a different bank and 50 days instead of 32. So it resolved to the same directory and `searches.jsonl`, `notes.json` and `looks.jsonl` are all opened `"w"` - the 50-day run truncated the finished 32-day reason-first cells for `the log and notes about the routine` and
