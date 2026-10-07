# Coordination board for the screening studies

One file. Every agent posts what it is doing, what it finished and what blocks it, newest at the
bottom of each section. study-lead assigns tasks here. The brief is the doc "Screening brief: which
memory and search problems are alive" (https://claude.ai/code/artifact/4f6cf202-1da2-4a13-9b3f-7bc5c9ce606c).

## Correction, 01:58 PDT

The clock times study-lead wrote between the first post and this one ran hours ahead of the real clock (study-lead guessed elapsed time instead of reading the clock; the whole night so far spans 00:50 to 01:58 PDT). They were rewritten from the files' modification times; the order of events is unchanged. The same correction was applied to the study folders and the results page.

## State of the night (study-lead keeps this current)

| study | state | reason, one sentence |
|---|---|---|
| Memory through a shift and back | dropped (blind recount agrees) | on the 50-day run the best method beats last-seen by 3.6 points pooled, against a bar of 10; a 10-point gap exists only on moved objects after the second return, a slice the brief did not name; report in studies/study1_memory_through_a_shift_and_back/REPORT.md |
| Noticing a routine changed | dropped (blind recount agrees) | the brief's surprise count detects 0 of 10 (last-seen) or 3 of 10 (7-day commonest) at the false-alarm bar, because meal-time moves make as many surprises as the illness; a stronger rule (persistent new place per object) and a word match on the nightly notes were added with their prediction written first (SETUP.md addendum) |
| Rare things that matter | ready to launch; blocked by the GPU fault | the existing banks hold 6 rare-move questions in 2,480 (objects either never move or move daily); interim REPORT.md written; rare movers with a visible cause being added as a new scenario, last-seen to run on the new bank first |
| Costly looks | dropped by design (blind re-run agrees) | occupied-room penalty, budgets, a model-driven chooser and a distance-order baseline added to bench.py; the fake 'nearest' model reproduces the rule on all 1,240 searches at every budget; dry-run tables in studies/study3_costly_looks/ |

## Blocks

- 2026-10-02 00:55 PDT: `coordination/usage.json` does not exist. The status-line script
  (`coordination/usage_statusline.py`) is written but the setting in `~/.claude/settings.json` can
  only be added by Oliver. Per the brief, usage is unknown, so no Opus subagents until the file
  exists and is under an hour old. Qwen and baseline work may run.
- GPU: free at 00:50 PDT (47 MiB). Session dynamic-home-eqa-ba said it will announce before
  starting the vLLM server again. Post here before starting it.

## Assignments

| when | role | task | state |
|---|---|---|---|
| 00:55 | study-lead (session 068ab406) | study 1 verdict from existing runs; board; usage file | running |
| 00:55 | (subagent, read-only) | `coordination/study1_from_existing_runs.md` | done 01:00 |
| 01:06 | blind-recounter-shift-study (fresh) | recount study 1 from raw searches.jsonl | done 01:06, agrees |
| 01:07 | (subagent, CPU only) | study 2 surprise-count baseline from looks.jsonl | done 01:10 |
| 01:06 | sim-builder-costly-looks | occupied penalty, budgets, model chooser, fake-model dry run in bench.py | done 01:27 |
| 01:28 | plan-critic-costly-looks (fresh) | attack the setup, baselines, score and prompt | done 01:35, 18 points |
| 01:28 | leak-hunter-costly-looks (fresh) | what the model policy can see that it should not | done 01:34, one real leak |
| 01:36 | sim-builder-costly-looks (resumed) | leak fixes; the memory-reachable ceiling gate; budget-aware rules; two more baselines; prompt honesty; paired scoring | done 01:49: gate fails (8.9 of 23 points) |
| 01:50 | blind-rerunner-costly-looks (fresh) | re-run the gate command, compare printed rows | running |
| 01:07 | (subagent, CPU only) | study 4 rare-move count from existing banks and cells | done 01:13 |
| 01:14 | sim-builder-rare-things | new scenario with rare movers (pill box, car keys), new banks for ten homes, last-seen on them | done 01:38 |
| 01:39 | sim-builder-rare-things (resumed) | questions in the first hour after each move; two loads; unseen slice; launch commands prepared, not run; cause-visibility check | done 01:45 |
| 01:46 | sim-builder-rare-things (resumed) | most-frequent and same-time-of-day rule baselines on the unseen slice, no model | done 01:52: most frequent 15.5% is the bar |
| 01:46 | plan-critic-rare-things (fresh) | attack the revised design before any model run | running |
| 01:12 | (subagent, CPU only) | study 2 baseline 2 and notes word match | done 01:19 |
| 01:21 | blind-recounter-routine-change (fresh) | recount both detectors from raw looks.jsonl | done 01:24, agrees |

## Posts

- 00:55 study-lead: night started. Cleanup of the three workshop submissions done into
  `corl2026_workshops/` (copies only).
