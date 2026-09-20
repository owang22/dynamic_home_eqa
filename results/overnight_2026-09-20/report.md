# Overnight 2026-09-20: patrol-stream evaluation on situation_sim

**What was built.** `src/baselines/patrol/` replaces the budgeted look economy with a fixed patrol
(`bank.py`), runs the classical beliefs with one free look per question and a logged top probability for
abstaining (`run.py`, `sweep.py`), runs three LLM agents in told / not-told and look on / off arms against
the local vLLM Qwen3.8-27B (`llm.py`, with a prompt-hash cache and a leak check, `leak_check.py`), and pools
everything into the tables and figures here (`summary.py`, `figures.py`). The simulator gained an 8-day,
Tuesday-start episode (`situation_sim.run --days 8 --day0 Tuesday`; the old 5-day output is unchanged
byte for byte). Households: seeds 0-19 in `data/situation_sim/week8/`. Everything is deterministic
(rebuilt bank and rerun log compared with `cmp`; LLM reruns replay from the cache with zero new calls).

**What was run.** Classical: 20 households x patrol every {1, 2, 4, 8} h x look {off, voi, top} x 10
beliefs = 465 024 agent-question records (`classical/`). LLM: households 0-9 at 4 h patrol x 3 memories x
told/not told x look on/off = 120 arm runs (`llm/`), plus a density check (1 h and 8 h, households 0-4, look
on, both told arms, all three memories). 32 610 local calls, 45.7 M prompt tokens, 1.1 M completion tokens,
**hosted spend $0** (no API model was called). Leak check over every prompt: clean (`leak_report.md`).
Everything that ran for more than a minute ran in tmux session `overnight`; the queue scripts
(`run_classical_queue.sh`, `run_llm_queue.sh`, `run_llm_missing.sh`) are resumable.

**Figures:** `figs/fig1_accuracy_per_day_look_off.png`, `figs/fig1_accuracy_per_day_look_on.png`,
`figs/fig2_accuracy_vs_density.png`, `figs/fig3_told_vs_not_told.png`, `figs/fig4_abstain_per_day.png`.
The same numbers are in the tables below; `classical_summary.md`, `llm_summary_p4.md` and
`llm_summary_density.md` hold every table for every density and look mode. Prompt samples for hand review:
`prompt_samples.md`.

## Headline results, against the brief's checklist

1. **Curves that start low, rise, drop on the weekend, recover: not what the simulator produces.**
   Pooled over 20 households at 4 h patrol with no look, every classical agent is flat Wednesday-Friday
   (79-80%), *rises* on Saturday/Sunday (83-87%), and falls back on Monday/Tuesday (77-78%). The reason is
   the truth mix, not the harness: OUT_OF_HOUSE truths are 11-13% of questions on weekdays and 1-2% on
   weekends (people take their things to work), and no classical agent can answer OUT_OF_HOUSE without a
   look (0-10%; Markov1 34% by a coin flip between ON_PERSON and OUT_OF_HOUSE). On in-house spot truths
   alone every agent is ~89% every day. The shift the generator makes (guests, illness, weekend schedules)
   moves things between in-house spots, and a 4-hourly patrol sees those moves before they are asked about.
   I checked this is not a bug three ways: the stream reaches the beliefs (accuracy rises monotonically with
   patrol density, 77% -> 86% for last-seen from 8 h to 1 h), belief differences reach the answer
   (LastObservation and Markov1 disagree on 19 of 224 seed-0 questions, one traced by hand in
   `problems_found.md`), and the per-truth-type columns explain the day pattern exactly.

2. **No learning curve for the classical agents.** With a sighting of every in-house object at most 4 h
   old, every belief answers the last sighting; a week of history is too short for frequency or timetable
   statistics to outvote it. Most-frequent, timetable, smoothed recency, hierarchy backoff and periodic
   persistence are within 1 point of last-seen at every density; Markov1 is 2-4 points above (it puts mass
   on ON_PERSON/OUT_OF_HOUSE), daytype mixture and the Perpetua pair 2-4 below. No belief was tuned.

3. **Patrol density works as expected.** Look off: last-seen 77 / 80 / 84 / 86% at 8 / 4 / 2 / 1 h; every
   agent is monotone and the ordering between agents is the same at every density. With a look the density
   matters much less (last-seen 89-94%): one look at the right room replaces a lot of patrol.

4. **The free look helps every agent, and helps most where confidence was low.** Pooled over agents,
   questions with top probability under 0.4 go from 58% to 73% right after the look, 0.4-0.6 from 55% to
   75%, 0.8-0.95 from 80% to 91%. But the brief's rule — one-step value of information over rooms, argmax,
   no threshold — is nearly useless for a confident belief: its VoI is flat and it picks the room with the
   most spots, finding the object in ~50% of looks; a look at the belief's top room finds it in 87% and
   scores 1-3 points higher (`look top` columns). Both are reported.

5. **Abstaining works for the classical agents and is well targeted.** At threshold 0.5, last-seen abstains
   on 13% of weekday questions and 3-6% of weekend questions and is right on 96-98% of the questions it does
   answer (vs 80% without abstaining); Markov1 abstains on ~45% (its ON_PERSON/OUT_OF_HOUSE tie sits at
   0.33). Perpetua/Perpetua* never abstain (top probability always high). Abstain rate is *lower* on the
   weekend shift days, for the same truth-mix reason as point 1.

6. **LLM agents (Qwen3.8-27B, no thinking, local).** Parse fallback rate 0%. Without the look, naive and
   recent-log memories match last-seen (80%); the routine-summary memory also lands at 80% overall but is
   the only agent that answers ON_PERSON (33-38%) and OUT_OF_HOUSE (15-24%) from evidence rather than a
   coin flip. With the look on, naive/recent ask for a look on 4-7% of questions and gain 1 point; the
   routine-summary agent asks on 12-14%, finds the object in 8-9%, and reaches **85-87%** — the best
   look-on LLM result, 5-7 points above the same agent without a look, but still 4-6 points under the
   classical agents with the VoI look (89-93%), which look on every question.
   The model states 0.85-0.99 confidence on almost everything, so the confidence-threshold abstain route
   never fires (1-5% at every threshold, unchanged from 0.4 to 0.6) and its answered accuracy stays at
   82-89%; outright ABSTAIN answers are 1-4%.

7. **Told vs not told: no effect.** The message is in every told prompt from the shift day's first
   question on (verified per prompt) and in no not-told prompt; per-day accuracies differ by 0-2 points in
   both directions for all three memories (`fig3`, table B3). Recovery after a shift is the same in both
   arms because the model does not act on the message. This is a finding about Qwen3.8-27B without
   thinking, not about the channel.

8. **Nothing above 95% that is not explained.** The 96-98% cells are classical agents with a look at their
   top room on weekend days (residents home, nothing leaves the house, a look at the last-seen room
   confirms). The look reads only the chosen room at the question instant through the same accessor as a
   paid sense; ON_PERSON's pseudo-room is excluded from looks (problems_found.md #2).

## What I would change next

- The question distribution ("uniform over movable objects") makes ~89% of in-house questions trivial for
  last-seen at 4 h patrol. Weighting questions toward objects that moved since the last patrol (the
  "moved in the last 24 h" slice in the tables: 63-73% vs 99-100%) would put the differences between agents
  where they exist.
