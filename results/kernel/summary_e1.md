# Kernel arms (K0/K1/K5) — E1, Brier-PRIMARY

54000 rows. Transition kernel replaces marginal C1-C4. bin_hours=4 (cadence-matched; 1h/2h discard >90% of pairs, see D2). PRIMARY = Brier (lower better); top-3 secondary; top-1 in appendix.

## D2 — discarded-pair fraction by bin width (why bins are wide)

| bin | mean discard frac | mean kept pairs |
|---|---|---|
| 1h | 98.26% | 25 |
| 2h | 93.05% | 71 |
| 4h | 71.32% | 291 |

1h/2h bins discard almost every pair at this observation cadence (~7h between snapshots) -> 4h operational. This is a data-density limit, not a modeling choice; EM was deliberately avoided (states are observed).

## Brier (PRIMARY, lower=better) vs D (moved_enriched, mean [95% CI])

| arm | D0 | D1 | D2 | D3 | D5 | D7 | D10 | D14 | D21 | D28 |
|---|---|---|---|---|---|---|---|---|---|---|
| K0 | 0.947 [0.946,0.947] | 1.000 [0.923,1.080] | 1.000 [0.920,1.077] | 1.000 [0.923,1.080] | 1.000 [0.920,1.083] | 1.000 [0.923,1.077] | 1.000 [0.917,1.083] | 1.000 [0.920,1.077] | 1.000 [0.920,1.080] | 1.000 [0.920,1.083] |
| K1 | 0.947 [0.946,0.947] | 0.936 [0.933,0.940] | 0.915 [0.901,0.928] | 0.892 [0.872,0.913] | 0.745 [0.716,0.772] | 0.663 [0.629,0.695] | 0.538 [0.502,0.575] | 0.626 [0.585,0.671] | 0.544 [0.501,0.585] | 0.542 [0.501,0.584] |
| K5 | 0.247 [0.217,0.277] | 0.248 [0.215,0.282] | 0.283 [0.252,0.312] | 0.308 [0.271,0.350] | 0.142 [0.117,0.169] | 0.260 [0.228,0.292] | 0.192 [0.165,0.220] | 0.221 [0.193,0.251] | 0.298 [0.262,0.335] | 0.232 [0.199,0.265] |

## top-3 acc (secondary) vs D (moved_enriched, mean [95% CI])

| arm | D0 | D1 | D2 | D3 | D5 | D7 | D10 | D14 | D21 | D28 |
|---|---|---|---|---|---|---|---|---|---|---|
| K0 | 0.047 [0.032,0.063] | 0.500 [0.462,0.540] | 0.507 [0.467,0.548] | 0.500 [0.458,0.538] | 0.505 [0.467,0.543] | 0.500 [0.460,0.542] | 0.500 [0.460,0.540] | 0.500 [0.460,0.540] | 0.500 [0.462,0.538] | 0.507 [0.467,0.548] |
| K1 | 0.047 [0.030,0.063] | 0.255 [0.220,0.290] | 0.287 [0.252,0.325] | 0.403 [0.363,0.440] | 0.488 [0.450,0.530] | 0.763 [0.728,0.797] | 0.870 [0.842,0.897] | 0.893 [0.868,0.917] | 0.920 [0.897,0.942] | 0.928 [0.908,0.948] |
| K5 | 0.997 [0.992,1.000] | 0.993 [0.987,0.998] | 0.995 [0.988,1.000] | 0.992 [0.983,0.998] | 1.000 [1.000,1.000] | 0.997 [0.992,1.000] | 0.993 [0.987,0.998] | 0.993 [0.985,0.998] | 0.988 [0.980,0.997] | 0.998 [0.995,1.000] |

## Paired K1 - K0 (Brier; same episodes; moved_enriched, pooled D>=1)

| slice | ΔBrier [95% CI] | n |
|---|---|---|
| all | -0.288 [-0.313,-0.265] | 5400 |
| moved | -1.106 [-1.119,-1.093] | 2700 |
| not-moved | 0.529 [0.513,0.545] | 2700 |

Negative ΔBrier = K1 better-calibrated than last-obs parroting. This is the headline the marginal arms could not move (their paired Δacc was ~0).

## D4 — K1 vs K5 headroom by slice (moved_enriched Brier, pooled D>=1)

| slice | K0 | K1 | K5 |
|---|---|---|---|
| moved | 2.000 | 0.894 | 0.364 |
| not-moved | 0.000 | 0.529 | 0.121 |