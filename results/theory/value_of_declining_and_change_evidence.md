# Two measured effects turned into mathematics, and tested

Offline modelling on saved logs, 2026-09-23. No new runs, no model calls. Scripts beside this file:
`part1_value_of_declining.py`, `part2_change_evidence.py`. Every number below is printed by one of them;
raw stdout is kept in `part1_output.txt` and `part2_output.txt`.

The order of work was: derive, write the prediction down, then compute. The prediction blocks below were
written into this file before the corresponding table existed, and each is marked SUPPORTED, PARTLY
SUPPORTED or REFUTED afterwards. Where the model misses, the miss is the headline.

## Summary of verdicts

| # | prediction | verdict |
|---|---|---|
| P1 | predicted V matches the measured F9 gain within ±0.5/day everywhere | **REFUTED** (misses Perpetua* by 1.4/day; the plug-in's noise floor is as large as the effect) |
| P2 | the timetables' small measured gains are mostly estimation noise | **SUPPORTED** (never-forgets timetable at the shift: p = 0.115 against its own null) |
| P3 | Perpetua*'s advantage sits in the mass term m | **REFUTED** (m is 0.36 vs 0.37 — indistinguishable; the advantage is the SIGN of the ordering value) |
| P4 | V is exactly invariant to monotone relabelling while ECE is not | **SUPPORTED** (identical to 3 dp in all 20 cells; ECE moves up to 3×) |
| P5 | the max probability barely moves at the shift; the NLL of the truth moves > 2 sd | **REFUTED** for the long-memory timetables (C moves −2 sd) |
| P6 | C is near chance as a change detector, L is good | **REFUTED** in half (AUC of C 0.33, of L 0.77 — L is ~1.5× better, not categorically different) |
| P7 | confidence is HIGHEST on the objects that moved | **REFUTED** (r = −0.12 ± 0.10 for the never-forgets timetable — confidence is *lower* there) |
| repair §2.4 | C detects change in proportion to how much pre-change data its memory still holds | **PARTLY SUPPORTED**, rank order held on three held-out scenarios |

The two results worth carrying forward are both negative-flavoured: F9's "+0.3 for the never-forgets
timetable at the shift" is *no measurable gain at all*, and the reason Perpetua* gains 2.8 is that its
confidence still ORDERS questions at the shift while the timetables' confidence orders them backwards.

---

## Part 1 — a closed form for the value of being allowed to decline

### 1.1 Derivation

One question. The method emits an answer and a confidence signal `s` (any scalar it computes before seeing
the truth: for the counters the posterior maximum `top_prob`, for long-context the stated `raw_confidence`).
Let `Y = 1` if the answer it would give is right. Scoring is `+1` right, `-1` wrong, `0` declined.

Define the *ordering function*

    q(s) = P(Y = 1 | s).

Answering a question with signal `s` has expected score `q(s) - (1 - q(s)) = 2q(s) - 1`; declining scores 0.
So for any policy `a(s) ∈ {answer, decline}` the expected score is `E_s[a(s)·(2q(s) - 1)]`, which is
maximised pointwise by answering iff `2q(s) - 1 > 0`, i.e. iff `q(s) > 1/2`. Hence

    S_forced  = E_s[2q(s) - 1]
    S_optimal = E_s[max(2q(s) - 1, 0)]
    V         = S_optimal - S_forced = E_s[(1 - 2q(s))^+].                              (★)

`V` is the expected *avoided regret*: the score the method would have thrown away by answering questions it
was more likely than not to get wrong. Three immediate consequences, all falsifiable:

**(a) V is a functional of q only.** Write `m = P(q(s) < 1/2)` (the mass the signal puts on below-even
questions) and `d = E[1 - 2q(s) | q(s) < 1/2]` (how far below even those questions are). Then

    V = m · d.                                                                          (★★)

A method can only have a large `V` by pointing at a lot of questions it will probably get wrong (`m`), or by
pointing at questions it will get *very* probably wrong (`d`). Nothing else enters.

**(b) V is calibration-free.** Let `g` be strictly increasing on the range of `s` and let `s' = g(s)`. Then
`σ(s') = σ(s)` — the two signals generate the same σ-algebra, because `g` is invertible on that range — so
`q'(s') = E[Y | s'] = E[Y | s] = q(s)` almost surely, and `(★)` gives `V' = V`. The same holds for strictly
decreasing `g` (the sign of the ordering flips, but a threshold rule can flip with it, and `q` as a function
of the *event* `{s' = g(s)}` is unchanged). So no monotone rescaling of a confidence scale — no temperature,
no Platt map, no "say 0.95 to everything" — can change the value of being allowed to decline. Only a
relabelling that changes which questions are grouped together or how they are ORDERED can. Being better
calibrated *in level* buys exactly zero; ordering questions better buys everything. This is the formal
version of the sentence the project has been saying in words.

Estimator note: the population statement is unconditional, but a plug-in estimate is only invariant if the
binning is rank-based. Fixed-width bins on `s` are not invariant (the bin edges move under `g`); quantile
bins are. The primary estimator here is rank-based for that reason, and the fixed-width variant is reported
as sensitivity, not as the estimate.

**(c) Accuracy does not bound V, and V does not bound accuracy.** `S_forced = 2·acc - 1` where `acc = E[q]`.
A method can have `acc = 0.5` and `V = 0` (an uninformative signal: `q(s) ≡ 1/2` for all `s`, so nothing is
below even) or `acc = 0.5` and `V = 0.5` (a perfect ordering: `q(s) ∈ {0, 1}` in equal mass). "Moves a lot"
is not the same as "discriminates": a confidence that swings wildly but is independent of correctness has
`q(s) ≡ acc` and therefore `V = (1 - 2·acc)^+`, which is 0 for any method better than chance.

### 1.2 Estimation

`q̂` is a plug-in: within one household and one window, sort the questions by confidence, cut them into `K`
rank bins that never split a tied confidence value and hold ≥10 questions each, and set `q̂` on a bin to the
fraction correct in it. Then `V̂ = (1/n) Σ_i (1 - 2q̂(bin(i)))^+`. Primary `K = 4`; `K ∈ {2,3,6,8}` and two
fixed-width binnings are reported as sensitivity.

Units. `(★)` is per question. The measured F9 gain is a *daily* score — the sum over the 16 questions asked
each day, averaged over the days in the window, then averaged over households. So the comparable quantity is
`16 · V̂`. Per household first, mean ± se across the 10 households; cells under 10 questions dropped.

Two biases pull in opposite directions and both are measured rather than argued away:

* `V̂` is **upward** biased. `E[max(0, X)] > max(0, E[X])` whenever `X` has noise, so a signal carrying no
  information at all still scores `V̂ > 0` in a finite sample. The size of that bias is measured directly by
  re-running the whole estimator on **shuffled correctness labels** (400 permutations per cell), giving a
  null `V̂₀`, and the bias-corrected figure is `V̂ - V̂₀`.
* The **measured** F9 number is a *single* threshold shared by all ten households, chosen with hindsight to
  maximise the cross-household mean. A single threshold attains the optimum in `(★)` only if `q` is monotone
  in `s`; if it is not, the measurement is **downward** biased relative to the formula. A per-household
  hindsight threshold is also reported, as the like-for-like comparison.

### PREDICTIONS (written before Tables 1-5 were computed)

* **P1.** Bias-corrected `16·V̂` agrees with the measured F9 gain to within about ±0.5 score points per day
  for every method × window cell, and reproduces the ordering at the shift: Perpetua* ≫ long-context >
  3-day timetable ≈ never-forgets timetable.
* **P2.** Raw (uncorrected) `16·V̂` *overstates* the gain for the near-zero cells, because the permutation
  null `16·V̂₀` is not small compared with 0.3-0.4 per day. If `V̂₀` came out negligible I would have to
  withdraw the claim that the timetables' small gains are mostly estimation noise.
* **P3.** Perpetua*'s advantage at the shift is carried by the **mass** term `m`, not the shortfall `d`.
  Concretely: `m` at days 14-16 above ~0.3 for Perpetua* against below ~0.12 for the never-forgets
  timetable, while `d` differs between them by less than a factor of two. Reasoning: `d ≤ 1` by
  construction and a wrong answer is wrong in much the same way for every method, so the room for a method
  to differ is in *how much of its mass it can put below even*, which is a statement about ordering.
* **P4.** `16·V̂` is numerically identical under `s → s³` and under `s → (s+3)/(s+4)` (both strictly
  increasing on [0,1]) to the last printed digit, while ECE — the gap between mean stated confidence and
  accuracy — moves by a large factor under the same maps. Under the non-monotone map `s → |s - 0.5|` V
  changes.

### 1.3 Results

The F9 numbers are reproduced exactly by the replication inside `part1_value_of_declining.py`
(0.04 / 0.33 / 0.19 / 0.17 / 0.44 for the never-forgets timetable, 0.32 / 2.83 / 0.34 / 1.43 / 1.50 for
Perpetua*, matching `F9_value_of_declining/numbers.md` to the printed digits), so the comparison below is
against the same estimator the figure uses, not a re-derivation of it.

**Table 1 — predicted V against the measured gain, first sick days (score per day, mean ± se over 10
households).** Full arc in `part1_output.txt`.

| method | V̂ per question | 16·V̂ raw | permutation null | null-corrected | F9 measured | F9 with a per-household bar |
|---|---|---|---|---|---|---|
| never-forgets timetable | 0.18 ± 0.06 | 2.93 ± 0.95 | 2.38 | 0.56 ± 0.27 | **0.33** | 2.50 ± 0.70 |
| 3-day timetable | 0.10 ± 0.04 | 1.60 ± 0.62 | 1.44 | 0.16 ± 0.14 | **0.40** | 1.50 ± 0.50 |
| Perpetua* | 0.17 ± 0.03 | 2.73 ± 0.54 | 1.30 | 1.44 ± 0.35 | **2.83** | 3.37 ± 0.53 |
| long-context | 0.07 ± 0.02 | 1.20 ± 0.35 | 0.27 | 0.93 ± 0.30 | **0.77** | 1.33 ± 0.32 |

**P1 — REFUTED as stated.** The null-corrected prediction misses the measured gain by 1.4 points per day for
Perpetua* (1.44 against 2.83) and the plug-in's own noise floor for the never-forgets timetable (2.38/day) is
seven times the number it is supposed to be predicting. Agreement inside ±0.5 holds for three of four methods
and fails for the one the headline is about. Binning is not the culprit: Table 3 in the output shows 16·V̂ at
the shift moving only between 2.4 and 3.0 for the never-forgets timetable and 2.4 and 2.9 for Perpetua* over
K ∈ {2,3,4,6,8}, and Table 8 shows the null-corrected figure flat in K as well (Perpetua* 1.50, 1.70, 1.44,
1.66, 1.66). The estimator is stable; the model as first written is what missed. §1.4 says why.

**P2 — SUPPORTED, and it is the sharper half.** Table 6 of the output runs *F9's own estimator* on shuffled
correctness labels, 200 draws per cell. A hindsight threshold on a signal carrying no information at all
still scores:

| method, first sick days | F9 gain | null mean | null p95 | p |
|---|---|---|---|---|
| never-forgets timetable | 0.33 | 0.16 | 0.53 | **0.115** |
| 3-day timetable | 0.40 | 0.11 | 0.37 | **0.020** |
| Perpetua* | 2.83 | 0.11 | 0.37 | **<0.005** |
| long-context | 0.77 | 0.04 | 0.13 | **<0.005** |

The never-forgets timetable's gain at the shift is not distinguishable from what the estimator returns on
pure noise, and with each household allowed its own threshold neither timetable is (p = 0.21 and p = 0.35).
Perpetua* and long-context are. F9's headline contrast is therefore *stronger* than the figure states: the
correct reading of "+0.3" is not "a small gain" but "no measurable gain".

### 1.4 What actually carries Perpetua*'s advantage

The plug-in above is fitted and evaluated on the same questions, which is why its noise floor is so high.
Table 9 of the output replaces it with an honest estimator: the decline rule (which rank bins have q̂ < 1/2)
is fitted on a random half of each household-window and its avoided regret is *measured on the other half*,
both directions, 200 splits. Its expectation under no signal is exactly zero, so nothing has to be
subtracted, and the mass and shortfall come out of sample.

(Tables 9 and 12 of the output run the same estimator with independent split draws, so they differ in the
second decimal — 1.66 ± 0.60 against 1.71 ± 0.59 for Perpetua* at the shift. Nothing below turns on that.)

That estimator immediately exposed a term the derivation had left implicit. By Jensen,

    V = E[(1 - 2q(s))^+] ≥ (1 - 2·E[q])^+ = (1 - 2·acc)^+ =: V_const.                   (★★★)

If a method's accuracy in a window is below one half, it collects `V_const` **by declining every question,
with no signal whatsoever**. Only the excess `V_order = V - V_const` is attributable to the confidence
ordering anything. `(★★)`'s split into mass and shortfall does not separate these: a method can have large
`m` purely because it is below even everywhere.

**Table 12 — the decomposition that matters (per day, mean ± se over households).**

| method, first sick days | accuracy % | V_const | V honest | **V_order** | F9 measured |
|---|---|---|---|---|---|
| never-forgets timetable | 51.3 ± 5.3 | 2.07 ± 0.86 | 1.72 ± 0.97 | **−0.34 ± 0.18** | 0.33 |
| 3-day timetable | 57.9 ± 5.0 | 1.00 ± 0.55 | 0.49 ± 0.51 | **−0.51 ± 0.23** | 0.40 |
| Perpetua* | 55.4 ± 3.5 | 0.67 ± 0.46 | 1.71 ± 0.59 | **+1.05 ± 0.48** | 2.83 |
| long-context | 61.7 ± 3.1 | 0.00 ± 0.00 | 0.48 ± 0.31 | **+0.48 ± 0.31** | 0.77 |

**P3 — REFUTED.** The advantage is not in the mass term, and not in the shortfall term either. Out of
sample, at the shift, the never-forgets timetable declines *more* mass than Perpetua* (m = 0.37 ± 0.09
against 0.36 ± 0.05) and its shortfall is not far behind (d = 0.17 ± 0.10 against 0.25 ± 0.07). The
prediction that `m` would separate them by a factor of three is simply wrong. What separates them is the
sign of `V_order`: **Perpetua*'s confidence orders questions usefully at the shift (+1.05 ± 0.48 per day),
and both timetables' confidence orders them worse than useless (−0.34 ± 0.18 and −0.51 ± 0.23).** A decline
rule driven by a timetable's confidence at the shift loses to both of the two no-signal policies available
to it.

Table 10 of the output shows this directly as the ordering profile — q̂ by confidence rank bin, bin 1 the
least confident:

| method, first sick days | q bin 1 | q bin 2 | q bin 3 | q bin 4 |
|---|---|---|---|---|
| never-forgets timetable | 0.72 ± 0.05 | 0.49 ± 0.07 | 0.42 ± 0.14 | 0.43 ± 0.17 |
| 3-day timetable | 0.56 ± 0.06 | 0.60 ± 0.05 | 0.61 ± 0.08 | 0.55 ± 0.08 |
| Perpetua* | 0.30 ± 0.04 | 0.42 ± 0.07 | 0.69 ± 0.05 | 0.81 ± 0.06 |

The never-forgets timetable's profile **inverts** at the shift (it is right 72% of the time where it is least
confident and 43% where it is most confident) and the 3-day timetable's goes flat. Perpetua*'s stays
monotone and spans 0.30 to 0.81. In every other window both timetables' profiles rise normally
(0.64 → 0.91 in the settled week), so this is a property of the shift, not of the method in general.

