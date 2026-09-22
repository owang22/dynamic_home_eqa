# Expectations for the UQ roster on the regime banks — written 14:25, BEFORE the runs

Banks (primary): results/regime_search/sick_owner (10 hh, 28 d, 32 q/day about the sick resident's own routine objects;
resident_1 sick days 14-18; stages lead 0-13 / sick 14-18 / return 19-27) and sick_all (everyone sick, 64 q/day).
Secondary: sick_spell, holiday_to_work. Base counter = TimetableLookup(bin=2h, days=all), negative evidence off, spots only.
Coordinator's classical numbers (10-hh means): sick_owner timetable 90 -> 52 on day 14, 67-68 in the sick stage, return 84;
most frequent 63 -> 32 and stuck. sick_all timetable 77 -> 53/50/56/70/64, return 74-84.
Verified before writing this: hh_s0 sick_owner classical timetable 654/864, mostfreq 478/864; sick_all 1211/1728, 973/1728.

Roster (output uq/regime/<regime>/<agent>/hh_s*.jsonl + .side.json):
  none_mf      plain most-frequent            (degenerate reference only)
  none_tt      frozen timetable               (== classical TimetableLookup(bin=2h,days=all) to the digit)
  none_tt72    timetable, 72 h half-life      (== classical ...hl=72h rows once the coordinator's rewrite lands)
  ocp_tt       online conformal, decaying steps, relevance tau 24 h, on the frozen timetable
  ocp_tt_norel same, tau = 0 (no relevance weighting)
  mon_tt       martingale MONITOR (factor 1: fires logged, no reset) on the frozen timetable
  mon_tt72     martingale monitor on the 72 h timetable
  mart_tt      martingale with reset (factor 0.1) on the frozen timetable
  mart_tt72    martingale with reset on the 72 h timetable
  bma_tt       fixed-share BMA over timetable half-lives {24, 72, 168, inf} h, share 0.02

Numbers I expect (checked by uq_check.py per household while the sweep runs; a FAIL stops the sweep until explained):
E1  none_tt / none_mf: 0 answer or top_prob mismatches vs the classical rows; same per-day accuracy.
E2  ocp_tt: pooled coverage per stage in [0.85, 0.95] (target 0.90) for lead (from day 3, after the 20-question warm start),
    sick and return; mean set size on days 14-15 > mean set size on days 12-13 (sets grow when the stream breaks); mean set
    size on days 24-27 < days 14-15 (they shrink again). Accuracy == none_tt (the answer is unchanged by the set).
    Rel < 1 never lowers coverage: coverage(ocp_tt) >= coverage(ocp_tt_norel) - 0.02 per stage.
E3  mon_tt (frozen timetable, monitor): fires on day 14 or 15 in >= 7/10 households; fires on days 1-13 in <= 2/10
    households (delta 0.01 false-alarm budget, ~400 lead questions); does NOT fire on days 19-21 (the frozen timetable's
    accuracy goes UP on the return: 67 -> 84, and the test is one-sided) in >= 8/10 households.
E4  mon_tt72 (72 h timetable, monitor): fires on day 14 or 15 in >= 7/10 households AND fires again on days 19-21 in
    >= 6/10 households (its accuracy drops on the return because 5 sick days outweigh the decayed lead).
E5  mart_tt (reset 0.1): after the day-14/15 fire the sick-stage accuracy on days 16-18 is >= none_tt's on the same days
    (+3 pts or more pooled); on the return the reset counter then DROPS (days 19-20 below none_tt) and fires again on
    days 19-21 in >= 6/10 households — the "drop again" from a detector that forgot on purpose.
E6  bma_tt: on lead days 8-13 the weight on {168, inf} >= 0.6; on days 14-15 the weight on {24, 72} rises vs day 13 (mean
    over households, by >= 0.10); by days 22-27 the weight on {168, inf} is above its day-15/16 value; accuracy on lead
    days 8-13 within 2 pts of none_tt and on days 16-18 >= none_tt.
E7  Reliability: none_tt top_prob has positive slope (bin 0.8-1.0 accuracy > bin 0.4-0.6 accuracy); ocp conf_set on the
    sick stage is lower than on the lead stage (mean).
Wrong-direction rules: any stage coverage < 0.85; set size falling on day 14; monitor firing on the lead stage in > 2/10;
bma below none_tt by > 2 pts on lead days; martingale reset making days 16-18 WORSE than none_tt -> stop, explain in
uq/problems_found.md, then continue.

## added 14:31, before the run — nexcp: conformal beyond exchangeability (weighted quantile)
Barber, Candès, Ramdas, Tibshirani, "Conformal prediction beyond exchangeability", Ann. Stat. 2023 (arXiv 2202.13415):
the prediction set uses the (1 - alpha) quantile of the WEIGHTED empirical distribution of past nonconformity scores plus a
point mass at +inf for the new point; with weights decaying in time the coverage gap is bounded by the weighted total
variation between the recent and the current distribution — a burst of high scores after a shift moves the quantile at
once, unlike the decaying-step update which moves by eta_min = 0.005 per question. Adaptation: score 1 - p(truth) (same
as ocp), weights w_i = 2^(-(t - t_i) / tau_w) with tau_w = 24 h by default (effective window ~1.5 days of questions),
w_inf = 1; set = {y : 1 - p(y) <= q_t}; confidence 1/|set|. Degenerate: tau_w = inf gives the plain split-conformal
quantile over all past scores. Agent `nexcp_tt` (timetable base).
E8  nexcp_tt on sick_owner: coverage lead >= 0.88 and sick >= 0.88 (ocp_tt: 0.928 / 0.854), return in [0.85, 0.95]; set size
    days 14-15 >= ocp_tt's 4.9 (it reacts faster, so the sets are larger on the shift days) and back below 2.5 in the
    last 4 days; on sick_all sick-stage coverage >= 0.88 (ocp_tt: 0.879). Accuracy == none_tt (the answer is unchanged).
    Wrong direction: sick coverage below ocp_tt's, or lead sets larger than 2x ocp_tt's.

## added 14:34, before the run — LLM confidence channels, sick_owner hh_s0, days 13 (plain, timetable 100%) and 14 (sick day 1, timetable 22%)
uq_llm.py (naive memory, not told; local Qwen3.8-27B on :8300), 64 questions x 3 calls (greedy JSON with verbalized
confidence; 5 samples at T 0.7 -> agreement; 10-way multiple choice with first-token logprobs). Output uq/llm_channels/regime_sick_owner_hh_s0/.
E9  (a) verbalized confidence: mean >= 0.85 on both days and day-14 mean within 0.05 of day 13 (it does not know it is stale);
    (b) token probability and (c) agreement: mean on correct answers - mean on wrong answers >= 0.15 for (c), >= 0.10 for (b);
    day-14 mean of (c) at least 0.10 below day 13 (it notices the break through disagreement); accuracy day 13 > day 14.
    Wrong direction: a channel whose mean is HIGHER on wrong answers than on right ones.

## added 14:42, before the run — R6 banks (sick10_owner 16 q/day, sick10_all 64 q/day; 32 days; sick days 14-23, return 24-31)
Coordinator's design: a 10-day spell so that forgetting bases re-learn inside it and DROP on the return; the frozen timetable
stays flat through the return. Bases: frozen tt, tt72 (3-day), tt24 (1-day). Detector = CUSUM e-detector monitor, threshold 1000.
E10 fires on days 14-15: frozen tt >= 5/10 on sick10_owner (16 q/day, ~10 non-duplicate: at the detection floor), >= 8/10 on
    sick10_all; lead false alarms <= 2/10 per base.
E11 the discriminating number — fires on the return days 24-26: frozen tt 0-1/10 (its accuracy goes UP on the return);
    tt72 >= 5/10 and tt24 >= 6/10 on sick10_all (their own accuracy falls on day 24 because the spell's 10 days outweigh
    the decayed lead: none_tt72 day 23 -> day 24 drop >= 10 pts); on sick10_owner at least tt24 >= 4/10.
E12 reset variant mart_tt: after the day-14 fire, days 19-23 >= none_tt + 5 pts (it re-learns the spell); drop on days
    24-25 vs none_tt >= 8 pts and a second fire on days 24-26 in >= 4/10 (the window now holds the re-learned spell, so
    the return IS a deterioration for it, unlike after a 5-day spell).
E13 bma_tt: short-hl weight rises on days 14-15 (>= +0.10 vs day 13), stays above the lead level through days 20-23, rises
    AGAIN on days 24-25 vs day 23 (>= +0.05), and the long-hl weight is back above 0.6 by days 29-31.
E14 ocp/nexcp: coverage per stage within [0.85, 0.95] for both; nexcp sick-stage coverage >= ocp's; set size grows on days
    14-15 AND on days 24-25 relative to the two days before each boundary.
14:43 coordinator's numbers for R6 (banks now repeat-free; classical: tt72 lead 46 -> 85, day 14: 42, 90 inside the spell,
day 24: 58, 80 later; frozen tt 87 -> 40 -> 77 flat on the return; sick10_all tt72 82±10 -> 34±11 -> 88±4 -> 54±28):
detector fires day 14-15 in >= 7/10, never in the lead, day 24-25 for the 3 d base and not the frozen base. What my detector
needs: ~20 non-duplicate questions whose error rate has risen by >= 30 points (synthetic: median 21 questions for 90 -> 50%);
sick10_owner has 16 q/day, so day 14-15 = 32 questions -> I expect >= 5/10 by day 15 and >= 7/10 by day 16 there, and
>= 7/10 by day 15 on sick10_all (24 q/day). Per-stage numbers reported as mean ± 1 sd across households.

