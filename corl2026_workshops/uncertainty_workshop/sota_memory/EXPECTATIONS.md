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

## The residents' descriptions kept TRUE for each day (`truecard`) — written ~02:51, before launch (launched 02:52). Six households, hh_s0-5.
Days 14-23: the sick resident's line (the name comes from that household's day-14 message) reads "Every day: home sick at
the moment, resting on the couch in the living room through the day; no work or trips out." That wording is the
simulator's own description of the sick-day event ("Off sick, resting on the couch all day"; schedule: work and trips
removed, rest_couch added). All other days: the original card. Other residents: unchanged. It carries MORE than the start
message ("X is home sick today"): it names the couch. So this is the "accurate written routine" condition, not "told the
stage".
Same days 11-17, 21-22, 24-28. Card-removed is extended to hh_s3-5 so both compare on six households, paired.
Predictions (coordinator's recorded as theirs; mine separate):
- Coordinator: the true card beats both the stale card (the recent-sightings list) and no card in the spell, and beats no
  card on the return. Reading if so: "keep written context current", not "do not give context". If the true card only
  MATCHES no card, the routine text does nothing useful even when accurate.
- Mine: lead-up identical to the recent-sightings list, since the prompts are identical before day 14 (a check, not a
  prediction: any difference there is a bug). Spell: the true card beats the stale card by more than card removal did (cold
  +30 or more), because it names the couch. Return: equal to the recent-sightings list, because the card is the original
  again on day 24 (the prompts differ only in the day's card, so any return cost would come from the model's own
  sick-day sightings).
- Expect shrinkage from three to six households (hh_s0 was +35 alone); report both numbers.

## Rerun noise floor for the whole-log-in-the-prompt memory (written ~03:30, before launch)
The whole-log memory's no-message arm re-run fresh on hh_s0-2, days 11-17, 21-22, 24-28, compared with the existing
chain_person run (prompts verified byte-identical, 16/16 on day 11). This arm has no LLM writes, so the day subset is exact.
- Coordinator (theirs): the floor is LARGER than the recent-sightings list's (~3% of answers changed), because longer
  prompts give batching more to vary over.
- Mine: about the same (~3%), because the floor tracks how marginal each decision is more than prompt length.

## Stage-only card (`stagecard`) — written ~03:46, before launch (launched 03:47). hh_s0-5, same days.
On days 14-23 only the sick resident's line changes, to "Every day: home sick at the moment; not working." No location
named. On all other days the original card. It separates "an accurate card" from "a card that names the couch".
- Mine: it sits between the stale card and the couch card. Cold spell gain about +10 to +15 over the stale card (the
  couch card gave +29); all questions about +5 to +8. Lead-up and return are identical to the baseline by construction.
- If it matches the couch card, accuracy alone carries the effect. If it matches the stale card, the effect was the
  location information.
- Coordinator (theirs; written ~03:48, AFTER the 03:47 launch and BEFORE any stage-card result was read): the stage-only card
  may land near the couch card, by analogy with the whole-log memory's start message (+10.4 first sick days, +26.9 cold,
  against the couch card's +13.9 / +29.3).
- A closer analogue exists on the SAME memory (noted ~03:48, from STORY.md): the recent-sightings list with the start message
  gave +12.9 (se 3.0, n=10) on the first three sick days and +23.5 cold (n=10). That arm keeps the stale card and ADDS a
  message; the stage card REPLACES the card's line. If the stage card lands near +13 / +24, the message and the card are
  two routes to the same information.

## Stale card + start message, re-run in this session (`naive`, told) — written 03:48, before launch (launched 03:48:56). hh_s0-5, same days.
The recent-sightings list with the stale card AND the residents' daily "X is home sick today" messages on days 14-23
(banks_f1 header), generated fresh tonight so it pairs with the card arms on the same households, days and session.
- Mine: close to the stage-only card (within ~3 points on all questions). The prompt then holds two incompatible assertions
  about the same person, and the earlier 10-household arm (+12.9) shows the model prefers the newer, specific one.
- Coordinator (theirs): if the message route and the current-card route agree, the finding is "a stale description can
  be corrected by appending a correction". If the current card is meaningfully better, the finding is "fix the description".
- Wording differs across arms. The message and the stage card are OUR wording; the couch card is the simulator's own
  description. A small difference is not necessarily about the mechanism.

## Fact store with MECHANICAL extraction + the validity-window judge (`facts_zep_mech`) — written 06:28, before launch
Facts are made by rule from each day's sightings: the object's stays that day (spot, from, to), stays under 60 min dropped,
times rounded out to the hour, same-spot overlaps merged. No LLM writes facts. The only LLM call in the write path is the
revision judge (the Graphiti-style policy: ADD / DUPLICATE for new facts, INVALIDATE for old current facts), with the same
prompt as before. hh_s0-2, days 11-17, 21-22, 24-28, hard stop 09:00. It tests whether the judge closes a fact's
validity window when shown a clean contradiction.
- Coordinator (theirs): the judge lags one to two nights, as it did on hh_s0 (0 and 1 invalidations after days 14 and 15).
- Mine: the lag is shorter than before but present. The day-14 facts (couch or coffee table all day) contradict "desk
  09:00-17:00" plainly, so I expect some invalidations on night 14 but not most (under half of the contradicted desk facts),
  and most by night 16. Accuracy: within a few points of the recent-sightings list (the 40 sightings in the prompt dominate).
- Check before trusting: nightly invalidation counts must NOT be constant; spot-check night 14 by hand.
- Smoke (days 0-3, hh_s0, read BEFORE the full launch, so not a result): the judge over-invalidates in the settled period,
  closing 30/30 and 42/48 facts whose only difference was the hours ("desk 00:00-23:00" vs "desk 03:00-24:00"). Not tuned:
  the judge is the thing under test. The full run will show whether it over-invalidates in the lead-up and under-invalidates
  at the break, which would be the opposite of what a validity window is for.