So the formal answer to "why 2.8 against 0.3" is: **not mass, not shortfall, but whether `q` is increasing in
`s` at all.** `V = m·d` is a true identity and a useless explanation; `V = V_const + V_order` with a sign
test on `V_order` is the one that separates the methods.

### 1.5 The calibration-free part, demonstrated

**Table 4 of the output — 16·V̂ under relabellings, with ECE for contrast.** Every cell of the arc, all four
methods; the first sick days shown here.

| method | V raw | V under s→s³ | V under s→(s+3)/(s+4) | ECE raw | ECE s³ | ECE Möbius |
|---|---|---|---|---|---|---|
| never-forgets timetable | 2.933 | 2.933 | 2.933 | 0.167 | 0.337 | 0.265 |
| 3-day timetable | 1.600 | 1.600 | 1.600 | 0.213 | 0.507 | 0.196 |
| Perpetua* | 2.733 | 2.733 | 2.733 | 0.127 | 0.164 | 0.231 |
| long-context | 1.200 | 1.200 | 1.200 | 0.276 | 0.119 | 0.179 |

**P4 — SUPPORTED.** `V` is identical to the last printed digit in all 20 method × window cells under both
strictly increasing maps, while the calibration error of the same signal moves by up to a factor of three
(the 3-day timetable's settled-week ECE goes 0.346 → 0.679 under `s³`, and long-context's sick-window ECE
goes 0.276 → 0.119 — it becomes *better* calibrated at no gain whatsoever). Nothing was fitted to make this
happen; it is `(b)` of §1.1 arriving on the data.