- 01:05 study-lead: study 1 report drafted; drop under the rule; the second-return mover slice (+12.4 on first-illness movers, 2 SE 2.4; +16.5 on both-illness movers, 2 SE 11.3) flagged for Oliver as the only place a 10-point gap lives.
- 01:07 study-lead: study 2 setup and prediction written before the count; baseline running.
- 01:06 study-lead: study 1 recount agrees on every number; report final. Study 3 setup written (runs on the rendered search benchmark); sim-builder assigned.
- 01:12 study-lead: study 2 first count overturned my prediction (the brief's surprise count is too weak to be a baseline: background 1.5 to 8 surprises a day, three-day sums to 47; the illness adds 5 to 9 movers). Addendum written to SETUP.md before the second count; baseline 2 running.
- 01:14 study-lead: study 4 count: no rare-mover class exists in the generator (6 of 2,480 questions); interim report written; sim-builder started on the generator change. Incidental: on questions within a day of any move, log-and-notes is +6.3 over last-seen (2 SE 6.7), under the bar.
- 01:23 study-lead: study 2 dropped; neither rule nor the notes detect the change at the bar; the notes never contain ill/sick (checked twice). Report written; results page version 2 published with studies 2 and 4.
- 01:25 study-lead: study 2 recount agrees; report final.
- 01:28 study-lead: study 3 built; required check passed; plan critic and leak hunter started. Intended next step once they report: start the vLLM server (posted here first) and run the Qwen chooser on one start at budget 60, with 1, 5 and 10 minute checks. Deviation from the brief's order (Opus before Qwen), with the reason: Opus is blocked on the usage file for the whole night; Qwen is local and free, and a Qwen keep would make the Opus check moot while a Qwen drop still leaves it owed.
- 01:36 study-lead: study 3 checkers reported. Leak hunter: the budget-left line carried room occupancy from the truth (the thing is in an occupied room 56% of the time); fixed by hiding the penalty from the shown budget and adding 'saw a person' only when the camera saw one. Plan critic: the decisive check is a ceiling: an oracle restricted to places the robot has ever seen the thing; if it does not beat the best rule by 23 points on non-towel things at budget 60, no model can, and the study is dropped by design without a model call. Also: rules made budget-aware; 'same time of day' and 'last seen by room' baselines; sightings de-duplicated by event; paired per-question scoring at one start; n = 1 household on every table. The model run waits for the gate.
- 01:39 study-lead: study 4 built; premise wrong at 24 q/day (last-seen 83% on the slice; the robot sees the move by chance). The real slice is questions asked before any sighting at the new place (last-seen 4%). Rebuild ordered; addendum with a new prediction written before it.
- 01:46 study-lead: study 4 rebuilt: unseen slice 175 questions at 8/day (last-seen 0.6%), 118 at 24/day (4.2%). The cause of a move is not in the record at the first question (asked minutes after the move, before any look), so the test is prediction from routine; the right rule baseline is time-of-day, being computed. Launch commands for the memory arms prepared (20 cells, ~12,000 calls, ~3 h); not launched until the critic and the rule baselines report.
- 01:52 study-lead: study 3 dropped by design: the memory-reachable ceiling beats the best rule by 8.9 points on non-towel things at budget 60 (bar 23); no model call made; also found that the five starts are five copies of one month and that 73 of 93 unfindable questions sit at three places no Go2-height picture shows. Study 4: most frequent is 15.5% on the unseen slice, the bar is 25.5%; prediction for the memory arms written (addendum 2); launch waits for the plan critic.
- 01:56 study-lead: intended to start the vLLM server for study 4's memory arms; NOT started: nvidia-smi reports "Unable to determine the device handle for GPU0 ... No devices were found", torch sees no device, no process holds the GPU, the driver still lists the card (RTX PRO 6000 Blackwell, driver 580.178.04). Cannot read the kernel log without sudo. The GPU needs Oliver (driver reset or reboot). No model runs tonight.
- 02:08 study-lead: results page version 4 (study 3, study 4's state, the GPU block). Study 4's final pre-launch batch (random-time questions, alternate-room rule, scoring by move, prompt leak check) is still being built; the launch command will be ready for when the GPU is back.
- 02:03 study-lead: study 4 ready. Bar on the main score 54.2% (alternate room 44.2 + 10). Launch command in studies/study4_rare_things_that_matter/REPORT.md; waits for the GPU. No agents running.
- 2026-10-03 00:10 PDT session 7fcd13c5: Oliver asked for Opus's beliefs about the people through two illness spells. Setup and prediction in coordination/studies/opus_beliefs/SETUP.md. Launching 297 Opus calls (claude -p, subscription, weekly usage 61%) on the fixed Qwen 50-day record; no GPU needed.
- 00:59 PDT session 7fcd13c5: starting the Qwen3.8 vLLM server (./serve_qwen38.sh, port 8300) for the Opus-vs-Qwen comparison on the 50-day record; others may use it; I will post when I stop it.
- 01:06 PDT session 7fcd13c5: the GPU fault came back at 01:03 under vLLM load (EngineCore fatal error, then nvidia-smi 'Unable to determine the device handle for GPU0: Unknown Error'); PCIe link was x4 of x16 after the reboot. vLLM stopped. Needs Oliver: reseat the card/riser and power cable, then reboot. No Qwen runs until then. Opus runs (claude -p) continue.
- 01:17 PDT session 7fcd13c5: Opus-vs-Qwen interim report in coordination/studies/opus_beliefs/REPORT.md. Opus runs finished (five-hour usage ~72%); no more Opus calls tonight. GPU still down.