## added 14:45, before the run — sliding calibration window for the e-detector (`--window N`)
Observed on sick10_all: the 72 h base's monitor fires on day 14-15 in 8/10 but on the return (its accuracy 88 -> 54 on day
24) in 0/10, because the calibration window since the day-14 fire holds the whole spell, including its own bad first days
(34, 49, 61%), so 54% on day 24 is not extreme against that mixture. The p-values should be computed against the RECENT
regime: a sliding window of the last N non-duplicate scores (N = 96 = 4 days at 24 q/day; conformal p-values within the
window are still valid under exchangeability of the window). Expectation on sick10_all with window 96: mon_tt72 fires on
days 24-26 in >= 5/10, still >= 7/10 on days 14-15, lead false alarms <= 3/10 (a shorter window is noisier); mon_tt (frozen)
still 0-1/10 on the return; mon_tt24 return >= 5/10. Wrong direction: lead false alarms > 3/10 or day 14-15 fires falling
below 7/10.

## added 14:50, before the run — LLM channels on the primary bank, sick10_all hh_s0, days 13 and 14 (24 q/day, 48 questions)
Same E9 expectations as for sick_owner hh_s0: verbalized flat (day-14 mean within 0.05 of day 13, separation < 0.05);
agreement separation >= 0.15 and day-14 mean >= 0.10 below day 13; token separation >= 0.10 on its own MCQ answer;
accuracy day 13 > day 14 by >= 30 points (frozen timetable hh_s0: check.md day 13 vs 14).

