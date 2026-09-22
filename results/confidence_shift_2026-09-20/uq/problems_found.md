
## 14:24 P1 — the plain mixture martingale can never fire on a 28-day bank (found on hh_s0 sick_owner, first household)
Symptom: mart/mon agents on sick_owner hh_s0: max martingale per day 1, 1, then 0.000 for days 3-27; 0 fires although the
frozen timetable drops 100 -> 22% on day 14. Cause: a nonnegative martingale started at 1 over ~400 stationary questions
decays to ~1e-5 (its expectation is 1 but the mass sits on rare paths); a 100x rise from there needs more evidence than 5
sick days give. This is also why the previous agent's fb-bank runs never fired (0/72 shift days) — not "no cliff to
detect". Fix: the CUSUM e-detector of Shin, Ramdas, Rinaldo 2024 (each mixture grid point restarts at 1 whenever it drops
below 1; threshold 1/delta with delta 1e-3 because the guarantee is an average run length, not Ville's inequality).
Synthetic: false alarms 2/50 stationary streams of 1000 steps at 1000; mild shift (90 -> 50% accuracy) detected after a
median 21 questions (max 61). The plain martingale needed 24-237 steps on the same mild shift (threshold 100) and is kept
as `--detector mixture`. uq_synth.py extended with the cusum checks; EXPECTATIONS E3-E5 unchanged (fire day 14-15, lead
<= 2/10 households).

## 14:27 P2 — repeated questions count as repeated evidence (hand check of the hh_s0 day-19 fire)
The frozen-timetable monitor fired on day 19 (return) in hh_s0 on d19q28-q30: mug_yuki asked five times in a row during
evening_tv, minutes apart, truth sink_k1, p(truth) = 0.00 each time (the found-it feedback lands 10 min after the first
question, after all five). The detector saw five independent p-values of 0.001-0.013 for one error. Also on day 18
(rest_couch: water_bottle / mug / charger each asked 3-4 times). Fix: the detector steps only on questions that carry new
information — a repeat of the same object with no positive sighting of it since its previous question and the same truth
is logged (`dup: true`) but does not move the detector (`--no-dedupe` restores the old behaviour). The conformal agent
is left per-question, since coverage is scored per question.

## 14:38 P3 — LLM token-probability channel: the JSON-string schema makes "J) somewhere else" a tokenization artifact
First 6 rows of the day-13/14 test on sick_owner hh_s0: mcq_answer "other" with conf_token 0.00 in 4/6, while the greedy
JSON answer was right in 5/6. The cache shows why: with the letter forced to be a JSON string, Qwen's tokenizer has
merged tokens '"A' .. '"I' but not '"J'; the first token's top alternatives are '"' (-0.53) vs '"C' (-1.34) vs '"B'
(-2.09) ..., the bare quote wins greedily, and after a bare quote only J follows (-0.0). So the channel chose "somewhere
else" by tokenization, and letter_probs (first token only) read the letter mass for A-I but 0 for J. Fix: the
multiple-choice call is made without a schema ("Answer with the letter only", max_tokens 2) so the bare letter is the
first token; the first 6 rows moved to hh_s0_v1_quoted_letter_bug.jsonl; greedy and sample calls are cache hits.

