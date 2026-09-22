# Overnight status (driver: session dynamic-home-eqa-37, tmux `oliver1`)

## MORNING SUMMARY (written 08:45; the chronological log follows below)

**What ran.** Protocol frozen at 01:25 (`configs/frozen_2026-09-21.yaml`): nightly patrol 03:00 + found-it feedback 10 min after
each question, activity questions, 64/day. Classical agents on all 20 held-out households; naive LLM on 8 (s10-14, s18, s19, s25);
hypothesis mixture told + not-told on 6 (s10, s11, s14, s18, s19, s25), told on s12/s13 still running at 08:45. $0 spent.

**Three bugs caught and fixed overnight before they cost the night** (problems_found #17-#23): (1) the mixture collapsed to one
document the moment a revision landed — a "fair entry" rule in longleaf_mixture gave every new document its replayed likelihood
on the evidence it was written from; fixed so documents earn weight forward from birth, plus likelihood floor 1e-3; (2) documents
carried no recency, so still objects were mispredicted at in-use spots — recency term added; (3) told = not-told: message
documents enter at ~0.02 and the shared-bin evidence blend makes every document answer alike — structural, documented, not fixable
tonight (v5 parity test confirmed it). Final run v4: ESS 5-16 all week on every arm, no collapse, ~12 revisions per arm.

**The result (driver/weekend_table_0650_told_final.md; findings.md point 3).** Moved-since-round questions, each household's own
shift days vs plain days, coverage-matched: the timetable counter learns the routine best (47%) and breaks hardest on shift days
(-15; its confident half -23) at unchanged confidence — confident and worse. The mixture learns less (39%; on s19 33 vs 62),
breaks half as much (-7; confident half -5), and its confident answers are the best of any agent on shift days (41 vs 37 vs
naive 28). No agent lowers its mean confidence on shift days (mixture 0.29 -> 0.30). Naive LLM: 31 -> 23 at 0.81-0.83, 93%
identical told/not-told. told = not-told for the mixture on all four complete pairs (99-100% identical answers).

**What this means for the goal.** "Keeps accuracy on what it is confident about" holds relatively; "loses confidence when the
routine shifts" is not shown by any agent under this protocol; the told message has no effect. Root cause is one trade-off:
the evidence blend that makes documents LEARN from feedback is what makes them AGREE. Way out (open_questions #12): per-document
conditional statistics (a document's bins built only from the days/hours its regime claims), so documents keep learning yet can
disagree about which regime is active. The honest-empty-bin timetable (tuning #46) shows a counter can already produce the
confidence shape at a cost in accuracy. s12 is a disclosed counter-example (its shift days are easier for every agent).

**Where things are.** Report: f1 assembles report.md ~08:45 from make_report.py + findings.md; Ledger artifact
https://claude.ai/artifact/KJPMaPPbgv4UmeVakrDSTA (v11 by me at 05:05, f1 republishes over it); Shift Baselines
https://claude.ai/artifact/PMxnzQYbCmFtAFm22hPb4G (oliver-7f, needs the fb-density labels + tag before it can show fb lines).
Logs: heldout_fb/{classical,llm,hyp/logs,hyp/study}; earlier partial mixture runs kept as hyp_v1_no_blend, hyp_v2_hindsight_entry,
hyp_v3_floor002, hyp_v5_message_parity. Driver tools: driver/check_fb.py (tables + red flags + story checks), driver/weekend_table.py
(coverage-matched shift table), driver/build_ledger.sh, driver/watch_fb.sh. Nothing deleted anywhere.

---

Read this first in the morning. Newest entry at the bottom. Times are PDT.

Roles: `oliver-f1` (session dc78…) owns the confidence-shift study, heldout*/ and the Longleaf Ledger.
`oliver-7f` (session c8b4…) owns followon/ and Shift Baselines (runbook: followon/RUNBOOK.md).
This session monitors, checks shapes, and records here; it writes only under this file and its own dirs.

## 00:38 — takeover
- Running: naive_p8 (naive LLM, 8 h patrol, hh_s10-14), arms_p8 (5 told mixture arms at 8 h), naive_fb
  (naive LLM on the new nightly + found-it feedback protocol, heldout_fb/). p8 not-told replay cancelled by f1 00:36.
- Crashed: all 10 heldout_fb mixture arms at 00:37 (converted banks banks/patrol/*_t03_bank.jsonl missing). f1 saw it 00:38.
- Concern: heldout_fb classical shape (report_classical/summary.md) does not meet the criteria — Wed->Fri rise
  +4..7, weekend drop +4..7 on working households, flat per-day accuracy. Raised with f1; awaiting its analysis.
- 7f handoff received: nothing of theirs running; waiting on heldout_p8/hyp/logs for the 8 h mixture lines.
  Top open problems: detector never fires (a,b: per-object surprise / residents' presence not tried),
  told reset hits unaffected as hard as affected (strength<1 never plotted), conformal sets 7-30 spots.

## 00:43 — handoffs complete, monitoring armed
- f1 handoff: feedback protocol frozen (configs/frozen_2026-09-21.yaml); classical done on 0-9 and 10-29; the
  story lives in the "moved since the 03:00 round" split (timetable 12/29/42 -> 31/37 -> 55, MF 7/15/28 -> 16/20 -> 29
  on 20 hh); pooled is flat by construction. Told arms hh_s10-14 restarted 00:38 (symlinks fixed), not-told replays after.
- Driver tools: driver/check_fb.py (moved/still tables + red flags), driver/watch_fb.sh (Monitor, re-armed every 30 min).
- Expectations being checked (from f1): naive tracks last seen (moved ~15-25% at ~0.8 conf); mixture accuracy on moved
  rises like the timetable, top_prob lower on Sat/Sun and on moved questions, coverage@0.7 dips on Sat/Sun, told != not
  told after each household's first message day (s13 Wed, s14 Thu, s11 Fri, s10/s12 Sat). Red flags: ESS 1.0 all day,
  exit != 0, repeated n_valid 0 revisions, naive >90% at one confidence AND above last seen.
- Open shape question sent to f1: on hh_s10-14 there is no weekend drop on the moved split; the decline is on the still
  split (counter dilution). Awaiting f1's answer.
- 00:42 check: naive Wed (3 hh) moved 8% @0.88 / still 99% @0.91; mixture told Wed moved 9% @0.43 / still 89% @0.53;
  hh_s10 told 0 answers after 5 min (watch). The 5 nottold tracebacks are stale (00:37 crash), will be overwritten.

## 00:50 — story confirmed on the classical side; mixture expectation fixed
- f1's answer: the cut is the moved-since-round half, each household's OWN shift days vs its plain days, Thu-Tue.
  20 hh: timetable plain 45% -> shift 35% (15/20 households down); last seen flat 18/17; MF 25/20.
  Verified on the 8 LLM households (s10-14 + s18,s19,s25) with driver/check_fb.py: timetable 46% -> 35% at the SAME
  confidence 0.43 (confident and worse = the story); last seen 18/19 @0.98; MF 22/20; periodic 24/23; Perpetua* 24/28.
  Only the timetable breaks; MF barely. The still-half erosion over the week is counter dilution from feedback
  sightings at in-use spots (not the story; a document model should not have it).
- f1 is adding working households hh_s18, s19, s25 to the LLM set (4/5 of s10-14 are retired homes) — elicitation ~1 h,
  arms after; disclosed in the report. The 20-hh classical set stays the unbiased one.
- MIXTURE EXPECTATION (act if it fails by Fri on a household): on moved questions >=35% on plain days after Wed (last
  seen ~15%), LOWER accuracy AND LOWER confidence on its shift days than plain days; still questions >=85% all week;
  told recovers the day after the first message faster than not-told. Red flags -> pause that arm (exact cmdline),
  read revisions/*.json, message f1: below last seen on moved Thu-Fri; still <80%; conf on moved not below still; ESS 1.0 a day.

## 00:52 — in command (Oliver: "flag and use your best judgement ... you're the one in command; also maintain the artifact")
Ledger republished (v8) from ledger_live_fb.html via driver/build_ledger.sh "<status>" + Artifact url KJPMaPPbgv4UmeVakrDSTA;
now shows the feedback protocol (2 h / 8 h superseded, kept on disk as ledger_live.html).

### How I look for red flags (checked at every day boundary, every 30 min at least; driver/check_fb.py --flags-only)
Mechanical (the run is broken):
  - arm process gone or exit != 0 in arms_fb.log / Traceback in arm_s*_*.log (stale ones marked);
  - stall: process alive but live.jsonl untouched > 40 min (one revision call is 7-18 min under load);
  - two consecutive revisions with n_valid 0; a not-told arm with zero revisions through Sunday.
Statistical (the run is producing the wrong shape; against f1's expectation):
  - ESS <= 1.05 for a whole day (one document took over);
  - still-object accuracy < 80% on a completed day (erosion the mixture should not have);
  - confidence on moved questions >= on still questions on a completed day (no uncertainty signal);
  - moved accuracy on Thu/Fri below last seen's for that household (not learning);
  - moved accuracy > 80% on any day (implausible; would mean the feedback sighting leaks before the question);
  - told and not-told IDENTICAL on >= 32 questions after the household's first message day;
  - naive LLM: > 90% of answers at one confidence value (and above last seen = suspicious).
Judgement calls: per-household plain-vs-shift on the moved half by Friday (mixture >= 35% plain, lower on shift, lower conf on shift);
told recovers faster than not-told the day after the first message. Any flag -> pause that arm (exact cmdline), read revisions/*.json,
message f1; if f1 is gone, decide and record here.

## 01:02 — RED FLAG: hh_s12 told collapses to the revised document at entry
- live.jsonl: ESS 6.4-7.6 for Wed q1-50; revision_1 (claim, n_valid 3) lands at q51; new doc p_4c7a weight 0 -> 1.000 at
  q52 (instant, not gradual); ESS 1.0 for the rest of Wed and 1.05-1.4 on all 60 Thu answers (p_4c7a top 60/60).
  Thu acc 47%, top_prob 0.3-0.57. From here the "confidence" is one document's own spread — the mixture mechanism is gone.
- Likely cause: the revised document is written from Wednesday's feedback sightings (its text cites "four sightings each")
  and is then scored on that same evidence -> hindsight document wins every time. Secondary: LL temper 0.03 was set for
  35-listing patrol passes; a feedback row is a single listing, so 50 feedback rows weigh 50x what one pass did.
- s13/s14 revised at q1 (no evidence yet) -> no jump, but ESS only 2.0-4.5 from the start; s11 ESS 8.5, no revision yet.
- Action: could NOT pause the arm (this session's auto-mode classifier denies killing processes). Messaged f1 with the
  diagnosis and two candidate fixes (score a new doc forward-only / capped entry share; per-listing temper for feedback rows).
- Added goal-level STORY CHECKS to driver/check_fb.py (learning on moved, not flat, lower acc AND conf on own shift
  days, selective acc@0.7 holds while coverage dips, no rise on shift days, still half >= 80, not a copy of last seen /
  naive, confidence moves over the week, told != not told after the message and recovers faster, pooled: mixture does
  not just move with the timetable). Verdicts appear as days complete.

## 01:03 — f1 killed all fb told arms at 01:01 (exit 143) and is relaunching
- Not because of my flag (message still queued): f1 added a time-of-day evidence blend to the document belief
  (TIMETABLE_EVIDENCE_BLEND / FALLBACK_BIN_H in beliefs/timetable_hypothesis.py: once the robot has seen an object in the
  same hour bin, the document's claim is blended with those sightings) and relaunches with it. Old outputs moved to
  heldout_fb/hyp_v1_no_blend/ (nothing deleted). The auto-started not-told arms were killed too.
- My s12 collapse finding stands regardless of the blend; waiting for f1's answer on the entry rule / temper.

## 01:08 — f1's fix and new expectation (arms restarted 01:02)
Env: TIMETABLE_FALLBACK_BIN_H=2, TIMETABLE_EVIDENCE_BLEND=0.7 (once seen in the query's 2 h bin: 0.7*bin stats + 0.3*document),
MIN_COUNT=1, HYPOTHESIS_DECAY=0.998 (~1 day memory), HYPOTHESIS_ENTRY=share_cap (new doc enters at exactly 1/(n+1)),
LONGLEAF_SCHEDULED_DAYS=1..7 (review at every day's first question, both arms; told also sees messages). TEMPER stays 0.03.
Fixed-arm check by f1 on s12/s10: mixture tracks the timetable on moved questions, ESS 4-9.
NEW EXPECTATION hh_s12 Thu: mixture moved >= 25% (timetable 29), ESS >= 3 all day, no single document > 0.7 for a whole day.
Checker now flags mean ESS < 3 on a completed day and a document > 0.7 all day. Killing stays with f1 (I message, it kills).

## 01:20 — throughput check (arms at 0 answers 17 min after relaunch: not a bug)
vLLM: 8 running + 7 waiting (naive_fb 6 threads + 5 fb reviews + 3 p8 arms + elicitation). At ~166 tok/s aggregate a 40k-token
review takes ~30 min when the server is saturated. Budget: 7 scheduled reviews per arm -> told arms done ~04:00-05:00,
not-told replays (pre-message reviews hit the cache) ~+1-2 h, then hh_s18/19/25 ~+3 h. Tight for 10:00 but feasible.
Escalation deadline for "first answer" moved to 01:50. p8 arms (fallback, day 3-7) left running on f1's instruction.

## 01:24 — RED FLAG on the relaunched run: hh_s11 told collapses at q1 to a NEW review document
ESS 1.07-1.1 all Wednesday, max weight 0.94-0.97; dominant doc p_f2c3 is one of the 3 docs written by the day-1 scheduled
review, at 0.967 on the very first answer after entry (share_cap should give 1/13). Old run, same evidence, q1: ESS 8.22.
So the entry cap does not hold, or a new document is scored on the evidence it was written from. Sent to f1 with a
suggested test (dump weights before/after the revision). Recommended pausing s11 and fixing before the other four
arms finish their reviews. Wed s11 told: moved 11% @0.32, still 92% @0.40, all 44% (last seen 55%, timetable 47%).

## 01:28 — mechanism of the collapse (sent to f1)
The scheduled review fires on the first EVIDENCE event of the day = first room listing of the 03:00 round; the new doc
enters at 1/14 and is then scored on the other 8 room listings of that round with likelihood floor 1e-12 (27.6 nats per
"impossible" object x temper 0.03). A doc written from the walkthrough predicts the rest spots exactly -> 0.07 -> 0.967
before q1. Levers proposed: raise the floor to ~0.02-0.05; fire the review at the day's first QUESTION; birth grace.

## 01:32 — which households carry the story (classical, moved half, plain vs own shift days, timetable acc)
Breaks (>= 8 pts): s10 44->32, s11 43->33, s14 46->35, s15 61->36, s16 51->37, s18 50->29, s19 62->32, s22 48->31, s24 54->42,
s25 44->29, s26 41->29, s27 44->36, s28 56->41, s29 45->27 (14/20). Does NOT: s12 37->51 (reverse), s13 47->40 (weak),
s17 39->36, s20 35->34, s21 31->38 (reverse), s23 29->36 (reverse).
LLM set: s12 is the wrong household for the headline (reverse shift; naive plain 25 -> shift 39 there too); s13 weak.
Strongest: s19 (-30), s18 (-21), s25 (-15), s10 (-12), s14 (-11), s11 (-10). Suggested to f1: run s18/s19/s25 before
s12/s13 in the relaunch, keep s12 as a disclosed counter-example rather than in the pooled headline.
Naive told finished on s10-12: moved plain 23% @0.79 vs shift 29% @0.81 pooled (s10 27->17 with conf up; s11/s12 reverse).

## 01:36 — relaunch v3 (f1): likelihood floor raised, three arms first
Previous partial run moved to heldout_fb/hyp_v2_hindsight_entry/. New env adds HYPOTHESIS_MIN_LIKELIHOOD=0.02 (a miss costs
3.9 nats, not 27.6) and LONGLEAF_SCHEDULED_DAYS=2..7 (no day-1 review; reviews at each later day's first event). Told arms
running: hh_s10, hh_s11, hh_s14 (the three from the original five whose classical shape breaks). Checker expectation unchanged:
ESS >= 3, no doc > 0.7 all day, moved >= timetable-ish, conf lower on moved and on shift days.
- f1's root cause (01:38): longleaf_mixture._rebuild overrode the parent's entry rule with a "fair entry" = the new doc's
  untempered log-likelihood replayed over the whole evidence log -> a doc written from that evidence enters on top by
  construction. Fixed (under share/share_cap the override now defers to the parent; documents earn weight forward from
  birth) + floor 0.02. Verified on cached s11 day-1 review: ESS 6.7-7.2 through Wed (was 1.1).
  Order: told s10, s14, s11 now -> s12, s13 -> not-told per group -> s18/19/25 auto-start when libraries land. s12 = counter-example.

## 01:44 — v3 first Wednesday: healthy
s10 told Wed: ESS 8.2, top doc 0.17, 1 revision; s14: ESS 7.4, top 0.17, 1 revision; s11 at 29 answers (in a revision), ESS 6.3.
Pooled Wed mixture: moved 15% @0.44, still 89% @0.51, all 54% (last seen 54, timetable 51) — at recency's level on day 1
as expected; confidence already lower on moved than still. No flags. Ledger republished (v9).

## 02:03 — s14 Thursday (guest evening, first message day) and a watch item on the mixture's confidence range
s14 told Thu: ESS 5.7, 2 revisions (message + scheduled), moved 22% @0.36, still 70% @0.49 (flag: <80; the 8 still misses are
"usual place" answers (razor->sink, phone->coffee table, dog food->pantry) against a 03:00 sighting elsewhere: documents carry
no recency and the bin blend only applies once the object was seen in the query's 2 h bin; all at top_prob 0.23-0.46).
WATCH ITEM (all three arms, Wed-Thu): the mixture's top_prob lives in 0.2-0.55 — coverage@0.7 is 0-5% (30% on s14 Thu still),
so at the paper's 0.7 threshold the mixture line would be empty. At 0.5: coverage 24-77%, selective accuracy 100% on still and
0% on moved (confident = "it's at its rest spot", wrong whenever it moved). Agreement confidence is 0.97-1.0 everywhere (every
document answers the rest spot) so it carries no signal. The moved-vs-still top_prob gap is ~0.1 and consistent; whether the
range opens up as bins get covered (blend from Thu on) decides the figure. Told f1; report at 0.5 as well as 0.7.
Checker fix: "rise on a shift day" now compares with the plain-day level after Wed (Wed->Thu is the learning step).

## 02:05 — relaunch v4 (f1, 02:02): recency in documents
v3 moved to heldout_fb/hyp_v3_floor002/. New env: TIMETABLE_RECENCY_HALF_LIFE_H=4 (a document's prediction leans on the last
sighting with a 4 h half-life — addresses the still-half misses) and HYPOTHESIS_MIN_LIKELIHOOD=1e-3 (was 0.02 in v3; 6.9 nats
per miss). Same three told arms (s10, s14, s11). Cost: v3's Wed/Thu (~30 min) discarded; each relaunch costs ~30-45 min of the
night. Budget check at 02:05: told s10/s11/s14 ~04:00, s12/s13 ~05:30, not-told replays ~06:30, s18/19/25 ~08:30-09:30. Tight.
- f1 (02:08): the 0.02 floor I suggested was too blunt (a miss capped at 0.1 nats after tempering -> weights never moved;
  fixed-mixture late-week moved accuracy collapsed, s12 Tue 83 -> 14). Sweep 1e-12/1e-4/1e-3 identical (ESS 4-8 with the
  entry fix alone), 1e-2 hurts -> 1e-3. Recency term: fixed-arm s14 still Wed 82 -> 96, s12 Thu 63 -> 66, moved unchanged.
  Report will add coverage-matched selective accuracy (every agent at 25/50/75% coverage) and a risk-coverage curve for the
  mixture instead of a single 0.7 threshold. Expectation Thu: ESS 4-8, moved >= timetable (~24-29%), still >= 85%, conf moved < still by ~0.1.

## 02:13 — v4 first Wednesday (s11): still half fixed, confidence even lower
s11 told Wed: ESS 6.6, top 0.21; moved 18% @0.21, still 92% @0.27 (v3: 85% @0.54), all 48%. Recency term works for accuracy,
but top_prob is now ~0.2-0.3 everywhere (v3 0.35-0.55): the mixture is badly UNDER-confident in stated terms (92% right at 0.27).
v5 note, not a restart: the mixture needs a calibration map (or a sharper dist, e.g. temperature on the blend) before its
stated confidence can be compared with the naive LLM's 0.8-0.9; the coverage-matched view is unaffected (ranking only).

## 02:15 — naive LLM finished on hh_s10-14 (4173 calls, 307 cached, 8.0 h server time, $0)
Expectation (a) "naive tracks last seen, flat, confident" — holds with one nuance: moved half 18/19/34/15/27/27/36 Wed..Tue
(last seen 16/12/25/12/21/18/15; timetable 16/28/31/33/40/51/55): it does use the feedback sightings a little (+10 over last seen
by Tue) but nowhere near the timetable; still half 83-94%. Confidence 0.78-0.91 on every day, 47% of answers at 0.95, 27% at 0.85;
on moved questions it says 0.83 and is right 15-36% -> overconfident, exactly the counter-example the story needs.
Told vs not-told: 93% identical answers; the message barely changes the naive agent (as in the overnight study).
Pooled moved half Thu-Tue, own shift days: see line below.
naive told: moved Thu-Tue plain 27%@0.80(n=433) vs shift 26%@0.82(n=577)

## 02:45 — all six told arms have a clean Wednesday (v4)
ESS on Wed: s10 8.8, s11 6.6, s14 7.9, s18 5.5, s25 7.7, s19 (below); top doc <= 0.22 everywhere; still half 91-97%;
moved 7-21% (recency level, as expected on day 1); conf moved < still on 5/6 (s14 inverted 0.29 vs 0.24).
s11 through Thu: moved 19% (timetable 27, last seen 4), still 82%, ESS 7.1. Naive told finished on s10-14, running on s18/19/25.
No flags. Next: Thursday/Friday boundaries decide "learns" and "breaks".

## 03:08 — s14 Thursday (v4): moved on track, still half 70% again — a property, not a bug
s14 told Thu: ESS 8.0, moved 24% (= timetable 24, last seen 19), still 70% (timetable ALSO 70%, last seen 100%), conf 0.32/0.32.
The 8 still misses are routine predictions at in-use spots (razor -> sink at 07:48 "morning routine", phone -> coffee table,
dog food -> pantry) while the object was in fact still where the 03:00 round saw it; the recency term (4 h half-life) has faded
by 07:48. The timetable makes the same mistakes; the mixture states 0.19-0.32 on them, so they drop out at any selective
threshold. v5 note: the documents predict routine, not recency — that is the design; the cost is the still half on mornings.
The moved-vs-still confidence gap is absent on s14 (0.32 vs 0.32 Thu) but present on s10/s11/s18/s19/s25 — watch by Fri.

## 03:22 — f1 status: Ledger v10, findings.md draft, llm_usage.py, --confidence monitored; open concern on the shift signal
f1's read of v4 so far matches mine: mixture tracks the timetable on the moved half (Wed 8-27, Thu 19-25, Fri 26-30%) at
top_prob 0.22-0.33, ESS 7-10, but its mean confidence is NOT lower on a household's own shift days (s14 Thu 0.33 vs Wed 0.30;
s11 Fri 0.30 vs Thu 0.23) — confidence rises through the week as bins get covered, which masks any shift dip.
Plan for the Saturday/Sunday boundaries (s10/s18/s19/s25 weekend shifts, ~04:00-05:00): judge the claim the way the report
will — coverage-matched selective accuracy (25/50/75%) on the moved half, shift days vs plain days, mixture vs timetable.
If the mixture's selective accuracy holds on shift days while the timetable's drops, the story stands even with a flat mean
confidence; if both drop alike, the mixture's uncertainty carries no shift information and that is the honest finding.

## 03:27 — f1 found why told == not-told and launched a v5 side run (message parity)
Message-triggered documents enter at 1/(n+1) of the top weight (0.01-0.02 on s14 Thu) and the tempered weights never lift
them: the told arm effectively ignores its message. v5: HYPOTHESIS_MESSAGE_ENTRY=parity (documents written for the day's message
enter level with the leading document; other triggers unchanged), told-only on s14 and s11 into heldout_fb/hyp_v5_message_parity/
(v4 study + its not-told chain untouched; code inert unless the env var is set). Cost: 2 more arms on a saturated server;
pace ~45 min per simulated day per arm -> v4 group-a told ends ~06:30, its not-told ~09:00-09:30; group b (s12/s13) not-told
will not make 10:00 (told-only reported). tuning_log #42-44 record the post-freeze checks.
DECISION POINT ~04:30 (when v5 s14 reaches Fri): if parity makes told differ from not-told and recover faster, the paper's
told/not-told contrast should come from v5, and the v4 not-told chain on group a may be the wrong thing to spend 06:30-09:30 on.
- f1 (03:32): the not-told arm never fires the message trigger, so the v4 not-told replay IS the v5 not-told arm (same code
  path, same cache). The group-a not-told chain is therefore kept: it is the not-told half of the v5 contrast for s11/s14;
  v4 told becomes a third line ("told, message ignored"). Plan: keep everything; at ~04:30, if v5 s14 hedges on the message
  day and recovers (moved acc >= v4), add v5 told for s10 (days 1-3 replay from cache) and s18 once naive ends; group b told-only.
  If v5 shows nothing, stop v5 and the v4 pair stands. I deliver the s14 v4-vs-v5 comparison and the weekend table at ~04:30.

## 03:35 — s11 Saturday; "moves together" note
s11 told Sat: ESS 8.8, moved 39% (timetable 42, last seen 9), still 84%, conf moved < still every day (0.27 vs 0.38 Sat).
s11's flags (Sat above its plain level) reflect the household: retired home, only Thu/Mon are plain, its classical break comes
from Sun/Tue. Not actionable.
NOTE (Oliver's "everything moves together" shape): pooled day-to-day deltas of all-question accuracy, mixture [8,-11,16] vs
timetable [11,-12,16] vs naive [2,-6,2]. The mixture moves almost exactly with the timetable — expected, since the evidence
blend makes each document 70% the robot's own 2 h-bin statistics once a bin is covered. So "mixture tracks the timetable on the
moved half" is partly by construction; the claim that can distinguish them is confidence behaviour on shift days and the
told/not-told contrast, nothing else. This goes into the weekend table and findings.md.

## 03:45 — v5 stopped: told = not-told is STRUCTURAL under this protocol (f1, problems_found #23, open_questions #12)
With parity entry the message documents held 0.10-0.11 each on s14 Thu (v4: 0.02) and every answer and confidence was identical
to v4. Cause: each document predicts 0.7 x the shared hour-bin statistics + 0.3 x its own claims, and the bins pool all days, so
Wednesday's sightings outvote "board game on the coffee table" inside the guest document itself — the library cannot disagree
with its own statistics. Pseudo-count blend (tuning #45) sharper, not better. The v4 chain stands as the paper's pair.
For Oliver (design, not tonight): the blend that makes documents LEARN (v1 without it: mixture worse than the counter, no
learning) is the same thing that makes them AGREE (v4/v5: no disagreement, no told effect, moves with the timetable). The way
out is per-document CONDITIONAL statistics: a document's bins are built only from the days/hours its regime claims to cover
(guest document <- guest evenings; weekend document <- weekend days), so documents keep learning from feedback but can
disagree about which regime is active — that is where the "told" message and the shift-day uncertainty would live.

## 03:52 — f1: findings.md point 3 = learn-vs-agree; extra classical line "timetable wd/we, honest empty bin"
Calendar-aware timetable with separate weekend bins and an honest empty bin (no sighting -> last-seen at conf 0.3, not
whole-history most-frequent at full Dirichlet confidence; tuning #46, logs heldout_fb/classical_extra/): the one agent whose
coverage and confidence FALL on the weekend (moved coverage@0.5 3/7/12 -> 2/5 -> 17/25%; conf .33/.34/.37 -> .32/.34 -> .37/.40),
paying with Saturday moved accuracy 14 vs 31 for the frozen timetable (whose weekday bins are half right on a Saturday).
Post-freeze extra line, not a replacement. This is the cheap agent that shows the wanted confidence shape; worth a sentence
for Oliver: a counter with an honest "I have not seen this situation" answer already does what the story asks on confidence.

## 04:05 — naive finished on all 8 households; coverage-matched table ready (driver/weekend_table.py), early read
Moved half, Thu-Tue, own shift vs plain days, days completed by the mixture so far (mostly weekday shifts; s10/s18/s19/s25
weekends not in yet). Pooled n = 183 plain / 221 shift:
| agent | plain acc / conf / sel@25|50|75 | shift | d acc | d sel@50 |
| mixture told | 30 / 0.28 / 39|38|33 | 31 / 0.29 / 38|41|33 | +1 | +3 |
| timetable    | 34 / 0.39 / 43|46|41 | 29 / 0.41 / 36|37|31 | -4 | -8 |
| most frequent| 22 / 0.43 / 24|25|28 | 20 / 0.45 / 29|19|20 | -2 | -6 |
| last seen    | 16 / 0.98 / 41|23|19 | 19 / 0.98 / 18|19|22 | +2 | -4 |
| naive LLM    | 24 / 0.78 / 37|27|26 | 20 / 0.83 / 31|30|23 | -4 | +3 |
Early read: the timetable's selective accuracy at 50% coverage falls 8 points on shift days at the same/higher confidence
(confident and worse); the mixture's holds (+3) — the claim in coverage-matched form — but its mean confidence does not fall
either (0.28 -> 0.29), so "loses confidence" is not shown, only "its ranking still knows". Judge again with the weekends in.

## 04:30 — first full week: hh_s11 told (exit 0 at 04:27; not-told replay starts after the group)
Week: ESS 6.6 -> 10.1, top doc 0.21 -> 0.15, 12 revisions, no collapse. Moved half Wed..Tue 18/19/26/39/21/43/34 (timetable
21/27/26/42/30/54/34; last seen 24/4/33/9/24/9/0); still 92/82/86/84/71/69/75 (erodes late-week: routine predictions on
still objects, same as the timetable's 85/79/86/81/71/59/66); conf moved < still every day; mean conf climbs 0.23 -> 0.36.
Own shift days (Fri/Sat/Sun/Tue) vs plain (Thu/Mon), moved half: acc 30 vs 33 (-3, small break) at conf 0.29 vs 0.25 (higher
on shift). s11 is a retired home; expected weak. The still-half erosion is now visible in the mixture as well as the timetable.
- f1 04:28: s11 not-told started early into heldout_fb/hyp_early/study (global elicitor cache -> the chain's own s11 not-told later is all cache hits; the chain's copy in hyp/study stays the one converted). Naive done on 8 hh, leak check 0.

## 04:36 — s10 through Sunday: weekend = Sat hard, Sun easy for everyone; a calibration inversion to watch
s10 moved half Wed..Sun 19/25/20/14/45 (timetable 7/28/34/14/52, last seen 15/9/11/9/16): Saturday breaks everyone, Sunday
(guest evening, repeated questions) is easy for everyone. Coverage-matched on s10, plain vs shift: mixture sel@50 24 -> 36 (+13),
timetable 41 -> 27 (-14), naive 21 -> 21. But the mixture's top-25%-confidence answers on PLAIN days are 6% right (overall 22):
on moved questions its most confident answers are its rest-spot answers, i.e. wrong by definition of "moved". The timetable's
ranking is informative (29|41|36). Pooled earlier it was mildly informative (39|38|33 vs 30). If this holds across households,
the honest statement is: the mixture's confidence separates still from moved (good) but does not rank WITHIN the moved half.

## 04:40 — s18 Saturday (working household): the clean example
Moved half plain (Thu/Fri) vs Sat: mixture 41 -> 21 at conf 0.28 -> 0.32; timetable 36 -> 18 at 0.38 -> 0.46; last seen 26 -> 24;
naive 33 -> 26 at 0.81 -> 0.84. Coverage-matched sel@25|50|75: mixture 71|55|45 -> 12|35|23; timetable 50|45|48 -> 0|6|12
(its confident Saturday answers are all wrong); naive 50|38|39 -> 0|35|31. Still half stays 90% for the mixture on Saturday.
So on a working household: everyone breaks on Saturday; every agent's mean confidence goes UP, not down; the mixture's
confident answers degrade least (sel@50 -20 vs the timetable's -39). "Keeps accuracy on what it is confident about" holds
relatively; "loses confidence" does not hold for any agent under this protocol.

## 04:48 — s14 told finished (exit 0, 04:45); s10 is the last of group a (Tue in progress), then the not-told chain
s14 week: ESS 7.9 -> 10.3, 12 revisions; moved 8/24/47/29/37/41/46 (timetable 8/24/37/34/39/41/46 — nearly identical, the
blend); still 96/70/85/69/50/85/72 (Sunday 50: sick-day + guests, routine predictions on still objects). Plain (Tue only, n=35)
vs shift (n=188): mixture 46 -> 36 at 0.30 -> 0.31, sel@50 61 -> 47; timetable 46 -> 35 at 0.49 -> 0.43, sel@50 56 -> 46.

## 05:05 — POOLED coverage-matched table (6 households, days completed so far; full file driver/weekend_table_0502.md)
Moved half, Thu-Tue, each household's own shift days vs its plain days. n = 332 plain / 533 shift.
| agent | plain: acc / conf / sel@25|50|75 | shift | d acc | d sel@50 |
| mixture told | 38 / 0.29 / 51|48|44 | 32 / 0.30 / 42|42|36 | -6  | -6  |
| timetable    | 43 / 0.42 / 55|54|49 | 32 / 0.42 / 38|37|34 | -12 | -16 |
| most frequent| 20 / 0.43 / 22|25|26 | 21 / 0.46 / 21|21|21 | +1  | -4  |
| last seen    | 18 / 0.98 / 34|19|19 | 20 / 0.98 / 20|21|20 | +1  | +2  |
| naive LLM    | 27 / 0.80 / 37|30|30 | 24 / 0.83 / 31|29|26 | -3  | -1  |
Reading: (1) the timetable learns the routine best (43 plain) and breaks hardest on shift days (-12; its confident half -16)
at unchanged confidence 0.42 — confident and worse, the counter-example the story needs. (2) The mixture learns almost as well
(38), breaks half as much (-6; confident half -6) and its confident answers stay the best on shift days (42 vs 37 timetable, 29
naive) — "keeps accuracy on what it is confident about" holds RELATIVELY. (3) No agent lowers its confidence on shift days; the
mixture's 0.29 -> 0.30 like everyone's. (4) The naive LLM sits between last seen and the timetable at 0.80-0.83 everywhere.
So the paper can say: the mixture is the only learner whose confident answers survive the shift; it cannot say it "loses
confidence" — that needs per-document conditional statistics (findings.md point 3). Sent to f1 for findings.md.

## 05:10 — s25 Saturday: everyone breaks; the mixture's confidence dips slightly (first household where it does)
Moved half plain (Thu/Fri) vs Sat: mixture 41 -> 26 at 0.29 -> 0.28, sel@50 54 -> 22; timetable 46 -> 34 at 0.38 -> 0.44,
sel@50 54 -> 33; last seen 27 -> 9; naive 38 -> 11 at 0.85 -> 0.83. On this household the mixture's confident answers
degrade MORE than the timetable's (-32 vs -21); pooled it is still the other way. Per-household variance is large (n=35).

## 05:38 — s19 Monday (its first plain day after Thu-Sun shifts): the timetable out-learns the mixture here
Moved half Monday (n=34): timetable 65% (sel 75|76|69), mixture 32% (25|29|35), naive 29, last seen 6. Shift days (n=149):
timetable 32, mixture 36. So on s19 the timetable's break is -32 (65 -> 32) and the mixture's is +3 because the mixture never
learned as high: with 4 days of bins the timetable's routine answer is right 2/3 of the time on a plain Monday, while the
document prior (0.3 of the blend) keeps pulling the mixture toward rest spots. Honest caveat for the pooled table: part of the
mixture's smaller break is a smaller rise. The mixture's confident answers on shift days are still the best (43 vs 26 timetable).

## 05:42 — told = not-told confirmed on s10 (structural, not a run bug; no kill)
s10 not-told through Sunday: 100% identical answers to told on all 128 post-message questions (Sat+Sun), same confidences
(moved 17 vs 14 on Sat is one question). This is the expected outcome of problems_found #23 (message documents enter at ~0.02
and the shared-bin blend makes every document answer alike). The paper's told/not-told pair is therefore a null result under
this protocol, to be stated as such with the mechanism and the conditional-statistics fix as future work.

## 06:03 — five of six told arms finished cleanly; not-told replays running for s10/s11/s14/s19; s25 on Sunday
Exit 0: s11 04:27, s14 04:45, s10 05:08, s19 05:54, s18 06:01. ESS 5.5-16 through every week, no collapse, 12 revisions
per arm. s18 week (moved): 7/50/27/21/39/54/52, still 91/82/98/90/69/75/85. s19 week: 27/22/49/31/38/32/33.
Group b (s12/s13) told arms not started yet at 06:03 — f1's chain runs them after the group-a not-told replays.

## 06:52 — ALL SIX TOLD ARMS COMPLETE (s25 exit 06:48). FINAL coverage-matched table (told; not-told == told)
File: driver/weekend_table_0650_told_final.md. Moved half, Thu-Tue, own shift days vs plain days, n = 541 plain / 682 shift.
| agent | plain: acc / conf / sel@25|50|75 | shift | d acc | d sel@50 |
| mixture told | 39 / 0.29 / 48|46|44 | 32 / 0.30 / 44|41|36 | -7  | -5  |
| timetable    | 47 / 0.42 / 61|59|51 | 32 / 0.42 / 33|37|36 | -15 | -23 |
| most frequent| 22 / 0.44 / 20|23|27 | 20 / 0.47 / 18|19|20 | -1  | -4  |
| last seen    | 18 / 0.98 / 27|21|20 | 19 / 0.98 / 21|21|19 | +1  |  0  |
| naive LLM    | 31 / 0.81 / 39|33|35 | 23 / 0.83 / 32|28|24 | -8  | -5  |
Per household (mixture d acc / d sel@50 ; timetable d acc / d sel@50): s10 -7/-5 ; -13/-30 | s11 -3/+8 ; -10/-11 | s14 -10/-14 ;
-11/-10 | s18 -16/-17 ; -20/-44 | s19 +3/+5 ; -30/-54 | s25 -12/-24 ; -16/-24.
Final reading (unchanged from 05:05, now on complete weeks): the timetable learns the routine best (47 plain) and breaks
hardest on shift days (-15; its confident half -23) at unchanged confidence 0.42 — confident and worse. The mixture learns less
(39; on s19 much less, 33 vs 62), breaks half as much (-7; confident half -5) and its confident half is the best of any agent on
shift days (41 vs 37 timetable, 28 naive). Mean confidence does not fall for any agent on shift days (mixture 0.29 -> 0.30;
it dips only on s25, 0.30 -> 0.26). The naive LLM: 31 -> 23 at 0.81 -> 0.83. told == not-told (s10 99%, s11 100% identical).
- f1 06:52: final table + caveat in findings.md point 3. Group-b not-told chain started 06:49; s18 (days 1-5) and s19 (days 1-2)
  replayed from the early runs' cache instantly; early duplicates killed; four chain arms left (s14 Sun, s18 Sat, s19 Thu,
  s25 Wed). Group-a conversion when s14 not-told finishes (~07:30). f1 assembles the report at ~08:45 with whatever not-told
  logs exist, republishes the ledger over v11, and notes which not-told arms were still running.

## 07:00 — group a complete and converted; group b (s12/s13) told arms started 06:58
heldout_fb/hyp/logs now has told + not_told for s10/s11/s14 and told for s18/s19/s25. s14 not-told: 99% identical to told
after its Thursday message; Friday recovery identical (47 vs 47). Three complete pairs, all null. Group b told arms (s12
counter-example, s13 weak) started 06:58; at ~45 min/day they finish ~12:00 — after the 10:00 deadline; f1 reports them
as partial/told-only. s18/s19/s25 not-told replays continue.

## 08:48 — f1 hand-over build done
report.md assembled (findings first, my final table in point 3, six-household main tables, naive-only table for s12/s13,
secondary 8 h section, usage: 12.0 M prompt / 3.7 M completion tokens, 53.7 h summed generation, $0). Ledger v13 published
(over my v11, wording merged). Logs converted: told x6, not-told x4 (s10/s11/s14/s18); s19/s25 not-told finish ~09:30 and f1
re-runs assemble.sh. s12/s13 told on their Sunday, out of the tables (noted). Nothing else planned before 10:00.

## 08:58 — all six told + not-told pairs complete (s25 not-told finished 08:56); group b told on Mon/Sun
told = not-told on all six: s10 99%, s11 100%, s14 99%, s18 100%, s19 99%, s25 (below) identical answers after the message day.
f1 re-runs assemble.sh now that s19/s25 not-told logs exist.
    [FAIL] hh_s25: told differs from not-told after message day Wed (100% identical)
    !! story: hh_s25: told differs from not-told after message day Wed (100% identical)

## 09:00 — DELIVERABLES FINAL (f1 done with changes)
results/confidence_shift_2026-09-20/{report.md (re-assembled 08:57 with all six pairs; told and not-told pooled rows identical),
findings.md, tuning_log.md (#1-47), problems_found.md (#1-23), open_questions.md (#1-14)}; Ledger v14
https://claude.ai/artifact/KJPMaPPbgv4UmeVakrDSTA. s12/s13 told still running (out of the tables). Driver keeps watching.

## 09:22 — group b told arms finished (s13 09:15, s12 09:20); their not-told replays started automatically
Both weeks clean (12 and 11 revisions, no collapse). s12 (the disclosed counter-example) and s13 (weak) stay out of the
paper tables as noted in findings; their logs land in heldout_fb/hyp/logs when the chain converts. Numbers below.
### hh_s12 (days [1, 2, 3, 4, 5, 6, 7])
| mixture (told) | 34 / 0.30 / 39|30|40 (n=91) | 45 / 0.32 / 59|45|48 (n=89) | +11 | +15 |
| timetable | 37 / 0.40 / 35|46|44 (n=91) | 51 / 0.47 / 36|55|54 (n=89) | +13 | +9 |
### hh_s13 (days [1, 2, 3, 4, 5, 6, 7])
| mixture (told) | 40 / 0.36 / 36|45|42 (n=111) | 32 / 0.36 / 43|37|36 (n=93) | -7 | -8 |
| timetable | 47 / 0.49 / 50|57|54 (n=111) | 40 / 0.44 / 57|48|43 (n=93) | -7 | -9 |

## 11:40 — ALL ARMS FINISHED. s13 not-told done; 16 mixture logs (told + not-told x 8) once the chain converts group b. Nothing running.

## 02:05 — two-spells anomaly resolved (structural reuse, not a confound)
- 0a's three checks (no server time): last seen breaks neither time (world not easier); moved-share 26% vs 28% (second spell moves as much);
  1-day timetable: 53% of its spell-2 questions fall in an hour slot whose only sightings come from spell 1 → 97% right there.
- Verified in code (uq_agents.py DiscountedTimetable._predict_for_object / timetable.py): half-life only reweights sightings
  inside a slot; a slot the normal routine never writes keeps the spell-1 placement for ever. Forgetting is relative within a slot.
- Decision: two-spells buffer+retrieval no-message (3 hh) runs at ~05:00 BEFORE long-context start+end. Prediction on record:
  retrieval (time-of-day keyed) re-learns spell 2 faster than spell 1; buffer (recency only) does not.
- Story page v22 published 02:01. Asked 0a to strip "bin/novelty/counters/E30" from the gist wording.

## 02:30 — no-message pass: retrieval done (10 hh), reflection 5/10; red flag on reflection cleared
- Retrieval no message: 81 → 56 (shift) → 64 → 76 (return) → 82; cold 79 → 28 → 43 → 62 → 78; confidence 87-88 everywhere; gate asks 59% at the shift.
- Reflection no message: day-level 73 → 66 → 79 (above lead!) → 70 → 70. Checked: cold split 68 → 35 → 62 → 51 → 67 stays below lead;
  timetables show the same day-level rise on the same questions (sick person's things sit in fewer places) → regime property, not artefact.
  Notes audit hh_s0-3: no unseen observations, no future days, no "sick"-words in 299 notes. Cleared.
- Gist bullet 1 reworded by 0a: "every memory breaks on the first sick day — by 7 (reflection) to 25 points (retrieval) on all questions, 30-54 on cold".
- Revised ETAs: start-message retrieval ~03:20 → start+end ~04:10 → long-context 3 hh ~06:00 → two-spells no-message ~06:40 → long-context start+end ~07:20 → two-spells start-message ~08:00.

## 03:15 — retrieval no-message + start-message complete (10 hh); three independent lanes
- Retrieval  no message: 81/79 · 56/28 · 64/43 · 76/62 · 82/78 (all/cold; lead | sick 1-3 | rest | return 1-3 | rest); conf 85-88; gate asks 58% at the shift.
- Retrieval  start msg:  81/79 · 68/40 · 80/67 · 58/50 · 69/58; conf 82-88; lead-cal gap on shift +17 → +1; return costs it 18 points and the gate asks 52%.
- Buffer for comparison — no msg 78/75 · 58/21 · 66/41 · 74/58 · 77/70; start 78/75 · 71/44 · 83/78 · 62/38 · 72/63.
- Point for the gist: the start message helps during the sick days and costs on the return; costs time-of-day retrieval the most (same mechanism as two-spells reuse, other side).
- Lanes: retrieval start+end launched 03:13; reflection waits only on its own start-message tail; long-context lane started at 3 streams with a 40/min rate guard.

## 03:55 — retrieval lane complete; start+end result; two-spells + reflection start+end running; guests scout
- Retrieval start+end vs start only: return days 24-26 all 58 → 74 (+16, buffer +8), cold 50 → 59 (+9, buffer +12); days 27-31 79 vs 69 (+10).
  Prediction E32 (≤ +6 all) partly wrong: on cold questions retrieval recovers a little less than the buffer (as predicted),
  but overall the end message helps retrieval far more — a sentence lets the model discount retrieved evidence it cannot forget.
  Start-message damage persists longer for a time-indexed memory: days 27-31 retrieval 69 vs 82 untold (−13), buffer 72 vs 77 (−5).
- Running: reflection start+end (5 hh), two-spells no-message buffer+retrieval (3 hh), long-context no-message (3 hh, ~390/496). Rate 61/min.
- Guests scout (classical, CPU only): configs/regime/guests10.yaml, expectation E33 = 10-15 pp break all / 20-25 cold, ceiling 30-40%.

## 04:40 — what makes a disruption hard: both hypotheses tested, "unusual place" wins
- 0a's "questions come at hours never seen" and my "unseen hour AND wrong fallback" were both refuted on three regimes (sick / guests / holiday-at-home).
- Tracks the break: share of questions where the thing is away from its usual place — sick +41 pp → break 23; guests +16 → 11; holiday +7 → 2.
- Does not track: new-hour share (holiday shifts most, breaks least). New hour + usual place scores 89-95% everywhere: the empty-hour
  fallback is the object's usual place, and that is usually right. In the sick spell, unseen hour + unusual place (65%) beats seen hour + unusual place (35%).
- The break is a change in the MIX of questions, not the methods getting worse: sick cells themselves got easier (−18) while the hard kind grew +41.
- Page: replace the old (object,hour) novelty "ceiling" with "how much of the household's stuff is out of its usual place".

## 05:00 — paired contrasts (Oliver's 1-sd rule) applied to every LLM claim
- Matched households first (reflection's cold lead-up moved 9 points between the 10-hh and 5-hh sets), then paired per-household differences ± sd.
- Survives: buffer's message +12.9 ± 9.5 on the shift days (cold +23.5 ± 13.4), its return cost −11.3 ± 7.9; retrieval's COLD gains +12.8 ± 12.3;
  retrieval's LATE return damage −11.4 ± 11.3 at days 27-31; long-context rest-of-spell +12.7 ± 4.9 (3 hh).
- Does NOT survive: retrieval's first-days-back damage (−13.1 ± 22.2 — the old headline, now restated as the later, sharper persistence claim);
  retrieval's all-question gains; reflection anywhere (+4.6 ± 9.1); routine table (+3.3 ± 4.7); buffer start+end at 24-26 (−3.6 ± 8.3 = message repaired).
- Guests dead: evening-only break 15 points, morning after −1. Negative bullet on the page.

## 06:40 — chain complete (78 arms, no failures); E31b not supported
- Two-spells LLM arms landed 06:08. E31b (pre-registered): retrieval +4.9 ± 7.3, buffer −4.9 ± 5.2 across 3 households — neither clears.
  Prediction not supported; page says so and claims nothing from it. The classical reuse result stands on its own.
- Long-context complete on its matched 3 households; its other 7 no-message households abandoned (terminal state in watcher + page).
- Outstanding: workshop session's end-message contrast on 18 households (phase 1 of 2 running, due ~07:05), which settles how much
  of the return-day repair the retraction itself is doing.
- Page v42 published. Commit 03762bbcf pushed at 05:05; another commit due once the end-message number lands.
