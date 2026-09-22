# Uncertainty-aware prediction roster for the patrol testbench

Written before the runs (21 Sep 13:55). Setting: a stream of sightings (nightly patrol at 03:00 plus
found-it feedback 10 min after each question) and 64 "where is X" questions a day; answer = one in-house
spot of ~38 with a confidence. All agents are wrappers around the frozen most-frequent counter (sighting
histogram, empty-look suppression off) unless stated; every agent has a degenerate setting that must
reproduce the classical most-frequent log to the digit. Code: `src/baselines/patrol/uq_agents.py`.
Logs: `results/confidence_shift_2026-09-20/uq/<bank set>/<agent>/hh_s*.jsonl`, classical row format
(answer, top_prob, correct, truth, ...) plus agent-specific columns.

## 1. Online conformal with decaying step sizes, relevance-weighted ("explore until confident")

Papers: Angelopoulos, Barber, Bates, "Online conformal prediction with decaying step sizes", ICML 2024
(arXiv 2402.01139): threshold update `q_{t+1} = q_t + eta_t (1[y_t not in C_t] - alpha)` in SCORE space,
`C_t = {y : s_t(y) <= q_t}`, `eta_t = eta_0 * t^(-1/2 - eps)`; long-run coverage for arbitrary sequences and
convergence to the population quantile when the stream is stable. Ren et al., "Explore until Confident",
2024 (arXiv 2403.15941): relevance-weighted score `rho_y = Rel(x) (f_y - 1)`, nonconformity `1 - rho`,
prediction sets built causally and intersected over steps, stop exploring when one answer remains.

