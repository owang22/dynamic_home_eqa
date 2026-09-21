# Open questions and assumptions

## Wrong or unresolved

1. **Criterion (1), the Wed->Fri rise, is not met and cannot be met by the classical agents on this stream.**
   With the empty-look suppression on, every classical belief reduced to the last patrol listing; with it
   off (the frozen setting) most frequent / timetable / periodic still agree with last seen on 99% of the
   held-out answers, because a patrol every 2 h mostly catches objects at rest and the modal spot is the
   rest spot. Nothing accumulates that a fresh sighting does not already say. The simulator has no
   time-of-day placement regularity strong enough to learn from (same clock time yesterday: 69% on
   weekdays, measured from truth). The +4 rise on the frozen tuning set and +1 on the held-out set are the
   households' weeks, not learning. Reported as is.

2. **The weekend drop is a working-household effect and is smaller on the held-out set** (most frequent
   Fri->Sat: +12 on seeds 0-9, +3 on seeds 10-29; weekday->weekend for households without a retired
   resident: +7 tuning, +6 held-out; households with a retired resident: 0). The tuning set has 7 working
   and 3 retired households, the held-out set 13 and 7. The split is by the intro cards every agent sees,
   declared before the LLM runs. Expect the LLM figures to show the same: per-household tables are the
   honest view, the pooled curve understates the shift for working households and overstates it for
   retired ones.

3. **Event-day drop vs the day before is ~0 pooled** (+2 tuning, +1 held-out) although grouped by day
   type sick days (55%) and guest days (57%) sit under plain weekdays (60%) on the tuning set. A guest
   evening touches only the last third of a day's questions and 'the day before' is itself a noisy
   32/64-question cell. The generator has only weekday / weekend rates, so the event could not be pinned
   to Monday; raising the weekday rates to 0.10 each put an event on a scored weekday in 8/10 (tuning)
   and 15/20 (held-out) households, on any scored day in 9/10 and 18/20.

4. **The naive LLM's confidence is one number.** ~90% of answers at 0.95 (see problems_found.md #7).
   Its coverage at 0.7 is therefore ~95% every day and its reliability diagram has one bin. This is the
   behaviour the study is about, but a thinking-mode or stronger model would be the next thing to try.

