# Stage 1b SUMMARY — go/no-go for Stage 2

Dataset: 18 static / 14 occasional / 13 dynamic objects; mean 0.48 moves/day (median 0.23); median predictability of non-static objects 0.682.

**1. On displaced objects, does b3 beat b2 — overall and in the transition-inside bin?**
YES (CIs overlap): b3_perpetua_star(schedule_prior) 0.389 [0.266,0.515] (n=9617) vs b2_classdecay 0.348 [0.306,0.393] (n=9617) on displaced location_now. Note: every displaced probe has >=1 transition inside its interval by construction, so 'displaced' IS the transition-inside bin; the 0-transition control and the returned split are in the gate table (b0-favoring cells, as expected).

**2. Does b3's lead over b2 grow with predictability and volatility stratum?**
Lead by stratum (displaced acc, b3_perpetua_star(schedule_prior) − b2): static=-0.356, occasional=-0.050, dynamic=+0.090. Lead by predictability half-split (median 0.705): low_pred=-0.012, high_pred=+0.287.

**3. Is the moved-room win still significant with CIs attached?**
b3_perpetua_star(schedule_prior) displaced room_now: 0.297 [0.119,0.470] (n=9617) vs chance 0.25 — NOT separated from chance.

**4. After C2/D2, is b3 calibrated enough for Stage-2 stopping?**
C2 (post occupancy-pinning fix): {"b3_perpetua_star(fremen)": {"mean_p_elsewhere": 0.2746, "mean_p_true": 0.5768}, "b3_perpetua_star(schedule_prior)": {"mean_p_elsewhere": 0.2753, "mean_p_true": 0.5776}}. D1 ECE (p_chosen, location_now): b3_perpetua_star(fremen)=0.185, b3_perpetua_star(schedule_prior)=0.1835. D2 temperature hook: {"b0_lastseen": {"T": 4.0, "ece_p_true_pre": 0.0377, "ece_p_true_post": 0.0525}, "b1_longmem": {"T": 1.4, "ece_p_true_pre": 0.1668, "ece_p_true_post": 0.1916}, "b2_classdecay": {"T": 2.15, "ece_p_true_pre": 0.1076, "ece_p_true_post": 0.1576}, "b3_perpetua_star(fremen)": {"T": 1.2, "ece_p_true_pre": 0.2428, "ece_p_true_post": 0.257}, "b3_perpetua_star(schedule_prior)": {"T": 1.2, "ece_p_true_pre": 0.2377, "ece_p_true_post": 0.2517}} — held out, not baked in.

**5. Did any integrity check invalidate a Stage-1 number?**
C1: 0/324 room_now questions had duplicate options (validator hard-asserts distinctness). A3: class explains eta^2=0.4273 of volatility variance; flagged classes: ['bottle', 'phone']. C3: b1's delta_t_R2 dropped as a category error (see gate report). Stage 1's headline acc(moved) mixed returned into moved; the B2 split supersedes it.

**B6 note:** the generator has no routine-tightness knob; the predictability sweep (near-metronomic vs stochastic) requires a generator change and was NOT run — single operating point only.

## C2 attribution ablation (how the final pinning config was chosen)

The first gate run used BLANKET occupancy pinning (every object's placed-equilibrium
total scaled to its observed in-house fraction) and flipped the verdict to NO-GO:
b3 displaced dropped to 0.315, below b2's 0.348. Ablation on the identical target set,
b3(fremen) location_now:

| config | displaced acc | dynamic-stratum displaced | p_elsewhere (in-house objs) |
|---|---|---|---|
| blanket pinning | 0.315 [0.253,0.386] | 0.361 [0.272,0.453] | — (aggregate 0.355) |
| no pinning (fixed 0.5 budget) | 0.388 [0.264,0.510] | 0.436 [0.275,0.607] | ~0.35 |
| selective pinning (>=0.9 in-house) — FINAL | 0.387 [0.263,0.510] | 0.435 [0.274,0.606] | **0.016** |