The converse half needs a map that destroys the ordering rather than one that reverses it. `s → |s − 0.5|`
turned out to be a poor choice — for the timetables almost every confidence is below 0.5, so that map is
strictly *decreasing* on their support and the theorem predicts no change, which is what happens. Table 7
does it properly, permuting the distinct confidence values at random (same confidences, same labels, order
destroyed), 200 draws:

| method, first sick days | V raw | V order-scrambled | label-shuffle null |
|---|---|---|---|
| never-forgets timetable | 2.93 | 2.64 | 2.37 |
| 3-day timetable | 1.60 | 1.49 | 1.46 |
| Perpetua* | 2.73 | **1.31** | 1.32 |
| long-context | 1.20 | **0.80** | 0.27 |

Scrambling the order costs Perpetua* more than half its value and lands it exactly on its no-information
null. It costs the timetables almost nothing — there was no order to destroy, which is the same finding as
`V_order < 0` arriving by a different route.

### 1.6 Verdict on Part 1

The closed form is correct and the derivation is worth keeping: `(★)` is exact, `(★★★)` is the floor the
first draft of it missed, and the invariance result `(b)` is clean, general and confirmed to three decimals.
But the model as originally stated — "predicted V should match the measured gain" — **does not fit**, and two
of its four predictions were refuted:

