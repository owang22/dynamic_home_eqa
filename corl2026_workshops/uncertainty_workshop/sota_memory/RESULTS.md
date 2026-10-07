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

## The recent-sightings list with the residents' descriptions removed — landed 02:50, days 11-17, 21-22, 24-28, 0 fallbacks
Paired on the same questions against the recent-sightings list; n=3 households, so the bar is mean bigger than the spread.
Pinned is shown on the SAME question ids for comparison.
| window | all questions: card removed | per household | pinned | cold: card removed | per household | pinned |
|---|---|---|---|---|---|---|
| lead-up 11-13 | +4.1, spread 5.5 | 83->83, 72->83, 90->92 | +9.2, spread 7.6 | +4.2, spread 7.2 | 92->92, 69->81, 83->83 | +9.7 |
| first sick days 14-16 | **+9.7**, spread 6.4 | 44->48, 65->73, 50->67 | +2.8 | +5.5, spread 5.3 | 12->18, 37->47, 20->20 | +2.0 |
| later spell 17, 21, 22 | **+18.8**, spread 15.7 | 42->77, 69->73, 62->79 | +5.6 | **+28.6**, spread 15.8 | 13->60, 35->53, 36->57 | +14.5 |
| first days back 24-26 | -8.3, spread 8.3 (at the bar, not past it) | 75->67, 67->67, 90->73 | +1.4 | -15.6, spread 33.3 | 50->50, 50->57, 92->38 | +2.0 |
| 27-28 | -2.1, spread 6.5 | 75->78, 71->71, 94->84 | +3.1 | -4.2 | | +6.7 |
Moved vs unmoved (strata.py), later spell: moved +21.0, spread 15.7 (40->77, 68->74, 62->82; passes). Unmoved +6.7, spread
11.5; POOLED 67->70 (n27, pooled, not a paired test). First days back: unmoved -8.0, spread 7.2 (80->70, 68->68, 93->79).

Reading:
- The shape the coordinator predicted holds on three households: nothing measurable while the card is true, a gain once
  it is stale, a cost when it becomes true again (at the bar, not past it). The gain is on the things the shift moved.
- Lead-up bound: per household +0, +11, +2; mean +4.1, standard error 3.2. A gain of up to ~10 points or a loss of ~2 is
  not excluded, so the card carried no measurable useful information in the settled fortnight at this resolution.
- WINNER'S CURSE AGAIN: hh_s0 alone (reported at 02:32) gave +35 on the later spell; the other two gave +4 and +17. The
  three-household mean is about half the first household's.
- Card removed vs pinned, paired on the same questions, later spell: cold 60 vs 33, 53 vs 59, 57 vs 36 (+14 mean, spread
  ~18); all questions +13, spread ~15. NOT distinguishable at n=3. The claim "removing the written routine beats pinning
  the right line" is NOT established. Both help; the card removal's point estimate is larger. These are two
  interventions that differ in more than one way, not a decomposition.

