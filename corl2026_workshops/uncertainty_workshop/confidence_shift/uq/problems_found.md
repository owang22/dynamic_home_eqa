
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

## 00:45 — the "hung" reflection arm had actually crashed on a leak-check false positive; two fixes, one misdiagnosis logged
Symptom (00:27 proactive check): hh_s5 / reflection / no-message sat at 2 calls for 50 min while its 29 siblings
were at ~170. I read the process's threads (all sleeping in poll, no busy loop) as "one request vLLM never
answered", proposed and did a cache-backed kill+relaunch (approved), and added a 900 s hard per-request deadline
to LLMClient (a watchdog that shuts the socket; verified on a silent server). After relaunch the arm stuck at the
same 2 calls again -> deterministic -> reproduced offline with --replay-only: `RuntimeError: LEAK in LLM-authored
notes d1q01: ['cause']`. The arm had DIED at 23:35:38 on its first day-1 question because its own day-0 reflection
note ended "...the likely cause of the error (e.g. ...)" and the leak gate's LLM-authored-prose pattern still
forbade the truth-row field names cause/causes/reason as bare words. The pool keeps a dead arm's thread idle and
main() only prints "ARM FAILED" when its ordered result loop reaches that future (at the end of the pass), so a
crash in the middle of a 30-arm pass is indistinguishable from a hang from the outside. Misdiagnosis: a thread in
poll() is also what an idle pool thread looks like; I should have checked for a dead future (or reproduced offline)
before calling it a lost request.
Fixes: (1) leak_check.PROSE_PATTERN now forbids only structural ids in model-written text (snake_case event/field
names, resident_N, "whim") — the model never sees the truth rows' cause/reason fields, so its own English use of
those words cannot leak them; they stay forbidden in harness-authored text. (2) llm.main() attaches a done-callback
per future that prints "ARM FAILED (live)" the moment an arm dies. (3) chain_watch.py (every 5 min) flags any arm
with 0 new calls in 15 min while others move, as a VERDICT line. The 900 s deadline stays as hardening. hh_s5/
reflect/no-message rerun standalone into the same out/cache dir at 00:45; the told passes pick up the fixed code
automatically (separate processes). No other arm has tripped the gate so far; any that did would now show up live.