* the plug-in estimate of `V` has a noise floor of 1-2.4 score points per day at the shift, comparable with
  the entire effect being predicted, so raw agreement between prediction and measurement (Perpetua*: 2.73
  against 2.83) is a coincidence of two biases and must not be reported as a success;
* the mass/shortfall decomposition the brief asked for does not carry Perpetua*'s advantage — both terms are
  within noise of the never-forgets timetable's. The decomposition that does carry it is signal-free floor
  against ordering value, and the answer is that **the timetables' ordering value at the shift is negative**;
* against that, the theory's best result is the one nobody asked for: F9's "+0.3 for the never-forgets
  timetable" is not a small gain, it is no gain at all (p = 0.115 against its own null), and the project can
  say so.

---

## Part 2 — confidence is concentration, and concentration is not a change statistic

### 2.1 Derivation

Fix a question at time `t`. The method holds a predictive distribution `p_t(·)` over the 38 places, and the
truth is `y_t`. Two functionals of that same object:

    C_t = max_x p_t(x)                    "confidence": how PEAKED the distribution is
    L_t = -log p_t(y_t)                   "surprise": how much mass it put where the world actually was

`C_t` is a function of `p_t` alone. It can be computed before `y_t` is revealed, and it is therefore, by
construction, incapable of containing any information about whether `p_t` is right — except through the prior
statistical relation between peakedness and accuracy that holds *while the regime is the one the model was
fitted to*. `L_t` is the per-observation log-likelihood ratio term against the truth; the sum of `L_t` over
recent questions is, up to an additive constant, the statistic a CUSUM or a likelihood-ratio change detector
accumulates:

    CUSUM_t = max(0, CUSUM_{t-1} + (L_t - E_0[L]))

