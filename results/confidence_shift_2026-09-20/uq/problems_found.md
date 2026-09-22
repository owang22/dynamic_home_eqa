
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