- A shift that actually breaks the routine for a tracker is "someone leaves the house with things at an
  unusual time"; the generator's guests/illness days mostly move things between in-house spots.
- For the LLM arms: a model with thinking, or a prompt that asks for the look decision separately, so the
  free look is used; and a calibrated confidence (ask for a probability per ranked option, or use the
  look-found signal).

`problems_found.md` lists every bug found and fixed tonight in order; `open_questions.md` lists what was
underspecified, what I assumed, and what still looks odd.


---

# Tables

All numbers pool every household listed in each table's header (per-household record counts are in the summary files). Day columns: `*` = every household shifts that day (weekend), `°` = some households shift (guests or illness).

## A. Classical agents, 20 households

Source: `classical_summary.md` (every density and look mode).

### A1. Accuracy per day, patrol every 4 h, look off

### patrol every 4 h, look off

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 79% | 79% | 74% | 76% | 81% | 72% | 69% | 76% | 78% | 74% | 85% | 0% | 0% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 79% | 79% | 78% | 83% | 87% | 77% | 78% | 80% | 83% | 78% | 89% | 3% | 0% |
| LastObservation | 79% | 79% | 77% | 83% | 87% | 77% | 78% | 80% | 83% | 78% | 89% | 0% | 0% |
| Markov1(a=1,cut=24h,hl=24h) | 82% | 82% | 81% | 83% | 86% | 81% | 81% | 82% | 84% | 81% | 88% | 39% | 34% |
| MostFrequentLocation | 80% | 80% | 77% | 83% | 86% | 77% | 78% | 80% | 83% | 78% | 89% | 0% | 3% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 80% | 80% | 78% | 83% | 87% | 77% | 78% | 81% | 84% | 78% | 89% | 7% | 4% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 79% | 79% | 77% | 82% | 83% | 73% | 75% | 78% | 82% | 76% | 87% | 0% | 0% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 79% | 79% | 77% | 82% | 85% | 74% | 76% | 79% | 82% | 77% | 88% | 0% | 0% |
| SmoothedRecency(hl=6h,freq=24h) | 79% | 80% | 78% | 83% | 87% | 77% | 78% | 80% | 83% | 78% | 89% | 5% | 0% |
| TimetableLookup(bin=1h,days=all) | 80% | 79% | 78% | 83% | 85% | 77% | 78% | 80% | 83% | 78% | 88% | 1% | 9% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 2891 | 63% | 1589 | 99% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 2891 | 69% | 1589 | 100% |
| LastObservation | 2891 | 69% | 1589 | 100% |
| Markov1(a=1,cut=24h,hl=24h) | 2891 | 73% | 1589 | 100% |
| MostFrequentLocation | 2891 | 69% | 1589 | 100% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 2891 | 70% | 1589 | 100% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 2891 | 67% | 1589 | 99% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 2891 | 68% | 1589 | 100% |
| SmoothedRecency(hl=6h,freq=24h) | 2891 | 69% | 1589 | 100% |
| TimetableLookup(bin=1h,days=all) | 2891 | 69% | 1589 | 99% |

Questions by truth type: on_person 75, out_of_house 390, spot 4015
(* every household shifts that day; ° some households do)

### A2. Accuracy per day, patrol every 4 h, look voi (the brief's look rule)

### patrol every 4 h, look voi

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 94% | 92% | 89% | 92% | 92% | 83% | 86% | 90% | 91% | 89% | 95% | 35% | 46% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 86% | 91% | 89% | 96% | 97% | 89% | 89% | 91% | 94% | 88% | 99% | 9% | 24% |
| LastObservation | 92% | 91% | 89% | 92% | 93% | 90% | 90% | 91% | 92% | 90% | 96% | 41% | 53% |
| Markov1(a=1,cut=24h,hl=24h) | 86% | 89% | 88% | 92% | 92% | 90% | 89% | 89% | 91% | 88% | 95% | 59% | 42% |
| MostFrequentLocation | 91% | 91% | 92% | 96% | 97% | 91% | 91% | 93% | 95% | 91% | 99% | 35% | 44% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 92% | 91% | 90% | 94% | 95% | 89% | 89% | 91% | 93% | 90% | 97% | 24% | 43% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 84% | 87% | 84% | 94% | 95% | 84% | 85% | 88% | 92% | 84% | 98% | 0% | 0% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 84% | 87% | 85% | 94% | 96% | 84% | 86% | 88% | 93% | 85% | 98% | 0% | 0% |
| SmoothedRecency(hl=6h,freq=24h) | 90% | 91% | 90% | 96% | 96% | 89% | 89% | 92% | 94% | 90% | 98% | 23% | 36% |
| TimetableLookup(bin=1h,days=all) | 91% | 88% | 88% | 90% | 87% | 84% | 84% | 87% | 88% | 87% | 92% | 44% | 44% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 2891 | 85% | 1589 | 99% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 2891 | 86% | 1589 | 100% |
| LastObservation | 2891 | 86% | 1589 | 100% |
| Markov1(a=1,cut=24h,hl=24h) | 2891 | 84% | 1589 | 100% |
| MostFrequentLocation | 2891 | 89% | 1589 | 100% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 2891 | 87% | 1589 | 100% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 2891 | 81% | 1589 | 100% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 2891 | 81% | 1589 | 100% |
| SmoothedRecency(hl=6h,freq=24h) | 2891 | 87% | 1589 | 100% |
| TimetableLookup(bin=1h,days=all) | 2891 | 81% | 1589 | 99% |

Questions by truth type: on_person 75, out_of_house 390, spot 4015
(* every household shifts that day; ° some households do)

### A3. Accuracy per day, patrol every 4 h, look top (look at the belief's argmax room)

### patrol every 4 h, look top

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 94% | 95% | 90% | 93% | 95% | 88% | 89% | 92% | 93% | 91% | 97% | 20% | 52% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 88% | 90% | 89% | 95% | 96% | 90% | 91% | 91% | 94% | 89% | 99% | 8% | 31% |
| LastObservation | 92% | 92% | 93% | 96% | 96% | 91% | 90% | 93% | 95% | 92% | 98% | 33% | 54% |
| Markov1(a=1,cut=24h,hl=24h) | 90% | 89% | 90% | 94% | 96% | 90% | 89% | 91% | 94% | 89% | 97% | 57% | 38% |
| MostFrequentLocation | 92% | 95% | 91% | 96% | 96% | 89% | 90% | 92% | 95% | 91% | 99% | 31% | 41% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 93% | 93% | 90% | 96% | 97% | 89% | 90% | 92% | 95% | 91% | 98% | 23% | 44% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 85% | 87% | 85% | 94% | 94% | 84% | 85% | 88% | 92% | 85% | 98% | 0% | 0% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 86% | 87% | 85% | 95% | 95% | 84% | 85% | 88% | 92% | 85% | 98% | 0% | 0% |
| SmoothedRecency(hl=6h,freq=24h) | 90% | 90% | 91% | 96% | 97% | 90% | 90% | 92% | 94% | 90% | 99% | 31% | 35% |
| TimetableLookup(bin=1h,days=all) | 91% | 90% | 89% | 92% | 92% | 88% | 88% | 90% | 92% | 89% | 95% | 28% | 47% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 2891 | 88% | 1589 | 100% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 2891 | 87% | 1589 | 100% |
| LastObservation | 2891 | 89% | 1589 | 100% |
| Markov1(a=1,cut=24h,hl=24h) | 2891 | 86% | 1589 | 100% |
| MostFrequentLocation | 2891 | 88% | 1589 | 100% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 2891 | 88% | 1589 | 100% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 2891 | 81% | 1589 | 100% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 2891 | 82% | 1589 | 100% |
| SmoothedRecency(hl=6h,freq=24h) | 2891 | 88% | 1589 | 100% |
| TimetableLookup(bin=1h,days=all) | 2891 | 85% | 1589 | 99% |