where `E_0[L]` is the entropy-scale reference under the pre-change regime. A change in the world changes the
*location* of the mass relative to the truth, which is `L`; it need not change how *concentrated* the mass
is, which is `C`. Under a pure relocation of the truth with the model unchanged, `C` is exactly invariant:
if the world moves object `o` from place `a` to place `b` while `p_t` still says `a`, then `C_t` is
unchanged and `L_t` goes from `-log p_t(a)` to `-log p_t(b)`, an increase of `log(p_t(a)/p_t(b))`, which is
LARGE exactly when the model was confident. Hence the sharp corollary:

**The methods are most confidently wrong on the objects with the most regular past**, because regularity is
what produced the peak, and the peak is both what makes `C` high and what makes `L` explode when the truth
moves. Confidence and change evidence are not merely different; at a regime change they are *anti*-aligned.

### PREDICTIONS (written before Tables 13-16 were computed)

* **P5.** The max probability barely moves from the settled week to the first sick days: the shift in daily
  mean `C` is under 0.5 settled-week standard deviations for each timetable. The negative log-likelihood of
  the truth moves by more than 2 settled-week standard deviations.
* **P6.** As a detector of "the regime has changed", `C` is close to useless and `L` is good: question-level
  AUC for days 14-16 against days 9-13 near 0.5 for `C` (say within [0.45, 0.60]) and at least 0.70 for `L`,
  for the never-forgets timetable. If `C`'s AUC comes out high, the formalisation is wrong and I will say so.
