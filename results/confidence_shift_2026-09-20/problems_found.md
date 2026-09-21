# Problems found (in order): symptom, cause, change

1. **Symptom:** every uniform-in-time question bank was flat across the week (all classical agents 78-94%,
   Saturday no worse than Friday), so no shift could be shown.
   **Cause:** a last-patrol sighting is right ~80% of the time on every day: the simulator puts things back
   at rest spots and the weekend changes who is home, not the rest spots. Measured from the truth rows
   alone (seeds 0-9): 'where it was at 03:00 today' 78-83% every day; 'same clock time yesterday' 69%
   weekdays, 62% Saturday. There is no learnable time-of-day placement to be gained from history.
   **Change:** questions are drawn from what the residents are doing (`bank.py`, `--questions activity`):
   a few minutes around an activity start, about one of the objects that activity uses (from the sim's
   `trace.json` start lines and `activities.yaml` `uses` lists, harness-only), plus a share of chore
   objects after someone leaves. The moment is asked at, not the truth, so nothing about locations leaks.

2. **Symptom:** a class mix that showed a +15 Saturday drop on seeds 0-9 (meal / going-out objects,
   nightly patrol) gave -2 on the same seeds regenerated with another event rate.
   **Cause:** the drop came from 4 of 10 household-weeks; 32 questions per household-day is +-8 points of
   sampling noise, and the class mix was fitted to that noise.
   **Change:** the class mix knob was abandoned (all classes the activities use are eligible); questions
   per day raised from 32 to 64 at freeze time; per-household tables and a working / retired split were
   added to the report so a pooled number is never read alone.

3. **Symptom:** the 'base' households (default event rates) came back different after a config with a
   raised sick-day rate had run.
   **Cause:** the rate writer only overrode the events a config named and left every other event at
   whatever `events.yaml` currently held; a config with no overrides inherited the previous config's rates
   and regenerated the households.
   **Change:** `confshift.py` carries the committed rates (`DEFAULT_RATES`, git 5b6bbe52d) and resets every
   event to its default before applying a config's overrides, so a config fully determines the rates; the
   contaminated households and the four schedule probes run on them were deleted and rerun.

