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