Questions by truth type: on_person 75, out_of_house 390, spot 4015
(* every household shifts that day; ° some households do)

### A4. Accuracy vs patrol density

## 2. Accuracy vs patrol density (all days, no abstaining)

### look off

| agent | every 1 h | every 2 h | every 4 h | every 8 h |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 81% | 78% | 76% | 74% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 86% | 84% | 80% | 77% |
| LastObservation | 86% | 84% | 80% | 77% |
| Markov1(a=1,cut=24h,hl=24h) | 90% | 87% | 82% | 77% |
| MostFrequentLocation | 86% | 83% | 80% | 77% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 86% | 84% | 81% | 78% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 83% | 81% | 78% | 76% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 84% | 82% | 79% | 76% |
| SmoothedRecency(hl=6h,freq=24h) | 86% | 84% | 80% | 77% |
| TimetableLookup(bin=1h,days=all) | 88% | 85% | 80% | 77% |

### look top

| agent | every 1 h | every 2 h | every 4 h | every 8 h |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 93% | 93% | 92% | 92% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 93% | 92% | 91% | 90% |
| LastObservation | 94% | 94% | 93% | 92% |
| Markov1(a=1,cut=24h,hl=24h) | 93% | 93% | 91% | 90% |
| MostFrequentLocation | 93% | 93% | 92% | 92% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 94% | 93% | 92% | 92% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 88% | 88% | 88% | 88% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 89% | 88% | 88% | 88% |
| SmoothedRecency(hl=6h,freq=24h) | 93% | 92% | 92% | 92% |
| TimetableLookup(bin=1h,days=all) | 94% | 92% | 90% | 88% |

### look voi

| agent | every 1 h | every 2 h | every 4 h | every 8 h |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 93% | 92% | 90% | 87% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 92% | 92% | 91% | 90% |
| LastObservation | 94% | 93% | 91% | 89% |
| Markov1(a=1,cut=24h,hl=24h) | 93% | 92% | 89% | 87% |
| MostFrequentLocation | 94% | 94% | 93% | 92% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 93% | 92% | 91% | 90% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 88% | 88% | 88% | 87% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 88% | 88% | 88% | 87% |
| SmoothedRecency(hl=6h,freq=24h) | 93% | 92% | 92% | 90% |
| TimetableLookup(bin=1h,days=all) | 93% | 91% | 87% | 83% |

### A5. What the free look is worth

## 3. What the free look is worth (all densities pooled)

| agent | look off | look voi | look top | before-look answer (voi runs) | found by voi look | found by top look |
|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 77% | 90% | 93% | 79% | 55% | 87% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 82% | 91% | 92% | 84% | 57% | 87% |
| LastObservation | 82% | 92% | 93% | 84% | 50% | 88% |
| Markov1(a=1,cut=24h,hl=24h) | 84% | 90% | 92% | 87% | 50% | 87% |
| MostFrequentLocation | 82% | 93% | 93% | 83% | 57% | 87% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 82% | 92% | 93% | 85% | 53% | 88% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 79% | 88% | 88% | 82% | 50% | 88% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 80% | 88% | 88% | 83% | 50% | 88% |
| SmoothedRecency(hl=6h,freq=24h) | 82% | 92% | 92% | 84% | 53% | 88% |
| TimetableLookup(bin=1h,days=all) | 82% | 89% | 91% | 81% | 51% | 85% |

Look gain by confidence before the look (pooled over agents, look-on runs):

| top prob before look | n | acc before look | acc after look |
|---|---|---|---|
| [0.00, 0.40) | 25110 | 57% | 71% |
| [0.40, 0.60) | 21336 | 52% | 74% |
| [0.60, 0.80) | 26523 | 64% | 82% |
| [0.80, 0.95) | 70304 | 81% | 92% |
| [0.95, 1.01) | 215127 | 92% | 96% |

### A6. Abstain rate and answered accuracy per day

## 4. Abstain rate and answered-accuracy per day (look voi for classical agents, look on for LLM agents; all densities pooled)

### outright ABSTAIN answers only (LLM direct route)

| agent | Wed abstain / acc | Thu abstain / acc | Fri abstain / acc | Sat abstain / acc | Sun abstain / acc | Mon abstain / acc | Tue abstain / acc | shift abstain / acc | non-shift abstain / acc | mean score |
|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0% / 94% | 0% / 92% | 0% / 90% | 0% / 92% | 0% / 93% | 0% / 85% | 0% / 87% | 0% / 92% | 0% / 89% | +0.81 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0% / 87% | 0% / 90% | 0% / 90% | 0% / 96% | 0% / 97% | 0% / 89% | 0% / 89% | 0% / 95% | 0% / 89% | +0.82 |
| LastObservation | 0% / 92% | 0% / 91% | 0% / 90% | 0% / 94% | 0% / 94% | 0% / 90% | 0% / 90% | 0% / 93% | 0% / 91% | +0.83 |
| Markov1(a=1,cut=24h,hl=24h) | 0% / 87% | 0% / 89% | 0% / 90% | 0% / 93% | 0% / 94% | 0% / 90% | 0% / 90% | 0% / 92% | 0% / 89% | +0.81 |
| MostFrequentLocation | 0% / 91% | 0% / 92% | 0% / 91% | 0% / 96% | 0% / 97% | 0% / 91% | 0% / 92% | 0% / 95% | 0% / 91% | +0.86 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0% / 92% | 0% / 91% | 0% / 90% | 0% / 95% | 0% / 95% | 0% / 90% | 0% / 89% | 0% / 94% | 0% / 90% | +0.83 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 0% / 84% | 0% / 87% | 0% / 85% | 0% / 94% | 0% / 95% | 0% / 85% | 0% / 85% | 0% / 92% | 0% / 85% | +0.76 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 0% / 84% | 0% / 87% | 0% / 85% | 0% / 94% | 0% / 96% | 0% / 85% | 0% / 85% | 0% / 92% | 0% / 85% | +0.76 |
| SmoothedRecency(hl=6h,freq=24h) | 0% / 91% | 0% / 91% | 0% / 91% | 0% / 96% | 0% / 96% | 0% / 89% | 0% / 89% | 0% / 94% | 0% / 90% | +0.84 |
| TimetableLookup(bin=1h,days=all) | 0% / 90% | 0% / 89% | 0% / 89% | 0% / 91% | 0% / 91% | 0% / 85% | 0% / 86% | 0% / 90% | 0% / 87% | +0.77 |