Adaptation: score `s(y) = 1 - Rel * p(y)` where p is the counter's spots-only probability and Rel in (0, 1]
is the freshness of the counter's evidence for that object, `Rel = 2^(-age / tau)` with age = time since the
object's last positive sighting (tau = 24 h; Rel = 1 switches it off). Stale evidence -> larger scores ->
larger sets. Set `C_t = {y : s(y) <= q_t}`; answer = argmax p (unchanged); confidence = 1 / |C_t| and the
top probability both logged. Explore-until-confident: with `--look`, when |C_t| > 1 the agent spends the
one free look on the room holding the most set mass, folds it in and re-answers (off by default; the fb
banks have no free look). Knobs: alpha 0.1, eta_0 0.05, eps 0.1, tau 24 h, step floor eta_min 0.005 (so a
shift late in the week can still move the threshold; the paper's pure decay would freeze it).
Expectation: stationary synthetic stream -> coverage within 0.90 +- 0.03 after 200 questions and q_t
converging (sd of q over the last 100 steps < 0.05); on the fb banks coverage 0.87-0.93 pooled over plain
days; set size grows on shift days; Rel < 1 must never lower coverage (it only enlarges sets).

## 2. Staleness detector: conformal test martingale on the question errors, with a reset

Papers: Vovk, Gammerman, Shafer, "Algorithmic Learning in a Random World" (conformal test martingales;
"simple mixture" betting `M_t = integral_0^1 prod_i eps p_i^(eps-1) d eps`); Shin, Ramdas, Rinaldo,
"E-detectors: a nonparametric framework for sequential change detection", New England J. Stat. Data Sci.
2024 (the martingale is an e-process; a threshold 1/delta gives a false-alarm guarantee).
Adaptation: after each question the found-it feedback reveals the truth; nonconformity `s_t = 1 - p_t(truth)`;
conformal p-value `p_t = (#{i < t : s_i > s_t} + U #{s_i = s_t} + 1) / (t + 1)` over the calibration window
since the last reset (U uniform, seeded); martingale over a grid of eps in (0, 1). When `M_t >= 1/delta`
(delta = 0.01 -> 100) the counter is reset: counts multiplied by `factor` (default 0.1) for all objects,
window and martingale restarted. Logs M_t, p_t, fires. Knobs: delta, factor, minimum window 20.
Expectation: on a stationary synthetic stream M_t stays below 10 for 1000 questions (no false alarm at
delta 0.01 with probability >= 0.99); on a synthetic shift (the true spot distribution changes at t = 300)
M_t exceeds 100 within 60 questions; on the fb banks it should fire on more shift days than non-shift days
(BOCPD on patrol surprise never fired). Why it can work where BOCPD did not: it watches the model's own
question errors under feedback, not the household-level patrol surprise.

## 3. Forget-rate hedging: Bayesian model averaging over counters with different half-lives

Papers: Herbster and Warmuth, "Tracking the best expert", 1998 (fixed share); Raftery, Karny, Ettler,
"Online prediction under model uncertainty via dynamic model averaging", 2010. Current use in the shift
literature: model averaging over forgetting factors is the standard baseline for "learn, saturate, drop,
re-learn" without a detector.
Adaptation: K = 6 counters with half-lives {6, 12, 24, 48, 96, none} h; weights `w_k` updated at every
positive sighting (patrol and feedback) by the counter's spots-only probability of the seen spot, then
mixed with fixed share `alpha_share = 0.02` toward uniform; prediction = sum_k w_k p_k; confidence = top
probability of the mixture; logs the weight on each half-life. Knobs: the half-life set, alpha_share.
Expectation: with a single half-life the agent equals that counter to the digit; on a stationary stream the
weight moves to the longest half-lives (>= 0.6 on {96, none} by day 3); after a shift the weight on
{6, 12} h rises within a day; on the fb banks accuracy >= plain most frequent on Mon/Tue (the re-learn
days) and never lower by more than 2 points on plain days.

## 4. LLM confidence channels (small test only: one household, two days, local Qwen3.8-27B)

Papers: Kadavath et al. 2022 (P(True)); Tian et al. 2023 (verbalized confidence); Farquhar et al., "Detecting
hallucinations in large language models using semantic entropy", Nature 2024; Lyu et al. 2024 "Calibrating
large language models with sample consistency"; Ulmer et al. 2024 (APRICOT, calibration from generations).
Adaptation on the existing naive agent (`patrol.llm --format conf`): three confidence channels for the same
answer: (a) verbalized (already logged: ~0.95 always), (b) token probability: the first-token logprob of
the chosen spot under constrained decoding (vLLM `logprobs`), renormalized over the spot options that share
no prefix, (c) sample agreement: 5 samples at temperature 0.7, confidence = share agreeing with the greedy
answer (semantic entropy reduces to this for exact-match answers). Expectation: reliability diagram of (a) is
a flat line at 0.95; (b) and (c) must have positive slope; (c) must separate correct from wrong answers by
>= 0.2 mean confidence. Budget: ~120 questions x (1 + 5) calls.

## Trivial-case checks (run before any bank)
- `none` settings == classical most-frequent log: 0 mismatches.
- Synthetic stream (`uq_synth.py`): 40 spots, object at spot A with prob 0.85 then, after t = 300, spot B with
  prob 0.85; base counter with 24 h half-life. Conformal coverage 0.90 +- 0.03 on the stationary segment;
  martingale < 10 before the shift, > 100 within 60 questions after; BMA weight on short half-lives rises
  after the shift.

## Addendum, 21 Sep 14:40 (second research agent) — what changed for the regime banks

* Base: every wrapper now sits on `--base timetable` (TimetableLookup, 2 h bins, days=all — the learner that shows the
  regime shape; `DiscountedTimetable` adds the martingale's count discount) or `--base mostfreq`; `--half-life` applies
  to either. Degenerate checks to the digit against the classical logs: none+mostfreq, none+timetable, bma with one
  half-life, martingale with an unreachable threshold, ocp's answers (0 mismatches on sick_owner and sick_all hh_s0).
* Rows carry `stage`, `moment` and `owner` (from the bank's question rows and the resident cards).
* Detector (2): the plain simple-mixture martingale decays to ~1e-5 over a stationary lead and can never fire
  (problems_found P1); the default is now the CUSUM e-detector of Shin, Ramdas, Rinaldo 2024 — each grid point's
  product restarts at 1 when it falls below 1, `M_t = max(M_{t-1}, 1) e_t` — at threshold 1000 (delta 1e-3; ARL
  guarantee). `--factor 1.0` makes it a monitor (fires logged, no reset). Repeated questions (same object, no new
  sighting since its previous question, same truth) do not step the detector (P2). Synthetic: 2/50 false alarms in 1000
  stationary steps; a 90 -> 50% accuracy shift detected after a median 21 questions.
* (5) `nexcp`: conformal beyond exchangeability (Barber, Candès, Ramdas, Tibshirani 2023): (1 - alpha) quantile of the
  time-weighted past scores (weights 2^(-age/tau_w), tau_w 24 h; 0 = unweighted split conformal) plus a unit mass at
  +inf; same score as ocp. Expectation E8 in uq/regime/EXPECTATIONS.md.
* BMA default half-lives on the timetable base: 24, 72, 168, inf hours (a 6 h half-life on 2 h bins is last-seen).
* LLM channel (b): the multiple-choice letter is asked without a JSON schema (P3: the quoted letter is a merged token
  for A-I but not J, which made "somewhere else" a tokenization artifact).
