# Regime search — running notes (2026-09-21, driver session; newest at the bottom)

Goal: a regime where cheap learners climb visibly to ~80%+ on a unified question group, break sharply (>= 20 pts) at a
scripted shift, re-learn inside it, and break again on the return. No LLM methods while iterating.

## 13:45 A0 clean21 — 22 days, no events, activity questions at activity START, all classes (configs/regime/clean21.yaml)
Timetable all 55 -> 72, moved half 16 -> 74 (learns; weekends dip ~10); last seen flat 50-59. Ceiling diagnosis: only 16% of
routine-object questions have a stable truth +-15 min around the question — questions at activity start catch objects mid-move.

## 14:05 A1 clean21_during — same households, questions DURING the activity (new knob question_moment: during)
Timetable all 54 -> 82-88 by week 3, moved half 25 -> 87; most frequent 47 -> 68; Perpetua* 56 -> 60; last seen ~50 flat.
Per class: the learnable group = moved-since-round >= 70% AND timetable >= 60% in week 3: mug bowl plate glass water_bottle pan
pot spatula kitchen_knife serving_dish recipe_book snack_bowl tablet charger remote glasses razor book shopping_bag dog_food_bag.
Static classes (laundry basket, detergent, toolbox, dog bowl, skincare, laptop, pen) are 90-100% for everyone -> pointless;
recency-dominated ones (towel, blanket, phone, vacuum) confound.

## 14:15 A2 clean21_routine — the group only: timetable 28 -> ~80 (all and moved), last seen 31-36, most frequent 34 -> 62.
The learning slope Oliver asked for, on one unified question type: "things used in daily routines, asked while in use".

## 14:35 R1 nightshift — 14 weekdays lead, resident_1 -> shift_worker days 14-20, return 21-27 (calendar knob by f1)
NO drop: timetable lead 71 / shifts 77 / return 80 on the moved half; per class most kitchen classes go UP in the shift week.
Reading: questions asked DURING an activity are keyed to the activity, so a TIMING shift (breakfast at 11 instead of 8) does not
move the answer ("mug on the kitchen table while breakfast is happening" is regime-invariant). Only PLACEMENT shifts can break
this question type: sick spell (couch/coffee table), guests (armchair/sink), holiday vs work (different activity sets).
Timing shifts would only bite scheduled-clock questions ("where is the mug at 08:00") — a second question type to consider.
Also: only charger (76 -> 53) and snack_bowl moved under the shift; resident_1 was the works-from-home resident in hh_s0.

## 14:05 R2 holiday_to_work / R3 sick_spell (10 households each, routine group, during)
R3 sick spell (resident_1 off sick days 14-18): timetable all 76 -> 62 on sick day 1 (-14), back to 78-79 by day 2, 61 on day
18, return 75-83. R2 holiday -> work: 79 -> 68 on the first work day (-11), 84 by day 3. Most frequent dips similarly; last seen
flat. So placement shifts DO bite this question type, but only ~10-15 points and for a day: (a) the learners re-fill their 2 h
bins within a day, (b) most questions in the shift stage are about activities that go on unchanged (the other resident's
meals). The next diagnostic is "regime novelty": the share of shift-stage questions whose true location is NOT the lead-stage
answer for that (object, hour bin) — that is the ceiling of any drop. Design the group and the shift to make it large.

