# sota_memory — results as they land (dynamic-home-eqa-34). Predictions are in EXPECTATIONS.md, written before each run.

All figures: per household, paired on the same questions against the recent-sightings list (the workshop session's run1),
households hh_s0, hh_s1, hh_s2 of banks_f1, no message. n=3, so the bar is "mean bigger than the spread across households".
Tools: stage_table.py, strata.py (moved = true spot differs from the object's usual spot at that hour in the lead-up).

## Most recent same-hour sighting pinned to the top of the prompt — landed 02:34, all 496/379/496 questions, 0 fallbacks
First-of-the-day questions about an object (cold), pinned minus recent-sightings list:
| window | hh_s0 | hh_s1 | hh_s2 | mean | spread | bar |
|---|---|---|---|---|---|---|
| lead-up 9-13 | 82->82 | 64->82 | 85->95 | +9.3 | 8.9 | not distinguishable: one household (hh_s1) carries it |
| first sick days 14-16 | 12->18 | 37->37 | 20->20 | +2.0 | 3.4 | no |
| rest of spell 17-23 | 21->33 | 36->64 | 33->42 | **+16.8** | 10.3 | **passes; all three up** |
| day 24 alone | 40->80 (n5) | 50->50 (n6) | 75->50 (n4) | +5.0 | 32.8 | cannot be tested: 4-6 cold questions per household |
| first days back 24-26 | 50->64 | 50->57 | 92->77 | +2.0 | 15.5 | no |
| later return 27-31 | 68->86 | 62->69 | 91->82 | +5.3 | 13.7 | no |
All questions, rest of the spell, things the shift moved: 46->52, 66->77, 57->61, mean +7.3, spread 3.6 (passes).

Against the predictions:
- Lead-up "within 3": WRONG. +9.3, mostly hh_s1 (64->82), whose lead-up was weak for every memory. Pinning helps a memory
  that had not locked on to the routine, too.
- First sick days "+10 to +20 cold": WRONG, +2. Days 15-16's pinned line is often still a lead-up sighting, because
  day 14 had no sighting at that hour.
- Rest of the spell "cold 45-60": PARTLY. 33/64/42. A real gain, all three households up, but only hh_s1 reached the range.
- Day 24 "pinning hurts": NOT SEEN, and the window cannot say either way (4-6 cold questions per household, spread 33).
Reading: salience is part of the read-time failure but not most of it. Pinning the right line recovers about 17 of the
roughly 45-60 cold points lost in the spell.

Notes on reading (agreed with the coordinator, 02:40):
- First sick days: the +2 means the intervention had nothing to work with, not that pinning does nothing. On day 14 there is
  usually no sighting at that hour from the new routine yet, so the pinned line is a lead-up sighting. Pinning then makes the
  stale record more prominent at the break, although the data show no measurable harm from it (+2, spread 3.4).
- Day 24: the prediction that pinning hurts there is neither seen nor refuted. It cannot be tested on 4-6 cold questions per
  household.
- Bound: pinning the right line recovers roughly a third of the cold loss in the spell (~17 of ~45-60 points). Most of
  the read-time failure is not the model failing to notice the line.
- The comparison with removing the resident card (next section) compares two INTERVENTIONS paired on the same questions. It
  is not a decomposition: the two arms differ in more than one way.

## Problems found (newest last)
- 02:45 FUTURE SIGHTINGS LEAKED INTO THE FACT STORE. The nightly fact write for day d read the memory as it stood when it
  ran, not as it stood at the end of day d. Because the write for days 0-10 runs only when the first answered question
  (day 11) arrives, the day-0 facts were built from 11 days of sightings. Found because the day-0 prompt differed between
  the smoke run (--days 4) and the real run (--days 11-...). Fixed: the write filters sightings to before the end of its
  own day. Verified: the day-2 extraction prompt is now byte-identical under --days 4 and --days 11. The leaky partial run
  was moved to withdrawn/. The earlier smoke runs (extraction v1-v3) carry a smaller version of the same leak (one day's
  early sightings); they were only used to judge extraction wording.
  My earlier statement that the day subset is exact for the fact store was FALSE until this fix. It is true now.
- Method note: an UNEXPECTED CACHE MISS is evidence about the pipeline. The prompt cache is not a correctness check, but
  a miss where a hit was expected means something upstream is not deterministic, and here that non-determinism WAS the
  bug. The irony is worth one line in the write-up: a memory built to represent when facts were true was building its
  early facts from evidence that did not exist yet, and it would have looked well-behaved in the settled period for the
  wrong reason. The day-subset exactness statement is now scoped per arm in llm_sota.py's docstring.
