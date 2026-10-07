# The five variants in this wave read no sighting log, 2026-09-26

`search_driven.py` decided whether the robot is handed the raw log of past sightings of the
quizzed object - and whether it is asked what the people are doing - by testing the arm name with
`==` against the single name `the log and notes about the routine`. The five arms built on that
one are named differently, so **all five searched and answered without the log while the arm they
are variants of had it**:

    ours_sixteen_notes_a_night      ours_eight_notes_a_night      ours_allowance_derived
    ours_told_the_night_before      ours_told_on_the_first_night

What the log is worth, paired on the three homes, first room right, from these very cells:
+17.3 points in the settled window (2 SE 8.1, 3 of 3), +26.0 during the illness (2 SE 2.0),
+20.8 on the day the routine goes back to normal (2 SE 19.2).

**So no number from these five cells is a statement about our method.** They are an ablation of a
different arm: notes written about the routine, with no log to read when answering. Kept under
that reading, and useful under it - notes without the log lose to a mechanical rule over the same
log by 16.1 points in the settled window. The arms rerun with the log are in
`results/self_improve/wave_the_family_reads_the_log`, and the cap results quoted before this file
was written - eight against sixteen on day 24, sixteen against the counted allowance - belong to
this ablation, not to the method.

The fix is membership in `THE_LOG_AND_THE_ROUTINE_FAMILY` at both places, `search_driven.py:480`
and `:590`. It was checked rather than assumed: one day of the sixteen-a-night arm rerun after the
fix made 0 model calls and 34 cache hits, and its day-1 searches are now byte-identical to the
parent arm's, where before the fix they differed.

One smaller drift in this wave. The sentence that states the nightly note limit landed at 00:34 on
2026-09-26, so `the_log_and_notes_about_the_routine` ran on hh_s32 and hh_s48 without it and its
hh_s2 cell, rerun after the overwrite, has it. On hh_s2, where both exist, it moves first room
right by at most 4.2 points on any one window, inside the rerun noise floor. The cell without it
is kept in `damaged_by_the_50_day_overwrite_2026-09-26/`.