### threshold 0.4 on the top probability / stated confidence, plus outright ABSTAIN answers

| agent | Wed abstain / acc | Thu abstain / acc | Fri abstain / acc | Sat abstain / acc | Sun abstain / acc | Mon abstain / acc | Tue abstain / acc | shift abstain / acc | non-shift abstain / acc | mean score |
|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 10% / 96% | 9% / 96% | 9% / 94% | 4% / 94% | 3% / 95% | 10% / 90% | 10% / 92% | 5% / 95% | 10% / 94% | +0.81 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 8% / 92% | 7% / 94% | 7% / 94% | 2% / 97% | 2% / 98% | 7% / 93% | 7% / 94% | 3% / 97% | 8% / 93% | +0.84 |
| LastObservation | 10% / 95% | 9% / 95% | 10% / 95% | 4% / 96% | 2% / 95% | 9% / 94% | 9% / 94% | 5% / 95% | 10% / 95% | +0.83 |
| Markov1(a=1,cut=24h,hl=24h) | 39% / 95% | 30% / 95% | 29% / 97% | 27% / 98% | 22% / 98% | 26% / 96% | 26% / 96% | 26% / 97% | 31% / 96% | +0.66 |
| MostFrequentLocation | 11% / 97% | 9% / 96% | 9% / 96% | 4% / 98% | 2% / 98% | 9% / 95% | 9% / 95% | 5% / 97% | 9% / 96% | +0.86 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 11% / 97% | 8% / 95% | 9% / 95% | 4% / 97% | 2% / 96% | 8% / 93% | 8% / 93% | 4% / 96% | 9% / 94% | +0.84 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 0% / 84% | 0% / 87% | 0% / 85% | 0% / 94% | 0% / 95% | 0% / 85% | 1% / 86% | 0% / 92% | 0% / 85% | +0.76 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 0% / 84% | 0% / 87% | 0% / 85% | 0% / 94% | 0% / 96% | 0% / 85% | 1% / 86% | 0% / 93% | 0% / 85% | +0.76 |
| SmoothedRecency(hl=6h,freq=24h) | 11% / 95% | 9% / 95% | 10% / 96% | 3% / 98% | 3% / 98% | 10% / 95% | 9% / 94% | 5% / 97% | 10% / 95% | +0.84 |
| TimetableLookup(bin=1h,days=all) | 13% / 95% | 14% / 95% | 14% / 96% | 11% / 98% | 10% / 96% | 15% / 94% | 16% / 94% | 11% / 96% | 15% / 95% | +0.79 |

### threshold 0.5 on the top probability / stated confidence, plus outright ABSTAIN answers

| agent | Wed abstain / acc | Thu abstain / acc | Fri abstain / acc | Sat abstain / acc | Sun abstain / acc | Mon abstain / acc | Tue abstain / acc | shift abstain / acc | non-shift abstain / acc | mean score |
|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 13% / 98% | 13% / 98% | 12% / 96% | 5% / 95% | 4% / 96% | 14% / 93% | 13% / 94% | 7% / 96% | 13% / 96% | +0.82 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 10% / 94% | 9% / 95% | 9% / 95% | 3% / 98% | 2% / 98% | 10% / 95% | 9% / 95% | 5% / 98% | 10% / 95% | +0.85 |
| LastObservation | 14% / 97% | 13% / 97% | 14% / 97% | 5% / 96% | 3% / 96% | 14% / 96% | 12% / 96% | 7% / 96% | 14% / 97% | +0.83 |
| Markov1(a=1,cut=24h,hl=24h) | 47% / 100% | 43% / 100% | 41% / 99% | 36% / 99% | 31% / 99% | 39% / 99% | 38% / 99% | 36% / 99% | 42% / 99% | +0.60 |
| MostFrequentLocation | 15% / 98% | 12% / 97% | 12% / 98% | 5% / 99% | 3% / 99% | 12% / 97% | 11% / 96% | 6% / 98% | 13% / 97% | +0.86 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 14% / 98% | 12% / 97% | 12% / 97% | 4% / 97% | 3% / 97% | 13% / 95% | 10% / 94% | 6% / 97% | 12% / 96% | +0.84 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 0% / 84% | 0% / 87% | 1% / 85% | 0% / 95% | 1% / 96% | 1% / 85% | 2% / 87% | 0% / 93% | 1% / 85% | +0.76 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 0% / 84% | 0% / 87% | 1% / 86% | 0% / 95% | 0% / 96% | 1% / 86% | 1% / 86% | 0% / 93% | 1% / 85% | +0.76 |
| SmoothedRecency(hl=6h,freq=24h) | 12% / 96% | 10% / 96% | 11% / 96% | 4% / 98% | 3% / 98% | 12% / 96% | 10% / 95% | 5% / 97% | 11% / 96% | +0.85 |
| TimetableLookup(bin=1h,days=all) | 21% / 98% | 22% / 97% | 22% / 97% | 15% / 98% | 15% / 97% | 24% / 97% | 22% / 96% | 17% / 97% | 22% / 97% | +0.76 |

### threshold 0.6 on the top probability / stated confidence, plus outright ABSTAIN answers

| agent | Wed abstain / acc | Thu abstain / acc | Fri abstain / acc | Sat abstain / acc | Sun abstain / acc | Mon abstain / acc | Tue abstain / acc | shift abstain / acc | non-shift abstain / acc | mean score |
|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 13% / 98% | 13% / 98% | 13% / 96% | 5% / 95% | 4% / 96% | 15% / 94% | 14% / 94% | 7% / 96% | 14% / 96% | +0.82 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 11% / 95% | 9% / 96% | 11% / 96% | 3% / 98% | 3% / 99% | 11% / 96% | 10% / 95% | 5% / 98% | 10% / 95% | +0.85 |
| LastObservation | 14% / 97% | 13% / 97% | 14% / 97% | 5% / 96% | 3% / 96% | 14% / 96% | 13% / 96% | 7% / 96% | 14% / 97% | +0.83 |
| Markov1(a=1,cut=24h,hl=24h) | 50% / 100% | 46% / 100% | 47% / 100% | 42% / 99% | 37% / 100% | 46% / 100% | 45% / 99% | 42% / 100% | 47% / 100% | +0.55 |
| MostFrequentLocation | 16% / 98% | 13% / 98% | 13% / 98% | 5% / 99% | 4% / 99% | 13% / 98% | 12% / 97% | 7% / 99% | 14% / 98% | +0.86 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 16% / 98% | 12% / 97% | 12% / 97% | 4% / 97% | 3% / 97% | 13% / 96% | 11% / 95% | 6% / 97% | 13% / 96% | +0.84 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 1% / 84% | 1% / 88% | 2% / 87% | 1% / 95% | 1% / 96% | 2% / 86% | 3% / 88% | 1% / 93% | 2% / 86% | +0.77 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 1% / 84% | 1% / 88% | 3% / 87% | 1% / 95% | 1% / 96% | 3% / 87% | 2% / 87% | 1% / 94% | 2% / 86% | +0.77 |
| SmoothedRecency(hl=6h,freq=24h) | 12% / 96% | 11% / 96% | 12% / 97% | 4% / 98% | 3% / 98% | 12% / 96% | 11% / 95% | 6% / 98% | 12% / 96% | +0.85 |
| TimetableLookup(bin=1h,days=all) | 26% / 99% | 27% / 98% | 28% / 98% | 22% / 98% | 21% / 98% | 29% / 98% | 28% / 97% | 23% / 98% | 28% / 98% | +0.71 |