## 14:30 regime novelty (tools/novelty.py) and R3c sick_all (first 4-5 households)
Novelty = share of shift-stage questions whose truth differs from the lead-regime answer for that (object, 2 h bin).
Same-regime baseline (the return stage) is 25-27%: that is the irreducible ambiguity, consistent with the ~80% ceiling.
sick_spell (one resident): 38% (sick resident's own objects 50-75%, shared kitchen objects 35%) -> a 13-point ceiling, the
14-point dip we saw. holiday_to_work: 43%. nightshift: 38% but concentrated on the shift-worker's objects (68-81%) and the
timetable did not drop — those questions come at new hours (empty bins -> fallback) and the bins fill in a day.
R3c sick_all (EVERY resident off sick days 14-18; new calendar value resident: all): novelty 55%. Timetable all-questions
77 -> 53 / 50 / 56 / 70 / 64 -> return 74-84: a 24-27 point drop that lasts three days, then visible re-learning inside the
sick regime (56 -> 70) — the entry half of the shape. Most frequent 54 -> 32/23/32/43/31 and stays down (stuck on the lead
histogram), back to 60 on the return. No drop on the RETURN for the frozen timetable (14 lead days outvote 5 sick days in
every bin) — the return drop needs agents that forget: adding timetable/most-frequent with a 3-day half-life
(extra_beliefs, f1's registry hook) to sick_all, sick_owner and the new vacation config.

## 14:40 R3b sick_owner (resident_1 off sick days 14-18; questions only about resident_1's own routine objects, 32/day)
The cleanest entry shape so far. Timetable all-questions: lead 43 -> 90 (saturates 85-90: personal objects are the most
learnable), sick day 1: 52 (-38), then 67 67 67 68 (partial re-learning inside the regime), return 84 -> 82. Most frequent
63 -> 32/41/40/32/41 -> 73. Last seen flat 41-53. Novelty 51% (baseline 21%). Still no drop on the RETURN (frozen learner).
Re-running sick_owner and sick_all with the 3-day-half-life timetable and most-frequent (extra_beliefs) and launching
R5 vacation (14 work days, 10 days at home, 8 work days; personal group).
Design reading so far: the shape needs (1) questions DURING activities, (2) a question group the regime actually moves
(the affected residents' schedule-timed personal objects), (3) a regime that hits the whole asked group (everyone sick /
everyone home), (4) agents that forget for the return drop.

## f1 (session dc78…, 2026-09-21 13:30-14:25) — what is done and what is not

Done:
- Simulator calendar knobs (see SIM_KNOBS.md): `calendar` stages with `day_kind`, `force_events`, `suppress_random_events`,
  `roles`; `--calendar FILE` on situation_sim.run; confshift `calendar:` plumbing; stage tags on bank questions / run-log
  rows; default output byte-identical (cmp on seed 10, 8 and 28 days). Files: src/situation_sim/{situation,run,schedule,
  placement,checks}.py, src/baselines/patrol/{confshift,bank,run}.py, configs/regime_example.yaml.
- `extra_beliefs` config key (confshift): extra registry specs appended to the roster, default roster unchanged. Used for
  a decayed-count timetable (`{name: timetable, half_life_h: 72}` / 24) and most-frequent hl 24 h; labels "timetable hl 3d",
  "timetable hl 1d", "most frequent hl 1d" in the report. Check: half_life 1e9 h equals the frozen timetable on hh_s1 of
  sick_spell except 32/1728 exact-tie rows (identical top_prob, tie order differs); no probability differs by > 1e-3.
- tools/boundary.py <dir> <day...>: per-class accuracy 5 days before vs first 2 days after a stage boundary (timetable,
  last seen, most frequent; all and moved half).
- Runs: sick_spell_hl (R3 banks + forgetting agents) and holiday_to_work_personal (R2 households, classes
  [razor, mug, snack_bowl, book, tablet, recipe_book, glasses, glass]); analyze.txt in each dir.
  Results, all questions: sick_spell_hl timetable 40..76 | sick 64 73 72 72 66 | return 76..80; timetable hl3d tracks it
  within 2 points; hl1d 65 71 72 72 70 | 68 75 75 72 76 — no return drop with any half-life (the sick regime does not
  re-teach the routine group's bins; the return day 19 is 68-76 for every timetable). holiday_to_work_personal: timetable
  47..83 | work 70 77 73 74 86 ...; boundary drop pooled -5 (5 days before vs 2 after), one-day dip 83 -> 70 (-13) — the
  same size as with all 20 classes; restricting to the "personal" carriers did not amplify it (their per-class deltas in
  R2 were small-n and regressed). Per stage (moved|still) timetable home 77|65, work 80|61.
Not done / open:
- No seeded worker_out-only run (not started, per the wrap-up request).
- The return-drop question: with the routine group, neither regime (5-day sick, holiday->work) changes the bins enough
  for any timetable to fall on the way back; a longer spell (10 d) on the sick resident's own objects, or a regime that
  moves the asked objects' resting places (roles / night shift), is the next lever — see the R1 night-shift run.
Carriers in sick_owner (novelty by class during the spell): book 81%, water_bottle 75%, tablet 60%, mug 58%, charger 57%,
glasses 43%, glass 39%, razor 34%; plate 16%, bowl 12% (meals still happen at the table). So the unified question type for a
sick-spell regime is "the person's everyday things" (book, water bottle, tablet, mug, charger, glasses, glass), which is
exactly the set the sick-day placement rules move to the couch / coffee table. Plate and bowl should leave the group.

## 14:55 forgetting agents on sick_owner; vacation; the next candidates
sick_owner with 3-day-half-life agents: timetable_hl3d lead 90 -> 53 (day 14) -> 69/68/69/74 (re-learns further than the
frozen one, 74 vs 68) -> return 80 -> 70 (a 10-point RETURN dip on day 20) -> 83; most-frequent_hl3d 64 -> 35/48/48/48/56
-> 57/42 (return dip) -> 65. The frozen agents: no return dip. So the return drop is a property of adaptive learners — the
plasticity/stability trade-off is the method axis the shape exposes: frozen = never re-learns B, adaptive = re-learns B and
breaks again on the return.
R5 vacation (10 days at home on the weekend schedule, personal group): only a 10-point dip (84 -> 74) despite 46% novelty —
holiday questions come at NEW hours (breakfast at 10 instead of 7), i.e. empty bins whose fallback (whole-history most
frequent = the usual spot) is often right. Novelty must be split: "same bin, different spot" (sick: mug on the couch at
08:00) is what breaks a time-of-day learner; "new bin" novelty does not. Vacation is out.
Next: R6 sick10_owner / sick10_all — 10-day spell (days 14-23), 8-day return, the everyday-things group (book, water bottle,
tablet, mug, charger, glasses, glass, razor), frozen + 3 d + 1 d half-life agents. Expect: deeper re-learning inside the
spell and a larger return drop for the forgetting agents; the frozen timetable may finally lose bins where 10 sick days
outvote... no: 14 lead days still outvote 10 — the frozen line should stay flat on the return, which is the contrast.

## 15:05 repeats fixed at the source (research agent's P2), R6 relaunched at the natural question rate
`question_moment: during` + an owner filter drew the same object several times inside one activity block (5 of 32 per day in
sick_owner) — the found-it feedback of the first answers the second, which flatters recency agents and double-counts one
error for a detector. New knob `question_min_gap_min` (bank.py: greedy in time order, >= gap minutes between questions
about the same object; a day takes its natural number of distinct questions when that is below per_day). With a 30-min gap
one person's everyday things yield 12-16 distinct questions a day, the household's 22-24 — that is the honest rate.
sick_owner / sick_all numbers above were computed with repeats (kept as classical_v1_*); R6 sick10_owner (16/day) and
sick10_all (24/day) are the repeat-free candidates. The research agent's roster (uq/regime/) runs on R6 once it lands.

## 15:20 R6 sick10_owner — THE SHAPE (10 households, 16 questions/day, one person's everyday things, no repeats)
Calendar: 14 weekdays lead, resident_1 off sick days 14-23, return days 24-31. All-question accuracy per day, mean over 10 hh:
  timetable 3-day half-life:  lead 46 -> 84-85 | sick 42, 59, 72, 75, 84, 86, 90, 86, 91, 88 | return 58, 65, 58, 72, 76, 78, 80, 79
  most frequent 3-day hl:     lead 42 -> 61-64 | sick 26, 44, 60, 66, 73, 80, 81, 79, 82, 82 | return 24, 33, 40, 50, 67, 69, 70, 63
  most frequent 1-day hl:     lead 42 -> 62    | sick 37, 68, 75, 78, 77, 81, 79, 75, 81, 82 | return 31, 55, 64, 60, 70, 68, 65, 62
  timetable (frozen):         lead 41 -> 87    | sick 40, 53, 61, 66, 65, 68, 72, 69, 74, 77 | return 77, 87, 71, 79, 81, 83, 79, 79
  most frequent (frozen):     lead 33 -> 62    | sick 22, 25, 25, 35, 37, 48, 51, 50, 59, 62 | return 58, 59, 54, 52, 67, 63, 64, 64
  last seen:                  flat 46-59 throughout.
Bands (sd across households of daily accuracy, 16 q/day): timetable_hl3d d23 88±8 -> d24 63±27 -> d26 59±14; mostfreq_hl3d
d23 82±6 -> d24 26±19. Entry drop 42-46 points (2.5-3 sd); return drop 25-58 points for the forgetting agents (clears 1 sd
by day 26); the frozen agents show the entry drop, a slower partial re-learning, and NO return drop; last seen nothing.
Per stage (moved half): timetable_hl3d lead 76 / sick 78 / return 73; frozen timetable 76 / 66 / 81; mostfreq_hl3d 60 / 68 / 51;
frozen mostfreq 58 / 42 / 59; last seen 45 / 56 / 45.
This is the regime to freeze (candidate F1). Unified question type: "the person's everyday things asked while in use"
(book, water bottle, tablet, mug, charger, glasses, glass, razor), one question per object per half hour at most.

## 15:25 R6 sick10_all — same shape, tighter bands (everyone sick days 14-23; 24 q/day about everyone's everyday things)
  timetable 3-day hl: lead 47 -> 82 | sick 34, 49, 61, 72, 78, 81, 86, 83, 88, 88 | return 54, 60, 71, 77, 76, 81, 75, 79
  most frequent 3-day hl: 43 -> 55 | 18, 30, 42, 59, 72, 73, 72, 75, 80, 82 | 29, 40, 50, 54, 59, 66, 60, 60
  frozen timetable: 46 -> 80 | 35 ... 74 | 80 (no return drop); frozen most frequent 55 | 14 ... 51 | 64; last seen 40-55 flat.
Bands: timetable_hl3d d13 82±10 -> d14 34±11; d23 88±4 -> d24 54±28 -> d25 59±11 -> d26 70±12. mostfreq_hl3d d23 82±8 ->
d24 29±17. Entry drop ~4 sd, return drop > 2 sd on the stage level. Candidate F2; with 24 q/day and the whole household it
is the better primary; F1 (one person) is the cleaner story for a robot serving one person. Both frozen as configs.

## 15:50 F2 replicates on ten fresh households (seeds 10-19, results/regime_search/sick10_all_s10_19)
timetable 3 d hl: d13 86±6 -> d14 38±13 -> d18 82±11 -> d23 82±11 -> d24 62±13 -> d25 69±12 -> d26 76±8 (seeds 0-9: 82 -> 34 ->
78 -> 88 -> 54 -> 59 -> 70). most frequent 3 d hl: 68 -> 22 -> 73 -> 80 -> 25 -> 30 -> 45 (0-9: 55 -> 18 -> 72 -> 82 -> 29 -> 40 -> 50).
Frozen timetable: 85 -> 35 -> 68 -> 71 -> 81 (no return drop, again). Last seen 44-53 flat. Same shape, same magnitudes,
entry and return drops beyond 1 sd on both samples. The regime is frozen: F2 household (primary), F1 person (companion).

## 16:00 research agent (dynamic-home-eqa-0a) — UQ roster on the frozen regime (uq/REPORT.md, uq/regime/*/check.md)
Frozen timetable 72±7 | 61±12 | 80±7 (no return drop); 3 d hl 73 | 72 | 72; e-detector (CUSUM, thr 1000, de-duplicated
questions) + targeted reset on the 3 d base: fires day 14 in 8/10 and on the return in 5/10, lead false alarms 0/10, spell
accuracy 76±6 vs frozen 61±12; on the frozen base it fires day 14 in 10/10. Online conformal: coverage 0.91-0.93 in every
stage, set size 2.3 -> 16 at the shift; the return shows as a 5-7 point coverage loss with small sets (one-day event).
BMA over half-lives: short-memory weight 0.06 -> 0.68 on day 14, back to the frozen counter by the return (hedges the return
drop away; spell 66-69 vs frozen 61); per-object BMA +3 in the spell, still below the 3 d base (per-object weights move
too little on 1-3 sightings a day). LLM channels (Qwen, one household, ~70 q per test): verbalized confidence carries no
signal; sample agreement noticed the break in one test (+0.195) and not the other (+0.069) — low power, stated as such.
Three bugs caught on the first household: a mixture martingale that decays to 1e-5 and can never fire (-> CUSUM e-detector),
repeated questions double-counted as evidence (-> de-dup; and fixed at the source in the bank), a tokenizer quirk that hid
the MCQ letter mass. Degenerate checks to the digit on every base.

## 16:45 note from the workshop session (dynamic-home-eqa-5a) — fix before any LLM arm runs on a 32-day bank
patrol/llm.py clock() renders sighting times as "Fri 10:40" with no day index; on a multi-week bank the model cannot tell
which week a sighting is from (it reasoned a sighting was "in the future"). Their worktree uses "day 18 Fri 10:40";
port that to main before running LLM arms on the frozen regime. vLLM is back with --max-num-seqs 64 (restart script:
dynamic_home_eqa_fm/results/fm_memory/server/restart_vllm_64.sh) — the old cap of 8 was the overnight throughput limit.

## 17:05 reviewer feedback -> today's plan (Oliver: all of it today)
Critical read: (1) the return, not the first drop, is the memory result — but it is a SURFACE (memory length x spell length),
not a point: the never-forgets learner wins the return only because 14 lead days > 10 sick days. (2) Partial shift with
affected/unaffected labels is the untested question 2; granularity = per person (per-object streams are too thin).
(3) A planning cost from the logged distributions (places searched; ask-or-search policy) closes the loop cheaply.
(4) Our hedge already is fixed-share and moves fast; the suspicious bit is its weights draining to the never-forgets
timetable on days 19-23 while the 3-day one is 10-15 points better -> scoring loss / switching rate / per-person weights.
Launched 17:00 (classical, 4 workers each): sick5_all, sick10_all_hl (7 d agents on the frozen banks), sick20_all (42 days),
sick10_partial (resident_1 sick, everyone's things asked), sick10_all_natural (weekends + random events). Research agent:
fixed-share scoring, planning metric from uq logs, per-person detection + told-oracle on sick10_partial.

## 17:35 research agent: hedge fixed (clean positive result) and planning metric done
Hedge root cause: weights were scored on each counter's predictive log-loss (rewards calibration, not hits) so the smoother
never-forgets counter out-scored the sharper 1-day one on days 19-23. Scored on hits (`--score hit`, switching rate 0.02):
spell 74.4±5.0 (sick10_all) / 77.9±6.4 (owner) vs best single memory 76.9 / 80.2 and frozen 60.9 / 64.5; return 78.5 / 76.8
vs frozen 79.7 / 79.0; it re-snaps to the long memory on day 24 (short weight 0.79 -> 0.18 the same day). Old hedge: 66.0 / 71.1.
So the hedge is within ~2.5 points of the best memory inside the spell AND within ~1-2 of the never-forgets learner on the
return — the near-best-of-both result, stated with its 0.3-0.5 pt shortfall of the 2-point bar on the full spell. Higher
switching rates were strictly worse (fixed-share pulls toward uniform). Per-person grouping helps only where there is a split.
Planning metric (uq/planning/): places searched in probability order, or ask at cost c when not confident (top_prob >= 0.6
or set size <= 3). Sick-stage total cost per question at c=2: e-detector+reset 2.04 vs its base 2.14; hedge 2.39 vs frozen
3.28; lead-stage cost unchanged (no price on plain days). Conformal: its set size only balloons on the first shift day, so
gating on it does not cut cost (2.98 -> 3.71) — set size is calibrated to coverage, not to "is my guess wrong today":
an honest negative. Last seen: always confident (top_prob ~0.98), never asks, pays 12-14 places per bad guess.
Also caught before use: DiscountedTimetable.discount() ignored its objects= filter (P4) — the per-person reset needed it.

## 17:45 partial shift (sick10_partial: resident_1 sick, questions about everyone's things) — affected vs unaffected
Accuracy ± sd across hh / mean stated confidence, lead | sick | return, affected (the sick person's objects) vs unaffected:
  frozen timetable   aff 72±9/.52 | 64±20/.56 | 78±9/.63    una 67±7/.49 | 78±9/.63 | 79±12/.66
  timetable 3 d      aff 72±9/.41 | 76±7/.39  | 70±7/.39    una 68±9/.39 | 78±8/.39 | 76±11/.40
  most freq 3 d      aff 55/.43   | 68/.46    | 46/.41      una 41/.39   | 43/.40   | 46/.40
  last seen          aff 43/.98   | 59/.98    | 47/.98      una 35/.98   | 29/.98   | 36/.98
The break is confined to the affected group (frozen timetable: affected 72 -> 64, unaffected 67 -> 78); the 3-day learner
re-learns the affected group inside the spell (76) and breaks on them at the return (70) while the unaffected group stays
put (78 -> 76). But NO classical agent's stated confidence tells the groups apart: the frozen timetable's confidence on the
affected objects goes UP during the spell (0.52 -> 0.56) as it does on the unaffected ones (0.49 -> 0.63). So "which beliefs
should become less trusted?" is not answered by the learners' own confidence; it needs a detector at the person level —
the research agent's per-person e-detector and the told-oracle reset run on these banks now. Question mix note: the sick
person's rest-day activities generate more questions about their things (sick stage: 1688 affected vs 712 unaffected).

## 18:10 partial shift — per-person detection (research agent, uq/regime/sick10_partial)
Per-person CUSUM e-detector (one per resident, resetting only that resident's bins): every fire in 10 households is on the
sick resident; the other resident's detector fires 0/10 ever; catches the sick resident's break on day 14 in 4/10 (global 5/10).
Per-person reset leaves the unaffected resident bit-for-bit identical to the frozen baseline (accuracy 75.6/74.2, confidence
.36/.38); the GLOBAL reset does not cost them accuracy (75.6 -> 76.2) but leaks uncertainty (confidence .36 -> .32 in the spell,
.38 -> .35 on the return). Global conformal leaks the same way: the unaffected resident's set balloons 2.6 -> 9.7 -> 12.2 on
days 14-15 although nothing in their routine changed (shared threshold). Told-oracle reset (resident_1 on days 14 and 24):
resident_1 72.1 | 82.2 | 73.2 vs detected 79.4 | 70.4 — detection lag costs ~3 points. So: "which beliefs to distrust" is
answered at the person level by a per-person detector, not by any learner's own confidence; global mechanisms are safe
on accuracy but spread doubt to people whose routine did not change.

## 18:20 planning metric, ask-rate-matched control (uq/planning/*_matched{25,50}.md) — a real correction
At equal lead-day ask rates (25% / 50%), only the detector + targeted reset (mart_tt72) is cheaper on sick days than on its
own lead days (sick10_all 3.31 -> 2.55 at 25%, 2.67 -> 2.25 at 50%; owner 2.92 -> 2.48, 2.40 -> 2.30). The hedge does NOT
(3.15 -> 3.55): its raw-tau win was the confidence-scale confound (it already asked 68% of the time on lead days). Conformal
gating and the plain 3-day counter also fail the matched test. So the planning claim narrows to: a detector-triggered reset
converts noticing into fewer wasted searches; a lower confidence scale alone does not. Story page text to be corrected.

## 18:30 memory x spell surface complete (sick5_all / sick10_all_hl / sick20_all; story page v4)
Timetable, return-day drop by memory length x spell length:   5 d spell: 1 d -28, 3 d -11, 7 d +10, never +18
                                                              10 d spell: 1 d -34, 3 d -34, 7 d -17, never +6
                                                              20 d spell: 1 d -35, 3 d -42, 7 d -44, never -11
Spell accuracy: 5 d: 68/59/55/51; 10 d: 77/72/66/61; 20 d: 82/80/77/69 (1 d / 3 d / 7 d / never).
Reading: the cost of forgetting (return drop) grows with spell length for every finite memory; the cost of remembering
(spell accuracy gap to the 1-day learner) shrinks as the spell gets long enough to re-teach even a long memory; the
never-forgets learner's return advantage disappears once the spell (20 d) exceeds the lead (14 d): -11. A law of the
testbench, not a single point — the reviewer's "return is your result" made quantitative.
- 18:40 per-person conformal (ocpperson_tt): the unaffected resident's collateral set growth shrinks (day 14: 9.7 -> 6.7;
  day 15: 12.2 -> 8.9) but does not vanish like the per-person reset did — a per-person threshold calibrates on that
  person's ~110 questions only, so its lead-stage sets are already larger (2.6 -> 4.7) from small-sample calibration,
  not contamination. Honest partial fix, logged. uq/REPORT.md (268 lines) now carries all four of today's results.

## 21:15 evening summary and the overnight LLM-strategy chain
Direction (Oliver, ~19:40): the paper is about whether current LLM-based memory / reasoning / planning strategies cope
with a temporary routine shift (recognise it, use memory through it, recover on the return) and how their confidence
calibration compares with trivial learners; classical learners are yardsticks only; in-house methods out of scope.
Tonight: research agent (dynamic-home-eqa-0a) built retrieval memory (Mem0 / A-Mem style), long-context (whole log),
error-driven reflection (Reflexion-style) and a daily "has the routine changed?" self-report into llm.py (on the workshop
worktree's llm.py with dated timestamps); KnowNo-style conformal sets come post-hoc from the logged token probabilities.
Smoke test clean. Throughput under the shared server is ~15 s per call, so the wide runs are an unattended chain from
23:30 (uq/llm_strategies/run_chain.sh; progress uq/llm_strategies/chain_progress.log; expectations EXPECTATIONS.md;
cold read STATUS.md): sick10_all then sick10_partial, not-told then told, hh_s0-s2 x retrieval/long-context/reflection,
then confidence channels + conformal on retrieval for a 14-day subset. The workshop session (dynamic-home-eqa-5a) runs
rolling buffer + nightly per-object table, not-told then told, on sick10_partial hh_s0-s2 (results in its worktree,
dynamic_home_eqa_fm/results/fm_memory/partial*/), landing ~22:45-23:30.
Morning read: chain_progress.log verdicts, STATUS.md, then per strategy: the four-stage shape vs timetable-3d / last
seen, the self-report as a detector, calibration (ECE) of each confidence channel vs the timetable, ask-or-search cost,
and on the partial shift the sick person's things vs everyone else's — the shared-memory slot on the story page fills
from those numbers.