### 00:52 — leak-gate audit (coordinator's condition for the prose-rule change): strict rule re-run over every model-written span
`python3 -m baselines.patrol.leak_audit` (new, re-runnable): 126 arms on disk (90 finished, 5a's run1/run2_told/run3_toldret/
partial/partial_told + this session's chain_person), 49,507 prompt rows. Strict-rule hits inside MODEL-WRITTEN spans:
ENGLISH 4 (all the word "cause", all in hh_s5/reflection/no-message's day-0 note, quoted into 4 prompts), STRUCTURAL 0.
Running tally of flagged/near-miss model-written text under the old rule: 1 arm, 4 prompts, 1 distinct word, 0 structural.
To be re-run once every arm has finished (end of night) and the count updated here.

## 01:55 — two spells: the counters' second break is much smaller than the first, and I cannot yet explain why (OPEN)
sick2x_owner classical suite (10 hh, 42 days; E30 predicted |break2 - break1| <= 5 pp for the forgetters): 3-day
timetable break1 23 pp (81 -> 58) but break2 5 pp (79 -> 74); 1-day timetable 14 pp then NO break (77 -> 78);
never-forgets 31 then 14; hedge 24 then 12. Checked before believing it: (1) the bank IS a sick spell both times —
sick_day causes and hints on 14-20 and 28-34, and the truth matches the object's usual lead spot only 5% of the time in
spell 2 (9% in spell 1); (2) it is not a same-day-feedback flattery — cold questions show the same thing (tt3d cold 47%
at break 1 vs 70% at break 2; tt1d 53 vs 71). A 1-day forgetter holds nothing of spell 1 on day 28, so this is NOT
memory reuse; the second spell must be easier for a time-of-day counter in some way my per-object "usual spot" measure
does not see (the binned time-of-day overlap between the sick and normal routines, or which activities the questions
sample on days 28-30 vs 14-16). Consequence for the reuse question: the counters are a weak absolute yardstick here;
the LLM two-spells arms must be read RELATIVE to the counters on the same days (second break of buffer minus second
break of tt1d), which cancels whatever makes spell 2 easier. Flagged to the coordinator; on the page as "unexplained".

### 02:10 — RESOLVED: the small second break is real reuse through the bin structure (coordinator's three checks, no server)
(1) last seen: no break either time (47->57 then 49->59) — the world is not easier in spell 2. (2) novelty vs the
preceding normal stage at (object, 2 h bin): 26% of spell-1 questions vs 28% of spell-2 — the second spell moves as many
asked things. (3) evidence source of the queried bin for the 1-day timetable: in spell 2, 53% of questions hit a bin
whose ONLY sightings are from spell 1 (the return days never put that object in that hour), and on those it is 97%
right; the 44% with fresh return-day sightings in the bin are 65% right (= its first-spell number, 66%). Mechanism:
TimetableLookup pools every past sighting in the bin and the half-life only REWEIGHTS them — a bin the normal routine
never writes is never overwritten, so a "1-day" memory keeps a spell-1 placement indefinitely. The sick routine happens
at hours (and for objects) the normal routine leaves empty, so a time-of-day-indexed memory reuses the first spell by
construction. Not a bug, not a confound: a property of per-hour memories worth stating. E30's prediction was wrong
because it assumed forgetting is absolute; it is relative within a bin. Consequence for the LLM arms: a retrieval memory
keyed on time of day (ours retrieves same-hour sightings) should show the same reuse; a recency buffer should not —
which makes the two-spells LLM comparison MORE interpretable, not less.

## 02:45 — reflection's "accuracy rises above its lead-up inside the spell" (79 vs 73): checked, explained, not a leak
(a) cold split: reflection lead 68 -> 35 (14-16) -> 62 (17-23): below its lead-up on cold questions; the day-level 79 is
warm repeats (same object asked again after that day's feedback). The timetables show the same day-level rise on the
same questions (3-day 81 -> 86, 1-day 79 -> 87 inside the spell, cold ~84 = lead) because the sick routine, once
learned, keeps things in fewer places. (b) notes audit, hh_s0-s3 (1,595 object-place claims in 122 notes): 11 name a
place never shown for that object before the note — all the model's own wrong answers being recorded ("assumed desk,
found at coffee table") or negations ("do not assume tablet at the sink"), none an observation it never saw; 29 of 1,091
quoted times were never shown — all round-hour heuristics the model invented (22:00, 09:00, 23:30), not timestamps; 0
mentions of a later day than the note's own. (c) 0 of 299 no-message reflection notes mention sick/unwell/ill/fever/
"feeling better"/"home all day" — at any day, not just before 14. Gist bullet 1 reworded with the measured drops (7 pp
reflection to 25 pp retrieval; 30-54 on cold questions) and this explanation.

## 04:20 — the ceiling measure alone misreads why a disruption bites; "no answer at that hour" is the missing column
Reporting the guests scout against the sick regime showed the ceiling (share of spell questions whose truth differs
from the settled lead-up answer for that object and 2 h bin) is nearly the SAME for both — sick10_owner 26% at days
14-16, guests10 30% — while the 3-day timetable's break is 23 pp vs 11 pp. So the ceiling as defined does not explain
the difference, and quoting it alone would have been misleading. Added a second column to tools/guests_report.py: the
share of window questions with NO lead-up answer at that (object, hour) at all. sick10_owner 54% (days 14-16), 56%
(17-23); guests10 9% and 11%. That is the separation: the sick spell changes WHEN questions are asked (the resident is
home all day, so activities move to hours the lead-up never covered), so for half the spell a time-of-day learner has
nothing rather than something wrong; guests only rearranges the evening at hours that already existed. Same mechanism
as the two-spells reuse (a bin the normal routine never writes is never overwritten) and as retrieval's persistent
post-message damage. Both columns now print side by side for every regime; neither should be quoted without the other.

## 04:35 — the "empty hours" separator I proposed at 04:20 is WRONG; the 14:55 NOTES reading was right
The coordinator caught that vacation (10 days at home on the weekend schedule) has a high empty-hour share and only a
10-point dip, contradicting my 04:20 column, and asked for a 2x2 test rather than adopting either story. Built
tools/break_cells.py: per window, from LEAD-STAGE SIGHTINGS ONLY (the timetable's own evidence), each question is
classed by {that object's 2 h bin was seen in the lead-up: yes/no} x {truth equals the object's most frequent
lead-up place overall — exactly what TimetableLookup falls back to on an empty bin: yes/no}, with the 3-day
timetable's accuracy per cell and a mix-vs-within decomposition of each window's break against the lead window.
Result (10 hh each, days 14-16; share shift into each cell vs the lead window -> break):
  unusual place (either hour): sick +41 pp -> break +23 | guests +16 -> +11 | vacation  +7 -> +2   TRACKS
  new hour     (either place): sick +49        +23      | guests  +8 -> +11 | vacation +22 -> +2   DOES NOT
  both cells at once:          sick +37        +23      | guests  +7 -> +11 | vacation +10 -> +2   DOES NOT
So neither my "empty hours" story nor the coordinator's "empty hour AND wrong fallback" survives: guests shifts only
7 pp into the both-cell and breaks 11 points; vacation shifts 10 pp and breaks 2. What tracks the break is the
unusual-place column alone. Why hours are harmless is visible in the cells: "new hour, usual place" runs 89-95% in
all three regimes (the empty-bin fallback IS the usual place, and it is right), and in the sick spell "new hour,
UNUSUAL place" (65%) beats "hour seen, UNUSUAL place" (35%) — a seen bin confidently asserts the old wrong spot,
while an empty bin's broad histogram sometimes catches the new one. The break is also almost all MIX, not within-cell
decay (sick +41 mix / -18 within; guests +10 / +1; vacation +8 / -5): the questions move into the hard cell, the cells
themselves do not get much harder. Consequence: the two-spells reuse and retrieval's persistent post-message damage
are still real (both measured directly), but "empty hours" is not the general explanation of what breaks a learner,
and the 04:20 entry above should be read with this one. Gist wording to use: things being somewhere they usually are
not is what breaks these methods; being asked at an hour never seen before is not a problem by itself.

## 04:45 — told-vs-untold was being compared across DIFFERENT household sets; caught by the coordinator before write-up
Reflection's no-message arm ran on 10 households and its told arms on 5 (a throughput cut agreed at 01:55), and I
reported "the message barely helps reflection, 66 -> 68" straight off those two numbers — a comparison across
different household sets. The banks run 287-496 questions and the per-household spread on one arm is several points,
so that difference was not a result. Size of the error, measured: reflection no-message on all 10 households is 73%
(cold 68) in the settled lead-up and 66% on the first three sick days; on the matched s0-s4 it is 75% (cold 77) and
64%. So the shift-day number moves 2 points and the COLD LEAD-UP number moves 9 points (68 -> 77) — the cold
comparisons were the ones at real risk. Fix in llm_live_extra.py: every arm now also stores windows_matched (the same
arm restricted to the households every message arm of that memory kind ran on) plus hh_matched, and the extractor
prints one "matched <pop>/<memory>" line per memory kind saying which households the comparison uses and whether it
is an intersection. The page's gist takes every told-vs-untold number from windows_matched, states the household set
in the sentence, and every arm label now carries a compact "hh 1-10" / "hh 1-5" tag. Matched vs unmatched effect of
the message on the first three sick days: reflection +4 (was +2 unmatched), buffer +13, retrieval +12 — the story
holds but the headline number was wrong. Same rule applies to long-context (s0-s2 only) and to the two-spells arms.

## 05:00 — the one-standard-deviation rule applied mechanically; three claims of mine did not survive it
Oliver's standing rule (an effect must exceed one standard deviation) applied to every told-vs-untold comparison as a
PAIRED contrast: per household, told minus no-message on the same household, then mean +- sd of those differences.
Implemented in llm_live_extra.py (paired_vs_nomsg per arm per window, all and cold, with clears_1sd), printed by the
extractor and tabled in STORY_numbers.md / STORY_paired.md. What it changed:
- SURVIVES: buffer's message, first three sick days +12.9 +- 9.5 (cold +23.5 +- 13.4) and the rest of the spell
  +16.3 +- 11.3 (cold +36.3 +- 18.8); its return cost -11.3 +- 7.9 (cold -20.4 +- 14.5); retrieval's cold gains
  (+12.8 +- 12.3 and +24.6 +- 14.5); retrieval's LATE return damage -11.4 +- 11.3 at days 27-31 (cold -21.2 +- 19.1).
- FAILS, and was on the page as a headline: "the start message costs retrieval the most, 76 -> 58 on the first days
  back" -- the paired contrast is -13.1 +- 22.2, households disagree more than the effect. Rewritten to say the first
  days back cannot be called and the damage is measurable a WEEK later instead, which is the true and sharper claim.
- FAILS: reflection's +4 (now "no measurable difference (+5 +- 9)", exactly as the coordinator predicted) and the
  routine table's +3.3 +- 4.7. Both bullets restated as no-difference claims, which are stronger, not weaker.
- Long-context (3 households): its first-sick-days difference does not clear (+11 +- 14) but its rest-of-spell
  difference does (+12.7 +- 4.9, cold +32.3 +- 9.2). I first wrote the bullet as "nothing can be concluded" from the
  three households and had to correct it after reading the full table -- an over-cautious claim is still a wrong one.
Also fixed: a duplicated dict key in story_numbers.py's window labels (harmless, but it was silently shadowing).

## 05:15 — RETRACTION: the shared-memory interference finding does not survive six households
Published on the page (gist bullet and the partial-shift panel) from the workshop session's first THREE partial
households, 11-33 questions a cell: "a message about the sick person, written into a shared nightly table, degrades
the other resident's things, and stated confidence never moves, so the interference is invisible to the robot"
(routine table, others, cold: 42 -> 26 -> 27 across the spell and the first days back). With all six households final
it is a wash. Recomputed here from 5a's final arms rather than taken on trust, as a paired per-household contrast
(start message minus no message on the same household), routine table, other resident's things:
  14-16  +0.6 +- 4.1 | 17-23  -5.1 +- 10.5 | 24-26  -5.6 +- 13.2 | 27-31  -8.4 +- 15.1   — none clears one sd
  per household in 17-23: -13.6, -10.3, -11.1, +8.2, +8.6, -12.0 (the two positives are the two largest-n households)
What survives and replaces it, a positive result that DOES clear on six households: the message is SELECTIVE. Buffer,
sick resident's own things, 17-23: +15.3 +- 9.4 all, +31.9 +- 8.6 cold; the same message on the other resident's
things: +0.4 +- 5.1 all, +0.7 +- 5.9 cold. Also surviving from the old bullet: the routine table is uniformly worse
than the buffer (no message, 17-23: sick resident's things 68 vs 70, other resident's 53 vs 71) and its stated
confidence sits at 82-89% in every window for both residents with or without a message.
Second retraction of the night for the same cause (after reflection's unmatched-household comparison, 04:45), so the
lesson is now ON THE PAGE, not only in this file: the method note above the findings says two results were withdrawn
for failing the spread test after being written up on too few households. Standing rule for the rest of this study:
no cross-arm claim goes on the page without its paired spread and the household count, computed by the extractor
rather than by hand.

## 05:45 — harness facts from the workshop session, checked against our own runs (3 already held, 1 cost us something)
5a wrote up four harness gotchas (dynamic_home_eqa_fm/results/fm_memory/tools/README_gotchas.md). Checked rather than
assumed, against this session's runs:
- "--workers parallelises across ARMS (bank x memory x told x look), not within one": our invocations are sized
  correctly by luck of habit — the two-spells pass is 3 banks x 2 memories = 6 arms with --workers 6, and the person
  passes were 10 banks x 1-2 memories against 30-40 workers. No wasted flag anywhere, but the rule is worth knowing:
  a single-bank single-memory invocation would have been ONE stream whatever the number said.
- "static header before the time-varying Now: line or the prefix cache never hits": already true in our prompts —
  checked a real day-20 prompt, "Now:" sits 80% of the way in, after the whole static header. Server side,
  --enable-prefix-caching IS on and VLLM_USE_FLASHINFER_SAMPLER=0 is set; measured hit rate 27.3% cumulative
  (49.3M hit tokens of 180.7M queried).
- "run message arms in PHASES, not in parallel, so the second replays the shared days from cache": this one cost us.
  At 04:30 I launched the two-spells no-message and start-message passes concurrently (to fill an idle server, on the
  coordinator's ask) with a shared cache dir. Days 1-13 are identical between those arms, so run sequentially the
  second pass would have replayed them; run concurrently both paid. Cost ~600 calls, roughly 16% of one pass. Not
  worth killing now: they are ~70% done and the remaining work is days 14+, where the prompts genuinely differ, so
  re-sequencing would waste more than it saves. For comparison the person suite, which WAS phased, replayed 44% and
  70% of its two told passes from cache.
- "greedy decoding is not bit-reproducible across batch compositions": matters for us because our degenerate checks
  and the cache both assume a prompt maps to one answer. It does within the cache (we never re-ask a cached prompt),
  but a re-run of an uncached arm can differ from the logged one. Any future claim of exact reproducibility should
  say "same prompts, cached answers", not "same numbers on a re-run".
(F1 seeds 12 and 15 failing to build banks does not touch us; we use seeds 0-9 throughout.)

## 08:05 — a null used as evidence of a difference (my error, caught on my own cold read)

The gist's second lead bullet read "a message makes no measurable difference to the memory that already writes its
own corrections each night — while it is worth +13 to a plain buffer and +13 to retrieval on cold questions". That
sets a null on 5 households beside two effects on 10 and invites the reader to conclude reflection is different.

**What is wrong.** Reflection's first-sick-days contrast is +4.6 ± 4.08 (n=5), so 2 se above it is **+12.8**. The
buffer's effect is **+12.9**. The two are 0.1 points apart, i.e. the reflection data cannot distinguish "the message
does nothing for it" from "the message does exactly as much for it as for the buffer". The bullet was asserting a
contrast the evidence does not carry.

**How it was caught.** Rendering the page to plain text and reading it as a cold reader, then computing the null's
upper bound instead of accepting the word "null". Nothing flagged it automatically: the contrast passes every check
we had, because each figure on its own is correctly computed and correctly labelled. The fault was in setting two
correct figures side by side.

**Fix.** Bullet rewritten to state what it actually establishes (we could not measure an effect at five households,
and a gain as large as the buffer's is still consistent with what we see), and demoted out of the lead group.

**Rule added.** A "no measurable difference" is evidence of no difference only when its upper bound sits below the
comparison it is being set against. Otherwise it is absence of evidence and must be written as such. This is the
same family as the 04:45 unmatched-household error and the 05:10 three-household retraction — the third time
tonight that two individually correct numbers made a wrong claim when placed next to each other.

## 11:30 — story_extra.json clobbered twice: once by a bug, once by me testing the fix for it

**The bug.** `tools/story_extra.py` built its output from a fresh dict and wrote the whole of `story_extra.json`,
destroying the keys the other four extractors own (`llm_live`, `knowno_live`, `owner_split_live`, `gap`,
`shared_state`, `affected_windows`). Nothing errored. It was caught only because the rebuilt page went from
2753 KB to 1288 KB and I happened to look at the number. Restored by re-running the other four.

**The fix, and what testing it revealed.** All five extractors now write through `tools/extra_store.py`, which
declares key ownership, refuses a write of another extractor's key, refuses an unknown caller, and reports the
key list and byte delta every time. The obvious guard — fail if the file shrinks — turns out NOT to catch the
case that matters: once writes are merged, a key can no longer vanish, so a broken extractor instead writes an
EMPTY value over a full one. The content is just as gone and the file barely changes size. The guard that works
is per-key: refuse to overwrite a non-empty value with an empty one, with an explicit `allow_shrink=True`
override. I found this only because I ran the tests rather than reasoning about whether they would pass.

**My own error, which is the part worth remembering.** I ran those destructive tests against the live
`story_extra.json` instead of a copy. The first test case wrote an empty `sweep` and `affected` into the real
file; the second run then reported "not caught" for the wrong reason, because there was no longer anything
non-empty left to protect — a corrupted file producing a misleading test result. Recovered from a backup taken
minutes earlier, verified against it key by key (10 keys, 4 sweep regimes, 11 affected agents), then re-ran the
whole suite with the store's PATH redirected to a sandbox copy.

**Rule.** A test that exercises a destructive path points at a copy, never at the artifact. And a guard against
silent data loss is exactly the kind of code whose tests can cause the loss it prevents.

## 11:35 — "the counters do better at knowing when they're wrong" was asserted, then measured, and it is false

The page's one-minute summary closed on "the counting methods, for all their simplicity, do better on that score",
meaning at telling from their own confidence that the world had changed. It rested on a real observation — the
counters' stated confidence moves with the stage (3-day timetable 46% → 37%) where the LLM memories' does not — but
that observation had never been put through the answer-or-ask gate that prices it. The coordinator asked for the
counter on the gate charts specifically because the comparison was asserted in prose but not shown.

**Measured, same gate, same alpha, same five windows, confidence = top probability as everywhere else:**

| method | first sick days: ask% / miss% | rest of spell: ask% / miss% |
|---|---|---|
| 3-day timetable | 70 / **43** | 30 / **9** |
| never-forgets timetable | 71 / 64 | 62 / 23 |
| buffer | 55 / 28 | 48 / 19 |
| retrieval | 59 / 31 | 47 / 18 |
| reflection | 43 / 19 | 41 / 12 |
| nightly routine table | 67 / 31 | 59 / 24 |

So at the break the counter is the WORST of the lot on both axes at once — it hands back 70% of the questions and
is still wrong on 43% of the rest. The claim was backwards.

**What is true instead.** Its confidence tracks the stage, but it tracks it *after* the break rather than during
it; and once it has re-learned the sick routine it becomes the only method on the page that keeps the 10% promise
(9% miss, against the best LLM arm's 12%). Tracking the stage and being usable at the moment it changes are
different properties, and only the second one is what an answer-or-ask gate needs.

**Fixed** in the one-minute summary and in the confidence finding; the counter is now drawn on both gate charts.

**Rule.** A comparison stated in prose but absent from the charts is an untested claim. Build the chart before
repeating the sentence — and expect roughly one in three of them to come back the other way, as this one did.

## 15:20 — two bugs in one figure, both found by looking at output rather than at code

**1. Conformal APS emitted EMPTY sets on 26% of questions (64 of 246), and did so hardest where the model was most
certain.** The set was built as `{y : aps_score(y) <= q}`. Two faults compounded. Structurally, that test drops the
model's own top answer whenever `q < p(top)` — a set that cannot contain the best guess is not an APS set. And the
boundary is float-fragile: for a fully confident distribution the cumulative mass sums to **1.0000000002**, which is
not `<= 1.0`, so a completely certain answer produced *nothing at all*. Logged example: `dist =
{medicine_cabinet_ba1: 1.0}`, `q = 1.0`, set size 0.

That second fault is the one worth remembering. **The method broke hardest exactly where the model was most
confident** — the least likely place to look, and invisible in any aggregate that averages over questions. Mean set
size merely drifted below 1, which reads as a tuning problem rather than as sets containing nothing.

Fixed with the standard prefix rule (add classes in descending probability until the cumulative mass reaches q,
always keeping the top one) plus a tolerance on the comparison. Verified on three constructed cases. Because every
row saves its sampled `dist`, both set types are now REPLAYED offline by the chart from the saved distributions, so
no server time was respent and rows written before the fix are corrected on read. After the fix: zero empty sets,
APS coverage 50% → 87% against a 90% target. The coordinator replayed it independently with its own prefix rule and
its own threshold and got 84.6% over 267 rows — consistent, sharing none of the same code.

**Caught by the coordinator watching live rows at day 8 of a 31-day run**, not by any check of mine. The tell was
mean set size below 1 combined with coverage drifting *down* rather than converging up. An adaptive procedure that
undercovers by 40 points and is not correcting is a bug, not a tuning matter.

**2. The partial-run guard produced a misleading picture of the partial run.** The same chart shades the sick spell
with `axvspan(13.5, min(23.5, maxd + .5))`. With data only to day 9 that evaluates to `axvspan(13.5, 9.5)` — drawn
BACKWARDS, colouring settled days 9–13 as if the resident were already ill. The machinery built to stop anyone
misreading an in-progress run was itself generating the misreading. Stages are now shaded only once the data
reaches them.

**Rule.** Both were found by rendering the output and looking at it, not by reading the code — the code looks
correct in both cases. And a guard is not exempt from the check it enforces.

## 22 Sept, evening — two summaries that erased what they were summarising

**3. A three-day average turned a 41-point cliff into a 6.8-point slope, on the figure whose whole purpose is that
cliff.** The paper figures draw a centred three-day rolling mean so the learn/break/re-learn shape reads at a
glance. Oliver then asked, reasonably, to drop the faint raw-daily lines underneath and keep only the smoothed one.
Measured before doing it: the 3-day timetable's fall at day 14 is **40.8 points** on the daily values, and the
centred average draws it as **6.8**. Day 13's window reaches forward into the first sick day and day 14's reaches
back into the last settled day, so each borrows the other's level and the boundary flattens. With the raw lines
removed there would have been nothing left on the figure to contradict it.

The fix is to bound the window by stage: a day's average only includes days in its own stage, so the boundary days
average over two days or one. That holds the break at 30.5. Smoothing still shrinks a one-day cliff even bounded,
so the manifest header and every `claims.md` now state that the numbers are measured on the daily values and must
be quoted from there rather than read off the line.

**This is the same failure as the mean hiding the mass, in a different costume.** There, an average over questions
concealed that a quarter of the sets were empty. Here, an average over days conceals the single day the whole
figure exists to show. In both cases the summary statistic is not wrong — it is faithfully reporting something
other than the effect, and it is most misleading exactly where the effect is sharpest. **Any smoothing applied
across a discontinuity has to be checked against the discontinuity it crosses, by computing the thing the reader
will try to read off the picture and comparing it with the raw number.** One line of arithmetic separated this
from publishing a figure that contradicts our own headline.

**4. A guard justified by a temporary state, with nothing able to expire it.** `llm_live_extra.py` carried
`ABANDONED = {("person","longcontext","nomsg"): hh_s3..s9}`, excluding seven households from every long-context
number on the page. The comment gave a sound reason: long-context costs about ten times the compute per question,
its told arms had only ever run on hh_s0–s2, and extra untold households could not improve a comparison that had
no told counterpart. All true when written.

It stopped being true at 19:12, when the run extending long-context to the other households started — and nothing
in the code, the comment or the page knew that. The untold arms for s3, s4 and s5 turned out to be almost entirely
cached and completed in two to four minutes, and the page went on reporting **3 households where it had 10** until
the exclusion was found by hand. Every long-context level on the page was computed from a third of the data
available.

**Rule.** A constant that hard-codes "we decided not to use this" is a decision with an expiry date and no timer.
Prefer a guard that derives the exclusion from the data — skip a household because its run log is missing or short,
which stops being true on its own — over a literal set of names that only a person can revisit. Where a literal is
unavoidable, the comment must say what event ends it, so a reader hitting it knows what to check.

**What removing it exposed.** With the untold arm back at ten households, told-once at six and told-twice at three,
the told-vs-untold figure would have drawn three different household sets on one chart and invited the gaps between
them to be read as the effect of the message. The figure now matches all three arms to the households all three
ran. The lesson is that a fix which enlarges one arm of a paired comparison silently unbalances the pair: after
lifting any restriction, re-check every comparison built on it.

**5. An axis default made a false claim, in the figure whose whole purpose was that claim.** The paper-figure
helper set `ylim=(30, 100)` as its default, chosen because the accuracy figures all live in that range and the
empty lower third was wasted space. F4 plots two rates that live near and below 30 — how often a method hands a
question over, and how often it is nonetheless wrong on what it kept. Every value below 30 was silently clipped
out of the frame. The bottom panel came back nearly empty, and what it showed was a picture asserting **"no
method is ever wrong on less than 30% of what it answers"** — the opposite of the figure's point, which is that
the promised one-in-ten is held comfortably in the settled fortnight and broken at the shift.

Nothing errored. The default was sensible for the figures it was written for and wrong for the first figure
that did not share their range.

**The category, now that there are three.** Today produced three faults with one shape, and it is worth naming
because it will happen again:

- an average over questions concealing that a quarter of the conformal sets were empty;
- an average over days rendering a 41-point cliff as a 6.8-point slope;
- an axis default clipping away every value the figure existed to show.

None is a calculation error. In each case the arithmetic is correct and something else — a summary statistic, a
smoothing window, a drawing default — quietly changed what the artifact asserts, and each was most misleading
exactly where the effect was strongest. **The check that catches all three is the same: compute the thing a
reader will try to take away from the artifact, and compare it against the raw number.** Reading the code finds
none of them; rendering the output and looking at it finds all three.

A fourth, related, from the same evening: a figure folder whose claim sentence computed itself from the data
while the paragraph explaining it did not, so the two disagreed the moment a household landed — the folder
contradicting itself in adjacent lines. `tools/paper_figures.py` now audits every number in every figure's prose
against that figure's own numbers table on each run, and a literal that is a parameter rather than a measurement
must be declared one at a time with a reason. An unexplained exemption is how a stale number hides.

**6. An effect applied for legibility changed what the artifact WAS, not how it looked.** The A and B markers on
the stage boundaries were drawn with a matplotlib path effect, to give each letter a white halo so it stays
readable wherever a line passes behind it. Matplotlib rasterises a glyph to vector paths when a path effect is
applied to it. The result: in every SVG, the two characters the paper refers to by name — A and B, the whole
point of the notation — were the only text in the set that was **not text**. Everything else was `<text>`, as the
figure contract requires; those two were outlines.

Nothing errored, the PNGs were identical, and the halo worked exactly as intended. The fault is invisible in the
rendered image and visible only in the file: a check that greps the SVG for `>A<` finds nothing while the figure
plainly shows an A. A white bbox behind the letter does the same job and keeps it as text.

**The general form is worth more than the instance.** An effect chosen for how something LOOKS can silently
change what the file IS — its format, its structure, whether its text is selectable, searchable, or
reproducible. The image is not the artifact; the file is. Whenever a visual effect is added, check the produced
file for the property the effect might have traded away, not just the picture for the effect you wanted.

A second-order fault rode along with it: because the halo was drawn as stroked paths, the letters registered as
a *data colour* in the palette checker, which then failed the pair red-against-green at 7.6 under protanopia.
That one cannot be fixed by choosing a different red — red against green IS the deficiency. It became moot when
the letter went back to being text on a white box, read against white rather than against the line. Recorded
because it is the distinction that matters: an annotation glyph and a data series are not held to the same
test, and a checker that cannot tell them apart will send you looking for a colour that does not exist.

**7. A name split across a string concatenation is invisible to any search of the source.** Renaming every
method to a plain description, the source came back clean — no occurrence of the old names anywhere in
`paper_figures.py`. The built folders still carried them. The reason is that the long prose strings are written
as adjacent literals, so a name lands half on one line and half on the next:

```
"...falls 40.8 points on day 14 and the never-forgets "
f"timetable {abs(...):.1f}; by day 23..."
```

No regular expression over the file can see `never-forgets timetable` there, because as far as the file is
concerned those are two different strings. A dozen occurrences survived that way, in exactly the sentences a
reader meets first.

They were found by grepping the **rendered output** — the generated `claims.md` and `caption.md`, where the
concatenation has already happened and the name is whole.

**The rule: after any rename, sweep the built artifacts, not the script.** This is the same lesson as rendering
a figure and looking at it, in a different medium. The artifact is the thing that ships and it can differ from
what the source appears to say — here because the source never contains the string at all. It joins the
rasterised-glyph entry above: there, an effect changed what the file was; here, concatenation hid what the file
would contain. Both were invisible upstream and obvious downstream.

A good outcome rode along with it. Forty-eight places looked their own numbers table up by the old literal
names, so the rename broke them loudly rather than silently producing wrong labels. They now resolve through
the single name dictionary, which means the next rename cannot leave a lookup pointing at a name that no longer
exists — a structural fix rather than a repair, and the reason to prefer a lookup that can break over a literal
that cannot.

## 23 Sept, early — one figure carrying two estimators, and a slice that swallowed four functions

Two faults of the same family: a thing that looked like one thing and was two.

**F8's table and F8's line disagreed about what a window number meant.** The figure draws each method's daily
score at ONE threshold chosen for the whole run. Its numbers table reported, per window, the score under a
threshold refitted *for that window* — a different estimator, the one F9 uses. Nothing was inconsistent enough
to catch the eye: both are decision scores, both in the same units, and the refit one is only a little larger.
The prose then took the table at its word and described the thresholds as "chosen with hindsight for the window
being scored", which is a true sentence about the table and a false one about the picture beside it. The table
columns are now the window means of the line that is actually drawn.

The prose read those columns **by position** (`list(nums[m])[2 + i]`), so swapping what the columns contained
changed every quoted number with nothing to announce it. It now reads them by name. A positional read of a dict
whose contents are being edited is a silent-change machine; the number-audit catches a number that has gone
stale, not one that has quietly become a different measurement with the same value nearby.

The wording is now written once, as a constant carried by all three decision figures, and it says what each one
actually does: one threshold per run (F8), one per window per household (F9), one per day (F10). None of them is
refitted on held-out data — every threshold in all three is chosen knowing the outcomes it is then scored on,
which is what makes them upper bounds rather than policies. An earlier description of F8 said its threshold was
swept for each day, which is true of none of the three; the replacement wording is deliberately the sort a
reader can check line by line against the code.

The structural fix, rather than the repair: **wherever a table sits beside a line, compute the table FROM the
drawn series.** F8's window figures are now the means of the daily values the figure actually plots, so the two
cannot come apart again. Recomputing a summary alongside a drawing, from the same source data by a second
route, is the arrangement that produced this.

**Separately: replacing a function by slicing between two markers deleted four other functions.** The slice ran
from `def f9` to `FIGS = {`, on the assumption that f9 was the last figure. It is not — f4 through f7 are
defined after it, and between f9 and f4 sat four module-level definitions (`GATE_ORDER`, `GATE_NAME`,
`gate_hh`, `gate_series`, `conf_shift`) that three later figures depend on. The build failed loudly with a
NameError, which is the lucky case; had the removed code been prose rather than definitions it would have
failed silently. Slice to the NEXT definition, found by grepping line numbers, never to a marker assumed to be
adjacent — and read what is between the two, because module-level code lives between functions too.

## 23 Sept — a rerun artefact was setting where a drawn line began

The told-arm figures draw each arm only from the day it departs from the arm above it, and that day is
*measured* from the data rather than taken from the calendar. The reasoning was that a calendar clip would hide
a real early departure. It found one: the twice-told arm differed from the once-told arm on days 21 and 22,
three days before its own message on day 24, and both F3 and the page's panel library drew its line from day 21
— a picture in which the second message appears to take effect before it was sent.

The difference is 0.625 points across ten households: one answer in a hundred and sixty. Day 20 and day 23 are
identical again.

The mechanism came from the memory strand. Identical prompts at temperature zero are **not** reproducible on
this server — measured on one household, 48 of 48 prompts byte-identical between two runs and 6 of the 48
completions different, 4 of them in the chosen location. The arms match before their message because those
prompts are prefix-cache hits, not because greedy decoding is deterministic. A cache miss means a fresh
generation, and a fresh generation can differ. We had already logged three such single-answer divergences and
guessed "cache miss"; this is the mechanism behind the guess.

What changed:
- The departure search now starts at the arm's OWN message day. Days it differed earlier are recorded in the
  numbers table ("days it differed BEFORE its message (rerun artefacts)", with the size of the largest), so the
  detection survives while a flipped answer no longer decides where a line begins. Same fix in both renderers.
- Wording everywhere: the arms are identical before their message because those prompts are cache hits, NOT
  because the server is deterministic. That is still exactly the guarantee a paired comparison needs — the same
  generated answers on both sides until they diverge — but a reader who assumes determinism will draw wrong
  conclusions elsewhere. METHODS.md now states this, with the measurement.
- The number audit gained a three-decimal rendering. It reported 0.625 as stale while the table carried exactly
  that value, because it only ever formatted table values to two places.

Nothing in any figure's numbers changes. Rerun noise is symmetric, so it does not bias a paired mean, and our
spreads are computed across households from the runs as they happened — the noise was already inside every bar,
and every effect that cleared the bar did so with it included.

## 23 Sept — the general form of the rule that keeps finding new places to apply

Three faults tonight were the same fault at three levels:

1. **A table recomputed beside a line instead of from it.** F8's window figures were per-window refits while its
   line used the whole-run bar — same units, nearby values, no audit fires.
2. **Prose typed beside a table instead of read from it.** Forty-eight lookups keyed by literal names, and a
   claim sentence quoting 2.9 while the table said 2.8.
3. **A number copied from another strand instead of imported from it.** The rerun floor, measured by the memory
   strand, about to be typed into ten figure folders and the page.

The rule in its general form: **anywhere one artifact quotes another's number, the quote is computed from the
source rather than copied — whether the source is a drawn series, a table, or another strand's result.** F8's
window figures are now means of the drawn series. The figure prose reads its own table by key. The rerun floor
lives in `tools/rerun_floor.py`, and both the figure folders and the page build their sentences from it, so
updating the measurement is one edit and drift is not possible.

A fourth instance, one level down in precision rather than in definition: the number audit rendered table values
to two decimals and so called 0.625 stale while the table held exactly that value. A single flipped answer
across ten households IS 0.625, which is the size of thing we had just started reporting — an audit that cannot
see the smallest quantity it is checking is the same failure as a table that cannot see the line it sits under.

## 23 Sept — "the counting methods are deterministic" checked rather than asserted

Having just been wrong about greedy decoding being reproducible, the claim that the counting methods reproduce
exactly was written into ten figure folders as an argument from their implementation: they are Python with fixed
seeds and make no model calls. That is the same SHAPE of argument that had just failed, so it was measured.

Household hh_s0's whole classical arm was regenerated from its stored config into a scratch directory: all nine
beliefs, 4464 rows. Byte-identical to the stored log, and the question bank it was scored on regenerated
byte-identically too — which is the stronger result, since it means the simulator and the bank generation
reproduce as well as the beliefs do.

The folders now say the counting methods were re-run and reproduced exactly, with the household and row count,
instead of appealing to what the code does. Cost: about four minutes of CPU.
