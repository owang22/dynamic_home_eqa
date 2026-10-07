# What Opus believes about the people, through two illness spells

Asked by Oliver, 2026-10-03 ~00:00 PDT: can an Opus model used only to answer questions form hypotheses
about the people in the home and their routines, update them when an illness strikes, and what does it
do when the illness comes back? Opus usage approved by Oliver the same night (status-line usage file
added; weekly usage 61% at 00:06, resets 20:00).

## Setup

- Record held fixed: the 50-day two-illness run, Qwen cell "the log and notes about the routine",
  homes hh_s2_t03, hh_s32_t03, hh_s48_t03 (resident 1 ill days 14-23 and 32-41, back on 24 and 42).
  The walk answers every room choice and answer from that cell; checked question by question
  (dry run 2026-10-03 00:08: 1,176 of 1,176 questions match in each home).
- Opus (fresh `claude -p` per call, no tools, no settings, default effort) gets the arm's own nightly
  notes prompt every night and keeps its own notes across 50 nights.
- Each night from 1, before the notes call, Opus answers five fixed questions with the same view
  (today's looks + its notes): routines; anything changed (who, what, since when); why; has it
  happened before (when, how it ended); what tomorrow brings and how long the pattern lasts.
  The questions never mention illness or change timing. Code: src/stronger_model/opus_beliefs.py.
- 297 Opus calls in all (99 per home). Output: results/stronger_model/opus_beliefs/claude_opus/cells/walk/<home>/
  (beliefs.jsonl, notes.json).

## How it will be scored (written before reading any answer)

A blind checker who is given the true spell days scores each home on:
1. first night the answers say the ill resident's days changed (onset 1 = day 14);
2. whether the stated reason is illness / being unwell (vs leave, holiday, working from home, other);
3. first night after day 24 the answers say the old routine is back;
4. at the second spell (nights 32-36): whether "happened before" names the first spell, and on which night;
5. whether it predicts a return, and the day it predicts, during the second spell;
6. after day 42: first night it says the routine is back.

## Prediction (study-lead, before any Opus call)

From Sonnet on the 31-day run (one clean closure in three homes, never named illness, never told):
Opus notices the change by night 16 in 3 of 3 homes; names illness or being unwell as a likely reason
in at least 2 of 3 (the "why" question asks directly, which Sonnet's notes never were); says the old
routine is back within 2 nights of day 24 in 2 of 3; links the second spell to the first by night 34
in 2 of 3 (only possible if its notes kept the first spell; Sonnet's notes did in 1 of 3); predicts a
return near day 42 (within 3 days) in at most 1 of 3.

## Change before any answer was read for scoring (00:12)

First launch 00:10: the five answers were cut at 1,200 characters each, and Opus writes ~2,200 for
"routines" (3 of 3 homes, night 1). The answers are the measurement, not the method, so the limit was
raised to 6,000 (not stated in the prompt either way) and the run restarted from night 0. The notes
keep the arm's own limits (16 edits, 240 characters a note). Night-1 notes calls are reused from the cache.

## Addendum 1 (01:01 PDT, before any count): Opus against Qwen on the same sightings

Oliver, 00:58: this run should be about whether Opus makes smarter decisions, summarises memory better
and proposes better hypotheses than Qwen. Code: src/stronger_model/opus_vs_qwen.py. Qwen = plain Qwen3.8
(no thinking), the study's own model; Opus = claude -p default effort.

- Hypotheses: plain Qwen answers the same five nightly questions with its own notes (exact replay of the
  cell's notes, checked equal). The blind checker scores both, labelled A and B, on the six points above.
- Notes: the blind checker compares both note sets at nights 13, 23, 31, 35, 41, 49 against the truth,
  labelled A and B.
- Decisions, a 2x2 on the first room opened: chooser (Qwen, Opus) x notes writer (Qwen, Opus), same
  sightings, days 12-13 (settled), 14-16, 24-26, 32-34, 42-44: 336 questions per home, 1,008 per cell.
  Paired per question; read per window and per home; Qwen's fresh answers on its own notes are compared
  with the cell's recorded first rooms to give a rerun floor for Qwen.

Prediction: Opus as chooser beats Qwen by 3 to 5 points on the same notes in the change windows, and is
level (within 2) in the settled days. Whose notes has less effect than who chooses (under 3 points
overall). Opus beats Qwen on noticing the change and on saying the routine is back; Qwen names illness
less often. Opus's notes are more numerous and more often split by condition (work days vs days off).
