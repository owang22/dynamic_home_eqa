# L1 design: T0 base-rate check, and the two-role architecture

**T0 VERDICT: not base-rate exploitation — the kernel's win is real
decay-dynamics modeling, concentrated at longer horizons.** Pooled across
the swept wait_hours values, the fitted kernel's Brier (0.234) beats a
trivial "stay put forever" predictor (0.491) by roughly 2x. But the
comparison is not uniform across horizons, and the shape is the actual
finding:

| wait_hours | kernel Brier | stay-put Brier | which wins |
|---|---|---|---|
| 0.25h | 0.228 | **0.171** | stay-put (slightly) |
| 0.5h | 0.321 | 0.329 | ~tied |
| 1.0h | **0.266** | 0.486 | kernel |
| 2.0h | **0.239** | 0.614 | kernel |
| 4.0h | **0.118** | 0.857 | kernel |
| **pooled** | **0.234** | **0.491** | kernel, ~2x |

At the shortest horizon, a trivial "nothing has moved yet" predictor is
competitive with (marginally better than) the fitted kernel — unsurprising,
since at 15 minutes elapsed most objects genuinely haven't moved and the
kernel's own hedging costs it a little. But stay-put's Brier gets
*monotonically worse* as wait grows (0.171 -> 0.857) while the kernel's
gets *better* (0.228 -> 0.118) — the opposite of what base-rate
exploitation would look like. A predictor that were merely encoding "this
category doesn't move much" would track stay-put's shape, not diverge
from it. What the kernel is actually doing is modeling the *decay curve*
— correctly lowering confidence as elapsed time grows — which requires
real fitted dwell-time statistics, not an aggregate persistence constant.

**Consequence for the cold-start framing:** the conditional the task list
asked to check ("if stay-put ~= kernel, the LLM substitutes for a base
rate it doesn't see") does not hold — stay-put is not ~= kernel, it loses
by 2x pooled and by 7x at the horizon (4h) that matters most for resense
decisions. This does not kill Role A; it changes what Role A is actually
substituting for. The LLM's job at cold start is not to approximate a
missing base rate (a low bar, since a base rate is roughly what "stay
put" already gives for free with zero fitting). It is to approximate
*fitted decay dynamics* while none exist yet — a substantially harder
target, and one L0 already measured the LLM to be weak at, especially at
long horizons (the state-axis wait=4h finding: every model overconfident
relative to the fitted kernel's own already-poor calibration there).
Read together with L0, Role A's honest framing is: "something bounded and
decaying beats nothing while real data accumulates" — not "the LLM
recovers the kernel's real skill early." T3's cold-start curve is where
this gets tested directly, not asserted here.

**Setup:** frozen scene, location axis, held-out eval-folder dwell events
(`embodied.belief.dwell_events`), same `wait_hours_sweep` as every other
reliability measurement this project uses. Kernel prediction reuses
`_posterior_validity_at_dwell` (embodied.belief) unchanged —
`kernel_reliability_diagram.py`'s own conditional-prediction machinery,
not a reimplementation. Deliberately NOT the same construction as
`l0_llm_prior_calibration.md`'s location-prior Brier (0.787) — that
scores a (category, time_bin)-bucket-level destination distribution
against the bucket's empirical mode, with no per-instance "current
position" at all, so a stay-put baseline has no analog there. This
report's numbers use the dwell/survival framing instead, which has a
well-defined starting position (each dwell event's own `start_state`).
Reproduce: `scripts/l1_base_rate_check.py`; raw numbers:
`results/reports/l1_base_rate_check.json`.

## Architecture: two roles, not a third belief source

The belief backbone is unchanged — the kernel/HSMM posterior remains the
sole source of transition dynamics. The LLM enters at exactly two points,
each a distinct level of the existing mechanism, never as a peer that can
outvote a working kernel:

**Role A — cold-start prior (bottom backoff level).** When a (category,
slot-type, time-bin) cell has too few fitted events for D1's own
scene -> profile -> global hierarchy to estimate reliably, LLM-elicited
Dirichlet pseudo-counts fill the gap, shrinking to zero influence as real
events accumulate (T1/T2). This is the one place L0's "worse than
kernel" verdict does not disqualify the LLM outright, because — per T0
above — the honest alternative at true zero-data is not "the kernel,"
it's "uniform," and a bounded, decaying LLM prior is a defensible
improvement over uniform even though it is not a substitute for real
fitted dynamics.

**Role B — situation reader at decision time.** The LLM reads a
structured belief summary (last observation, elapsed time, the kernel's
own posterior over anchors) plus the question, and contributes to the
answer-vs-resense decision. It never overwrites the posterior — it
consumes numbers the kernel already computed and reasons about the
decision, not the dynamics. This is the direct guardrail against L0's
finding that the LLM is a poor forecaster: Role B is never asked to
forecast.

No other role exists. The LLM does not supply primary transition
dynamics (T0 confirms the kernel's advantage there is real and largest
exactly where it matters — long horizons) and never overwrites an
observation or the posterior it produces.

## Do-no-harm ablation, mandatory per integration point

Every wire-in ships with the same test: on cells where the kernel is
already strong, the LLM-integrated belief must score within noise of
kernel-only. An integration point that regresses a strong cell is
reverted, not tuned — this is a gate, not a target to optimize past. T2's
ablation (backoff-with-LLM vs. kernel-only on strong cells) is the first
place this gets measured against real data.

## What is NOT yet built

T1 (Dirichlet pseudo-count interface), T2 (backoff wiring + ablation), T3
(cold-start payoff curve), T4 (Role B decision policy) are all still
open — this report is T0 plus the architecture only, per the task list's
own ordering ("no further L1 code until this number exists"). T5 (the
composed three-way decision) is explicitly gated on T3 and T4 each
independently passing their own ablations, not started.

**Traceability:** pure-Python, no code_hash/fingerprint dependency (T0
reads only existing frozen-scene manifests and the same kernel-fitting
code path `kernel_reliability_diagram.py` already uses). Tests:
`tests/test_l1_base_rate_check.py`.
