# E1 v2 -- adaptation from observation history

rows: 248  |  model: ['gpt-5.4-mini']  |  prompt_hash: 65fe04cb4ad9

## Comprehension probes: 3/3 passed
| probe | object | when | expected | predicted | pass | p(true) |
|---|---|---|---|---|---|---|
| static_vase | vase | Monday 12:00 | table_d1 | table_d1 | YES | 0.98 |
| immediate_parrot | toaster | Sunday 04:17 | counter_k1 | counter_k1 | YES | 0.98 |
| periodic_object | mug | Saturday 10:05 | sink_k1 | sink_k1 | YES | 0.72 |

If these fail, the model isn't reading the task. If they pass but moved-episode accuracy is ~0, the failure is forecasting (unrecorded movement), not prompt-fixable.

## profile_text = False  (accuracy / Brier / log-loss vs history-days)
| bank | metric | D=0 | D=1 | D=3 | D=7 | D=14 | moved@D14 |
|---|---|---|---|---|---|---|---|
| atyp_v2 | acc | 0.083 | 0.417 | 0.583 | 0.333 | 0.417 | 0.200 |
| atyp_v2 | Brier | 1.024 | 0.657 | 0.536 | 0.739 | 0.607 | 0.785 |
| atyp_v2 | logloss | 3.056 | 1.516 | 1.350 | 1.447 | 1.244 | 1.295 |
| typ_v1 | acc | 0.417 | 0.500 | 0.333 | 0.333 | 0.500 | 0.000 |
| typ_v1 | Brier | 0.713 | 0.721 | 1.013 | 0.714 | 0.605 | 1.155 |
| typ_v1 | logloss | 1.951 | 3.303 | 6.469 | 3.689 | 1.266 | 1.668 |

## profile_text = True  (accuracy / Brier / log-loss vs history-days)
| bank | metric | D=0 | D=1 | D=3 | D=7 | D=14 | moved@D14 |
|---|---|---|---|---|---|---|---|
| atyp_v2 | acc | 0.417 | 0.417 | 0.583 | 0.333 | 0.417 | 0.200 |
| atyp_v2 | Brier | 0.937 | 0.766 | 0.661 | 0.904 | 0.801 | 0.977 |
| atyp_v2 | logloss | 4.089 | 5.540 | 1.647 | 1.701 | 1.710 | 1.721 |
| typ_v1 | acc | 0.333 | 0.417 | 0.333 | 0.333 | 0.417 | 0.333 |
| typ_v1 | Brier | 1.022 | 0.823 | 0.998 | 0.956 | 0.847 | 0.878 |
| typ_v1 | logloss | 6.136 | 3.447 | 6.110 | 6.226 | 3.822 | 1.769 |

## Moved vs not-moved (pooled D>=1, profile_text=False)
| bank | not-moved acc | moved acc | moved Brier |
|---|---|---|---|
| atyp_v2 | 0.606 (n=33) | 0.067 (n=15) | 1.080 |
| typ_v1 | 0.613 (n=31) | 0.059 (n=17) | 1.248 |

## C4 (held-out vs observed, atyp_v1 vs atyp_shift_v1, D=7)
| slice | atyp_v1 | atyp_shift_v1 |
|---|---|---|
| all | - | 0.375 |
| held-out | - | 0.250 |
| observed | - | 0.500 |

Numbers only. C1 = atyp accuracy rises with history while typ stays flatter; lower Brier/log-loss = better-calibrated. With the mock client these are a last-observation baseline, not an LLM result.