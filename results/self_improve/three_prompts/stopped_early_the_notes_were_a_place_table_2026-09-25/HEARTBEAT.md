# three_prompts heartbeat

Written 2026-09-24T22:16:54-07:00 by `watch_the_heartbeats.py`. A cell beats once per completed night. Silence longer than 20 minutes counts as STALLED.

**0 finished, 10 running, 0 STALLED** (of which 0 have no live process at all). One row per CELL, liveness read from `ps` rather than from a pids file.

No cell has been silent longer than the stall threshold.

## detachment

This watcher's session id is `2868769`. Live cell session ids: [2864498, 2868010].

A cell sharing a session id with the shell that launched it is NOT detached and will be reaped with it. Distinct session ids here are the proof that `setsid` took effect; the command line alone is not.

## every cell

| arm | home | last night | quiet for | alive | finished | pid | sid | wave |
|---|---|---|---|---|---|---|---|---|
| control | hh_s19_t03 | 3/31 | 1.2 | yes | no | 2868157 | 2868010 | nightly12 |
| control | hh_s2_t03 | 3/31 | 2.1 | yes | no | 2868014 | 2868010 | nightly12 |
| control_wholesale | hh_s2_t03 | 11/31 | 2.2 | yes | no | 2868117 | 2868010 | nightly12 |
| describe_the_person | hh_s19_t03 | 3/31 | 0.7 | yes | no | 2868208 | 2868010 | nightly12 |
| describe_the_person | hh_s2_t03 | 3/31 | 1.6 | yes | no | 2868039 | 2868010 | nightly12 |
| rival_and_describe | hh_s2_t03 | 2/31 | 3.2 | yes | no | 2868089 | 2868010 | nightly12 |
| rival_beliefs | hh_s19_t03 | 2/31 | 1.1 | yes | no | 2868178 | 2868010 | nightly12 |
| rival_beliefs | hh_s2_t03 | 5/31 | 3.3 | yes | no | 2864498 | 2864498 | (not in any pids.txt) |
| told_unwell | hh_s19_t03 | 3/31 | 1.2 | yes | no | 2868238 | 2868010 | nightly12 |
| told_unwell | hh_s2_t03 | 3/31 | 1.9 | yes | no | 2868065 | 2868010 | nightly12 |

## the accounting: 10 homes x 6 arms = 60 cells

| arm | finished | running now | neither | duplicate writers |
|---|---|---|---|---|
| control | 0/10 | 2 | **8** | 0 |
| rival_beliefs | 0/10 | 2 | **8** | 0 |
| describe_the_person | 0/10 | 2 | **8** | 0 |
| told_unwell | 0/10 | 2 | **8** | 0 |
| rival_and_describe | 0/10 | 1 | **9** | 0 |
| control_wholesale | 0/10 | 1 | **9** | 0 |

**'neither' is the number that will be missing from the comparison unless something launches them: 50 right now.** Queued cells count as 'neither' - this watcher cannot see a launcher's queue, so a non-zero number means either queued or lost.

**1 launcher(s) still alive, so the 50 are QUEUED and will start as slots free:**

  * `2868010 bash results/self_improve/three_prompts/launch.sh nightly12 12 control:hh_s2_t03 describe_the_person:hh_s2_t03 told_unwell:hh_s2_t03 rival_and_describe:hh_s2_t03 control_wholesale:hh_s2_t03 control:hh_s19_t03 rival_beliefs:hh_s19_t03 describe_the_person:hh_s19_t03 told_unwell:hh_s19_t03 rival_and_describe:hh_s19_t03 control_wholesale:hh_s19_t03 control:hh_s20_t03 rival_beliefs:hh_s20_t03 describe_the_person:hh_s20_t03 told_unwell:hh_s20_t03 rival_and_describe:hh_s20_t03 control_wholesale:hh_s20_t03 control:hh_s32_t03 rival_beliefs:hh_s32_t03 describe_the_person:hh_s32_t03 told_unwell:hh_s32_t03 rival_and_describe:hh_s32_t03 control_wholesale:hh_s32_t03 control:hh_s48_t03 rival_beliefs:hh_s48_t03 describe_the_person:hh_s48_t03 told_unwell:hh_s48_t03 rival_and_describe:hh_s48_t03 control_wholesale:hh_s48_t03 control:hh_s63_t03 rival_beliefs:hh_s63_t03 describe_the_person:hh_s63_t03 told_unwell:hh_s63_t03 rival_and_describe:hh_s63_t03 control_wholesale:hh_s63_t03 control:hh_s93_t03 rival_beliefs:hh_s93_t03 describe_the_person:hh_s93_t03 told_unwell:hh_s93_t03 rival_and_describe:hh_s93_t03 control_wholesale:hh_s93_t03 control:hh_s109_t03 rival_beliefs:hh_s109_t03 describe_the_person:hh_s109_t03 told_unwell:hh_s109_t03 rival_and_describe:hh_s109_t03 control_wholesale:hh_s109_t03 control:hh_s123_t03 rival_beliefs:hh_s123_t03 describe_the_person:hh_s123_t03 told_unwell:hh_s123_t03 rival_and_describe:hh_s123_t03 control_wholesale:hh_s123_t03 control:hh_s151_t03 rival_beliefs:hh_s151_t03 describe_the_person:hh_s151_t03 told_unwell:hh_s151_t03 rival_and_describe:hh_s151_t03 control_wholesale:hh_s151_t03`

## is the memory really uncapped? read off the notes, not the code

The wholesale summary's schema used to cap the WHOLE memory at 2400 characters and its prompt told it to fit 8 lines. A summary longer than 2400 characters, or longer than 8 lines, is direct evidence from the artifact that both caps are gone in the process that wrote it.

| arm | home | longest summary so far | fact-lines | over the old 2400 cap? | over the old 8-line instruction? |
|---|---|---|---|---|---|
| control_wholesale | hh_s2_t03 | 2330 chars | 25 | not yet | YES |

'not yet' is not evidence of a cap: an early night may simply be short. A single YES in either column is conclusive for that cell.

## the waves


