# Frozen regime (2026-09-21, 15:30) — the testbench shape

Two configs, same design, frozen as `configs/frozen_regime_2026-09-21_person.yaml` (F1) and
`configs/frozen_regime_2026-09-21_household.yaml` (F2). Results: `results/regime_search/sick10_owner` (F1) and
`results/regime_search/sick10_all` (F2); page https://claude.ai/artifact/H1q17m8yUpCEac8kAek2pc.

## The regime
- Calendar (scripted, no random events): 14 weekdays lead-up (A); days 14-23 off sick — F1 one resident, F2 every
  resident — (B); days 24-31 back to the weekday routine (A again). Day 0 is a Monday and the walkthrough day.
- Observation channel: one patrol round at 03:00 plus found-it feedback 10 min after every question.
- Question type (unified): "the person's everyday things, asked while in use" — book, water bottle, tablet, mug, charger,
  glasses, glass, razor — the question is asked DURING the activity that uses the object (uniformly inside the block),
  at most one question per object per 30 min, so a day carries its natural number of distinct questions (F1: 12-16 about
  one person's things; F2: 22-24 about everyone's). 10 held-out households (seeds 0-9); 20 more are one command away.
- Agents: last seen, most frequent, timetable (2 h bins), periodic, Perpetua*, plus timetable and most frequent with
  3-day and 1-day half-lives (`extra_beliefs`). No LLM agents in the loop.

## The shape (mean daily accuracy over 10 households, all questions)
F2 household: timetable 3 d hl  lead 47 -> 82 | B: 34, 49, 61, 72, 78, 81, 86, 83, 88, 88 | A: 54, 60, 71, 77, 76, 81, 75, 79
             most freq 3 d hl   43 -> 55 | 18, 30, 42, 59, 72, 73, 72, 75, 80, 82 | 29, 40, 50, 54, 59, 66, 60, 60
             frozen timetable   46 -> 80 | 35, 47, 55, 56, 64, 67, 72, 64, 75, 74 | 80, 78, 79, 82, 83, 84, 75, 79
             last seen          40-55 flat.
F1 person:   timetable 3 d hl  46 -> 85 | 42, 59, 72, 75, 84, 86, 90, 86, 91, 88 | 58, 65, 58, 72, 76, 78, 80, 79.
Error bars (sd across households of daily accuracy): F2 timetable 3 d hl day 13 82±10 -> day 14 34±11; day 23 88±4 ->
day 25 59±11 -> day 26 70±12. Entry drop ~4 sd; return drop > 2 sd; the frozen learners show the entry drop, a slower
partial re-learning, and NO return drop (14 lead days outvote 10 sick days in every bin); last seen shows nothing.

## Design rules learned (each one cost a run; see NOTES.md)
1. Ask DURING the activity, not at its start: at the start the object is mid-move (16% stable), ceiling ~55-70%.
2. A TIMING shift (night shift, holiday hours) does not break use-time questions: the answer is keyed to the activity.
   Only PLACEMENT shifts break them (sick: things migrate to the couch / coffee table). Novelty must be "same hour,
   different spot"; "new hour" novelty is answered by the usual-spot fallback.
3. Ask about the objects the regime moves — the affected people's everyday things — not about the meal set or static
   objects; regime novelty (share of questions whose truth leaves the lead answer) is the ceiling of any drop
   (F1/F2: 51-55% vs a 21-26% same-regime baseline).
4. The shift must be long enough to re-teach the bins (10 days; 5 days gave one-day dips) and must hit the whole asked
   group (one resident sick + whole-house questions gave 13 points; everyone sick or that person's own things gave 40+).
5. The return drop is a property of learners that forget; frozen counters never show it. That contrast (plasticity vs
   stability) is the method axis the testbench exposes.
6. No repeated questions inside an activity block: the feedback of the first answers the second and double-counts errors.