## B. LLM agents (Qwen3.8-27B, local) next to the classical agents on the same 4 h banks

Source: `llm_summary_p4.md`.

### B1. Accuracy per day, look off

### patrol every 4 h, look off

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 79% | 79% | 77% | 73% | 83% | 71% | 65% | 75% | 77% | 74% | 84% | 0% | 0% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 79% | 79% | 79% | 81% | 88% | 76% | 77% | 80% | 82% | 78% | 89% | 0% | 0% |
| LastObservation | 79% | 79% | 79% | 81% | 88% | 76% | 78% | 80% | 82% | 78% | 89% | 0% | 0% |
| Markov1(a=1,cut=24h,hl=24h) | 82% | 83% | 81% | 80% | 87% | 79% | 80% | 82% | 83% | 81% | 88% | 21% | 33% |
| MostFrequentLocation | 81% | 79% | 79% | 81% | 87% | 76% | 77% | 80% | 82% | 78% | 89% | 0% | 3% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 81% | 80% | 79% | 81% | 88% | 76% | 78% | 80% | 82% | 79% | 89% | 7% | 4% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 79% | 79% | 78% | 80% | 83% | 71% | 75% | 78% | 80% | 76% | 87% | 0% | 0% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 79% | 79% | 79% | 80% | 86% | 71% | 75% | 79% | 81% | 77% | 88% | 0% | 0% |
| SmoothedRecency(hl=6h,freq=24h) | 79% | 79% | 79% | 81% | 88% | 76% | 78% | 80% | 82% | 78% | 89% | 3% | 0% |
| TimetableLookup(bin=1h,days=all) | 82% | 79% | 80% | 81% | 85% | 75% | 77% | 80% | 82% | 78% | 88% | 0% | 10% |
| llm_naive/not_told/look_off | 82% | 82% | 78% | 84% | 88% | 75% | 75% | 80% | 83% | 78% | 90% | 21% | 4% |
| llm_naive/told/look_off | 81% | 81% | 78% | 82% | 88% | 76% | 77% | 80% | 82% | 78% | 89% | 31% | 4% |
| llm_recent/not_told/look_off | 78% | 81% | 78% | 81% | 87% | 74% | 76% | 79% | 82% | 77% | 88% | 20% | 7% |
| llm_recent/told/look_off | 81% | 80% | 79% | 82% | 86% | 75% | 78% | 80% | 82% | 79% | 88% | 26% | 6% |
| llm_summary/not_told/look_off | 82% | 81% | 81% | 80% | 85% | 77% | 73% | 80% | 81% | 79% | 86% | 38% | 24% |
| llm_summary/told/look_off | 84% | 81% | 79% | 82% | 87% | 75% | 74% | 80% | 82% | 78% | 87% | 33% | 15% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 1451 | 63% | 789 | 99% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 1451 | 69% | 789 | 100% |
| LastObservation | 1451 | 69% | 789 | 100% |
| Markov1(a=1,cut=24h,hl=24h) | 1451 | 72% | 789 | 100% |
| MostFrequentLocation | 1451 | 69% | 789 | 100% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 1451 | 70% | 789 | 100% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 1451 | 66% | 789 | 99% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 1451 | 67% | 789 | 100% |
| SmoothedRecency(hl=6h,freq=24h) | 1451 | 69% | 789 | 100% |
| TimetableLookup(bin=1h,days=all) | 1451 | 69% | 789 | 100% |
| llm_naive/not_told/look_off | 1022 | 70% | 546 | 100% |
| llm_naive/told/look_off | 1451 | 70% | 789 | 100% |
| llm_recent/not_told/look_off | 1318 | 68% | 698 | 100% |
| llm_recent/told/look_off | 1297 | 69% | 719 | 100% |
| llm_summary/not_told/look_off | 1451 | 69% | 789 | 100% |
| llm_summary/told/look_off | 1297 | 70% | 719 | 99% |

Questions by truth type: on_person 27, out_of_house 198, spot 1929
(* every household shifts that day; ° some households do)

### B2. Accuracy per day, LLM with the look on (`look llm`) and classical `look voi`

### patrol every 4 h, look llm

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| llm_naive/not_told/look_on | 83% | 81% | 81% | 84% | 88% | 75% | 76% | 81% | 83% | 79% | 89% | 26% | 7% |
| llm_naive/told/look_on | 84% | 81% | 80% | 82% | 89% | 77% | 78% | 82% | 83% | 80% | 90% | 31% | 8% |
| llm_recent/not_told/look_on | 83% | 82% | 80% | 82% | 85% | 79% | 78% | 81% | 82% | 81% | 89% | 26% | 5% |
| llm_recent/told/look_on | 83% | 81% | 79% | 83% | 86% | 78% | 79% | 81% | 83% | 80% | 89% | 22% | 9% |
| llm_summary/not_told/look_on | 84% | 87% | 88% | 84% | 89% | 82% | 84% | 85% | 86% | 85% | 90% | 55% | 43% |
| llm_summary/told/look_on | 85% | 85% | 88% | 86% | 92% | 83% | 88% | 87% | 88% | 86% | 92% | 70% | 39% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| llm_naive/not_told/look_on | 1164 | 71% | 628 | 100% |
| llm_naive/told/look_on | 1451 | 72% | 789 | 100% |
| llm_recent/not_told/look_on | 1311 | 71% | 705 | 100% |
| llm_recent/told/look_on | 1297 | 71% | 719 | 100% |
| llm_summary/not_told/look_on | 1451 | 78% | 789 | 99% |
| llm_summary/told/look_on | 1297 | 79% | 719 | 100% |

Questions by truth type: on_person 27, out_of_house 183, spot 1843
(* every household shifts that day; ° some households do)

### patrol every 4 h, look voi

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 93% | 92% | 91% | 91% | 92% | 84% | 86% | 90% | 91% | 89% | 95% | 38% | 45% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 86% | 91% | 88% | 95% | 97% | 88% | 88% | 90% | 93% | 88% | 99% | 10% | 20% |
| LastObservation | 90% | 92% | 92% | 90% | 94% | 88% | 89% | 91% | 91% | 90% | 96% | 41% | 50% |
| Markov1(a=1,cut=24h,hl=24h) | 84% | 90% | 91% | 89% | 92% | 90% | 88% | 89% | 90% | 88% | 95% | 55% | 41% |
| MostFrequentLocation | 90% | 91% | 92% | 95% | 97% | 90% | 92% | 92% | 94% | 91% | 98% | 28% | 43% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 91% | 91% | 91% | 92% | 95% | 88% | 89% | 91% | 92% | 90% | 97% | 17% | 41% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 82% | 87% | 87% | 93% | 96% | 83% | 85% | 88% | 91% | 84% | 98% | 0% | 0% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 83% | 87% | 87% | 93% | 96% | 83% | 85% | 88% | 91% | 85% | 98% | 0% | 0% |
| SmoothedRecency(hl=6h,freq=24h) | 89% | 92% | 91% | 95% | 97% | 89% | 88% | 91% | 93% | 90% | 98% | 24% | 36% |
| TimetableLookup(bin=1h,days=all) | 88% | 88% | 90% | 90% | 88% | 82% | 82% | 87% | 88% | 86% | 92% | 45% | 43% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 1451 | 85% | 789 | 99% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 1451 | 85% | 789 | 100% |
| LastObservation | 1451 | 86% | 789 | 100% |
| Markov1(a=1,cut=24h,hl=24h) | 1451 | 83% | 789 | 100% |
| MostFrequentLocation | 1451 | 88% | 789 | 100% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 1451 | 86% | 789 | 100% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 1451 | 81% | 789 | 100% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 1451 | 81% | 789 | 100% |
| SmoothedRecency(hl=6h,freq=24h) | 1451 | 87% | 789 | 100% |
| TimetableLookup(bin=1h,days=all) | 1451 | 80% | 789 | 99% |