5. **Last seen is one number by construction** (confidence 0.98 = 1 - floor mass on every answer). The
   other classical agents spread once the empty-look suppression was cut (problems_found.md #4), but
   they are overconfident everywhere: ECE 0.31-0.40, and their coverage at 0.7 does not move on shift days.

6. **The hypothesis mixture is calibrated and selective, not more accurate.** On the finished held-out
   households its overall accuracy is ~10 points under last seen and the naive LLM (which answer everything at
   ~0.95 and are right ~58% of the time); its confidence is the best-ordered on the table (lowest ECE) and on
   the questions it answers at >= 0.7 it is the most accurate agent. Its coverage does not fall on shift days,
   and told vs not told differ by a point or two: the message-triggered revisions add documents, but the
   library's agreement on the asked objects does not move with the weekend. The brief's claim ("loses
   confidence when the routine shifts") is therefore not supported by this run; "keeps its accuracy on the
   answers it is still confident about" is.

7. **The method needed six changes to run at all on a passive patrol stream** (problems_found.md #8-#15):
   in-use windows in the elicitation, hourly evidence in revisions, no empty-look suppression inside particles,
   weekend days from the bank's day 0, fair-share entry for revised documents, per-pass tempered weights, and
   a robustness fix for unbuildable revised documents. Each was traced on one question before being applied;
   all are env-gated in `run_arms.sh` and documented. The original settings were made for the budgeted-look
   protocol and are not wrong there; they are wrong for a stream of ~35 listings per pass.

8. **The two LLM agents were run on 5 held-out households, not 20**, per Oliver's instruction to check on five
   first. The classical agents cover all 20. Extending to 20 costs ~6-8 h of local server time at the current
   thinking budget; a lower reasoning effort on revisions would roughly halve it (untested).

9. **Revision count is uneven**: told arms revise on every message day (4-7 revisions per week), not-told arms
   only on claim triggers (1-5). More revisions did not buy accuracy (told ~= not told).

10. **Only one counter actually learns and breaks.** Under the feedback protocol the timetable (hour bins over
    outcome sightings) rises from ~12% to ~45% on the moved-since-round questions and falls to ~35% on the
    household's shift days at the same confidence (~0.43); most frequent, periodic and Perpetua* never learn a
    time-of-day routine and sit at 20-28% on that half on plain and shift days alike; last seen is flat at
    ~18% at 0.98. The headline figure is therefore timetable vs last seen vs the mixture; the other counters
    go in the table. "Frequency counters get worse" is true of the one counter that learns.

11. **The observation channel was the missing piece, and it is a modelling choice.** Found-it feedback (the
    resident's answer 10 minutes after a question) is what lets any agent learn where things are when they
    are needed; every patrol-only protocol tried tonight (2/4/8 h, nightly, fixed times) only ever sees
    objects at rest, and no simulator-regularity setting changes that (tuning_log.md #33). It conflicts with
    the human-quiz rule of sealed verdicts; for the robot it is stated as part of the protocol, delivered
    identically to every agent, and the sealed 8 h protocol results are kept as a separate section.

12. **No confidence we have tracks the shift day.** The mixture's top_prob (0.22-0.36), its library agreement, the
    timetable's Dirichlet mean (~0.42), the naive LLM's stated 0.8 and a self-monitoring rescale (top_prob times
    the agent's running hit rate on the feedback already received today; `--confidence monitored`) all move by at
    most 3-5 points between a household's plain days and its shift days. The day-level accuracy change is the
    same size (Fig. 1: 4-8 points), so a calibrated confidence *should* only move that much; the 10-point story
    lives on the moved-since-round half, where the accuracy change is 10-25 points and the confidence still does
    not follow because every agent's evidence (clock bins over the week's sightings) is pooled across days. What
    would follow: a confidence that is conditioned on the day type (calendar for the weekend, the message for
    the told arm), i.e. separate weekend bins with an honest empty-bin confidence (tuning_log #42 shows the
    accuracy side of that: Saturday breaks harder; the confidence side needs the empty-bin fallback to say so).

13. **The mixture's confidence scale is compressed** (0.2-0.36 on both halves) because each document blends its
    clock-bin counts with the author prior at 0.7/0.3 and the tempered weights keep 7-10 documents alive; its
    *ranking* still carries information (selective accuracy at its top quarter is above its all-questions
    accuracy on most days) so the coverage-matched tables are the fair view, not the thresholds.

14. **Still-half erosion on shift mornings.** The documents (and the timetable) send an in-use object to its
    routine spot even when the nightly round saw it elsewhere and nothing had moved it yet (hh_s14 Thursday:
    still half 70% vs last seen 100%). A 4 h recency half-life fixes the early morning only. A designed
    belief would keep "where the round saw it" as the default until the first sighting of the day contradicts
    it - a change-point per object, not a clock bin; not built tonight.

## Underspecified in the brief, and what I assumed

- **Question model.** The brief said 'oversample, filter, keep 32'. After the first hour showed that
  uniform-in-time questions cannot show a shift (problems_found.md #1), and with your go-ahead, questions
  were tied to activities: 85% are asked -5..+15 minutes around an activity start, about an object that
  activity uses (owned by that resident or shared), 15% are chores 10-90 minutes after someone leaves
  (vacuum, laundry, dog bowl, ...). The share after the in-house filter is about 77 / 23 because chore
  objects are always in the house. 64 per day, not 32 (noise). The activity comes from the sim's trace
  (harness-only); the prompts never mention it.
- **Confidence of a classical agent** = its top probability after dropping ON_PERSON / OUT_OF_HOUSE mass
  and renormalizing (the object is in the house by construction). The raw top probability and the dropped
  mass are logged (`raw_top_prob`, `p_outside`).
- **Hypothesis mixture** = the longleaf timetable-document mixture (`passive:longleaf:longleaf_named`),
  weighted by the patrol stream, re-asking the elicitor on its own triggers, confidence = its
  renormalized top probability. The notebook (`hypothesis_llmdecide`) variant grades its hypotheses
  only through looks ('weights change at looks alone', notebook_mixture.py), so it has no learning signal
  without a look and was not ported; that would be a method change, not a port.
- **Shift days** = Saturday, Sunday, and scored days with a guest_visit or sick_day, per household, as in
  the overnight bank. The told arm sees one dated sentence per shift day from that day's first question.
- **Timetable bins** = the patrol spacing (2 h). With 1 h bins the agent was most-frequent in disguise.
- **Perpetua** (plain) was left out; Perpetua* is in, as the brief listed.
- **Hosted spend** = $0; only the local vLLM Qwen3.8-27B was called. Token and wall-clock counts are in
  the report.