* **P7 (the sharp one).** Within the first sick days, a method's stated confidence is HIGHER on objects whose
  truth differs from their settled-period modal location than on objects that did not move. Point-biserial
  `r(C, moved) > 0` per household, and positive for all three timetables on average. If `r` is negative or
  zero the corollary is refuted, and with it the "confidently wrong" reading of the effect.

### 2.2 What the logs carry, and one method that is missing

`dist` is a full 38-place distribution summing to 1, and `max(dist)` equals the logged `top_prob` exactly, so
`C` really is the confidence used everywhere else in the project. The truth is always one of the 38 keys, so
`L` never needs the floor. The `none_tt` rows are identical to the classical `TimetableLookup(bin=2h,
days=all)` rows used in Part 1 (496/496 matched on both `top_prob` and `correct`), so the two parts are about
the same questions.

**Perpetua\* logs no distribution anywhere under `results/`** — checked across every `.jsonl` in the tree.
The third distribution-logging classical method here is therefore the **1-day timetable**
(`TimetableLookup(bin=2h,days=all,hl=24h)`), with **last seen** as a degenerate control. That is a real gap:
the method Part 1 is about cannot be examined in Part 2. Everything below is about the timetable family.

### 2.3 Results

**Table 13/14 — the two functionals across the shift** (per household, then mean ± se over 10 households).

| method | C settled | C sick | L settled | L sick | C shift, sd of settled daily | L shift, sd |
|---|---|---|---|---|---|---|
| never-forgets timetable | 0.607 ± 0.008 | 0.509 ± 0.018 | 0.909 ± 0.051 | 2.141 ± 0.162 | **−1.95 ± 0.36** | **+3.61 ± 0.74** |
| 3-day timetable | 0.459 ± 0.008 | 0.375 ± 0.008 | 1.174 ± 0.043 | 1.960 ± 0.121 | **−2.02 ± 0.27** | **+2.77 ± 0.63** |
| 1-day timetable | 0.278 ± 0.011 | 0.264 ± 0.010 | 1.757 ± 0.058 | 2.071 ± 0.098 | **−0.48 ± 0.32** | **+1.52 ± 0.48** |
| last seen | 0.981 ± 0.000 | 0.981 ± 0.000 | 4.182 ± 0.220 | 3.301 ± 0.206 | — (C is constant) | −1.08 ± 0.37 |

**P5 — REFUTED for the two long-memory timetables, supported for the short-memory one.** The max probability
does not "barely move": it falls by about two settled-week standard deviations for both the never-forgets and
the 3-day timetable. It moves by less than half a standard deviation only for the 1-day timetable, and not at
all for last seen, whose confidence is a constant 0.981 in every window of the arc. The `L` half of the
prediction holds for the two long-memory timetables (+3.6 and +2.8 sd) and fails for the 1-day one (+1.5 sd).

**Table 15 — separation, days 14-16 against days 9-13, question level inside a household.**

| method | AUC of C | AUC of −C | AUC of L | AUC of entropy |
|---|---|---|---|---|
| never-forgets timetable | 0.332 ± 0.025 | **0.668 ± 0.025** | **0.767 ± 0.031** | 0.606 ± 0.023 |
| 3-day timetable | 0.337 ± 0.018 | 0.663 ± 0.018 | 0.718 ± 0.029 | 0.586 ± 0.012 |
| 1-day timetable | 0.473 ± 0.024 | 0.527 ± 0.024 | 0.570 ± 0.028 | 0.485 ± 0.022 |
| last seen | 0.500 ± 0.000 | 0.500 ± 0.000 | 0.442 ± 0.020 | 0.500 ± 0.000 |

**P6 — REFUTED in its first half, supported in its second.** `L` reaches AUC 0.767 as predicted. But `C` is
not near chance: at 0.332 it is 0.168 away from 0.5, against `L`'s 0.267 — a real detector, about
two-thirds as good, pointing *downwards*. The honest summary is not "concentration carries no change
evidence" but "concentration carries about 60% as much separation as likelihood does, in the opposite
direction to the naive reading".

**Table 18 — a detector built from each, one-sided CUSUM, drift and scale set on the settled week,
threshold 4 sd, per household.**

