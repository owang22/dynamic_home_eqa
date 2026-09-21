# Problems found (follow-on: baselines, told arm, affected split)

Started 2026-09-20 ~20:30 PDT. Same households, banks and questions as `../heldout/` (frozen config).

1. **The generator's cause log alone gives an affected share of 7% (10% on weekend days), under the brief's 20% floor.**
   Only ~5% of placements carry a cause tag, and the weekend is not a tagged cause at all: it is a
   different activity template per resident role. Also, a sick day or the weekend acts on a routine
   belief mostly by *removing* an activity (no commute, so the laptop stays on the desk); that placement
   was made the night before and is untagged. Fix: `baselines/patrol/affected.py` labels a question
   affected when (a) the placement carries a guest_visit/sick_day cause, (b) the placement was made on a
   weekend by a resident's weekend-only activity (per resident, from the templates in activities.yaml),
   or (c) the owner's routine weekday activity that uses the object is off the schedule that day
   (weekend template, sick-day or guest-visit removal) and did not happen. Result: 20-24% on weekend
   days, 17-28% among shift-day questions on event days, 1-4% among non-shift-day questions.
   Both labels are logged (`affected` and `cause_log_only`).
2. **Bug caught while building (fixed):** a resident sick on three weekdays made `rest_couch` a
   "routine" activity and it then counted as absent on the other days. Routine activities are now
   restricted to the weekday template and an activity actually done that day is never absent.
3. `shift_days` in the bank header = weekend days plus guest_visit/sick_day days (not only the
   weekend). The figure shades those. Other events (laundry_day, late_work, rain, grocery_delivery:
   2-5% of questions on late days) are never told to the robot and are counted unaffected.
4. **Observed in the running mixture arms (not mine, noted 20:55):** in all ten passive longleaf arms
   (hh_s10-14, told and not told) the effective sample size is 1.0 from the first scored question and
   only one document carries more than 1% of the weight (`live.jsonl` `ess`, `weights`). The walkthrough
   day plus 12 full patrols before the first question is enough to collapse the weights. So the
   "mixture" confidence is one document's top probability, and "agreement" is trivially 1. Flagged to
   Oliver; not changed here.
5. **Bug in the earlier harness (found 21:05, reported to Oliver and to the other agent):**
   `configs/frozen_2026-09-20.yaml` says `negative_evidence: off`; YAML reads `off` as boolean False and
   `confshift.cmd_classical` compares against the string "off", so the branch never fires. Every frozen
   classical log in `heldout/classical` and `tuning/*` ran WITH empty-look suppression (24 h half-life),
   contrary to the report text. Effect on most-frequent, tuning seeds 0-9: 44.6% accuracy / mean
   confidence 0.70 with suppression off (as intended) vs 56.5% / 0.94 as run. It is also why most
   frequent, last seen, periodic and timetable all show the same 58% in report.md: with suppression on,
   every full patrol pins every object to its last-seen spot. The passive longleaf arms started 20:19
   do not set `PARTICLE_NEGATIVE_HALF_LIFE_H` either, so their particles use the 24 h default.
   Not fixed by me (the other agent owns confshift.py and the arms); the follow-on runner
   (`patrol/bocpd.py`) takes the switch explicitly and both settings are reported.
6. **2 h patrol hid the shift (found by the other agent from the Monday rise; Oliver flagged it).** Every event
   parks its objects where the next pass re-sees them, so at 2 h affected questions were not harder for recency
   agents (last seen 72% on affected objects on Monday). Re-frozen at 8 h; p2 results kept under `p2/`.
7. **Detector burn-in (fixed):** with three patrols a day the warm-up on the walkthrough day is one sample, so
   the run length was trivially short on day 1 and every household "fired" at mass 1.0. No reset is now allowed
   until the detector has run `recent + 1` steps past the warm-up (applied at both densities; p2 detect logs
   regenerated).
8. **"Affected" mixed fresh moves with moves the patrol had already seen (Oliver, via the other agent, 21 Sep 00:10).**
   A Monday question about an object a Sunday activity moved was labelled weekend_moved although the patrol had
   seen it there since, so every recency agent got it right and the after-days cancelled the hard first-day
   cells. Fix: a move counts as affected only while it is *fresh* (the placement was made after the last patrol
   pass before the question); seen-since moves are their own kind, `after_shift`. Freshness depends on the
   patrol times, so the labels are now per density: `affected/labels_p8.jsonl`, `labels_p2.jsonl` (the previous
   labels kept as `labels_v1_anyfresh.jsonl`). Affected share on the weekend falls from 20-24% to 18-19% (p8).
   Per-kind accuracy at 8 h now reads as it should: event moved 6-22% and weekend moved 12-19% for every agent,
   after shift 62-100% (last seen 100%).
9. Page palette moved to pastel lines on a softer ground at Oliver's request (eye strain on dark backgrounds).
