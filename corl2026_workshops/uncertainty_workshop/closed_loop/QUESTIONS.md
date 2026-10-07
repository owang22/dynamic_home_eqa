# Closed-loop strand — candidate research questions (draft 2026-09-22, dynamic-home-eqa-34)

Owner: dynamic-home-eqa-34. Writes only under results/closed_loop/ (+ new modules it creates; no edits to src/situation_sim/).
Status: DRAFT for Oliver + coordinator (-37). No code, no GPU until one is chosen.

## The gap
Every result so far is open-loop: the sighting stream (03:00 patrol + truth 10 min after every question) is fixed in the
bank before any agent runs (bank.py:407-537; harness.py:5-9 "The passive patrol is FIXED and agent-independent").
So nothing a memory believes changes what it gets to see. The claim "a robot acting on wrong beliefs stays wrong
because its data is shaped by its own mistakes" is untestable here (coordinator, 2026-09-22).

## Prior closed-loop work in this repo (July 2026 — read before designing; do not re-derive)
Code: src/dynbelief/answer_or_resense. Reports archived in cbc6fd052; read with
`git show 060104283:reports/answer_or_resense/SUMMARY.md` and `git show f5de605a2:reports/two_capacities/SUMMARY.md`.
Setting: STATIONARY world, zero initial observations, per query ANSWER or RESENSE (budget 5/day), 24 households, DeepSeek/Qwen3.6/GLM.
Surviving findings:
- LLM confidence RANKING is usable (AUROC 0.75-0.79; when it chose to look, it was right to 0.79-0.89); its LEVEL is
  overconfident (0.68 stated vs 0.53 realised) and it under-looks by about half.
- "Decaying fidelity": follows its own latest sighting 0.94 (1 obs) -> 0.70 (4+ obs); overrides are right 0.245 vs 0.59.
- With the nightly-reflection scaffold in the loop the LLM was the BEST arm (5.78 vs classical 5.04).
- A single frozen look threshold sat below two models' whole confidence distribution, so they never looked ->
  any look-or-answer threshold is calibrated PER MODEL on dev households.
- Prompt wording alone (EV framing) drove near-ceiling looking at 0.15 accuracy -> fix wording on dev households only.
Retracted there (do NOT cite): "LLM fails to integrate self-gathered evidence"; the single-tau three-model table.
=> What is new here: closing the loop ACROSS A TIME SHIFT AND A RETURN, starting from memories that had already learned
   a routine. July never had a regime change.
In flight elsewhere (memory_cl, via -37): follow-vs-override accuracy by STAGE on the open-loop logs — does it
second-guess at the wrong times (wrong when settled, right at the shift) or everywhere? Feeds Q1's mechanism split.

## The loop (shared by all options)
World trajectories stay precomputed (residents move things; the robot looking does not) -> reuse frozen banks.
Remove the free truth feedback. The robot's observations are what its own actions produce:
  - answer = go to the believed spot; search the next-best places, up to k places, then give up
    (each place visited = an observation, incl. "not here"). Found within k -> learns truth; else learns only negatives.
  - optional nightly look budget of R rooms, agent-chosen (replaces the fixed 03:00 patrol).
Open-loop run on the SAME household = paired control. Knobs: k, R. k=inf + full patrol reproduces open loop (degenerate check, to the digit).

## Candidates
Q1 Lost -> stays lost?  Does acting on your own beliefs turn a temporary shift into a lasting failure, and which memory
   properties (forgetting rate, what its uncertainty tracks) prevent it?  Metric: closed-loop penalty per stage, paired;
   days to recover after day 14 / day 24; share of looks spent where the routine changed.
   Predictions (write to EXPECTATIONS.md): never-forgets counter flips from best-on-return (open) to worst (closed);
   Perpetua* (confidence tracks evidence age) gains most; LLM memories with flat confidence lock in.
Q2 What should the robot look at?  Holding the memory fixed, which look signal finds a regime change fastest per look:
   fixed patrol / random / most-uncertain / oldest-evidence / surprise-triggered (change detector boosts looking)?
Q3 When should the robot spend?  A detector (martingale/CUSUM exists in uq_agents.py) raises the look budget after a
   surprise; does adaptive spending buy most of the recovery at a fraction of the looks?
Q4 Does memory make re-exploration cheap?  On the return, does a regime-tagged memory (open-loop: no return drop)
   also need far fewer looks to re-settle than re-learning memories?  ("memory as a prior for where to look")
Q5 Sentence vs looks.  How many looks is "she is home sick today" worth, and does a stale sentence steer looks away
   from the truth on the return (closed-loop version of the -7/-12 return cost)?

## Cost (rough; to be re-measured on ONE household before any wide launch — past estimates were off 8x)
classical Q1-Q4: CPU only, run in-loop (no bank replay): ~minutes/household/agent.  LLM (buffer, retrieval) Q1/Q5:
~496 answer calls + search-order calls + nightly look choices per household-arm; est. 2-4 GPU-h for 2 memories x 2
arms x 10 households at <=3 streams — to be measured first.
