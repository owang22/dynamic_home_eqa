# Opus against Qwen on the same sightings: hypotheses, notes, first guesses (interim, 2026-10-03 01:17 PDT)

Setup and predictions: SETUP.md (written before any count). Same 50-day two-illness record for both models
(Qwen's cell, walked exactly); three homes; one run each, no repeats. Opus = claude -p, default effort.
Qwen = plain Qwen3.8 (the original cell, 26 Sep). Usage: ~2,300 Opus calls; five-hour window 0 -> ~72%,
weekly 61 -> ~72%.

## Hypotheses (CHECKER_SCORES.md, blind checker, Opus only; Qwen's nightly answers blocked by the GPU)
- Notices spell 1 on night 14 and its end on night 24, in 3 of 3 homes; spell 2 ends noted night 42, 3 of 3.
- Names illness on night 14 in 3 of 3; top guess on some nights in hh_s32 and hh_s48; settles on leave or a
  holiday by night 21-23 in all three ("he is up and about").
- Links spell 2 to spell 1 on night 32 in 3 of 3. Keeps the link only in hh_s32, whose spell-1 note was set
  aside intact; there it predicts the end "about 10 days, around day 41" (nights 36-37) and "day 41-42"
  (night 39); truth day 42. In hh_s2 (note rewritten night 32) and hh_s48 (rewritten night 34) the link and
  the duration estimate are lost. The prompt shows only a note's current wording (memory_notes.as_plain_words).
- Lasting error: hh_s48's Marco is a student out at classes; Opus calls him "working from home" all 49 nights.

## Notes (CHECKER_NOTES_AB.md, blind A/B, unblinded after)
- Opus's notes record both spells, start and end on the right day, in 3 of 3; rules by kind of day.
- Qwen's notes are ~95% snapshots and never record any change, in 3 of 3.
- The checker judged Opus's notes more useful in all three homes. Neither keeps spell 1's dates in a
  standing note during spell 2; neither estimates spell 2's length in a note.

## First room opened (results/stronger_model/opus_vs_qwen/score.py), mean over homes, 2 SE over homes
| comparison | settled | onset 1 | return 1 | onset 2 | return 2 | all 14 days |
|---|---|---|---|---|---|---|
| who chooses, Qwen's notes: Opus minus Qwen | +5.6 (6.1) | +1.9 (2.4) | +3.7 (2.4) | +0.9 (7.4) | -1.4 (2.8) | **+1.9 (1.5)** |
| whose notes, Opus choosing: Opus's minus Qwen's | +0.7 (1.4) | -0.9 (3.3) | +1.9 (3.7) | -1.9 (3.7) | -0.5 (0.9) | -0.2 (1.4) |
| both: Opus+Opus notes minus Qwen+Qwen notes | +6.2 (4.8) | +0.9 (5.6) | +5.6 (1.6) | -0.9 (3.7) | -1.9 (3.3) | +1.7 (2.0) |

- Whose notes hardly matters: Opus picks a different first room on 8-9 of 336 questions per home when
  given Qwen's notes instead of its own. The choice follows the sightings shown for that thing.
- Opus as chooser is ahead by +1.9 overall (3 of 3 homes positive, just past 2 SE), mostly in the settled
  days and the first return, not at the onsets.
- Prediction check: chooser +3 to 5 in the change windows and level when settled: wrong (largest when
  settled, ~0 at onsets). Notes effect under 3: right (~0).

## Caveats
- Qwen's cells are the 26 Sep run, not a same-session rerun; Qwen reruns move 2.5-6.2 points per home in
  change windows. One Opus run per cell, no Opus rerun floor.
- Qwen choosing on Opus's notes and Qwen's nightly belief answers are not run: GPU fault at 01:03.
