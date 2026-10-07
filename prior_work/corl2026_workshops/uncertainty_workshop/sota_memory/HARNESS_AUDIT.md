# Harness audit: three design decisions, checked against the banks and the records (2026-09-23 ~07:50)
Sources: banks_f1 (10 households, 4,130 questions), the workshop session's run1 prompts, results/confidence_shift_2026-09-20/tuning_log.md.

1. The truth arrives 10 minutes after each question.
   - Recorded rationale: tuning_log.md row 36 (10 min accepted with the nightly round), row 38 (60 min rejected: weaker
     rise), row 40 (delivery at the nightly review rejected: one timestamp per row put outcomes in the 03:00 bin). Nothing
     records why 10 minutes rather than 0.
   - Effect on which evidence a question has seen: none. 0 of 4,130 questions follow an earlier question about the same
     object within 10 minutes (minimum gap exactly 30 min, the question builder's rule).
   - Side effect: the correction carries the spot at the question instant but is stamped 10 min later (bank.py:486-490),
     so every correction is slightly misdated in memory.
2. The nightly round at 03:00.
   - Share of the evidence about the asked objects: 29% of sightings (23-41% per household); feedback after questions 70%;
     walkthrough 1%. In the recent-sightings prompts, 27% of sighting lines are stamped 03:00. The round gives exactly one
     sighting per asked object per night: where it rests overnight.
   - Chosen, and recorded as chosen: the Sept 20 sweep (tuning_log.md rows 1-24, 30, 36-38) tried patrols every 1-12 h and
     several fixed times. Dense patrols made every counter collapse to "last seen" and hid the shift; the sparse 03:00 round
     plus feedback was accepted because cheap learners then showed a learning slope and a break. A legitimate testbench
     choice, but not a neutral default, and it should be stated as a choice.
3. Unsensable questions (truth on a person, out of the house, or undefined): 0 of 4,130, in every household. Already
   excluded at the builder. The hard questions are something else; not measured.
