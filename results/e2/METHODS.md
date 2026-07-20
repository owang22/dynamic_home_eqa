# E2 methods note — one-shot prior: help vs harm

## Arms (identical filter + rate family; only the PRIOR differs)

- **P0** uninformative prior — no pseudo-observations; equals the C-arm as run.
- **Pllm** LLM-elicited prior (below), injected as pseudo-observations.
- **Porc** oracle-parameter prior — pseudo-observations sampled from the C5
  generator marginal, injected at the same kappa. Machinery control: Porc must
  help everywhere; if it does not, the injection is broken and Pllm is void.

Primary rate family **C3** (periodic GLM); secondary **C1** (constant rate).
Both reported; C3 carries the headline.

## Injection — MAP prior as pseudo-observations (NOT initialization-only)

A prior is expressed as `kappa` days of synthetic snapshots consistent with the
elicited (or oracle) parameters, PREPENDED to the real observation window before
fitting (`dynbelief/e2/inject.py`). The fit blends prior and data by sample
size, so a strong prior persists through several days of real data — harm
persistence is measurable, and one real day cannot overwrite it (which an
initialization-only scheme would allow). Equivalent sample sizes:

    kappa in {weak: 1 day, moderate: 7 days, strong: 28 days}.

The pseudo stream is weekday-aligned (t mod week), so day indices may overlap
the real window; this reinforces the prior at the correct weekday/time-of-day
rather than shifting the calendar. The transform (elicited params ->
pseudo-observations) is unit-tested for occupancy faithfulness and kappa scaling
(`tests/test_e2.py`).

## Elicitation

- **Source models: gpt-5.4-mini and gpt-5.5 ONLY. Never Claude** — Claude
  drafted the typical profiles, so using it as the prior source would be
  circular. Enforced by an assertion (`elicit.ALLOWED_MODELS`; refusal
  unit-tested).
- **Inputs:** the object-class list, the receptacle vocabulary, and a GENERIC
  household descriptor (`"a single working adult's home"`, `"a home shared by
  two college students"`, `"a two-parent, two-child family home"`). Never the
  profile YAML/prose, never observations. One-shot = zero household-specific
  data.
- 5 samples per model (temperature 0.7), mixture-averaged across models+samples
  into one prior per BASE profile; the same population prior is applied to a
  typical household and to its atypical transform (that misfit is the point).
- Fixed prompt, hashed; every raw output logged to `results/e2/raw/<base>/`.

Elicited per class: `home`, up to 3 `secondary` receptacles + relative
occupancy weights, `active_windows` (time-of-day buckets), `weekday_weekend`
skew, and `move_rate`. These drive the pseudo-observation sampler.

## Run grid

{typ_v1, atyp_v2} x D in {0,1,2,3,5,7,10,14,21,28} x kappa x {P0,Pllm,Porc} x
{natural, moved_enriched}. All offline except the one-time elicitation calls.
n=60 episodes/cell (shared stream episodes; paired deltas per episode).

## Pre-registered endpoints (computed first; exploratory kept separate)

1. Day-0 delta (Pllm - P0), typ — the help.
2. Day-0 delta (Pllm - P0), atyp — the harm.
3. Crossover day (first D with P0 >= Pllm) per (household, kappa) vs
   atypicality_distance.
4. NOT-MOVED accuracy at low D vs the P0/C0 reference — where a misaligned
   prior does its damage (moved episodes are ceiling-limited, C5 MOVED top-1 =
   0.203).
5. Porc - P0 >= 0 across the grid (machinery check).

See `summary.md` for the endpoint results and `rows.parquet` for the full grid.