| method | L fires on day | fired | −C fires on day | fired |
|---|---|---|---|---|
| never-forgets timetable | **14.25 ± 0.16** | 8/10 | 16.00 ± 0.56 | **10/10** |
| 3-day timetable | 17.67 ± 2.26 | 9/10 | 15.60 ± 0.31 | 10/10 |
| 1-day timetable | 16.75 ± 1.28 | 8/10 | 20.30 ± 1.25 | 10/10 |
| last seen | 28.33 ± 0.67 | 3/10 | never | 0/10 |

`L` fires on the first sick day itself in the households where it fires; the falling-confidence detector
fires about two days later but in every household. Neither is useless, which was the strong claim.

**Table 16 — THE SHARP PREDICTION.** Within days 14-16, comparing objects whose truth differs from their own
days 9-13 modal location ("moved", 78.3% of questions) with those that stayed.

| method | r(C, moved) | C ∣ moved | C ∣ stayed | accuracy ∣ moved | accuracy ∣ stayed |
|---|---|---|---|---|---|
| never-forgets timetable | **−0.124 ± 0.101** | 0.461 ± 0.008 | 0.557 ± 0.029 | 49.9 ± 7.0 | 83.3 ± 6.7 |
| 3-day timetable | **−0.042 ± 0.074** | 0.366 ± 0.010 | 0.411 ± 0.020 | 56.3 ± 6.4 | 79.5 ± 8.0 |
| 1-day timetable | **+0.094 ± 0.062** | 0.279 ± 0.015 | 0.247 ± 0.013 | 63.4 ± 5.4 | 71.8 ± 9.6 |

**P7 — REFUTED.** The correlation is *negative* for the never-forgets timetable, the method the prediction
was aimed at, and indistinguishable from zero for the 3-day one. Confidence is lower, not higher, on the
objects that moved. The "confidently wrong on exactly the objects that changed" reading of this effect is not
what the logs contain, and the project should stop writing it that way.

What is true, and is a weaker but defensible version of the same point, is the *size*: the never-forgets
timetable's confidence drops from 0.557 to 0.461, about a sixth, while its accuracy drops from 83% to 50%,
about two fifths. `C` is a direct probability claim about its own answer being right, so on the objects that
stayed it is wildly *under*-confident (0.557 stated against 0.833 achieved) and on the objects that moved it
is close to right (0.461 against 0.499). The failure is not over-confidence on the changed objects. It is
that the confidence barely distinguishes the two populations at all.

Table 17 shows which link of the mechanism breaks. Confidence does track regularity of the settled past, as
the derivation says it must — r(C, settled regularity) = +0.205 ± 0.063 (never-forgets) and +0.199 ± 0.058
(3-day); the 1-day timetable, which cannot see the settled past, gives +0.021 ± 0.060. The link that fails is
the next one: r(settled regularity, moved) = +0.135 ± 0.094, not distinguishable from zero. **In this
scenario the objects that move are not especially the regular ones**, so the chain "regular past → high peak
→ confidently wrong when it moves" has no second link, and the corollary dies there rather than in the
mathematics.

Table 16b ties Part 2 back to Part 1. Mean `C` on the questions the method got right, minus mean `C` on the
ones it got wrong:

| method | settled 9-13 | sick 14-16 | back 24-26 |
|---|---|---|---|
| never-forgets timetable | +0.127 ± 0.027 | **−0.047 ± 0.032** | +0.132 ± 0.024 |
| 3-day timetable | +0.099 ± 0.020 | **+0.004 ± 0.024** | +0.021 ± 0.021 |
| 1-day timetable | +0.051 ± 0.009 | +0.070 ± 0.012 | +0.064 ± 0.018 |
| last seen | 0.000 | 0.000 | 0.000 |

The long-memory timetables' confidence separates right from wrong by about 0.1 in the settled world and by
nothing at all — or backwards — at the shift. That is `V_order < 0` from Part 1, measured on the same rows by
a different statistic.

### 2.4 A repair, stated as post hoc, and then tested out of sample

The derivation assumed the model is fixed while the world moves. These methods are not fixed: the
never-forgets timetable ingests the sick days into the *same* time-of-day histogram, so during the first
sick days its predictive distribution is a mixture of two regimes. The maximum of a mixture falls as the
second component arrives. So:

