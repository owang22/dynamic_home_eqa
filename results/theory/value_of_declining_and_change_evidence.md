# Two measured effects turned into mathematics, and tested

Offline modelling on saved logs, 2026-09-23. No new runs, no model calls. Scripts beside this file:
`part1_value_of_declining.py`, `part2_change_evidence.py`. Every number below is printed by one of them;
raw stdout is kept in `part1_output.txt` and `part2_output.txt`.

The order of work was: derive, write the prediction down, then compute. The prediction blocks below were
written into this file before the corresponding table existed, and each is marked SUPPORTED, PARTLY
SUPPORTED or REFUTED afterwards. Where the model misses, the miss is the headline.

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

<!-- TABLES PART 1 -->

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

<!-- TABLES PART 2 -->
