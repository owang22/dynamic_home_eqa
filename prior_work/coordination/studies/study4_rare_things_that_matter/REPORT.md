# Study 4, rare things that matter: report (interim)

**Verdict: not yet decided. The generator change is built and checked, the rule baselines are in,
the verdict is pre-committed (SETUP.md addendum 3), the launch script is ready; the memory arms
could not run because the GPU failed.** Status 2026-10-02 02:03 PDT. The sections below are in
the order they were written.

## The bars, on the rebuilt 8-a-day banks (ten households)

| rule | first question after each move (86) | unseen (about 190) | after a miss (about 105) | seen (about 395) | background, no recent move (414) | ordinary (2,480) |
|---|---|---|---|---|---|---|
| last-seen | 3.5 | 0.5 | 0.9 | 100.0 | 97.8 | 81.0 |
| alternate room (the thing's other usual room) | 44.2 | 21.0 | 1.0 | 2.5 | 31.9 | 63.7 |
| most frequent | 33.7 | 14.8 | 0.9 | 50.0 | 72.7 | 75.3 |
| same time of day | 32.6 | 13.6 | 0.9 | 45.2 | 70.5 | 85.1 |

Main score (first question after each move), paired per household against last-seen: alternate
room +40.0 (2 SE 11.5), most frequent +29.6 (5.6), same time of day +28.1 (8.2). Pill box forward
move 0 of 10 for every rule; return 2, 8, 10, 9 of 10. **Bar for the memory arms on the main
score: 54.2%** (alternate room plus 10), and not below last-seen on seen, background and ordinary
questions by more than the rerun floor. Alternate room wins by exploiting the keys' two or three
landing spots and pays for it everywhere else; nothing works after a miss.

Prompt leak check (`PROMPTS_seen_by_the_arm.md`): the memory arm sees the map, the two residents'
names (also in the object ids), the day index and clock, and its own looks; no calendar, illness,
schedule or routine words.

Launch, when the GPU is back: `./results/self_improve/wave_rare_movers_8_a_day/launch_memory_methods.sh memory_methods 10`
(20 cells plus two rerun cells, about 13,000 calls, 3 to 4 hours; needs vLLM on :8300).


## Prediction, written before the count (SETUP.md, 01:06)

Last-seen under 40% on questions within a day of a rare move; no memory within 10 points of
beating it unless the move has a visible cause. The count was expected to show whether the
existing banks hold enough such questions (30 or more per household).

## Measured: the existing banks hold almost none

Ten households, 31 days, 145 asked-about objects, 2,480 questions asked by the cells
(`coordination/studies/study4_rare_things_that_matter/RESULTS_count.md`, script `rare_moves.py`):

| | place level (receptacle) | room level |
|---|---|---|
| objects that never move | 15 (every towel, one tablet) | 46 |
| objects with 1 to 3 moves a month | 1 | 8 |
| objects with more than 30 moves a month | 103 | 71 |
| questions within 24 h after a rare mover's move | **1** | **6** |
| questions within 24 h after any move | 1,459 | 1,046 |
| questions about objects that never change room | | 1,094 (44%) |

The full 24-a-day bank would give 18 room-level rare-move questions, not the 300 needed. The
50-day run: 0 (place) and 1 (room). The eight room-level rare movers that do move are mostly the
illness movers themselves (out on day 12 to 14, back on day 24 to 31), not a separate class.

So the simulator's objects are two kinds: fixtures that never move and things that move daily
with the routine. There is no "moves twice a month" class, and a question slice of 6 cannot
separate anything (2 SE 49 points).

## What the count showed on the way (not the study's question)

On the questions within a day of any move (n = 1,046, ten households), paired against last-seen
(62.7%): the raw record plus notes +6.3 (2 SE 6.7, not separated at 10); the claim store -8.3;
the reduced ACE store -9.5; the working memory and archive -16.2; notes hidden -47.0. An
offline most-frequent that used true rooms the robot never had: +13.0 (2 SE 7.9), which is an
upper bound for that rule, not a baseline. On all other questions every method is above 83% and
within a few points of last-seen's 96.2%.

## The generator change it needs (sim-builder, started 01:14)

Two or three objects per household that move once or twice a month, each move caused by a
resident's action that the robot can see: medication goes to where the ill resident rests on the
first sick day and back on the first well day; keys go to where the last person home put them
(entry, kitchen counter, bedroom) and stay until the next arrival; glasses go to the bedside at
night and the desk by day only on working days. Questions about them concentrated in the day
after each move, 30 or more per household. The baselines must be run on the new bank first
(last-seen takes seconds); the memory methods only if last-seen is under 40% on the slice, as
predicted.

## Checkers

Blind recount: not yet; the count is a prerequisite, not a result. The counting script and its
definitions (place of an object at time t from the bank's truth rows; a move = a change of
receptacle; room level separately) are in the folder for the recount once the new bank exists.

## Blocked

Opus (usage file). The new bank's model runs need the vLLM server, which is down; starting it is
posted on the board first.

## GPU fault, 02:08 PDT

nvidia-smi: Unable to determine the device handle for GPU0: 0000:04:00.0: Unknown Error / No devices were found. torch.cuda.is_available() False. No process holds the GPU. /proc/driver/nvidia lists the card. Kernel log not readable without sudo. Posted to coordination/board.md.