Questions by truth type: on_person 29, out_of_house 206, spot 2005
(* every household shifts that day; ° some households do)

### B3. Told vs not told

## 5. Told vs not told, per day (LLM agents; hint message in the prompt from each shift day's first question on)

| agent | Wed° told / not | Thu° told / not | Fri° told / not | Sat* told / not | Sun* told / not | Mon° told / not | Tue° told / not | all told / not | shift told / not | non-shift told / not |
|---|---|---|---|---|---|---|---|---|---|---|
| llm_naive/look_off | 81% / 82% | 81% / 82% | 78% / 78% | 82% / 84% | 88% / 88% | 76% / 75% | 77% / 75% | 80% / 80% | 82% / 83% | 78% / 78% |
| llm_naive/look_on | 84% / 83% | 81% / 81% | 80% / 81% | 82% / 84% | 89% / 88% | 77% / 75% | 78% / 76% | 82% / 81% | 83% / 83% | 80% / 79% |
| llm_recent/look_off | 81% / 78% | 80% / 81% | 79% / 78% | 82% / 81% | 86% / 87% | 75% / 74% | 78% / 76% | 80% / 79% | 82% / 82% | 79% / 77% |
| llm_recent/look_on | 83% / 83% | 81% / 82% | 79% / 80% | 83% / 82% | 86% / 85% | 78% / 79% | 79% / 78% | 81% / 81% | 83% / 82% | 80% / 81% |
| llm_summary/look_off | 84% / 82% | 81% / 81% | 79% / 81% | 82% / 80% | 87% / 85% | 75% / 77% | 74% / 73% | 80% / 80% | 82% / 81% | 78% / 79% |
| llm_summary/look_on | 85% / 84% | 85% / 87% | 88% / 88% | 86% / 84% | 92% / 89% | 83% / 82% | 88% / 84% | 87% / 85% | 88% / 86% | 86% / 85% |

LLM parse fallbacks and look requests:

| agent | n | fallback | asked for a look | look found it | direct ABSTAIN |
|---|---|---|---|---|---|
| llm_naive/not_told/look_off | 1568 | 0% | 0% | 0% | 1% |
| llm_naive/not_told/look_on | 1792 | 0% | 6% | 2% | 3% |
| llm_naive/told/look_off | 2240 | 0% | 0% | 0% | 0% |
| llm_naive/told/look_on | 2240 | 0% | 7% | 2% | 3% |
| llm_recent/not_told/look_off | 2016 | 0% | 0% | 0% | 4% |
| llm_recent/not_told/look_on | 2016 | 0% | 4% | 1% | 2% |
| llm_recent/told/look_off | 2016 | 0% | 0% | 0% | 4% |
| llm_recent/told/look_on | 2016 | 0% | 4% | 0% | 2% |
| llm_summary/not_told/look_off | 2240 | 0% | 0% | 0% | 2% |
| llm_summary/not_told/look_on | 2240 | 0% | 12% | 8% | 1% |
| llm_summary/told/look_off | 2016 | 0% | 0% | 0% | 2% |
| llm_summary/told/look_on | 2016 | 0% | 14% | 9% | 1% |

### B4. Abstain: outright ABSTAIN answers and confidence thresholds

## 4. Abstain rate and answered-accuracy per day (look voi for classical agents, look on for LLM agents; all densities pooled)

### outright ABSTAIN answers only (LLM direct route)

| agent | Wed abstain / acc | Thu abstain / acc | Fri abstain / acc | Sat abstain / acc | Sun abstain / acc | Mon abstain / acc | Tue abstain / acc | shift abstain / acc | non-shift abstain / acc | mean score |
|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0% / 93% | 0% / 92% | 0% / 91% | 0% / 91% | 0% / 92% | 0% / 84% | 0% / 86% | 0% / 91% | 0% / 89% | +0.80 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0% / 86% | 0% / 91% | 0% / 88% | 0% / 95% | 0% / 97% | 0% / 88% | 0% / 88% | 0% / 93% | 0% / 88% | +0.81 |
| LastObservation | 0% / 90% | 0% / 92% | 0% / 92% | 0% / 90% | 0% / 94% | 0% / 88% | 0% / 89% | 0% / 91% | 0% / 90% | +0.81 |
| Markov1(a=1,cut=24h,hl=24h) | 0% / 84% | 0% / 90% | 0% / 91% | 0% / 89% | 0% / 92% | 0% / 90% | 0% / 88% | 0% / 90% | 0% / 88% | +0.78 |
| MostFrequentLocation | 0% / 90% | 0% / 91% | 0% / 92% | 0% / 95% | 0% / 97% | 0% / 90% | 0% / 92% | 0% / 94% | 0% / 91% | +0.85 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0% / 91% | 0% / 91% | 0% / 91% | 0% / 92% | 0% / 95% | 0% / 88% | 0% / 89% | 0% / 92% | 0% / 90% | +0.82 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 0% / 82% | 0% / 87% | 0% / 87% | 0% / 93% | 0% / 96% | 0% / 83% | 0% / 85% | 0% / 91% | 0% / 84% | +0.75 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 0% / 83% | 0% / 87% | 0% / 87% | 0% / 93% | 0% / 96% | 0% / 83% | 0% / 85% | 0% / 91% | 0% / 85% | +0.75 |
| SmoothedRecency(hl=6h,freq=24h) | 0% / 89% | 0% / 92% | 0% / 91% | 0% / 95% | 0% / 97% | 0% / 89% | 0% / 88% | 0% / 93% | 0% / 90% | +0.83 |
| TimetableLookup(bin=1h,days=all) | 0% / 88% | 0% / 88% | 0% / 90% | 0% / 90% | 0% / 88% | 0% / 82% | 0% / 82% | 0% / 88% | 0% / 86% | +0.74 |
| llm_naive/not_told/look_on | 4% / 86% | 2% / 83% | 4% / 84% | 0% / 84% | 0% / 88% | 6% / 80% | 3% / 78% | 2% / 85% | 4% / 82% | +0.65 |
| llm_naive/told/look_on | 3% / 86% | 3% / 84% | 5% / 84% | 1% / 82% | 0% / 89% | 6% / 82% | 2% / 80% | 2% / 85% | 4% / 84% | +0.66 |
| llm_recent/not_told/look_on | 3% / 85% | 2% / 84% | 3% / 82% | 0% / 82% | 1% / 86% | 4% / 82% | 3% / 81% | 2% / 84% | 3% / 83% | +0.65 |
| llm_recent/told/look_on | 3% / 86% | 2% / 82% | 4% / 82% | 0% / 83% | 0% / 87% | 5% / 82% | 2% / 81% | 2% / 84% | 3% / 82% | +0.65 |
| llm_summary/not_told/look_on | 4% / 87% | 1% / 87% | 1% / 88% | 1% / 84% | 0% / 89% | 1% / 83% | 2% / 86% | 1% / 86% | 2% / 87% | +0.72 |
| llm_summary/told/look_on | 4% / 88% | 1% / 87% | 2% / 89% | 1% / 87% | 0% / 92% | 0% / 84% | 2% / 89% | 1% / 88% | 2% / 88% | +0.75 |