## added 14:52, before the run — per-object BMA (`--per-object`): one fixed-share weight vector per object
The global vector (bma_tt) hedges with one belief about "how fast the world forgets" for every object; per object, the weights
can follow the sick resident's mug (moved) without touching the other resident's plate (unchanged). Same update rule per
object, on that object's own sightings. Expectation on sick10_all (10 hh): sick-stage accuracy >= 72.0 (the 72 h base) while
the return stays >= 79.0 (within 1 pt of the frozen base's 79.7); lead within 1 pt of bma_tt; weights on the shifted
objects move to the short half-lives on days 14-15 and back by day 22. If it only matches bma_tt (66.0 sick), the reason
is that each object is asked/seen too rarely (~1-3 sightings a day) for its own weights to move within the spell — say so.

## added 14:53, before the run — ocp on the 72 h base (ocp_tt72), R6
Observed: on the frozen base the conformal sets do not grow on the return (days 24-26 sets 2.1-2.2, coverage 0.92-0.95)
because the frozen base does not break there. On the 72 h base (accuracy 88 -> 54 on day 24) I expect: coverage on day 24
in [0.65, 0.85] (a one-day miss like day 14's 0.71), set size on days 24-25 >= 2x days 22-23, back below 3 by day 27;
stage coverage still within [0.85, 0.95].

## added 19:28, before the run — hedge redesign (reviewer task 1): scoring rule, explicit alpha, per-person groups
Diagnosis to confirm first: on sick10_all/owner days 19-23 (late spell, re-learned), tt24 (best single memory: sick10_all
76.9±4.4, sick10_owner 80.2±4.7 mean over days 14-23) beats the global hedge (bma_tt: sick10_all 66.0±8.3, sick10_owner
71.1±12.2) by 10-15 points on those specific days, yet the hedge's weight has already drained back toward the frozen
(inf) counter by day 22-23 (0.90+ per the trajectory table) rather than toward tt24. Suspicion: `--score predictive`
(current default) scores each counter by ITS OWN predictive probability of the seen spot (log-loss / Bayes mixing) —
this rewards calibration, not argmax accuracy, and a broad/smooth counter (the frozen one, mass spread over many
historically-plausible spots) can score consistently "good enough" while a sharp, fast-adapting counter (tt24) that is
usually very right but occasionally very wrong (near-zero mass on the true spot) gets punished hard on its misses.
E15 `--score hit` (0-1 accuracy of each counter's own argmax) on the GLOBAL group should move weight to tt24 specifically
    on days 19-23 (short-hl weight there >= 0.5, vs bma_tt's current < 0.2) and should raise days-19-23 accuracy to
    within 2 points of tt24's own (76.9 / 80.2), while KEEPING the return (days 24-31) within 2 points of the frozen
    base's own (79.7 / 79.0) — this is the reviewer's target: within 2 pts of best-single-memory in the spell AND at the
    frozen level on the return, simultaneously. If it cannot do both, report which stage it loses and by how much.
E16 `--score tempered` (gamma in {0.3, 0.5}) should sit between predictive and hit: less aggressive than hit, still an
    improvement over predictive on days 19-23.
E17 alpha sweep {0.02, 0.10, 0.30} on whichever score wins E15/E16: higher alpha should shrink the return-recovery lag
    (fewer days for the weight to move back to frozen after day 24) at the cost of some spell stability (more variance
    day to day); report both, pick the alpha that clears the 2-point bars in E15 with the fewest side effects.
E18 `--group person` on the winning (score, alpha): sick10_all (2 owners, "shared" for household-common objects) should
    let the sick resident's own weight vector move to short memories while the other resident's vector stays on the
    frozen counter throughout (since nothing in their own history changed) — expect person-hedge accuracy on the
    UNAFFECTED resident's objects within 1 point of the frozen counter's own in every stage, and on the AFFECTED
    resident's objects at least as good as the global hedge's E15/E16 result.
Wrong direction: any score/alpha/group combination that is *worse* than the current bma_tt (66.0 / 71.1 sick-stage) —
that would mean the scoring change hurt rather than helped, and needs an explanation before moving on.

## added 19:34, before the run — planning metric (reviewer task 2): search cost, rooms, ask-or-search policy
Post-processing only, no new agent runs beyond `none_lastseen` (just added, degenerate-checked 0/0 vs classical
LastObservation on hh_s0). Uses the `dist` field already logged by none_tt, none_tt72, none_lastseen, mart_tt72, bma_tt,
ocp_tt. Definitions: rank = 1-indexed position of the truth receptacle in the agent's distribution sorted descending by
probability (ties broken the same way `answer` is picked: highest receptacle id wins), i.e. "places searched before
finding it" if searching in the agent's own probability order; a truth below the logged floor (p < 1e-4, omitted from
`dist`) gets the worst-case rank = total spot count (~38). rooms = number of distinct rooms entered by that point
(receptacle -> room from the bank header). Policy: confident = top_prob >= tau (tau = 0.6, a reasonable "pretty sure"
bar — most methods sit well above it on stable days) or, for ocp_tt, set_size <= k (k = 3); confident -> cost = rank
(physically search in probability order); not confident -> ask the resident at a flat cost c (c in {2, 4}) and retrieve
directly. Mean places and mean rooms are reported unconditionally (descriptive); total cost is policy-mixed.
E19 on shift days (14-15), the adaptive/UQ-aware agents (mart_tt72 after its reset, bma_tt, ocp_tt) should show a LOWER
    total cost than the frozen baselines (none_tt, none_lastseen) specifically BECAUSE they ask more often there (lower
    confident-share on the shift days), trading a flat ask cost for what would otherwise be a long physical search —
    the reviewer's claim to test. On lead/return (plain) days the UQ-aware agents' total cost should be statistically
    indistinguishable from (not worse than) the frozen baselines' — "no cost on plain days".
E20 mean places (unconditional) should track accuracy inversely: an agent with mean places near 1 has the truth at/near
    its own top guess almost always; a large jump in mean places on the shift day (frozen tt: expect several-fold) is
    the same break the accuracy chart shows, expressed in search-cost terms.
Wrong direction: a UQ-aware agent whose total cost is HIGHER than the frozen baseline's on the shift days despite a
lower confident-share — would mean the ask cost c is set too high relative to the search cost it is replacing, or the
confidence signal is not actually selective; report both c values so the crossover (if any) is visible.

## added 19:41, before the run — per-person detection (reviewer task 3), sick10_partial (resident_1 sick, everyone's objects asked)
Frozen-baseline digit checks pass (0/0 on all 5 none_* agents, 7189 rows, 10 hh). Coordinator's own check on the classical
logs: the frozen timetable's stated confidence goes UP on both resident_1's (affected) objects and resident_2's
(unaffected) objects during the spell (0.52->0.56 affected, 0.49->0.63 unaffected) — its own confidence cannot tell the
groups apart, so a per-person DETECTOR (not a per-person confidence readout) is the only thing that can. Owner split from
the earlier check: 634 questions about resident_1's things, 110 about resident_2's per household (~19/day vs ~3.4/day) —
the unaffected group is thin; report n alongside every unaffected-group number.
Three variants on the timetable-72h base (matches mart_tt72's base, the best global detector so far):
  detperson_tt72   `--agent martingale --group person` — one CUSUM detector per resident (+ "shared" for any
                    unowned-by-suffix object), each fires and resets ONLY that resident's known bins.
  detperson_tt72_g `--agent martingale --group global` on the SAME tt72 base, for a fair global-vs-per-person
                    comparison at equal detector settings (mart_tt72 already exists but let's confirm it matches).
  oracle_tt72       `--agent martingale --detector off --oracle-schedule "14:resident_1,24:resident_1"` — told upper
                    bound: reset resident_1's bins at the start of day 14 and day 24, nothing else, no detection.
E21 detperson_tt72: resident_1's own detector should fire on day 14-15 in most households (matching mart_tt72's global
    rate, since resident_1 carries 85% of the question volume so the global detector was mostly tracking them anyway);
    resident_2's own detector should NOT fire on day 14-15 in almost every household (nothing in their own error stream
    changed) — that is the discriminating number the whole task is testing for.
E22 UNAFFECTED-GROUP HARM CHECK: resident_2's stage accuracy/confidence/set-size under detperson_tt72 must be within
    1-2 points of the FROZEN (undetected/unreset) baseline on resident_2's own objects, in every stage — a per-person
    reset must not touch bins it has no reason to touch. Compare against the GLOBAL detector (mart_tt72 or
    detperson_tt72_g) on the SAME split: if the global detector's reset ALSO discounts resident_2's bins (it does, by
    construction — one global discount call touches every object), resident_2 should be measurably WORSE under global
    reset than under per-person reset or the frozen baseline. This is the concrete "does per-person avoid collateral
    damage" number.
E23 oracle_tt72 is the upper bound: resident_1's post-day-14 accuracy should be at or above detperson_tt72's own (same
    reset, but not delayed by detection lag), and resident_2 untouched (no reset ever applied to them) should equal the
    frozen baseline exactly on their own objects (same base, same beliefs, zero discounts) — an exact-match check, not
    just "close", since nothing about resident_2's bins is affected at all by an oracle scoped to resident_1.
Wrong direction: resident_2 accuracy/confidence dropping under detperson_tt72 by more than the frozen baseline's own
day-to-day noise (~1-2 points) — would mean the "shared" bucket or a naming/suffix mismatch is leaking resident_1's
reset onto resident_2's objects; check the fires log's `owner` field by hand if so.

## added 19:53, before the run — per-person conformal (coordinator's follow-up to task 3)
Degenerate check passed: `--group global` (default) reproduces ocp_tt on sick10_partial hh_s0 to the digit (0/744). New
`ocpperson_tt` = `--agent ocp --base timetable --group person`: one DecayingStepConformal q_t per resident (+"shared"),
so a coverage miss on resident_1's objects only widens resident_1's own set/threshold.
E24 resident_2's (unaffected) conformal set size on days 14-15 under ocpperson_tt should be close to its OWN lead-stage
    baseline (day 12-13, ~2-3, per the earlier finding) — NOT the 9.7/12.2 spike the GLOBAL ocp_tt showed on those same
    days for resident_2 (collateral leakage, already documented). If per-person removes that leakage, resident_2's
    day-14/15 set size under ocpperson_tt should sit within ~2x of its own day-12/13 level, well below the global
    agent's 9.7/12.2.
E25 resident_1's own set-size response and coverage under ocpperson_tt should be similar to (not worse than) the
    global agent's, since resident_1 already dominated the global q_t's behavior (85% of question volume).
Wrong direction: resident_2's set size still ballooning under ocpperson_tt — would mean the group split isn't reaching
the conformal object (same owner-suffix bug class as before), or resident_2's "shared"-bucket objects are actually
resident_1's mislabeled ones.

## added 20:06, before the run — windowed affected/unaffected analysis (Oliver's own review), 20 households
Target: replicate Oliver's own spot check on the frozen timetable (affected 82->48, unaffected 72->75, per-household
change -34±24 vs +2±14, 7/10 gap>=15) on the full 20 households (sick10_partial + sick10_partial_s10_19 pooled), then
extend the same 5-window analysis (last5lead d9-13, first3sick d14-16, restsick d17-23, first3return d24-26, restreturn
d27-31) to none_tt72, detperson_tt72, oracle_tt72, none_mf72, none_lastseen. Digit checks first: none_mf72 (new) and
none_lastseen/none_tt/none_tt72 against classical on both regimes, both 7189/7045 rows, 0/0. gap = unaffected's change
minus affected's change (positive = affected suffered more); gap bar = 15 (Oliver's own number), report N/20 clearing it.
E26 none_tt entry transition should be within a few points of Oliver's 10-household numbers and the clear-bar fraction
    should hold up (~70%) at 20 households, not regress toward noise.
E27 none_tt72 should show the SAME one-sided break at the return that Oliver found (85->58 affected, 79->80 unaffected)
    — since the return isn't the lead-vs-sick comparison, define its reference window as restsick (the settled mid-spell
    state), not last5lead.
