# reflect_DAG — results (Changes 1–3, FBN-motivated)

All arms on the frozen confirmatory banks (version22 = 12 idiosyncratic households;
version22b = 3 confusable pairs × 2 seed-instances = 12), rand3 observations,
distractors=6, day-14, object-clustered bootstrap 95% CI. Dev/test wall: α* and the
unit constant U estimated **only** on version22_dev. C3g, the banks, and the split
are unchanged. Code: `src/dynbelief/reflect_dag/`.

## Headline

The one clean, positive result is **Change 2**: contrastive (CounterfactCoT)
elicitation is calibrated where the entropy gate was not. The **Change-1 activity
DAG** is inert-to-negative at this thinning, and the **Change-3 precision fusion**
is mathematically correct but exposes that the LLM prior is *confidently wrong* on a
minority of objects — a correct Bayesian update with a wrong prior and starved data
loses. Reported honestly per the brief's guardrails; persona-only / surprise-gated
stay as the arms that hold up.

## Change 2 — CounterfactCoT do-contrast (the win)

Per-household do-contrast weight vs prediction correctness, next to the old
memory-entropy gate (figure: `calibration_{v22,v22b}_d6.png`):

| bank | OLD entropy-gate r | NEW do-contrast r | verdict |
|------|-------------------:|------------------:|---------|
| version22  | −0.13 | **+0.38** | positive, not sig at n=12 |
| version22b | −0.23 | **+0.58** | positive, **significant** (p≈0.048, n=12) |

Calibrated entropy would anti-correlate (low H = confident = correct); it is a flat
cloud. The do-contrast positively correlates on both banks and significantly on the
confusable-pair bank. **The confidence mechanism the entropy gate could not provide
is revived by contrastive elicitation** (FBN Eq. 1 / Table 1). Budget: 2 structure +
~16 contrast calls per household (192 total/bank) — within FBN's 3–8-calls/node.

## Change 3 — precision-weighted fusion (α estimated, not set)

Tier-1 α* on the dev bank: LLM regime-prior hit-rate 0.361 over 252 held-out
queries, mean |candidates| 13.5 → **α\* = 6.07 observations** (via the Dirichlet
inversion k=(C·h−1)/(1−h)). Reported as an empirical quantity — "the prior is worth
~6 observations" — not a tuned knob; reassuringly near the old hand-tuned α=8. The
one Tier-3 calibration constant **U = 15.48 pseudo-obs / unit contrast** (mean dev
contrast 0.392, so mean κ = α*). Framing: not parameter-free — one interpretable,
dev-calibrated unit-conversion constant replaces the free mixing hyperparameter.

The fusion form is correct; the finding is about the *prior it fuses*. See below.

## Change 1 — activity DAG (P-A1 / P-A2)

version22 day-14 accuracy (object-clustered):

| arm | rare (n=18) | medium (n=8) | frequent (n=10) | ALL (n=36) |
|-----|------------:|-------------:|----------------:|-----------:|
| persona_only (baseline)   | 0.246 | 0.464 | 0.229 | 0.290 |
| **persona+DAG (T3 fusion)** | **0.279** | **0.518** | **0.063** | 0.278 |
| persona+DAG+counterfact   | 0.279 | 0.518 | 0.095 | 0.286 |
| dag_stat_params (tying only) | 0.159 | 0.500 | 0.314 | 0.278 |
| C3g / scrambled / dag_only   | 0.159 | 0.500 | 0.314 | 0.278 |
| surprise_gated               | 0.270 | 0.464 | 0.329 | 0.329 |

- **P-A1 (rare lift): partially supported on version22.** persona+DAG lifts the rare
  tercile 0.246→0.279 and medium 0.464→0.518, over persona-only, and far over C3g
  (0.159). But it is not CI-separated (n=8–18), and it does **not** replicate on
  version22b (persona-only 0.367 > persona+DAG 0.306 in the rare tercile there).
- **P-A2 (confusable-pair differing-activity): NOT supported.** version22b pair
  targets: persona_only 0.448 > persona+DAG 0.361 ≈ C3g 0.373.
- **Structure tying alone is inert.** `dag_stat_params` == C3g everywhere: at ~3
  obs/day the pooled activity groups rarely clear the held-out MDL gate, so the tied
  model collapses to the classical fallback. The tying needs denser observation than
  the starved confirmatory regime provides.
- **Graceful-degradation control: PASSED.** Scrambling the object→activity map
  degrades exactly to the C3g floor (0.278), never below — a wrong tying merely fails
  to gate in; it does not break anything.

### Why persona+DAG crashes on the frequent tercile (0.063)

Not a bug — the honest cost of a miscalibrated prior. Three frequent objects the data
models **perfectly** (base=1.0) have a **confidently-wrong** LLM prior: gamer's phone
(desk at 23:00, prior says nightstand), astronomer's phone, teacher's thermos. With
α*=6 against the thinned own-count (~15 events), the correct Bayesian weight on the
prior is still ~29%, and a confidently-wrong prior at 29% flips a perfect prediction.
No fusion weight protects a data-rich object when the prior is confidently wrong and
the data is deliberately starved. The contrast-scaled arm already nudges these back
(0.063→0.095) — precisely the Change-2 direction: down-weight the prior where it is
untrustworthy. The identified fix is to gate prior injection by the (now-calibrated)
do-contrast, so the prior is trusted only where it discriminates.

## Bottom line (honesty guardrails)

- Change 2 is a real, modest, FBN-cited improvement: contrastive elicitation is
  calibrated where entropy was not (r up to +0.58, significant).
- Change 1's activity tying is null at this observation density (collapses to C3g);
  Change 3's fusion is correct but net-neutral-to-negative because the persona prior
  is confidently wrong on a minority of objects. Per the guardrail, persona-only and
  surprise-gated remain the arms that hold up (surprise_gated is best pooled, 0.329),
  and the DAG is reported as a discussed variant whose value would require (a) denser
  observation for the tying to engage and (b) contrast-gated prior injection to avoid
  the confident-wrong-prior regression.
- All v1/VERSION22 results untouched; these are additive arms in `reflect_dag/`.
