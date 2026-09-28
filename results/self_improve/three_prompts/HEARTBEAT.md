# three_prompts heartbeat

Written 2026-09-28T01:14:02-07:00 by `watch_the_heartbeats.py`. A cell beats once per completed night. Silence longer than 20 minutes counts as STALLED.

**1 finished, 0 running, 0 STALLED** (of which 0 have no live process at all). One row per CELL, liveness read from `ps` rather than from a pids file.

No cell has been silent longer than the stall threshold.

## detachment

This watcher's session id is `2956403`. Live cell session ids: none alive.

A cell sharing a session id with the shell that launched it is NOT detached and will be reaped with it. Distinct session ids here are the proof that `setsid` took effect; the command line alone is not.

## every cell

| arm | home | last night | quiet for | alive | finished | pid | sid | wave |
|---|---|---|---|---|---|---|---|---|
| control | hh_s2_t03 | 31/31 | 4403.0 | no | yes | 2903543 | 2903543 | (not in any pids.txt) |

## the accounting: 10 homes x 6 arms = 60 cells

| arm | finished | running now | neither | duplicate writers |
|---|---|---|---|---|
| control | 1/10 | 0 | **9** | 0 |
| rival_beliefs | 0/10 | 0 | **10** | 0 |
| describe_the_person | 0/10 | 0 | **10** | 0 |
| told_unwell | 0/10 | 0 | **10** | 0 |
| rival_and_describe | 0/10 | 0 | **10** | 0 |
| control_wholesale | 0/10 | 0 | **10** | 0 |

**'neither' is the number that will be missing from the comparison unless something launches them: 59 right now.** Queued cells count as 'neither' - this watcher cannot see a launcher's queue, so a non-zero number means either queued or lost.

**NO launcher is alive.** So the 59 cells counted as 'neither' will never start unless something launches them. If that number is not zero, the comparison is incomplete.

## is the memory really uncapped? read off the notes, not the code

The wholesale summary's schema used to cap the WHOLE memory at 2400 characters and its prompt told it to fit 8 lines. A summary longer than 2400 characters, or longer than 8 lines, is direct evidence from the artifact that both caps are gone in the process that wrote it.

| arm | home | longest summary so far | fact-lines | over the old 2400 cap? | over the old 8-line instruction? |
|---|---|---|---|---|---|
| - | - | no wholesale summary written yet | - | - | - |

'not yet' is not evidence of a cap: an early night may simply be short. A single YES in either column is conclusive for that cell.

## the waves


