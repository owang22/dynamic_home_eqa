# Cold start + re-asking — hh_001

Scoring: ON_PERSON ≡ OUT_OF_HOUSE. ± is one standard error.

## Passive protocol (fixed patrol, no policy)

| arm | n | top-1 | log-loss |
|---|---|---|---|
| llm · cold_anonymized | 2250 | 0.571 ± 0.010 | 1.461 ± 0.029 |
| llm · cold_named | 2250 | 0.603 ± 0.010 | 1.347 ± 0.030 |
| llm_fixed · cold_anonymized | 2250 | 0.620 ± 0.010 | 1.331 ± 0.027 |
| llm_fixed · cold_named | 2250 | 0.620 ± 0.010 | 1.332 ± 0.028 |
| mostfreq | 2250 | 0.638 ± 0.010 | 1.408 ± 0.026 |
| oracle | 2250 | 0.767 ± 0.009 | 0.658 ± 0.022 |
| periodic | 2250 | 0.621 ± 0.010 | 1.909 ± 0.052 |

## Active protocol (myopic VoI λ=0.05, random slice f)

| arm | top-1 (answer) | log-loss (pre-sense belief) | senses/day | random senses |
|---|---|---|---|---|
| llm · cold_named · f0 | 0.673 ± 0.010 | 1.115 ± 0.032 | 21.4 | 0 |
| llm · cold_named · f0.1 | 0.684 ± 0.010 | 1.074 ± 0.031 | 21.4 | 50 |
| llm_fixed · cold_named · f0 | 0.712 ± 0.010 | 0.987 ± 0.028 | 21.4 | 0 |
| llm_fixed · cold_named · f0.1 | 0.700 ± 0.010 | 1.025 ± 0.029 | 21.4 | 50 |
| oracle · f0 | 0.808 ± 0.008 | 0.791 ± 0.036 | 21.1 | 0 |
| periodic · f0 | 0.714 ± 0.010 | 1.425 ± 0.049 | 19.8 | 0 |
| periodic · f0.1 | 0.721 ± 0.009 | 1.402 ± 0.048 | 20.5 | 50 |

## Paired comparisons (A − B over the same questions, 95% bootstrap CI)

| comparison | top-1 | log-loss |
|---|---|---|
| named − anonymized (re-asking) | +0.032 [+0.018, +0.046]* | -0.114 [-0.139, -0.091]* |
| named − anonymized (fixed set) | -0.001 [-0.008, +0.005] | +0.000 [-0.012, +0.012] |
| re-asking − fixed (named) | -0.016 [-0.029, -0.004]* | +0.015 [-0.006, +0.036] |
| re-asking − fixed (anonymized) | -0.049 [-0.061, -0.037]* | +0.130 [+0.114, +0.146]* |
| LLM named − Periodic (no-LLM) | -0.018 [-0.032, -0.004]* | -0.562 [-0.632, -0.501]* |
| LLM named − MostFreq | -0.035 [-0.052, -0.019]* | -0.061 [-0.093, -0.031]* |
| random slice 0.1 − 0 (re-asking) | +0.011 [-0.002, +0.024] | -0.040 [-0.072, -0.009]* |
| random slice 0.1 − 0 (fixed set) | -0.013 [-0.023, -0.004]* | +0.037 [+0.018, +0.057]* |
| random slice 0.1 − 0 (Periodic) | +0.007 [-0.003, +0.016] | -0.023 [-0.071, +0.025] |
| LLM named − Periodic (active, f0) | -0.041 [-0.056, -0.024]* | -0.310 [-0.383, -0.241]* |

## Re-asking: calls, timing, outcome

| arm | re-asks | live LLM calls | generation s | events |
|---|---|---|---|---|
| active · llm · cold_named · f0 | 2 | 2 | 1191.3 | d3 scheduled → revised; d7 scheduled → revised |
| active · llm · cold_named · f0.1 | 2 | 2 | 1170.7 | d3 scheduled → revised; d7 scheduled → revised |
| active · llm_fixed · cold_named · f0 | 0 | None | None |  |
| active · llm_fixed · cold_named · f0.1 | 0 | None | None |  |
| passive · llm · cold_anonymized | 2 | 0 | 0.0 | d3 scheduled → revised; d7 scheduled → revised |
| passive · llm · cold_named | 2 | 0 | 0.0 | d3 scheduled → revised; d7 scheduled → revised |
| passive · llm_fixed · cold_anonymized | 0 | None | None |  |
| passive · llm_fixed · cold_named | 0 | None | None |  |

Cold-start elicitation (last elicit run): hh_001 cold_named 544s, 15291 tokens, 108.85s/hypothesis; hh_001 cold_anonymized 499s, 14019 tokens, 99.78s/hypothesis


## Per-object oracle gap

| arm | mixture log-loss | per-object oracle | gain | best-particle counts |
|---|---|---|---|---|
| passive · llm · cold_named | 1.347 | 1.275 | 0.072 | {'hyp2': 11, 'hyp1': 11, 'stat': 7, 'hyp4': 3, 'hyp3': 3} |
| passive · llm · cold_anonymized | 1.461 | 1.370 | 0.092 | {'hyp2': 11, 'hyp1': 14, 'stat': 9, 'hyp3': 1} |
| passive · llm_fixed · cold_named | 1.332 | 1.234 | 0.098 | {'hyp2': 11, 'hyp1': 16, 'stat': 5, 'hyp5': 1, 'hyp4': 1, 'hyp3': 1} |
| passive · llm_fixed · cold_anonymized | 1.331 | 1.287 | 0.045 | {'hyp1': 23, 'hyp2': 1, 'stat': 5, 'hyp4': 2, 'hyp5': 3, 'hyp3': 1} |
