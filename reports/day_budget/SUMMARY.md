# Day-Budget Active Probe — SUMMARY

Shared daily sensing budget B over Q=10 sequential queries/day; wake-up snapshot; paired
schedules (60% transition-adjacent); 21 scene-days across 3 scenes (ep049w 11 rooms, family 11,
roommates 9); cluster bootstrap at the (scene, day) level. Tier b3(fremen) unless stated;
truly-elsewhere fraction of the query mix: **0.38**. Full tables in `day_budget_gate.md`;
raw episodes in `queries*.parquet`.

Amended-F1 context (see `reports/active_probe/SUMMARY.md`): with per-object marginal beliefs
the sense order is pinned by the belief; policies here are ONE family differing in stopping/
allocation, and the belief tier selects which curve you are on.

---

## Headline: accuracy vs B (day-level, b3-fremen)

| B | answer_now | greedy | rationed | voi_fixed(0.05) | voi_adaptive | oracle* |
|---|---|---|---|---|---|---|
| 5  | 0.733 | 0.752 | 0.733† | 0.776 | **0.824** | 0.829 |
| 10 | 0.733 | 0.767 | 0.824 | 0.829 | **0.848** | 0.843 |
| 20 | 0.733 | 0.838 | 0.857 | **0.886** | 0.867 | 0.848 |
| 30 | 0.733 | 0.895 | 0.862 | **0.933** | 0.914 | 0.848 |
| 40 | 0.733 | 0.943 | 0.871‡ | 0.948 | **0.952** | 0.848 |

† floor(5/10)=0 looks/query — rationed degenerates to answer_now at B<Q (reported, not hidden).
‡ rationed does NOT converge at generous B: its 4-look/query cap can't fund deep searches.
\* oracle_allocator as implemented is NOT an upper bound — it allocates find-value only and
ignores abstention-value (confirming absence), so it plateaus at 0.848; keep as a caveat, not
a ceiling.

**Generous-B tie, reported prominently:** at B=40, greedy 0.943 ≈ voi 0.948–0.952 — the
advantage of allocation vanishes when budget is plentiful, as it must. The interesting regime
is B ∈ [10, 30] (greedy exhausts 50–95% of days; forced-answer fraction up to 0.80).

## Pre-registered predictions

**P1 (ordering voi_adaptive ≥ voi_fixed ≥ rationed ≥ greedy at tight B; convergence at 40):
PARTIAL PASS.** The full chain holds exactly at B=10 (0.848 ≥ 0.829 ≥ 0.824 ≥ 0.767). At B=5
the rationed link breaks mechanically (floor cap = 0). At B≥20 voi_fixed(0.05) noses ahead of
voi_adaptive (the adaptive price falls too low early and it overspends: 34.9 looks at B=40 for
+0.004 over fixed's 22.7). Convergence at B=40 holds for greedy/voi but not rationed (‡).
Directionally: the voi family ≥ the checklist family at every budget; the exact chain is
regime-dependent.

**P2 (voi-on-b3 > voi-on-b2 at every B): FAILS — and the decomposition is the most
informative result in this report.** Full curve (voi_adaptive): b2 wins at every B
(−0.071…−0.095, several CI-separated; b2+voi_adaptive at B=40 is the best cell in the entire
study at **0.981**). voi_fixed: b2 wins at B≤20, b3 edges ahead at B≥30 (+0.029/+0.043, CIs
overlap). Where it comes from (B=10, voi_adaptive):

| slice | b3 | b2 |
|---|---|---|
| elsewhere-true queries (38% of mix) | 0.699 | **0.986** |
| present-true queries | **0.927** | 0.905 |
| transition bin, B=30 voi_fixed | **0.911** | 0.556 |
| abstention (B=30) | P=1.00, R=0.85 | P=0.88, R=0.99 |

**b2 wins the aggregate by promiscuous abstention.** Its class-decay belief leaks mass broadly,
so per-room mass is low and ELSEWHERE is often the argmax — eager abstention (R=0.99 at P=0.88)
that happens to be nearly free in a 38%-elsewhere query mix. b3 abstains conservatively
(P=1.00, R=0.85) and — the specific failure — its emergence hazard predicts RETURNS for
objects that stayed gone (mass pulled back in-house), costing elsewhere-recall. Meanwhile b3
beats b2 by **+0.355** on the transition bin (0.911 vs 0.556), exactly where dynamics matter —
but that bin is 21% of queries while elsewhere-handling covers 38%, so the aggregate goes to
b2. **Conclusion, stated narrowly:** in a snapshot-anchored day with a large truly-elsewhere
share, day-level accuracy is dominated by elsewhere-recall, where eager abstention wins;
the routine model's advantage is real but confined to transition-affected queries. The
aggregate day-level metric, at this query mix, does not need b3 — a reviewer will see this,
so the paper must lead with the bin decomposition and treat the elsewhere share as a scenario
parameter (or fix b3's return-prediction bias — see next steps).

**P3 (advantage concentrates late-day + transition bin): PASS for voi_fixed.** Late-30% at
B=30: voi_fixed 0.937 vs rationed 0.825, greedy 0.762. Transition bin at B=30: answer_now
0.356 → rationed 0.822 → voi_fixed **0.911**. (voi_adaptive's transition-bin 0.800 lags
rationed — its early low price overspends before hard late queries; another face of the P1
nuance.)

**P4 (mechanism ablation — margins with vs without truly-elsewhere queries): PASS, the causal
chain is demonstrated.** At B=30: voi_fixed's margin over rationed **+0.071 → −0.005** when
elsewhere queries are removed; over greedy **+0.038 → −0.015**. At B=10 the greedy margins
likewise collapse (+0.062/+0.081 → 0.000). Predictive abstention on truly-elsewhere queries —
answer "gone" in ~1 look instead of draining the support — IS the engine of the day-budget
advantage; with those queries removed, voi has no edge over honest rationing. (Corollary: this
is the same lever b2 exploits, per P2.)

## Allocation discrimination (B=30, looks/query)

| policy | static | occasional | dynamic |
|---|---|---|---|
| greedy | 2.03 | 3.89 | 2.88 |
| rationed | 1.47 | 2.33 | 1.78 |
| voi_fixed | **1.01** | 3.09 | 2.66 |
| voi_adaptive | 1.98 | 3.58 | 3.03 |

voi_fixed is the only policy that materially discounts stable objects; voi_adaptive's early
cheap price erodes that discrimination.

## Verdict and next steps (for discussion, not run)

The day-budget design did what it was built to do: it converted look-efficiency into day-level
accuracy (P4 proves the chain), produced clean allocation curves, and surfaced a genuine
threat — **the aggregate metric rewards eager abstention, and the decay baseline with eager
abstention is the best overall system at this query mix.** Three candidate responses, in order
of scientific value:
1. **Diagnose/fix b3's return-prediction bias** (elsewhere-recall 0.85 vs b2's 0.99): its
   emergence term pulls absent objects back in-house too aggressively — likely interacts with
   the C2 occupancy-pinning choices. A calibration pass on p(elsewhere) could recover most of
   the aggregate gap while keeping the +0.355 transition-bin win.
2. **Treat the elsewhere share as a swept scenario parameter** (it is 0.38 here by
   construction of the schedule mix): report day-level curves at e.g. 10/25/40% elsewhere —
   the crossover point between b3 and b2 becomes a result, not an embarrassment.
3. **A staler regime** (no wake-up snapshot, or snapshot every k days) — the morning snapshot
   is precisely what flattens b3's within-day advantage; without it, staleness grows and the
   routine model should separate. This changes the scenario definition, so it needs a
   deliberate decision.
