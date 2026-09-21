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
