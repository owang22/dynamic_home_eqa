# E1 v2 -- adaptation from observation history

rows: 248  |  model: ['mock_lastobs']  |  prompt_hash: 65fe04cb4ad9

## Comprehension probes: 3/3 passed
| probe | object | when | expected | predicted | pass | p(true) |
|---|---|---|---|---|---|---|
| static_vase | vase | Monday 12:00 | table_d1 | table_d1 | YES | 0.7 |
| immediate_parrot | toaster | Sunday 04:17 | counter_k1 | counter_k1 | YES | 0.7 |
| periodic_object | mug | Saturday 10:05 | sink_k1 | sink_k1 | YES | 0.7 |

If these fail, the model isn't reading the task. If they pass but moved-episode accuracy is ~0, the failure is forecasting (unrecorded movement), not prompt-fixable.

## profile_text = False  (accuracy / Brier / log-loss vs history-days)
| bank | metric | D=0 | D=1 | D=3 | D=7 | D=14 | moved@D14 |
|---|---|---|---|---|---|---|---|
| atyp_v2 | acc | 0.167 | 0.333 | 0.667 | 0.417 | 0.250 | 0.000 |
| atyp_v2 | Brier | 0.953 | 0.864 | 0.550 | 0.750 | 0.976 | 1.459 |
| atyp_v2 | logloss | 2.911 | 2.562 | 1.581 | 2.227 | 2.819 | 4.006 |
| typ_v1 | acc | 0.083 | 0.417 | 0.417 | 0.333 | 0.500 | 0.000 |
| typ_v1 | Brier | 0.995 | 0.822 | 0.926 | 0.830 | 0.671 | 1.462 |
| typ_v1 | logloss | 3.088 | 2.422 | 2.586 | 2.498 | 1.992 | 4.129 |

## profile_text = True  (accuracy / Brier / log-loss vs history-days)
| bank | metric | D=0 | D=1 | D=3 | D=7 | D=14 | moved@D14 |
|---|---|---|---|---|---|---|---|
| atyp_v2 | acc | 0.167 | 0.333 | 0.667 | 0.417 | 0.250 | 0.000 |
| atyp_v2 | Brier | 0.953 | 0.864 | 0.550 | 0.750 | 0.976 | 1.459 |
| atyp_v2 | logloss | 2.911 | 2.562 | 1.581 | 2.227 | 2.819 | 4.006 |
| typ_v1 | acc | 0.083 | 0.417 | 0.417 | 0.333 | 0.500 | 0.000 |
| typ_v1 | Brier | 0.995 | 0.822 | 0.926 | 0.830 | 0.671 | 1.462 |
| typ_v1 | logloss | 3.088 | 2.422 | 2.586 | 2.498 | 1.992 | 4.129 |

## Moved vs not-moved (pooled D>=1, profile_text=False)
| bank | not-moved acc | moved acc | moved Brier |
|---|---|---|---|
| atyp_v2 | 0.606 (n=33) | 0.000 (n=15) | 1.459 |
| typ_v1 | 0.645 (n=31) | 0.000 (n=17) | 1.461 |

## C4 (held-out vs observed, atyp_v2 vs atyp_shift_v1, D=7)
| slice | atyp_v2 | atyp_shift_v1 |
|---|---|---|
| all | 0.417 | 0.250 |
| held-out | 0.000 | 0.000 |
| observed | 0.625 | 0.500 |

Numbers only. C1 = atyp accuracy rises with history while typ stays flatter; lower Brier/log-loss = better-calibrated. With the mock client these are a last-observation baseline, not an LLM result.