## 19:24 P4 — DiscountedTimetable.discount() accepted objects= but silently dropped it (found before any new run, from reviewer feedback on task 3)
`class DiscountedTimetable` (uq_agents.py, added for the martingale reset on a timetable base) took a `discount(t, factor,
objects=None)` call matching `DiscountedMostFrequent.discount()`'s signature (bocpd.py) but never stored `objects` and
never filtered by it in `weight_since` — every discount was applied to every object regardless of what was asked for.
Harmless so far: every existing caller (mart_tt, mart_tt72, martw_tt72, the monitors) only ever wanted a global reset and
passed `objects=None`, which is what happened either way. It would have silently broken task 3's per-person targeted
reset (discount only the sick resident's bins) had it shipped unfixed. Fix: `_discounts` now stores `(t, factor,
frozenset(objects) or None)`; `weight_since(t_obs, t, object_id)` filters by membership; `_predict_from_history` moved to
`_predict_for_object` (the hook that actually receives `object_id`), mirroring `DiscountedMostFrequent`. Verified no
regression: uq_synth.py all-pass; degenerate checks still 0/0 mismatches on both banks; mart_tt/mart_tt72 fire-day counts
on sick10_all and sick10_owner identical to the pre-fix numbers in REPORT.md (mart_tt 2/9/0 and 1/6/1; mart_tt72 0/8/5
and 1/5/3, lead/day14-15/return).

## 19:56 — per-person conformal reduces but does not eliminate resident_2's collateral set growth (not a bug, a data-thinness effect)
Split the online-conformal threshold per resident (ocpperson_tt), same pattern as the martingale/hedge. Verified clean:
every resident_2 row is scored under its OWN conformal object (0/744 cross-assignment on hh_s0). Result: resident_2's
set size on the shift days shrinks substantially (day14 9.7->6.7, day15 12.2->8.9, global vs per-person) but does not
drop to its pre-shift level the way the per-person RESET did (which was an exact match). Reason: resident_2's own
lead-stage baseline set size is ALSO higher under per-person (2.6->4.7 on days 12-13) — splitting the conformal
threshold gives resident_2's detector only ~110 questions total (vs 744 for resident_1) to calibrate on, and the
online conformal quantile is noisier with less data regardless of stage. Unlike a discrete reset (apply or don't,
to a chosen object set), online conformal's threshold is a continuously-updated statistic whose OWN calibration
quality depends on sample size — a genuinely thin group will have a wobblier q_t even with zero cross-contamination.

## 23:20 — llm_live_extra.py's first "lead" window definition was wrong (self-caught during cross-session validation)
Extended llm_live_extra.py to pull the workshop session's one-person-sick arms (run1/run2_told/run3_toldret —
"no message"/"start message"/"start + end messages" in Oliver's later naming decision) and sent 5a's own
headline numbers to check the join against: buffer(naive), no message, lead=78, 14-16=58, 17-23=66, 24-26=74,
27-31=77. My first pass defined "lead" as the full days 1-13 and got 74.4 for lead (the other four windows
already matched to within 0.4pp) — a >1pp miss, exactly the threshold 5a set for "something is off in the join,
tell me before publishing." Investigated before either trusting my own number or assuming the join was broken:
checked day-by-day accuracy for that arm (day1 54.8% -> day13 81.5%, a genuine ramp, not noise) and found
"last5lead" (days 9-13, the SAME window name/definition already used elsewhere in this study, uq_windows.py and
shared_state_extra.py's WINDOWS list) gives 78.3 — a 0.3pp match. The bug was mine: I'd used the full lead range
instead of this study's own established "lead" convention (the saturated end of the ramp, not the whole climb).
Fixed WINDOWS5 in llm_live_extra.py to use days 9-13 for "lead"; re-verified all 5 windows (both no message and
start message) now match 5a's numbers to within 0.7pp. No fix needed to the join itself (question_id match, truth
lookup, day assignment) — it was correct throughout; only the window LABEL was wrong. Logged because a future
script computing "lead" here should use days 9-13, not 1-13, to stay consistent with the rest of this study.

## 23:52 — AskGate's decaying-step update needed the opposite sign from DecayingStepConformal's
Built an adaptive-conformal answer-or-ask gate (score = 1 - stated confidence, alpha=0.10) for the LLM arms,
meaning to reuse `DecayingStepConformal` (uq_agents.py) directly the way `uq_llm_conformal.py` already does for
KnowNo sets. Caught before shipping: that class's update, `q += eta*(err - alpha)`, GROWS q on a miss because a
bigger q means a bigger, more inclusive prediction SET (safer when a candidate was missed). For an ask-gate, q
is instead the MINIMUM confidence required to trust the model's own answer — after a miss (trusted and wrong),
the gate should become MORE cautious, i.e. RAISE the bar, which the same `q += eta*(err-alpha)` formula already
does correctly once q is interpreted this way (bigger q = harder to trust = asks more) — the direction only
looks backwards if you carry over the SET-style "bigger q = more permissive" intuition from the honest-sets
agents. Re-derived it standalone as a small `AskGate` class in llm_live_extra.py (same decaying-step math, warm
start on the alpha-quantile of confidence) rather than force-fitting `DecayingStepConformal`'s `set_of()`
interface to a scalar case it wasn't built for. Verified directionally sound on real data before trusting it:
the naive/buffer/no-message arm's gate confidence bar rises 0.78 -> 0.90 right at the shift (tightened_at_shift)
and its ask rate and miss rate both climb then ease back down through the sick spell, the expected shape.
