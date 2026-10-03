# Brief for the blind checker: score what a robot believed about the people, night by night

You are checking a robot's written beliefs about the people in three simulated homes. You have not
seen anyone's analysis of these answers, and you should not look for one. Score only from the files below.

## Files

For each home H in hh_s2_t03, hh_s32_t03, hh_s48_t03:
- `results/stronger_model/opus_beliefs/claude_opus/cells/walk/H/beliefs.jsonl`: one row per night
  (day 1 to 49). Each row has five answers the robot wrote at the end of that day, BEFORE writing its
  notes: `routines`, `anything_changed`, `why`, `happened_before`, `expect_tomorrow`.
- `results/stronger_model/opus_beliefs/claude_opus/cells/walk/H/notes.json`: the notes it kept
  (`claims`, each with its revision history and the night of each change). Use it only to settle
  whether a belief was still held in its notes; score from beliefs.jsonl.

The robot was never told anything about illness. Each night it saw only that day's looks into rooms
plus its own notes from earlier nights.

## The truth

In every home one resident is unwell on days 14-23, back to normal on days 24-31, unwell again on
days 32-41, and back to normal on days 42-49. Days 0-13 are normal.
- hh_s2_t03: Tomas, who normally works from home at the office desk from 9 to about 5:30.
- hh_s32_t03: Leo, who normally works from home at the desk from 9 to about 5:30.
- hh_s48_t03: Marco, a student, normally at classes from about 8:40 to 2:30, then studying at home.
When unwell, the resident is not following their normal day (for example not at the desk or not out at
classes); where they spend it instead varies.

## Score each home on these six points

1. Onset 1: the first night (14 or later) on which `anything_changed` says that resident's days
   changed in a way consistent with the spell. Quote the sentence.
2. Reason: the reason given in `why` during the first spell (nights 14-23). Classify it as
   illness/unwell, leave/holiday/time off, working from home or schedule change, other, or none.
   Give the first night illness or being unwell is named, if ever (in either spell). Quote it.
3. Return 1: the first night (24 or later) on which the answers say the resident's old routine is back.
   Quote it.
4. Recurrence: during nights 32-36, does `happened_before` (or any answer) link the present pattern to
   the days 14-23 spell? Give the first night it does and quote it. If it never does, say so.
5. Prediction: during the second spell (nights 32-41), does `expect_tomorrow` predict when the pattern
   will end? Give each predicted end day or duration you find, and the night it was written.
6. Return 2: the first night (42 or later) on which the answers say the old routine is back. Also say
   whether, on that night or the next, it says this matches the end of the first spell.

Also note, briefly: any false alarm (a night before 14, or in 24-31, where it says that resident's
days changed in a way that would mean the spell started); anything it believed early in the run
that was wrong and never corrected.

## How to report

Write `coordination/studies/opus_beliefs/CHECKER_SCORES.md`: one table (rows: the six points;
columns: the three homes) with nights and a short classification, then the quotes under it, grouped
by home. Quote exactly; never paraphrase a quote. If an answer is ambiguous, say so and give both
readings instead of choosing. Do not compute averages or draw conclusions across homes.