**Repaired claim.** `C` is not a change statistic *of a fixed model*. For a model that folds post-change
observations into its own predictive mixture, `C` falls at a change, by an amount that grows with the share
of its memory window that is still pre-change. `C` therefore inherits change-detection power in proportion
to memory length, while `L` has it regardless.

This was written after seeing sick10_owner, so it is fitted, and it needs held-out data. It makes an ordered
prediction — never-forgets ≈ 3-day > 1-day > last seen (which never mixes at all, and whose `C` is exactly
constant) — which **Table 19 tests on three scenarios not used to form it**:

| scenario | never-forgets AUC(−C) | 3-day AUC(−C) | 1-day AUC(−C) | last seen | never-forgets AUC(L) |
|---|---|---|---|---|---|
| sick10_owner (in-sample) | 0.668 ± 0.025 | 0.663 ± 0.018 | 0.527 ± 0.024 | 0.500 | 0.767 ± 0.031 |
| sick10_all | 0.664 ± 0.025 | 0.676 ± 0.019 | 0.577 ± 0.020 | 0.500 | 0.763 ± 0.030 |
| sick10_partial | 0.590 ± 0.026 | 0.608 ± 0.019 | 0.545 ± 0.019 | 0.500 | 0.661 ± 0.038 |
| holiday_to_work | 0.546 ± 0.019 | 0.541 ± 0.016 | (not run) | — | 0.546 ± 0.017 |

The ordering holds in all four scenarios, and `AUC(L) ≥ AUC(−C)` for the never-forgets timetable in all four.
The numeric thresholds I wrote down were not all met (1-day reaches 0.577 in sick10_all against a predicted
ceiling of 0.56, and never-forgets falls to 0.590 in sick10_partial against a predicted floor of 0.60), so
call this **partly supported**: the mechanism's rank prediction survives three held-out scenarios, its
calibration does not. `holiday_to_work` is a weak change for every statistic (0.54-0.55), which is its own
finding and not a failure of the repair.

### 2.5 Verdict on Part 2

The functional distinction is mathematically right and worth stating: `C = max_x p(x)` and `L = −log p(y)`
are different functionals, only the second involves the truth, and only the second is what a change detector
accumulates. Both empirical claims built on top of it failed:

* **"the max does not move at a change" is false here** (−2 sd, AUC 0.67, and a CUSUM on −C that fires in
  10/10 households). `L` is better — earlier by about two days, AUC 0.77 against 0.67 — but the contrast is
  a factor of roughly 1.5, not a difference in kind;
* **"confidence is highest on exactly the objects that changed" is false here** — the correlation is
  −0.12 ± 0.10 for the method it was aimed at. The surviving statement is quantitative, not qualitative: the
  confidence falls by a sixth where the accuracy falls by two fifths, and it does not separate the moved
  objects from the stayed ones in any useful way;
* the reason the sharp version fails is measurable and is not in the mathematics: in this scenario the
  objects that move are not the ones with the most regular past (r = +0.135 ± 0.094).

What replaces them is the repair in §2.4, which has survived three held-out scenarios in rank order and
which makes `C`'s usefulness as a change statistic an explicit function of memory length rather than a
yes/no property.

---

## Standing caveats

* Ten households (`hh_s0`…`hh_s9`), one patrol setting (`t03`), one scenario family for Part 1. Every number
  is computed per household first and aggregated as mean ± se over households; nothing pools raw questions
  across households; cells under 10 questions are dropped, and the household count is printed beside every
  cell in the script output (some windows lose households to that rule — the "first days back" cells carry
  n = 5-6 in the cross-fitted tables, and their standard errors are correspondingly wide).
* Question counts per day are not constant across households (16/day for four of them, as few as 4/day on
  some days for others), so the per-question → per-day conversion is done with each household's own rate.
* Both F9's estimator and the plug-in `V̂` choose thresholds with hindsight; the cross-fitted estimator in
  Table 9/12 does not, and it is the one the conclusions rest on.
* Part 2 cannot include Perpetua*, which logs no distribution. Its Part 1 conclusion (`V_order > 0` at the
  shift) is therefore not backed by a Part 2 mechanism.
* The permutation nulls resample correctness labels inside a household-window, which treats questions as
  exchangeable within a cell. They are not exactly — consecutive questions about the same object are
  correlated — so the nulls are, if anything, slightly optimistic, which makes the "no measurable gain"
  finding for the timetables conservative in the direction it is claimed.