E28 none_lastseen should show the INVERTED sign Oliver found (affected accuracy goes UP entering the spell, not down) —
    a qualitatively different finding, not a "does it clear the bar" one; report it as such.
Wrong direction: the windowed gap failing to clear the bar in a clear majority of households for the entry transition on
none_tt specifically (that's the one already independently checked by hand) — would mean my windowing/owner-split code
has a bug, not that the effect is real but small.

## added 20:20, before the run — shared-state vs per-object: does global grouping harm the unaffected resident? (Oliver's correction)
Correction to the affected/unaffected panel: per-object learners (none_tt, none_tt72, none_mf72, none_lastseen) keep a
separate record per object by construction, so "unaffected held steady" there is a control, not a finding. The real
test is on the SHARED-state methods: the hedge (one household-wide weight vector), the conformal threshold (one q_t),
and the detector+reset (one martingale) — each mixes information across every object, including the unaffected
resident's. Comparison, same 20 households, same 5 windows, UNAFFECTED group only:
  hedge:      bma_hit (global, --score hit --share 0.02) vs bma_person (--group person, same score/share)
  conformal:  ocp_tt (global q_t) vs ocpperson_tt (--group person)
  reset:      mart_tt72 (global martingale+reset) vs detperson_tt72 (--group person)
Two metrics per pair: accuracy (does the unaffected resident get MORE WRONG under global grouping?) and confidence/set
size (does the unaffected resident get LESS SURE / larger sets under global grouping, even if the answer is unchanged
— the "spreads doubt" question). Already found on the whole-spell means (not windowed): the martingale reset leaks
confidence not accuracy onto the unaffected resident (36.3->31.8 sick, 38.1->35.3 return) and conformal partially
leaks set size (9.7->6.7 day14). This run puts those on the same windowed, paired-per-household footing as everything
else, plus adds the hedge (not checked before).
E29 for each pair, on the unaffected group: accuracy change (global vs person) should be small/noisy (matches the
    earlier whole-spell finding of no measurable accuracy harm); confidence/set-size change should show a real,
    larger gap for the GLOBAL variant specifically on the entry and return windows (the moments the affected
    resident's own signal is moving hardest) — that is "does it spread doubt."
Wrong direction: the per-person variant showing WORSE unaffected-group numbers than global on either metric — would
mean the per-person split itself is introducing noise/harm rather than removing collateral effects (plausible given
the conformal per-person finding of thinner-calibration noise already logged).
