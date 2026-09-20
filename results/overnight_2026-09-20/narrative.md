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
