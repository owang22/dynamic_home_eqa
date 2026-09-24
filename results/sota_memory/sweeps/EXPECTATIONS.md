# Two counting-method sweeps (CPU only). Predictions written BEFORE any run; `date` checked: see the first line of the log.
Written 2026-09-23 19:08 PDT (date checked), before any sweep run.

Methods reported: the timetable that never forgets, the timetable with a three-day memory (72 h half-life), most frequent
(never forgets), the survival-time model (Perpetua*). The default roster also runs (last seen, periodic, 1-day memories).
10 households (seeds 0-9). Windows: settled (days 9-13), break (first 3 sick days), re-learning (last 3 sick days), return
break (first 3 days back). Each reported on all questions and on first-of-day questions.

## Sweep 1: minimum gap between questions about the same object: 0, 5, 15, 30 minutes
Same households (a COPY of the frozen sick10_owner households, so the shared ones are never regenerated), same regime; only
the question files change. Note: gap 0 takes 16 questions a day from all candidates; gaps above 0 take up to 16 from the
distinct candidates, so questions per day can differ. Reported.
- Coordinator (theirs): on all questions a smaller gap raises accuracy and SHRINKS the apparent break, because more questions
  repeat something just corrected; first-of-day barely moves. If so, the gap is redundant with the first-of-day split.
- Mine: agree on the direction. All-question settled accuracy +5 to +10 at gap 0 vs 30. The break on all questions shrinks
  by a similar amount, most for the recency-leaning methods (the three-day memory), least for the timetable that never
  forgets. First-of-day within ~3 points. But the first-of-day SET is a different sample at each gap (which question is
  first depends on which were drawn), so "barely moves" is only testable up to that sampling noise.

## Sweep 2: length of the sick spell: 3, 6, 10, 20 days (lead-up 14 and return 8 fixed)
New households per length (own folders; shared ones untouched).
- Coordinator (theirs): the best forgetting rate tracks the spell length. At 3 days the timetable that never forgets is best
  overall; by 20 days the three-day memory wins clearly. The return break grows with spell length for the adaptive methods and
  stays near zero for the one that never forgets.
- Mine: the crossover in overall accuracy falls between 6 and 10 days. The three-day memory's return break grows with length
  but SATURATES by about 6 days, since a 72 h half-life has mostly forgotten the lead-up after a week. Sharpest prediction:
  at 20 days the timetable that never forgets ALSO breaks on the return, because 20 sick days outnumber the 14 lead-up
  days in its hour bins. Its "stability" is only a vote count, and a long enough disruption outvotes the routine. Most
  frequent (never forgets) likewise.
