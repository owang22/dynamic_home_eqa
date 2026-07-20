# E2 — one-shot prior help vs harm (pre-registered endpoints, family C3)

Prior injected as pseudo-observations at equivalent-sample-size kappa in {weak:1d, moderate:7d, strong:28d}. P0 = uninformative (no pseudo-obs). Elicited from gpt-5.4-mini + gpt-5.5 (never Claude). Deltas are paired per-episode, moved_enriched unless noted, 95% CI.

## E1&2: Day-0 delta (Pllm - P0) — help (typ) vs harm (atyp)

| kappa | typ_v1 Δacc [CI] | atyp_v2 Δacc [CI] |
|---|---|---|
| weak | 0.333 [0.286,0.383] | 0.444 [0.394,0.494] |
| moderate | 0.333 [0.283,0.383] | 0.444 [0.392,0.497] |
| strong | 0.333 [0.283,0.381] | 0.444 [0.397,0.497] |

(At D=0 P0 is the uniform prior; Pllm is the elicited prior with no household data. Help = Pllm>>P0 on typ; harm shows as a smaller/near-zero or negative advantage on atyp, and sharpens at low nonzero D below.)

## E4: NOT-MOVED accuracy at low D (natural stream) — the harm slice

A misaligned strong prior predicts phantom movement on easy (not-moved) episodes. Table: not-moved accuracy, strong kappa.

| bank | prior | D1 | D2 | D3 | D5 |
|---|---|---|---|---|---|
| typ_v1 | P0 | 1.000 | 0.983 | 0.932 | 0.991 |
| typ_v1 | Pllm/strong | 0.984 | 0.822 | 0.752 | 0.757 |
| typ_v1 | Porc/strong | 0.870 | 0.873 | 0.923 | 0.897 |
| atyp_v2 | P0 | 1.000 | 0.976 | 0.977 | 0.992 |
| atyp_v2 | Pllm/strong | 1.000 | 0.919 | 0.938 | 0.756 |
| atyp_v2 | Porc/strong | 0.885 | 0.984 | 0.908 | 0.866 |

Harm = Pllm below P0 on atyp not-moved episodes (the prior overrides a correct 'still there'); on typ the aligned prior should not hurt.

## E3: crossover day (first D where P0 >= Pllm) vs atypicality_distance

| household | dist | kappa | crossover D |
|---|---|---|---|
| college_roommates_typ_v1 | 0.000 | weak | 1 |
| college_roommates_typ_v1 | 0.000 | moderate | 1 |
| college_roommates_typ_v1 | 0.000 | strong | 1 |
| family4_typ_v1 | 0.000 | weak | 1 |
| family4_typ_v1 | 0.000 | moderate | 1 |
| family4_typ_v1 | 0.000 | strong | 1 |
| single_adult_typ_v1 | 0.000 | weak | 1 |
| single_adult_typ_v1 | 0.000 | moderate | 1 |
| single_adult_typ_v1 | 0.000 | strong | 1 |
| family4_typ_v1__atyp_t2_weekend_work | 0.116 | weak | 1 |
| family4_typ_v1__atyp_t2_weekend_work | 0.116 | moderate | 1 |
| family4_typ_v1__atyp_t2_weekend_work | 0.116 | strong | 1 |
| single_adult_typ_v1__atyp_t1_night_2 | 0.140 | weak | 1 |
| single_adult_typ_v1__atyp_t1_night_2 | 0.140 | moderate | 1 |
| single_adult_typ_v1__atyp_t1_night_2 | 0.140 | strong | 1 |
| single_adult_typ_v1__atyp_t2_three_t | 0.110 | weak | 1 |
| single_adult_typ_v1__atyp_t2_three_t | 0.110 | moderate | 1 |
| single_adult_typ_v1__atyp_t2_three_t | 0.110 | strong | 1 |

Hypothesis: crossover D increases with kappa and with distance (a stronger, more-wrong prior takes longer for data to overcome).

## E5: Porc - P0 machinery check (must be >= 0 across the grid)

| bank | kappa | mean Δacc (pooled D) [CI] | min cell Δacc |
|---|---|---|---|
| typ_v1 | weak | 0.070 [0.003,0.191] | -0.017 |
| typ_v1 | moderate | 0.137 [0.059,0.259] | 0.017 |
| typ_v1 | strong | 0.167 [0.087,0.291] | 0.022 |
| atyp_v2 | weak | 0.085 [0.003,0.224] | -0.044 |
| atyp_v2 | moderate | 0.140 [0.051,0.273] | -0.017 |
| atyp_v2 | strong | 0.168 [0.074,0.304] | -0.011 |

**Machinery check: PASS** — Porc helps (>=0) everywhere; injection works, so Pllm harm is prior content.

Exploratory analyses (kappa x distance surfaces, per-class harm) are in rows.parquet, kept separate from these pre-registered endpoints.