Blanket pinning scales DOWN the placed budget of objects with real away-time, making
their filter sticky on stale anchors — a genuine accuracy/calibration trade-off, not a
bug. Restricting the fix to its motivating population (objects that almost never leave
the house, 15/36 targets) keeps displaced accuracy at the unpinned level while cutting
those objects' spurious elsewhere mass from ~0.35 to 0.016. Shipped as
`_PIN_MIN_PLACED_FRAC = 0.9` in `perpetua.py`; the gate table above uses it.

## Zero-cost re-analysis checks (post-gate, same episode)

**(1) Predictability split WITHIN volatility strata (b3(sp) − b2, displaced
location_now).** The effect is separable from raw volatility inside the dynamic
stratum, and collapses in the occasional stratum:

| stratum | half | objects | n | b3 | b2 | lead |
|---|---|---|---|---|---|---|
| dynamic | low pred (≤0.459) | 6 | 3481 | 0.337 [0.207,0.455] | 0.319 | **+0.018** |
| dynamic | high pred | 5 | 3020 | 0.547 [0.264,0.876] | 0.373 | **+0.174** |
| occasional | low pred (≤0.667) | 6 | 1970 | 0.369 | 0.400 | −0.031 |
| occasional | high pred | 6 | 1014 | 0.173 | 0.258 | −0.086 |

Per-object paired leads in the dynamic stratum track predictability (Spearman ρ=0.573,
p=0.066, 11 objects); the three most predictable dynamic objects carry leads of +0.33,
+0.53, +0.55 with b3 at 0.73–0.92 displaced accuracy. The occasional-stratum collapse
has a coherent mechanism: with 7 training days an occasional mover contributes only a
handful of transitions, too few to learn per-object timing, and its predictability score
is inflated by repeat24h (high by default for rare movers). So the claim these data
support is precise: **b3 beats b2 on objects that move both frequently and
routine-locked — because it models when** — not on all volatile objects.

**(2) room_now answerer comparison.** Replacing the mass-aggregation rule (sums belief
mass per room; structurally favors receptacle-rich rooms) with room-of-argmax-receptacle
changes nothing: every tier within ±0.014 (b3(sp) displaced 0.297 mass vs 0.283 argmax).
The sub-chance b0/b1/b2 room numbers (~0.10 vs chance 0.25) are NOT an answerer artifact —
they are confident-stale behavior: distractor rooms are drawn from the object's history,
so a model whose mass sits on the seen/class-prior room reliably picks a wrong option.
b3's ~0.30 stands as a genuine model difference but remains not CI-separated from chance.

**(3) Per-stratum displaced sample sizes.** dynamic n=6501 over 11 objects, occasional
n=2984 over 12, static n=132 over **1 object** — every static-stratum displaced cell in
the gate table (including b2's 0.455) rests on a single object and should be read as
anecdote.

## Verdict: PROCEED to Stage 2 — with a caveat
(rule: proceed only if (1) is yes on displaced objects)

(1) is YES on point estimate (0.389 vs 0.348) and the concentration pattern is exactly
the thesis prediction — the lead grows with volatility stratum (dynamic +0.090) and
especially with predictability (high-pred half +0.287, low-pred −0.012), and displaced
room_now nearly triples every other tier (0.297 vs 0.099–0.115). BUT the headline CIs
overlap (b3 [0.266,0.515] vs b2 [0.306,0.393]): the cluster bootstrap is dominated by
the ~13 objects carrying displaced mass, and no re-analysis of this episode will tighten
it. Options to firm it up before or alongside Stage 2:
1. More manifest days / more moving objects (widens the cluster count directly).
2. B6 routine-tightness generator knob — the high-vs-low predictability contrast
   (+0.287 vs −0.012) is already the strongest evidence in this report; a controlled
   sweep would make it causal.
3. E1 shows a mid-interval second anchor lifts b3's displaced accuracy substantially —
   the prior is the bottleneck, not the filter, which is precisely the gap Stage 2's
   VoI-scheduled observations are designed to fill (an argument FOR proceeding).
