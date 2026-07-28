# Paper figures

One chart per file. Regenerate everything: `python -m dynbelief.paper_figures.make_figs`
Source: [`src/dynbelief/paper_figures/make_figs.py`](../../src/dynbelief/paper_figures/make_figs.py)

Conventions: phase-averaged over start weekday; bootstrap 95% CI over households;
**paired per-household deltas** wherever a claim must separate from zero; "LLM" =
best scaffolded implementation. The statistical baseline is labeled **Classical**
throughout (internally the held-out-gated periodic GLM; the weaker C1 variant is
never reported).

---

## passive_adaptation/ — world knowledge speeds up passive adaptation

Pool: **24 atypical households** (v22 + v22b, d0 run) and **6 typical households**
(version22_typ, matched protocol, α frozen at the same v22dev value 8). The older
6-household `atyp_regime_confirm_v1` bank is retired for this claim — it was the
original confusable-pairs confirmatory and is too small (its paired CIs separate
only on day 1; the 24-household pool separates on 6-7 of 7 days).

| file | claim |
|---|---|
| `accuracy_by_day_atypical_households.png` | LLM arms lead classical at every checkpoint (day 1: 0.25 vs 0.08) |
| `paired_delta_vs_classical_atypical.png` | paired edge +0.17 day 1, stays +0.10-0.15, **CI excludes 0 on every day** (reflective memory) |
| `accuracy_by_day_typical_households.png` | the prior pays MOST here: LLM 0.63 vs classical 0.17 on day 1; classical never closes (0.65 vs 0.35 at day 14) |
| `paired_delta_vs_classical_typical.png` | paired +0.46 [+0.28, +0.63] day 1, CI excludes 0 on 6/7 days; no-reflection nearly matches reflective memory here (conventional placements need no evidence organization) |
| `anonymization_ablation.png` | stripping receptacle names costs DeepSeek and Qwen on regime-flipped targets; **GLM gains (exception — 2 of 3 models support the mechanism)** |

---

## reflection_gating/ — why surprise-gated reflection is the default

24 households; distractors = static objects reported daily but never queried.
Gate: the LLM reflects only when Classical is contradicted (≥2 obs p<0.15 while max_p≥0.55).

| file | claim |
|---|---|
| `accuracy_by_day_distractor6.png` | at moderate load the three strategies track each other |
| `accuracy_vs_distractor_load.png` | nightly degrades with load (0.44→0.31); gate holds (0.43→0.39) |
| `paired_delta_vs_nightly_by_load.png` | paired: gate = nightly at loads 0-6, **beats it at 12 (+0.074 [+0.012, +0.137])** |
| `paired_delta_vs_nightly_by_day_load12.png` | the edge appears from day 5 on; ~6.5 LLM calls/household vs nightly's 14 |

The case is **cost + robustness under load**: same accuracy for less than half the
LLM calls, and strictly better once the stream is padded with noise.

---

## active_sensing/ — world knowledge choosing observations

Scarce loop: zero initial observations, Q=10 queries/day, budget B=5 looks/day;
ANSWER 1/0, RESENSE 0.4 + reveals truth. 24 households, DeepSeek, per-model τ/α.

| file | claim |
|---|---|
| `belief_accuracy_by_day.png` | LLM arms start at 0.24-0.29 vs classical's 0.01 and stay ahead through the ramp; fusion is fastest days 2-4. Counterfactual scoring on ALL queries — coverage cannot inflate an arm |
| `reward_per_household_day.png` | scaffold 5.78 > fusion 5.26 > classical 5.04 |
| `resense_targeting.png` | **88%** of the LLM's chosen looks were would-be errors vs 59% classical — world knowledge locates its ignorance (spending fewer looks: 18% vs 28%) |
| `calibration_stated_vs_realized.png` | both LLM arms mildly overconfident (gap 0.09 scaffold / 0.12 fusion); fusion does NOT improve calibration |

---

Caveats: LLM-number noise floor ≈0.06 (vLLM non-determinism); all hyperparameters
frozen on dev banks before confirmatory runs.