### threshold 0.4 on the top probability / stated confidence, plus outright ABSTAIN answers

| agent | Wed abstain / acc | Thu abstain / acc | Fri abstain / acc | Sat abstain / acc | Sun abstain / acc | Mon abstain / acc | Tue abstain / acc | shift abstain / acc | non-shift abstain / acc | mean score |
|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 12% / 96% | 9% / 97% | 9% / 96% | 5% / 92% | 2% / 94% | 10% / 90% | 11% / 90% | 6% / 94% | 10% / 93% | +0.80 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 10% / 93% | 7% / 94% | 6% / 93% | 2% / 96% | 1% / 97% | 8% / 93% | 7% / 93% | 4% / 96% | 8% / 93% | +0.83 |
| LastObservation | 12% / 95% | 9% / 96% | 11% / 98% | 6% / 94% | 2% / 94% | 10% / 93% | 10% / 93% | 6% / 94% | 11% / 95% | +0.82 |
| Markov1(a=1,cut=24h,hl=24h) | 48% / 95% | 36% / 95% | 35% / 100% | 36% / 96% | 28% / 98% | 31% / 95% | 33% / 95% | 33% / 96% | 37% / 96% | +0.60 |
| MostFrequentLocation | 12% / 96% | 9% / 95% | 10% / 97% | 5% / 98% | 2% / 98% | 8% / 95% | 9% / 95% | 5% / 96% | 10% / 96% | +0.85 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 13% / 97% | 9% / 96% | 9% / 96% | 5% / 96% | 2% / 96% | 8% / 92% | 8% / 93% | 5% / 95% | 10% / 95% | +0.83 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 0% / 82% | 0% / 87% | 0% / 87% | 0% / 93% | 0% / 96% | 0% / 83% | 0% / 85% | 0% / 91% | 0% / 85% | +0.75 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 0% / 83% | 0% / 87% | 0% / 87% | 0% / 93% | 0% / 96% | 0% / 83% | 0% / 85% | 0% / 91% | 0% / 85% | +0.75 |
| SmoothedRecency(hl=6h,freq=24h) | 12% / 94% | 9% / 95% | 8% / 95% | 4% / 97% | 2% / 98% | 10% / 93% | 9% / 94% | 5% / 96% | 10% / 94% | +0.83 |
| TimetableLookup(bin=1h,days=all) | 16% / 95% | 17% / 96% | 16% / 96% | 13% / 97% | 14% / 95% | 18% / 94% | 20% / 93% | 14% / 95% | 18% / 95% | +0.76 |
| llm_naive/not_told/look_on | 4% / 87% | 2% / 83% | 4% / 84% | 0% / 84% | 0% / 88% | 7% / 81% | 3% / 78% | 2% / 85% | 4% / 83% | +0.65 |
| llm_naive/told/look_on | 3% / 87% | 3% / 84% | 5% / 84% | 1% / 82% | 0% / 89% | 6% / 82% | 3% / 81% | 2% / 85% | 4% / 84% | +0.66 |
| llm_recent/not_told/look_on | 3% / 85% | 2% / 84% | 3% / 82% | 0% / 82% | 1% / 86% | 4% / 82% | 3% / 81% | 2% / 84% | 3% / 83% | +0.65 |
| llm_recent/told/look_on | 3% / 86% | 2% / 82% | 4% / 82% | 0% / 83% | 0% / 87% | 5% / 82% | 2% / 81% | 2% / 84% | 3% / 82% | +0.65 |
| llm_summary/not_told/look_on | 4% / 87% | 1% / 87% | 1% / 88% | 1% / 84% | 0% / 89% | 1% / 83% | 2% / 86% | 1% / 86% | 2% / 87% | +0.72 |
| llm_summary/told/look_on | 4% / 88% | 1% / 87% | 2% / 89% | 1% / 87% | 0% / 92% | 1% / 84% | 2% / 90% | 1% / 88% | 3% / 88% | +0.75 |

### threshold 0.5 on the top probability / stated confidence, plus outright ABSTAIN answers

| agent | Wed abstain / acc | Thu abstain / acc | Fri abstain / acc | Sat abstain / acc | Sun abstain / acc | Mon abstain / acc | Tue abstain / acc | shift abstain / acc | non-shift abstain / acc | mean score |
|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 14% / 97% | 12% / 98% | 11% / 97% | 5% / 93% | 2% / 94% | 14% / 93% | 13% / 91% | 7% / 94% | 13% / 95% | +0.80 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 11% / 94% | 8% / 95% | 8% / 95% | 3% / 97% | 1% / 97% | 11% / 94% | 8% / 94% | 5% / 97% | 9% / 94% | +0.84 |
| LastObservation | 14% / 96% | 12% / 98% | 12% / 98% | 6% / 94% | 2% / 94% | 14% / 95% | 13% / 95% | 8% / 95% | 13% / 96% | +0.82 |
| Markov1(a=1,cut=24h,hl=24h) | 57% / 100% | 49% / 99% | 49% / 100% | 44% / 98% | 38% / 98% | 45% / 98% | 45% / 97% | 44% / 98% | 49% / 99% | +0.52 |
| MostFrequentLocation | 16% / 98% | 12% / 97% | 11% / 97% | 5% / 98% | 2% / 98% | 11% / 95% | 11% / 96% | 7% / 98% | 12% / 97% | +0.85 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 16% / 98% | 11% / 97% | 10% / 96% | 5% / 96% | 2% / 96% | 12% / 94% | 9% / 93% | 6% / 96% | 12% / 96% | +0.83 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 0% / 82% | 0% / 87% | 1% / 87% | 1% / 94% | 0% / 96% | 0% / 83% | 1% / 85% | 0% / 92% | 0% / 85% | +0.75 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 0% / 83% | 0% / 87% | 1% / 87% | 1% / 94% | 0% / 96% | 1% / 84% | 1% / 86% | 1% / 92% | 0% / 85% | +0.76 |
| SmoothedRecency(hl=6h,freq=24h) | 12% / 94% | 10% / 96% | 9% / 96% | 4% / 97% | 2% / 98% | 11% / 94% | 10% / 95% | 6% / 97% | 11% / 95% | +0.84 |
| TimetableLookup(bin=1h,days=all) | 25% / 98% | 24% / 97% | 24% / 98% | 19% / 97% | 19% / 96% | 26% / 95% | 27% / 94% | 21% / 96% | 26% / 97% | +0.71 |
| llm_naive/not_told/look_on | 5% / 87% | 2% / 83% | 4% / 84% | 1% / 84% | 1% / 88% | 7% / 81% | 3% / 78% | 2% / 85% | 4% / 83% | +0.65 |
| llm_naive/told/look_on | 3% / 87% | 3% / 84% | 5% / 84% | 1% / 83% | 1% / 89% | 7% / 83% | 3% / 81% | 2% / 85% | 4% / 84% | +0.67 |
| llm_recent/not_told/look_on | 3% / 85% | 3% / 84% | 3% / 82% | 1% / 82% | 1% / 87% | 4% / 82% | 3% / 81% | 3% / 84% | 3% / 83% | +0.65 |
| llm_recent/told/look_on | 3% / 86% | 2% / 82% | 4% / 82% | 1% / 83% | 1% / 87% | 5% / 82% | 2% / 81% | 2% / 85% | 3% / 82% | +0.65 |
| llm_summary/not_told/look_on | 4% / 87% | 1% / 87% | 1% / 88% | 1% / 84% | 1% / 89% | 1% / 83% | 2% / 86% | 1% / 86% | 2% / 87% | +0.72 |
| llm_summary/told/look_on | 5% / 89% | 1% / 87% | 2% / 89% | 1% / 87% | 1% / 92% | 1% / 84% | 3% / 90% | 1% / 89% | 3% / 88% | +0.75 |

