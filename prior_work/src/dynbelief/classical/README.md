# Classical belief-model arms (C-tier)

One shared Bayes filter; arms differ ONLY in rate parameterization. This is
literally true in code: every arm is a `RateModel` plugged into
`filter.Filter`, and every prediction goes through `Filter.predict(t)` /
`Filter.update(obs)` — no arm has a bespoke prediction path.

## Process model (the shared filter)

Inhomogeneous random-refresh Markov jump process. In receptacle r, an object
survives with rate lambda(o, r, t); at a refresh it redraws from the
time-varying occupancy pi(o, ., t):

    P(X_t = r | X_t0 = r0) = e^{-int lambda} 1[r=r0]
                             + int_t0^t lambda(s) e^{-int_s^t lambda} pi_r(s) ds

discretized on a 15-min grid. Constant-parameter two-state case reproduces the
telegraph solution q(t) = pi + (q0 - pi) e^{-lambda t} (unit-tested to 2e-3).

State modes (config flag, both implemented): `categorical` (R+1-state CT-HMM
forward pass, exact normalization — preferred) and `per_edge` (independent
binary recursion per (object, receptacle), renormalized at query — the FreMEn/
persistence-filter native form; renormalization mass logged, cost measured in
summary.md W5: ~0 at this scale). Observation likelihood pluggable via
`fn_rate` (false-negative prob, default 0 = noiseless banks).

## Arms — rate parameterization, reference consulted, hyperparameters

| arm | occupancy pi(o,r,t) | rate lambda | hyperparams (L4-selected) | reference consulted |
|---|---|---|---|---|
| C0 lastobs | uniform (unused after an update) | 0 | — | — (definition) |
| C1 constant | per-object empirical occupancy, per-class backoff, Laplace 0.5 | per-class MLE: changes / observed time (same-day pairs) | — | Persistence Filter (Rosen et al., github.com/david-m-rosen/Persistence-Filter): exponential survival + MLE hazard |
| C2 spectral | mu + sum_j a_j cos(w_j t) + b_j sin(w_j t); streaming Fourier sums at snapshot times, sample-mean basis correction; top-K by amplitude | as C1 | K in {1,2,3,5}; selected 2-3 typically | FreMEn (Krajnik et al., T-RO 2017; github.com/gestom/fremen + wiki), gestom/fremen_activity, sergimolina/STeF-Map |
| C3 GLM | per-object multinomial logistic on calendar features: sin/cos 24h (x2 harmonics), sin/cos 168h (x2), weekend flag, weekend x daily interactions; L2 | as C1 | C in {0.1, 1, 10} | statistical twin of C2 with day-type mixtures (standard GLM) |
| C4 regime-HMM | day-level latent regime chain shared across objects; emissions per (object, regime, 4h-tod-bucket), Dirichlet 0.5; Baum-Welch, 5 restarts; query-day regime = last posterior x transition | as C1 | n_regimes in {2,3,4} by held-out DAY log-likelihood | classical routine-inferencer (day-type HMM; EM per Rabiner) |
| C5m marginal oracle | Monte-Carlo MARGINAL occupancy from the generator (per object, minute-of-week) | MC move-frequency per (object, week-bucket) | n_sims=200 | the MARGINAL ceiling; ignores conditional dependence |
| **C5+ particle oracle** | posterior from generator TRAJECTORIES: 2500 sims, keep those where the object was at its last-observed receptacle at the last-observed time, read its state at the query time | (implicit in the trajectories) | n_particles=2500 | the **TRUE ceiling**: captures conditional dependence (dish cycle sink->cupboard, carry-chains) the marginal misses. Reduces to C5m with no observation. Both are the only arms allowed to read the profile (L1 exception) |

Candidate period set (W1; includes 24h AND 168h):
{168h, 84h, 56h, 42h, 24h, 12h, 8h, 6h, 4h}.

## Evaluation parity

Same banks / observation streams / query times / D grid {0,1,3,7,14} as the
LLM arms; output = top-3 receptacle distribution + implied remainder; scored by
`dynbelief.experiments.e1.score_prediction` (THE shared scorer) with Brier and
log-loss clipped to [0.01, 0.99] (clip stated in methods; LLM rows re-scored
from stored p_true for the combined tables). D=0 emits the explicit uniform
prior for C0-C4. Held-out objects get class-prior-else-uniform (W3; classes
are disjoint by construction, so uniform in practice — the C4-attribution
slice, not special-cased).

## Leakage

L1: no arm reads a profile YAML (spy-tested); C5 is the explicit oracle
exception. L2: calendar covariates only (clock, day-of-week, weekend flag).
L3: no resident day-type feature anywhere; C3/C4 must infer regime structure
(C4's learned schedule logged per household — see regime_schedule_t1.md).
L4: all hyperparameters selected on held-out observation likelihood within the
history window, never query accuracy; cold-start cells (D=1) fall back to
defaults and are logged `degenerate_fit` per row (W2), never hidden.

## Files

filter.py (shared filter) · rates/{base,c0..c4}.py · oracle.py (C5) ·
run.py (parity runner -> results/classical/rows.parquet + fits.jsonl) ·
summary.py (combined tables incl. LLM rows) · tests/test_classical.py
(C2-DC==C1, telegraph analytic, oracle-vs-MC, L1 spy, C4 synthetic recovery).