4. **Symptom:** under the 2 h patrol the five classical agents give the same answer on 99% of questions
   (most frequent and timetable disagree with last seen on 14 and 11 of 2240).
   **Cause:** every patrol lists every spot, and the belief pipeline's negative evidence (24 h half-life)
   suppresses every spot but the one the object was just seen on; no prior can outvote a 2 h old listing.
   **Change (Oliver's call, 15:45):** the empty-look suppression is switched off for the four pure classical
   baselines (`negative_evidence: off` in the config -> a vanishing `negative_half_life_h` on their specs;
   Perpetua* keeps its own filter). Answers barely change (the modal spot and the last sighting agree on
   99% of questions because objects are at rest most of the time), but the confidences become the
   models' own: most frequent now has 70% of answers at >= 0.95 and is right on 64% of those, instead of
   0.99 on everything. Tuning criteria numbers are unchanged to the point.

5. **Symptom:** the `timetable` agent was indistinguishable from most frequent under sparse patrols even
   before the negative-evidence effect.
   **Cause:** its hourly bins were empty for every hour without a patrol, so it fell back to the whole
   history. **Change:** the harness sets its bin width to the patrol spacing (`timetable_bin_hours: 2`).

6. **Symptom:** the hypothesis-mixture drivers could not run without a look: `run_tour_start` only handled
   told / not told under the free-look protocol, its prompts only described the patrol under that protocol,
   and it refused a bank whose questions start after the tour day.
   **Change:** `protocol.patrol` on the bank header; `protocol_text.patrol_sentence` renders for it (with
   the clock times when the patrol is at fixed times); `run_tour_start` applies the told / not-told message
   handling on any patrol bank; `hyp.py --passive` runs `passive:longleaf:longleaf_named` with
   `--room-look` (which on the passive path only skips the tour-day check) and converts the mixture's
   distribution to a spots-only answer and confidence.

7. **Symptom:** the naive LLM's confidence sits at 0.95 on ~90% of answers with the confidence prompt
   (worded scale, "do not give the same number every time").
   **Cause:** Qwen3.8-27B without thinking reasons "seen at X in every patrol, so still there" and rates
   that 0.95 regardless of the time of day. Prompt checked; left as the naive baseline (it is the behaviour
   the study is about); noted in the report.

8. **Symptom:** the first hypothesis-mixture run on hh_s10 answered like last seen (5 of 448 answers differ)
   and put 0.0009 on the dining table at dinner.
   **Cause:** none of the 19 elicited documents had any block for dishes at meals; the writer modelled the
   big moves (out of the house, the desk) and left everything else at a resting spot. The questions are asked
   at exactly the moments it never modelled.
   **Change:** the elicitation and revision prompts get a protocol sentence saying when the robot is asked
   (`protocol_text.QUESTIONS_ACTIVITY`, also given to the naive LLM for fairness) and the mechanics ask for
   in-use windows as blocks of their own. Re-elicited: 8 documents, all with meal-time blocks.

9. **Symptom:** the first arm outputs (per-question weights, revisions) for hh_s10 are gone.
   **Cause:** I removed the `heldout/hyp` folder when archiving the v1 run instead of moving it.
   **Change:** none possible; later runs are moved to `hyp_v2_before_hourly/` etc., never deleted.

10. **Symptom:** with the new library the mixture still answered exactly like most frequent, and every
    document gave the same answer on every question (agreement 100%).
    **Cause (three layers, found by tracing one document on one dinner question):**
    (a) each document particle applied the base pipeline's empty-look suppression (24 h half-life), so
    "table 18:00-19:30" was overruled by "the table was empty at the 18:00 pass";
    (b) with that off, the window's own WHERE counts were re-taught "cupboard" by the pass at the window's
    start (edge weight 0.5), and the author's stated spot decays with absolute time whether contradicted
    or not, so by day 3 every window said cupboard;
    (c) with the windows kept intact, the documents lost all mixture weight to the statistical particle
    because "table from 18:00" is wrong at the 18:00 pass on every day (dinner is at ~19:10). The writer had
    no way to know when dinner is: the revision report gave claim tallies, not when the plate was seen where.
    **Change (method configuration for this study, `run_arms.sh` env):** particles without the empty-look
    suppression (`PARTICLE_NEGATIVE_HALF_LIFE_H=1e-9`, the same policy as the classical baselines); a sighting
    refines a window only when it falls well inside it (`TIMETABLE_INTERIOR_MIN_EDGE=0.9`); the author's spot
    does not fade on its own (`TIMETABLE_PRIOR_DECAYS=0`); and the revision prompt carries every object's
    sightings by clock hour, weekdays and weekend apart, with the instruction to place in-use windows in the
    gaps between passes. Mistimed windows still lose library weight at the passes they cover, which is the
    right level for that.

11. **Symptom:** the documents' weekend blocks were applied on Sunday and Monday, weekday blocks on Saturday.
    **Cause:** `timetable_hypothesis.matches_day` / `hypothesis_program` used `day_index % 7 in (5, 6)`,
    i.e. day 0 = Monday, while the bank starts on Tuesday (the prompts knew this through `protocol_text`).
    **Change:** both use `protocol_text.weekday_index`, which the driver sets from the bank's `day0_weekday`.

12. **Symptom:** nothing to look at while an arm runs (rows were written only at the end).
    **Change:** the passive arm streams every answer (dist, weights, each particle's own answer, ESS) to
    `live.jsonl`; `live_progress.py` prints per-day accuracy / probability / agreement / ESS / revisions per
    arm against most frequent and the naive LLM on the same questions, plus the latest answers.

13. **Symptom (found by the other agent, oliver-f4, 20:50):** the classical logs said "empty-look suppression off"
    but ran with it on; the four pure baselines were identical to last seen.
    **Cause:** YAML reads a bare `off` as boolean False; `cmd_classical` compared it with the string "off", so
    the branch never fired. My check after the change looked at confidence spread and disagreement counts and
    misread them as the effect of the change.
    **Change:** the check accepts off/false/0; both seed sets rerun (old logs kept as `classical_suppression_on_bug/`).
    With the suppression really off the counters separate from last seen and drop: held-out most frequent 46%
    (was 58%), timetable 51%, periodic 58%, last seen 60%; tuning most frequent falls to 35% on Saturday, under
    the 40% floor of criterion (3). The tuning log's line 29 numbers are superseded by these.

14. **Symptom:** in every live arm the mixture's effective sample size was 1.0 from the first question and the
    top particle flipped between the statistical particle and one document within a day, so confidence and
    agreement carried no information.
    **Cause:** the mixture tempers its log weights by `decay = 0.6` per evidence event and adds each event's
    full log likelihood. An event is one spot listing and a patrol pass is ~35 of them, so the weights only
    ever reflect the last two or three listings of the latest pass; and single listings carry 10+ nat
    ratios (a document that calls a spot near-impossible pays for it in full). A setting made for a
    protocol with a few looks a day; memoryless under a patrol stream.
    **Change:** `HYPOTHESIS_DECAY=0.985` (0.6 per pass of 35 listings) and `HYPOTHESIS_LL_TEMPER=0.03` (the mean
    log likelihood per listing, i.e. one pass = one event) in `run_arms.sh`. On the fixed initial library
    this makes the mixture worse than the counter (54% vs 61%) with ESS 4-7 and agreement 72-93%: the honest
    state of an un-revised library. Arms restarted 21:14; earlier outputs kept in `hyp_v4_switch/`.

15. **Symptom:** both hh_s14 arms died at their first revision (exit 1, 21:28 / 21:53) and my waiter loop did
    not check exit codes, so it went unnoticed for an hour.
    **Cause:** a revised document named `class:keys`, a class never sighted in that home (keys stay in
    pockets); the revision parser accepted it, the particle builder (`parse_timetable`) raised.
    **Change:** `_rebuild` drops such a document and records it in `rejected_ops` instead of crashing; hh_s14
    rerun (revisions replay from cache); progress checks now report exit codes and tracebacks.

16. **Symptom (Oliver, 23:10):** accuracy rose on the weekend and on Monday/Tuesday for most agents, and the
    "affected" questions (the peer's labels from the residents' messages) were the EASIEST on Monday (last
    seen 94% on 5 households, 72% on 20).
    **Cause:** at the frozen 2 h patrol every event parks its affected objects (sick day -> couch and coffee
    table all day; guests -> coffee table for the evening) and the next pass re-sees them, so from then on
    "where I last saw it" is right; the shift makes affected objects more stationary. Same questions, sparser
    patrol, 20 households, last seen affected vs unaffected on Thu/Fri/Sat: 2 h 51/53/53 vs ~61; 4 h
    38/50/39 vs 57; 8 h 32/31/35 vs 54; nightly 34/24/32 vs 50; most frequent ~30% on affected everywhere.
    **Change:** re-frozen at patrol every 8 h (`configs/frozen_2026-09-20_p8.yaml`; results in `heldout_p8/`
    and `tuning/frozen_p8/`; the 2 h results stay in `heldout/`). Questions, truths and labels are unchanged
    (they come from the activity trace, not the patrol). Naive LLM and the mixture rerun on hh_s10-14 at 8 h;
    the primary figure becomes affected vs unaffected accuracy and confidence on shift days. Peer alerted.

17. **Symptom (Oliver, ~23:30):** with the 8 h patrol the classical curves were flat and the "affected"
    questions were the easiest on Monday; no configuration of patrol rate, question focus, simulator regularity
    or week length gave a learnable routine (tuning_log.md #30-35): the last-pass oracle beats the
    same-time-yesterday oracle on every day at every setting, because a patrol only ever sees objects at rest.
    **Change:** a new observation channel, found-it feedback (`feedback_delay_min`): 10 minutes after each
    question the robot learns where the object turned out to be, as an ordinary sighting for every agent, on
    top of a nightly round. It samples the world at the moments questions are asked, so counters can learn the
    weekday routine from outcomes and the shift days break it (tuning_log.md #36-37). Frozen as
    `configs/frozen_2026-09-21.yaml`; results in `heldout_fb/` and `tuning/frozen_fb/`.

18. **Symptom:** with feedback, the counters' accuracy on questions whose object had NOT moved since the
    round erodes over the week (timetable 75-95% Thu -> 48-90% Tue per household).
    **Cause:** outcome sightings are at in-use spots; a histogram over sightings then favours the in-use spot
    even at rest. A counter artefact, not a shift. The report reads the moved and still halves separately.

19. **Symptom:** the LLM household set (hh_s10-14) is four retired homes and one working home; retired
    homes have the weakest weekend shift. **Change:** hh_s18, hh_s19, hh_s25 (working, clear classical shift
    on moved questions) added to the LLM set overnight; disclosed as such. The 20-household classical set is
    the unbiased one.

20. **Symptom (01:05, feedback arms; also flagged by the overnight driver on hh_s12):** mixture 7% on
    moved-since-round questions on Thursday vs the timetable's 29%; the Wednesday revision's new document
    jumped to weight 1.0 at the very next question and stayed there (ESS 1.0-1.4 all Thursday).
    **Cause:** (a) a feedback sighting only refines a document's window if a window covers that hour;
    otherwise it goes into the document's flat rest histogram, so documents do not learn a time-of-day
    routine from outcomes between revisions, and revisions came only on claim/message triggers; (b) with
    ~500 evidence events a day the 0.985/event decay remembers ~3 h, and a revised document written from
    the day's outcomes explains exactly that evidence and takes everything (hindsight); the `share` entry
    rule used max(mean, share), which can enter a document above its fair share.
    **Change (env in the arm scripts):** each document's fallback is the robot's own time-of-day statistics
    (`TIMETABLE_FALLBACK_BIN_H=2`) and once the object has been seen in the query's hour bin the evidence
    leads: prediction = 0.7 * bin statistics + 0.3 * document (`TIMETABLE_EVIDENCE_BLEND=0.7`,
    `TIMETABLE_EVIDENCE_MIN_COUNT=1`, raw sighting count); a scheduled revision at every day's first
    question (`LONGLEAF_SCHEDULED_DAYS=1..7`); weight memory about a day (`HYPOTHESIS_DECAY=0.998`); a new
    document enters with exactly one particle's share (`HYPOTHESIS_ENTRY=share_cap`). Fixed-arm check on
    hh_s12 / hh_s10: the mixture on moved questions now tracks the timetable (14/28/35 -> 18 -> 42/28/83 vs
    14/28/42 -> 21 -> 50/42/86) with ESS 4-9. Arms restarted 01:02; the earlier run kept as `hyp_v1_no_blend/`.

21. **Symptom (01:20, both agents on this machine):** after the day-1 review, one of the NEW documents held
    0.94-0.97 of the mixture from the very next answer on (hh_s11 told, hh_s12 told in the earlier run).
    **Cause:** `LongLeafMixture._rebuild` overrides the parent's entry rule with a "fair entry": a new
    document gets the log-weight it would have had from the start, its log-likelihood replayed over the whole
    evidence log, untempered, anchored on the statistical particle. A document written FROM that evidence
    replays it near-perfectly and enters on top by construction; `share_cap` was applied by the parent and
    then overwritten. A second, smaller factor: the likelihood floor of 1e-12 (27.6 nats per miss) lets one
    round hand the mixture to any document that predicts the rest spots exactly.
    **Change:** under `HYPOTHESIS_ENTRY=share|share_cap` the longleaf override returns after the parent's
    rebuild (documents earn weight forward from birth); `HYPOTHESIS_MIN_LIKELIHOOD=0.02` (env) caps a miss at
    ~3.9 nats. Verified on the cached hh_s11 day-1 review: ESS 6.7-7.2 through Wednesday (was 1.1). Arms
    relaunched 01:34 in the order of the classical shift strength (hh_s10, 14, 11; then 12, 13; 18/19/25
    when elicited); earlier partial runs kept as `hyp_v2_hindsight_entry/`. hh_s12 is a disclosed
    counter-example: its shift days are easier for every agent (classical timetable 37% -> 51%).

22. **Symptom (02:00):** with the 0.02 likelihood floor from #21 the fixed mixture's late-week accuracy on
    moved questions collapsed (hh_s12 Tue 83% -> 14%): a miss capped at 0.1 nats after tempering means the
    weights never move and the mixture stays a flat average of its documents. And the still half sat at
    ~70% because documents carry no recency (they answer the usual place against a fresh nightly sighting).
    **Change:** floor `HYPOTHESIS_MIN_LIKELIHOOD=1e-3` (identical results to no floor on the fixed arms once
    the entry rule of #21 is fixed; ESS 4-8; caps a single miss at 6.9 nats), and a recency term inside the
    document blend (`TIMETABLE_RECENCY_HALF_LIFE_H=4`: the latest sighting counts as one extra sighting in the
    hour-bin statistics, fading with a 4 h half-life). Fixed-arm check: still half hh_s14 Wed 82 -> 96%,
    moved half unchanged. Arms restarted 02:04 (earlier partial run kept as `hyp_v3_floor002/`).

23. **Symptom (03:15, v4 told arm hh_s14 Thursday = guest evening, message day):** the three documents the
    message revision wrote for the gathering ("Friends Evening: Living Room Gathering", ...) sit at 0.01-0.02
    each for the whole day while the routine documents hold 0.16-0.23; all 19 documents give the same answer
    with the same probability on most questions (the 0.7 evidence blend over shared hour bins), so the told
    arm answers exactly like the not-told arm and its confidence does not move on the day it was told about.
    **Cause:** the `share_cap` entry rule (#21) gives every newcomer 1/(n+1) of the top weight, and the
    tempered per-event update (0.03) cannot lift it within a day. That rule was written against hindsight
    documents (written from the evidence); a message document is written from the resident's word about
    today, not from evidence, so the same rule is the wrong prior for it.
    **Change:** `HYPOTHESIS_MESSAGE_ENTRY=parity` (llm_hypothesis_mixture._rebuild, keyed on the revision
    trigger passed through longleaf_mixture._apply_revision): message-triggered documents enter level with
    the leading document; every other trigger keeps share_cap. Run as v5, told arms only, hh_s14 + hh_s11
    (`heldout_fb/hyp_v5_message_parity/`), the v4 arms left running for the paper's told/not-told pair.
    **Outcome (03:40):** with parity the message documents held 0.10-0.11 each on hh_s14 Thursday (v4: 0.02)
    and the answers were identical to v4 on every question (24% moved / 70% still, same confidences). The
    deeper cause: every document's prediction is 0.7 hour-bin statistics + 0.3 its own claims, and the hour
    bins are shared across all days, so on the guest evening the bookshelf sightings of Wednesday outvote
    the "board game on the coffee table" claim inside the message document itself; the library cannot
    disagree with its own statistics. Told = not told is structural under the evidence blend, not an
    entry-weight problem. v5 stopped at 03:40 (partial outputs kept in `hyp_v5_message_parity/`); a
    pseudo-count blend (tuning_log #45) does not fix it either. What would: day-typed evidence (a message
    document only counts sightings from days of its own kind), i.e. the calendar/message conditioning of
    open_questions.md #12.