## FINDING: an LLM-written fact store corrupted itself four ways before a single question was answered
The shared nightly fact store (used by the three published revision policies) was checked by reading the STORE, not the
accuracy. Each failure below was invisible in end-to-end scores, and the literature reports these systems by end-to-end
scores only.
| # | failure | what it would have done to the numbers | how it was caught | fix | archived at |
|---|---|---|---|---|---|
| 1 | Zero-length validity windows: the extractor copied single sightings as facts ("desk_b1, 18:00-18:00", "cupboard_k1, 03:00-03:00") | Every nightly 03:00 round contradicts yesterday's point facts, so the store becomes a sighting log with dates. A "validity window" policy then shows windows that mean nothing | Reading the day 0-2 facts after the smoke run | Extraction reads each day as merged stays (spot, from-to) and is told to give stretches, never single moments | smoke/facts_zep_extract_v1_pointfacts |
| 2 | Paraphrase churn: facts were rewritten each night with slightly different times, and the revision step invalidated them as contradictions (34 facts invalidated on day 2, including "desk 11:26-21:05" vs "desk 11:04-24:00") | The store reduces to "yesterday's timeline"; the validity-window policy would look like a one-day forgetter for reasons unrelated to revision | Counting the revision ops per night | Extraction is shown the facts already held and told to repeat their exact wording when today agrees (the prior context Graphiti also gives its extractor); by day 3: 25 duplicates, 10 adds, 10 invalidations | smoke/facts_zep_extract_v2_daytranscripts |
| 3 | Future sightings leaked into past facts: the nightly write for day d read the memory as of whenever it ran; with answering from day 11, the day 0-10 facts were built from up to 11 days of later sightings | Near-perfect settled-period facts for the wrong reason: a validity-window memory that had seen the future; the results would also have depended on which days were answered | An unexpected cache miss: the day-0 prompt differed between two runs that should have matched | Each write filters sightings to before the end of its own day; verified byte-identical prompts under --days 4 and --days 11 | withdrawn/facts_zep_hh0_future_sightings_leak |
| 4 | Empty nights: with an unconstrained list, extraction returned {"facts": []} on 4 of 9 nights (days 1, 2, 5, 8); at temperature 0 a retry reproduces it | A store with random missing days: facts stay "current" through days they were never checked, so revision appears to keep stale facts | Listing every extraction call's fact count | The schema requires at least one fact per object listed that night | withdrawn/facts_zep_hh{0,1,2}_empty_nights |
| 5 | Revision output truncated (MY harness bug): a 2,500-token limit cut the JSON on 6 nights; the failed parse passed silently as "no decisions" and the night's facts were dropped | A store frozen for most of the later spell | Listing nights with zero operations | Limit raised to 8,000; an unparseable revision now prints loudly and keeps the facts as additions | withdrawn/facts_zep_hh0_truncated_revisions |
| 6 | Copy-through freeze (caused by the fix for #2): the extractor copied held facts verbatim regardless of the day's evidence (day 17: stays on the coffee table, extracted "desk_b1, 00:00-23:00"); every new fact was a duplicate for 11 nights | The validity-window judge never sees a contradiction; accuracy equals the plain memory, which looks like 'no effect of the policy' | Identical duplicate counts night after night (76/76) | Not fixed tonight; the clean test is mechanical extraction | nottold/hh_s0_t03_facts_zep_nottold_lookoff |
Irony worth one line: #3 is a memory designed to represent WHEN facts were true, building its early facts from evidence
that did not exist yet.

## Problem found 02:58: the server is not deterministic at temperature 0; every comparison tonight carries rerun noise
The corrected card's lead-up prompts on hh_s0 are byte-identical to the workshop session's recent-sightings run, yet
6 of 48 answers differ (4 in the chosen spot, 2 in confidence only). Same prompt, temperature 0, seed 0, different
output: the vLLM server is not bitwise deterministic across load and batching, and the workshop run was made under
different server load (possibly also a different server configuration). Every paired number above compares a FRESH run with that older run,
so it includes rerun noise. The noise is symmetric, so it should not bias the means, but it widens the spread at n=3.
Measuring it: the recent-sightings list re-run fresh with the same code and cache on the same days, hh_s0-5
(results/sota_memory/nottold_rerun, launched 02:58). Its difference from the workshop run is the noise floor; it is also
a same-session baseline for all arms tonight.
Noise floor (03:25, hh_s0-2; hh_s3-5 to follow): the recent-sightings list run twice on the same data and days, the
workshop run vs tonight's fresh run (rerun_noise.py):
| window | per household (older -> fresh, share of answers changed) | mean diff | mean abs diff | spread | answers changed |
|---|---|---|---|---|---|
| lead 11-13 | 83->85 (6%), 72->76 (3%), 90->90 (0%) | +1.8 | 1.8 | 1.7 | 3% |
| sick 14-16 | 44->44 (2%), 65->62 (4%), 50->50 (6%) | -0.7 | 0.7 | 1.2 | 4% |
| sick 17,21,22 | 42->44 (4%), 69->69 (0%), 62->60 (2%) | 0.0 | 1.4 | 2.1 | 2% |
| ret 24-26 | 75->79 (6%), 67->67 (0%), 90->88 (4%) | +0.7 | 2.1 | 3.2 | 3% |
| ret 27-28 | 75->75, 71->71, 94->88 (9%) | -2.1 | 2.1 | 3.6 | 3% |
| all days | 63->65, 68->68, 76->74 | 0.0 | 1.2 | 1.8 | 3% |
Reading: the same memory re-run on the same data changes about 3% of its answers and moves a household-window by up to
6 points (typically 1-2). That is small against the spell effects (+19 all, +29 cold for card removal), and comparable to
the effects at the bar (the return cost -8.3 with spread 8.3; the card-removed vs pinned differences). Note: on hh_s0-2
days 11-13 the fresh re-run's prompts are byte-identical to the corrected-card arm's, so those answers were cache
hits shared with that arm.
How it was found, for the methods section: prompts were compared as strings and completions separately. Comparing
accuracies would have shown two similar numbers and hidden it. A prompt cache silently turns nondeterminism into apparent
determinism, so a cached arm and a freshly generated arm are not the same kind of measurement even when prompts match.

## SIX HOUSEHOLDS (03:47): the resident card kept true, removed, or left stale — against tonight's same-session baseline
Baseline = the recent-sightings list re-run tonight (nottold_rerun), whose card is the original one, i.e. STALE on days
14-23. Days 11-17, 21-22, 24-28; hh_s0-5; paired per household; detected = mean >= 2 standard errors (n=6). Floor = the
mean absolute rerun difference of the baseline itself in that window (rerun_noise.py, six households: 3% of answers change
overall; 0.7-3.2 points per window). Tool: six.py.

**The card kept true for its day. On sick days it says the resident is home sick, resting on the couch in the living
room, which is where their things now are**, so it carries location information, not just the stage:
| window | all questions | cold questions |
|---|---|---|
| first sick days 14-16 | **+13.9** (se 4.0; 20x floor): 44->69, 62->69, 50->77, 52->65, 75->83, 73->77 | **+29.3** (se 7.4; 17x floor) |
| later spell 17, 21, 22 | **+12.8** (se 5.3; 12x floor): 44->79, 69->79, 60->81, 77->81, 83->88, 79->81 | **+28.4** (se 10.6; 24x floor) |
| lead-up and return | identical to the baseline: the prompts are byte-identical there, so the answers were shared cache hits | identical |

**Card removed** (three-household figures from 02:50 in brackets, to show the shrinkage):
| window | all questions | cold questions |
|---|---|---|
| lead-up 11-13 | -3.4 (se 2.9) not detected | **-7.5 (se 3.7) detected: removing a TRUE card costs** (3x floor) |
| first sick days 14-16 | **+6.6** (se 2.6; 10x floor) [+9.7] | **+11.2** (se 4.5) [+5.5] |
| later spell 17, 21, 22 | +9.0 (se 5.9) not detected [+18.8] | **+18.2** (se 8.7; 2.1 se, marginal) [+28.6] |
| first days back 24-26 | -2.7 (se 3.6) not detected [-8.3] | -7.9 (se 9.4) not detected |
| 27-28 | -0.6 not detected | -3.7 not detected |
Winner's curse, third time tonight: on the later spell, card removal gave +35 on hh_s0 alone, +18.8 on three households and
+9.0 on six. hh_s3 went the other way (77->71 all, 75->56 cold).

**Corrected card minus card removed**, paired: later spell all +3.8 (se 1.6) detected; cold lead-up +7.5 (se 3.7)
detected (this is the same lead-up cost of removal); every other window not detected (first sick days cold +18.1, se 10.8).

Reading:
- A standing written routine is a real input the model follows. Kept true, it is worth about +13 on all questions and +29
  on first-of-day questions through the whole spell, 12-24x the rerun floor. Left stale, it costs that much. Removed, the
  model loses the stale harm in the spell but also the true card's help in the settled fortnight (cold -7.5), so
  removal is a trade, not a fix.
- The honest scope of "kept true": this card NAMES THE COUCH. The gap between it and the stale card combines two things,
  accuracy and extra location information. A stage-only card ("home sick today", no location) would separate them; not run.
- The return cost of card removal, borderline at three households, is NOT detected at six (-2.7, se 3.6).
- Predictions: the coordinator's "true card beats stale card and no card in the spell" holds against the stale card
  (large) and holds against no card on all questions in the later spell only (+3.8). The coordinator's "beats no card on
  the return" is not detected. My "cold +30 or more" nearly held (+29.3, +28.4). My "lead-up identical" and "return
  equal" were true by construction (identical prompts), so they were checks, not predictions.

## Fact store with the validity-window policy (Zep/Graphiti-style), hh_s0 only — landed ~04:50. NOT a fair test; see #5.
WITHDRAWN 07:37 (see the mechanical-extraction section; it was the extractor, not the judge). Previously marked as standing: after the first sick day the revision judge had
56 new facts and the contradicting evidence in front of it and invalidated 0; after day 15, 1; after day 16, 30.
DOES NOT STAND: the accuracy figures below, including the day 14-16 figure of 27. The store behind them was also missing facts
from truncated nights (#5). They are unusable as evidence and are kept only as a record. The clean re-run supplies the numbers
(output moved to withdrawn/facts_zep_hh0_truncated_revisions; re-run launched after the fix).
Same-session recent-sightings list -> fact store, same questions: lead-up 85->77, first sick days 44->27, later spell
44->56, first days back 79->75, 27-28 75->69, all 65->60. One household. The rerun floor is 1-3 points, but the spread
between households is 5-15, so one household can only show a direction.
Mechanism, read from the store: at the end of the first sick day the revision step checked 56 new facts and
invalidated NONE (47 marked duplicate, 9 added). It invalidated 1 after day 15 and 30 after day 16. The store kept
asserting "desk_b1 ... still current" for two nights after the change, and the answers follow it (d15q01: the reasoning
cites the desk facts and the resident card). This is STALE's finding (old entries judged stale 3.3% of the time) on our task:
the write-time judge does not recognise an implicit change until it has been contradicted repeatedly.
Precision: night 13 (the last lead-up night) was also truncated (#5), so the store entered the break missing day 13's facts.
The lag itself is the judge's: the day-14 and day-15 revisions parsed cleanly and invalidated 0 and 1 facts. But the day 14-16
accuracy (27) comes from a store with both problems.
#5 (added to the catalogue; MY harness bug, not a model property): REVISION OUTPUT TRUNCATED. The revision call's
2,500-token limit cut the JSON mid-list on 6 nights (7, 13, 19, 20, 21, 22). The output did not parse, so NO decisions were
applied and that night's new facts were DROPPED. Days 19-22 are most of the later spell, so the later-spell number above is
from a store that stopped updating after day 18. Caught by listing nights with zero operations. Fix: a larger limit, and
a parse failure must raise, not pass silently. A re-run of hh_s0 is ~90 min on one stream.

## FOUR ARMS, SAME SIX HOUSEHOLDS, SAME DAYS, SAME SESSION, PAIRED (05:05) — how the written routine is corrected
Baseline: the stale card (the recent-sightings list re-run tonight). The arms: stale card + the daily "X is home sick
today" message (our wording; never retracted, so the sick-day lines stay in the prompt after day 24); stage-only card (the
sick person's line replaced by "home sick at the moment; not working", our wording, reverted on day 24); couch card (the
line replaced by the simulator's own description, naming the couch in the living room, reverted on day 24). Full output:
four_arm.txt. Detected = mean >= 2 se; "floor" = the baseline's own rerun difference in that window.
| vs stale card | first sick days, all / cold | later spell, all / cold | first days back 24-26, all / cold | 27-28 all |
|---|---|---|---|---|
| + message | **+13.2 / +28.1** | **+16.0 / +40.0** | **-10.1 / -17.1 (both detected)** | -0.3 |
| stage-only card | **+10.1 / +19.9** | **+13.2 / +31.5** | identical (same prompts) | identical |
| couch card | **+13.9 / +29.3** | **+12.8 / +28.4** | identical | identical |
| card removed | **+6.6** / **+11.2** | +9.0 (n.d.) / **+18.2** | -2.7 / -7.9 (n.d.) | -0.6 |
Lead-up: identical for the three corrections (same prompts before day 14); card removed costs cold -7.5 (detected).

The three questions:
1. Does appending a correction work? YES in the spell (+13 to +16 all, +28 to +40 cold, 15-34x the floor). But the appended
   correction is never retracted, and it COSTS on the return: -10.1 all, -17.1 cold, detected on six households. This is the
   unretracted-message cost again, now on the same memory at n=6 in one session (the earlier 18-household figure was
   -7.0 all / -12.3 cold).
2. Does it matter where the correction goes? In the spell, barely. The message is slightly better than the stage card
   (first sick days -3.1, se 0.5, detected; later spell -2.8, not detected). On the return, the card corrected IN PLACE wins by
   +10.1 all / +17.1 cold (detected), because it reverts when the routine does. Honest scope: the card's reversion is by
   construction (we wrote it true for each day); the message arm had no retraction. What this compares is "a description kept
   current" against "an appended correction never withdrawn", not a card against a message in general.
3. Knowing the stage, or being told where things are? Naming the couch adds nothing detectable over "home sick": couch minus
   stage card +3.8 (n.d.) first sick days, -0.3 later spell; cold +9.5 (n.d.) and -3.1. The benefit is knowing the stage.
Predictions: mine for the stage card ("cold +10 to +15") was WRONG: +19.9 on the first sick days and +31.5 later. The
coordinator's ("near the couch card") HELD. Mine for the message ("within ~3 points of the stage card in the spell") HELD
(-3.1, -2.8).
Headline sentence this supports: the model follows whatever the prompt asserts about the resident's routine. A current
description is worth +13 overall and +30 cold through the spell, with most of it coming from knowing the STAGE, not the
location. An appended correction buys the same in the spell but keeps being followed after it stops being true, unless the
description is also restored.

## Rerun floor for the whole-log-in-the-prompt memory (05:27, hh_s0-2; same days)
Existing chain_person run -> fresh re-run tonight, prompts verified byte-identical:
| household | all days (share of answers changed) | largest window move | recent-sightings list, same household, answers changed |
|---|---|---|---|
| hh_s0 | 69->69 (4%) | 2-3 points | 4% |
| hh_s1 | 65->63 (6%) | lead-up 66->62 (10% changed) | 2% |
| hh_s2 | 74->76 (4%) | days 27-28 78->88 (9% changed) | 4% |
Mean: 4.7% of answers changed for the whole-log memory vs 3.3% for the recent-sightings list. All-days accuracy moves 0-2 points,
but single windows move up to 10. Verdict: slightly larger on average, carried by one household (hh_s1: 6% vs 2%), and not
distinguishable at three households. Neither prediction is confirmed: the coordinator's "larger" points the right way, mine
"about the same" is within the noise. For the told-vs-untold figure on this memory, the per-window floor is up to ~10 points
in single households, so a single-window claim on few households needs that margin.

## Fact store, clean re-run (06:27, hh_s0): no truncation, but a SIXTH failure. The policy still has not been tested.
Accuracy vs the same-session recent-sightings list, same questions: lead-up 85->83, first sick days 44->46, later spell
44->48, first days back 79->81, 27-28 75->78, all 65->67. Within a few points everywhere, one household.
#6 COPY-THROUGH FREEZE (caused by the fix for #2): from day 15 to day 25 the revision step marked every new fact a duplicate
(76/76, then 75/75, each night; one invalidation in eleven nights). The extractor was copying the held facts verbatim
regardless of the day's evidence. Day 17: charger_yuki's stays were "coffee_table_l1 from 09:24, still there at 16:03" and the
extracted fact was "desk_b1, 00:00-23:00", the held fact word for word. The instruction "repeat an existing fact's wording
where today agrees" became "repeat the existing facts". The store froze at the break, so the validity-window judge was never
shown a contradiction. The accuracy tie says nothing about validity windows: the answers came from the 40 recent sightings in
the same prompt. Caught by the identical duplicate counts night after night, a suspiciously constant metric.
Where this leaves the strand: six write-side failures, each found by inspecting the store. Fixing one (#2, paraphrase churn)
produced another (#6, copy-through). An LLM extraction step sits between the evidence and the revision policy, and with this
model we could not make it faithful. The revision policies are therefore UNTESTED on this task. The control that would test
them is the one the coordinator named at 02:20: facts extracted MECHANICALLY from the sightings (stays merged by rule), so that
only the revision judge is an LLM. Not run tonight.
What does stand from the fact store: the day-14/15 invalidation lag (0 and 1) from the first clean-parsing run, and the
failure catalogue itself.

## Fact store with MECHANICAL extraction: the validity-window judge audited directly (07:37, hh_s0-2, complete, 0 unparseable)
Facts made by rule from each day's stays. The only LLM call in the write path is the judge (ADD / DUPLICATE / INVALIDATE).
judge_audit.py reconstructs every decision from the revision prompt. "Contradicted" = none of that night's rule-made facts
put the object at the same spot with overlapping hours; "agreeing" = at least one does.
| household | stage | P(closed given contradicted) | P(closed given agreeing) | false closures, same spot + hours overlap (the claim) | same spot at all (upper bound) |
|---|---|---|---|---|---|
| hh_s0 | lead-up / sick / back | 100% / 99% / 100% | 44% / 37% / 31% | 38% / 39% / 41% | 69% / 76% / 74% |
| hh_s1 | lead-up / sick / back | 99% / 99% / 99% | 47% / 37% / 38% | 36% / 44% / 45% | 75% / 75% / 74% |
| hh_s2 | lead-up / sick / back | 99% / 99% / 100% | 52% / 42% / 36% | 31% / 38% / 34% | 70% / 69% / 70% |
Nights from first contradiction to closure: 0 in almost every case (hh_s0 sick: 279 of 280 same night, one after 5 nights).

Reading:
- NO LAG. Shown a clean contradiction, the judge closes the window the SAME NIGHT, 99-100% of the time, in every stage,
  including the night of the break.
- It OVER-CLOSES: it also closes 31-52% of facts the night's evidence agrees with. Between a third and a half of all its
  closures are false by the strict count. The discrimination gap is about 50-65 points (99% vs 31-52%), so it IS reading
  the contradiction; it is aggressive, not blind.
- The format caveat: counting any same-spot closure as false gives 69-76%; requiring overlapping hours gives 31-45%. Our
  rounding made the same behaviour look different from day to day, so about half the apparent over-closure is our fact
  format. A fact store's schema becomes the judge's evidence: a formatting choice upstream becomes a semantic judgement
  downstream. Added to the catalogue as a limit of the mechanical extractor.
- CORRECTION to the earlier "stands" claim. The 0 and 1 invalidations after days 14-15 in the first LLM-extraction run were
  NOT the judge's lag. On those nights the extractor was already copying the held facts through (day 15: charger_yuki's stays
  were the bed then coffee_table_l1 from 12:02, and the extracted facts were the held "desk_b1, 00:00-17:51" word for word).
  The judge was never shown a contradiction. That claim is withdrawn: it was failure #6 appearing earlier than we noticed.
- Accuracy vs the same-session recent-sightings list, same questions (all questions): lead-up 85->79, 76->66, 90->92; first
  sick days 44->46, 62->65, 50->62; later spell 44->60, 69->62, 60->58; first days back 79->77, 67->67, 88->77; all
  65->67, 68->64, 74->75. No window is consistent across households; nothing clears the spread (n=3). A store whose windows
  close fast and too often does not measurably change answers when the 40 recent sightings sit in the same prompt.
Predictions: the coordinator's "lag of one to two nights" was REFUTED (0 nights). Mine, "shorter lag, under half closed on
night 14, most by night 16", was REFUTED too (all closed the same night). Mine, "accuracy within a few points of the list",
roughly held (inconsistent, nothing detected).
Strand conclusion, updated: with an LLM writing the facts, the store failed six ways and the policies went untested. With
facts written by rule, the validity-window judge DOES detect change immediately. What it gets wrong is the reverse: it
closes too much. The "evidence present, not acted on" failure we see elsewhere tonight is NOT what this judge does. It sat
in the extraction step, where the LLM copied the old facts forward.
