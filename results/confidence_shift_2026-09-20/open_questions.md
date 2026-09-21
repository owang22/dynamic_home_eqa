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
