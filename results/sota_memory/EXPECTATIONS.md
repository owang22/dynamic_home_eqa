# sota_memory — predictions written BEFORE results (dynamic-home-eqa-34)

Task: frozen one-person regime, banks `dynamic_home_eqa_fm/results/fm_memory/banks_f1`, hh_s0-2, no message, fmt=conf.
Windows: lead 9-13, sick1 14-16, sick 17-23, ret1 24-26, ret 27-31. "cold" = first question about an object that day.
Bar: n=3, so an effect counts only if it is bigger than the spread across households (the stricter rule below n=6).
Tool: `python3 results/sota_memory/stage_table.py '<glob of run_log.jsonl>'`.

Recent-sightings list, the baseline (the workshop session's run1, called `naive` in the code; all|cold):
```
hh_s0  lead 85|82  sick1 44|12  sick 49|21  ret1 75|50  ret 79|68
hh_s1  lead 64|64  sick1 65|37  sick 66|36  ret1 67|50  ret 71|62   (379 questions; weak lead-up)
hh_s2  lead 84|85  sick1 50|20  sick 59|33  ret1 90|92  ret 92|91
```
Degenerate check PASSED 2026-09-23 01:50: the new runner fed the recent-sightings list (`--memory naive --replay-only`) on hh_s0 against the fm cache reproduces
the workshop session's recent-sightings run 496/496 (answer and confidence identical, all cache hits).

## Most recent same-hour sighting pinned to the top of the prompt (`pinned`; launched 01:55, 3 streams, ~30 min expected per household)
The recent-sightings list unchanged, plus the most recent sighting of the object within +-1 h of the query's clock time repeated at the top.
- lead: within +-3 of the recent-sightings list (the pinned line usually agrees with the latest sighting and the routine).
- sick1: day 14 pinned line is the old routine -> no help that day; days 15-16 it is yesterday's sick-routine sighting.
  Cold +10 to +20 over the recent-sightings list.
- sick (17-23): if salience is the failure, cold rises from 21/36/33 to 45-60. This is the main test.
- ret1: day 24's pinned line is a sick-day sighting -> pinned should be WORSE than the recent-sightings list on day 24 (cold -10 to -30),
  recovering by day 26. Pinning buys fast re-learning and pays for it on the return, like a timetable with a one-day memory. If it helps in the spell and hurts on day 24, report it as ONE finding: salience cuts both ways, like the unretracted message.
- If pinned is about equal to the recent-sightings list everywhere, salience is not the lever. The alternative mechanism is visible in the first
  smoke prompt: the model's reasoning quotes the resident card ("Yuki is at her desk from 9:00 to 17:30"). A written routine prior
  may override evidence even when that evidence is salient. Check by reading sick-window wrong answers' reasoning for card quotes.

## Evidence advocate versus routine advocate, with a judge (`debate`) — written ~02:00, before any debate result
One round of role-assigned debate over the recent-sightings list: two sides with FIXED positions (the evidence side argues
where the object was seen on the most recent day it was sighted within an hour of now; the routine side argues where it
has most often been at this hour), then a judge answers in the usual format. 3 calls per question.
Role v1 (free-form sides) was withdrawn after the day-15 smoke: the evidence side argued the routine. Archived at smoke/debate_roles_v1_hh_s0_d15.
Days answered: 11-17, 21-22, 24-28. This subset is EXACT, not an approximation: the recent-sightings list has no LLM writes,
so what the memory holds on any day does not depend on which earlier days were answered.
- lead-up: equal to the recent-sightings list within 3 points; the two sides mostly agree.
- the spell: the sides disagree on most of the sick person's things. If the judge still sides with the routine as often
  as the single call overrides its own evidence, debate adds nothing. My guess: the judge sides with the routine side, because
  the resident card ("at her desk 9:00-17:30") backs that side. Cold gain under +10, not detected at n=3.
- day 24: the evidence side argues a sick-day spot. The judge should be pulled toward the stale record, so a smaller loss than pinning.

## The same debate with the judge told which stage the world is in (`debate_oracle`)
The judge alone sees the residents' messages (sick from day 14, back at work day 24). The two sides argue blind, so their
arguments are identical to the plain debate's, and the difference between the two isolates what the judge does with the
stage information.
- It should approach the start+end-message single call (the recent-sightings list with both messages). The question that matters:
  does it reach the pinned arm in the spell? If being told the stage and hearing both sides still cannot beat simply
  pinning the right line, the failure is salience, not reasoning or detection.


## The recent-sightings list with the residents' descriptions removed (`nocard`) — written 02:05, before launch (launched 02:05)
Every existing arm, told arms included, carries a written daily routine per resident ("works from home. Every day: at the
desk at home from 9 to about 5:30"). It describes the PERSON's routine, not object locations, so it implies rather than
states where things are. It is identical across every arm and every stage: never updated when Yuki falls ill, and still
present in the told arms beside the message. This arm replaces only those lines with "- Yuki (a resident)" /
"- Nora (a resident)". Still present and unchanged: the generic "when the robot is asked" paragraph ("laptop, mug, notebook
and headphones at work") and the reply instruction's "what ... the residents' routine suggest".
Days 11-17, 21-22, 24-28 (exact subset: no LLM writes). Three households, one call per question.
- lead-up (11-13): the card and the record agree, so removing it loses a little real information. Change of 0 to -5.
- the spell (14-17, 21-22): cold rises. Guess +10 to +20 over the recent-sightings list. The written routine is part of the override.
- return (24-28): the card would have been RIGHT again, so removing it costs. Guess -5 on day 24-26.
- The coordinator's prediction (recorded as theirs): helps in the sick days, little in the settled fortnight, because the card
  only harms once it is stale. That is the same finding as the unretracted message, reached a third way.
- If there is no change in the spell, the override is a learned or generic prior, not our sentence, and the existing claims get stronger.
Follow-up ONLY if this shows an effect: the card corrected on day 14 to say she is home unwell.
- Reported split by MOVED vs UNMOVED (`strata.py`). A question counts as moved when the true spot now differs from the
  object's usual spot at that hour in the lead-up, meaning the most frequent true location among lead-up questions about the
  same object within +-1 h. The coordinator's point, recorded as theirs: if removing the card also changes accuracy on
  UNMOVED things, the card was carrying real information rather than only a stale prior. Caution: in the spell only ~15% of
  questions are unmoved (9-24 per household), so that control is thin.
- What a null here can and cannot conclude: it would clear only the per-person routine card. Two written priors stay in the
  prompt: the paragraph naming where work things live, and the reply instruction, which itself asks the model what "the
  residents' routine suggest[s]". Decided in advance (coordinator, 02:10): if this arm shows little, the next removal is that
  instruction wording, NOT a corrected card. Neither variant gets built until this arm lands.
- Which comparison carries the claim (agreed with the coordinator, 02:15): the PAIRED lead-up (days 11-13, where card and
  record agree) against the paired spell. The moved/unmoved split goes underneath as corroboration only. Unmoved questions in
  the spell are reported POOLED across households with their total n, marked as pooled and not as a paired test.
  Classification source: the bank's truth at question time (the base run's `truth` column), identical for every arm.