### threshold 0.6 on the top probability / stated confidence, plus outright ABSTAIN answers

| agent | Wed abstain / acc | Thu abstain / acc | Fri abstain / acc | Sat abstain / acc | Sun abstain / acc | Mon abstain / acc | Tue abstain / acc | shift abstain / acc | non-shift abstain / acc | mean score |
|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 14% / 97% | 12% / 98% | 11% / 97% | 6% / 93% | 2% / 95% | 15% / 94% | 13% / 92% | 8% / 95% | 13% / 95% | +0.81 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 13% / 96% | 8% / 95% | 9% / 96% | 3% / 97% | 2% / 98% | 12% / 95% | 9% / 94% | 6% / 97% | 10% / 95% | +0.84 |
| LastObservation | 14% / 96% | 12% / 98% | 12% / 98% | 6% / 94% | 2% / 94% | 14% / 95% | 13% / 95% | 8% / 95% | 13% / 96% | +0.82 |
| Markov1(a=1,cut=24h,hl=24h) | 58% / 100% | 53% / 100% | 55% / 100% | 51% / 99% | 46% / 99% | 53% / 100% | 52% / 99% | 51% / 99% | 54% / 100% | +0.47 |
| MostFrequentLocation | 17% / 98% | 13% / 98% | 12% / 98% | 6% / 98% | 3% / 98% | 13% / 96% | 11% / 96% | 7% / 98% | 14% / 97% | +0.85 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 16% / 98% | 12% / 97% | 11% / 97% | 5% / 96% | 2% / 96% | 13% / 95% | 10% / 94% | 7% / 96% | 13% / 96% | +0.83 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 1% / 84% | 1% / 88% | 4% / 90% | 1% / 94% | 0% / 96% | 2% / 85% | 3% / 87% | 1% / 92% | 2% / 86% | +0.77 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 1% / 84% | 0% / 87% | 4% / 90% | 1% / 94% | 0% / 96% | 3% / 86% | 2% / 87% | 1% / 92% | 2% / 86% | +0.77 |
| SmoothedRecency(hl=6h,freq=24h) | 13% / 95% | 11% / 97% | 9% / 96% | 4% / 98% | 2% / 98% | 12% / 95% | 11% / 95% | 6% / 97% | 11% / 96% | +0.84 |
| TimetableLookup(bin=1h,days=all) | 29% / 98% | 30% / 98% | 32% / 97% | 26% / 98% | 26% / 97% | 32% / 96% | 34% / 96% | 28% / 97% | 32% / 97% | +0.66 |
| llm_naive/not_told/look_on | 5% / 87% | 2% / 83% | 4% / 84% | 1% / 84% | 1% / 88% | 7% / 81% | 3% / 78% | 2% / 85% | 4% / 83% | +0.65 |
| llm_naive/told/look_on | 3% / 87% | 3% / 84% | 5% / 84% | 1% / 83% | 1% / 89% | 7% / 83% | 3% / 81% | 2% / 85% | 4% / 84% | +0.67 |
| llm_recent/not_told/look_on | 3% / 85% | 3% / 84% | 3% / 82% | 1% / 82% | 1% / 87% | 4% / 82% | 3% / 81% | 3% / 84% | 3% / 83% | +0.65 |
| llm_recent/told/look_on | 3% / 86% | 2% / 82% | 4% / 82% | 1% / 83% | 1% / 87% | 5% / 82% | 2% / 81% | 2% / 85% | 3% / 82% | +0.65 |
| llm_summary/not_told/look_on | 4% / 87% | 1% / 87% | 1% / 88% | 1% / 84% | 1% / 89% | 1% / 83% | 2% / 86% | 1% / 86% | 2% / 87% | +0.72 |
| llm_summary/told/look_on | 5% / 89% | 1% / 87% | 2% / 89% | 1% / 87% | 1% / 92% | 1% / 84% | 3% / 90% | 1% / 89% | 3% / 88% | +0.75 |

## C. LLM agents vs patrol density (look on)

Source: `llm_summary_density.md`.

## 2. Accuracy vs patrol density (all days, no abstaining)

### look llm

| agent | every 1 h | every 4 h | every 8 h |
|---|---|---|---|
| llm_naive/not_told/look_on | 86% | 82% | - |
| llm_naive/told/look_on | 88% | 82% | - |
| llm_recent/not_told/look_on | 86% | 82% | - |
| llm_recent/told/look_on | 86% | 82% | - |
| llm_summary/not_told/look_on | 91% | 86% | - |
| llm_summary/told/look_on | - | 87% | - |

### look off

| agent | every 1 h | every 4 h | every 8 h |
|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 81% | 77% | 74% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 85% | 81% | 77% |
| LastObservation | 86% | 81% | 77% |
| Markov1(a=1,cut=24h,hl=24h) | 88% | 82% | 74% |
| MostFrequentLocation | 86% | 81% | 75% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 86% | 81% | 78% |
| SmoothedRecency(hl=6h,freq=24h) | 85% | 81% | 77% |
| TimetableLookup(bin=1h,days=all) | 88% | 81% | 76% |

### look voi

| agent | every 1 h | every 4 h | every 8 h |
|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 93% | 89% | 88% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 92% | 92% | 90% |
| LastObservation | 92% | 91% | 89% |
| Markov1(a=1,cut=24h,hl=24h) | 92% | 89% | 87% |
| MostFrequentLocation | 93% | 93% | 93% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 93% | 91% | 90% |
| SmoothedRecency(hl=6h,freq=24h) | 93% | 92% | 91% |
| TimetableLookup(bin=1h,days=all) | 92% | 86% | 82% |
