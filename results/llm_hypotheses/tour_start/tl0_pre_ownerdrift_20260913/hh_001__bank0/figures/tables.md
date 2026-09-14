# Tour start + re-asking — hh_001

Scoring: ON_PERSON ≡ OUT_OF_HOUSE. ± is one standard error.

## Passive protocol (fixed patrol, no policy)

| arm | n | top-1 | log-loss |
|---|---|---|---|
| llm · tour_named | 2472 | 0.708 ± 0.009 | 1.159 ± 0.029 |
| llm_fixed · tour_named | 2472 | 0.708 ± 0.009 | 1.159 ± 0.029 |
| mostfreq72 | 2472 | 0.712 ± 0.009 | 1.164 ± 0.031 |
| oracle | 2472 | 0.763 ± 0.009 | 0.750 ± 0.024 |

## Active protocol (myopic VoI λ=0.05, random slice f)

| arm | top-1 (answer) | log-loss (pre-sense belief) | senses/day | random senses |
|---|---|---|---|---|
| llm · tour_named · f0 | 0.783 ± 0.008 | 0.831 ± 0.027 | 23.5 | 0 |
| llm · tour_named · f0.1 | 0.775 ± 0.008 | 0.884 ± 0.029 | 23.4 | 56 |
| llm_fixed · tour_named · f0 | 0.787 ± 0.008 | 0.831 ± 0.027 | 23.5 | 0 |
| llm_fixed · tour_named · f0.1 | 0.784 ± 0.008 | 0.838 ± 0.027 | 23.4 | 56 |
| mostfreq72 · f0 | 0.780 ± 0.008 | 0.849 ± 0.029 | 24.0 | 0 |
| mostfreq72 · f0.1 | 0.772 ± 0.008 | 0.880 ± 0.029 | 24.0 | 56 |
| oracle · f0 | 0.768 ± 0.008 | 1.052 ± 0.041 | 22.5 | 0 |

## Paired comparisons (A − B over the same questions, 95% bootstrap CI)

| comparison | top-1 | log-loss |
|---|---|---|
| re-asking − fixed (named) | -0.000 [-0.001, +0.000] | +0.000 [-0.000, +0.002] |
| LLM named − MostFreq72 (no-LLM) | -0.004 [-0.008, -0.001]* | -0.005 [-0.016, +0.007] |
| random slice 0.1 − 0 (re-asking) | -0.008 [-0.019, +0.002] | +0.053 [+0.028, +0.077]* |
| random slice 0.1 − 0 (fixed set) | -0.004 [-0.013, +0.006] | +0.007 [-0.011, +0.026] |
| random slice 0.1 − 0 (MostFreq72) | -0.008 [-0.015, +0.000] | +0.030 [+0.011, +0.050]* |
| LLM named − MostFreq72 (active, f0) | +0.003 [-0.007, +0.013] | -0.018 [-0.044, +0.007] |

## Re-asking: calls, timing, outcome

| arm | re-asks | live LLM calls | generation s | events |
|---|---|---|---|---|
| active · llm · tour_named · f0 | 2 | 2 | 1850.3 | d3 scheduled → revised; d7 scheduled → revised |
| active · llm · tour_named · f0.1 | 2 | 2 | 1903.5 | d3 scheduled → revised; d7 scheduled → revised |
| active · llm_fixed · tour_named · f0 | 0 | None | None |  |
| active · llm_fixed · tour_named · f0.1 | 0 | None | None |  |
| passive · llm · tour_named | 2 | 2 | 1410.6 | d3 scheduled → revised; d7 scheduled → revised |
| passive · llm_fixed · tour_named | 0 | None | None |  |

Tour-start elicitation (last elicit run): hh_001 tour_named 586s, 16464 tokens, 117.24s/hypothesis


## Per-object oracle gap

| arm | mixture log-loss | per-object oracle | gain | best-particle counts |
|---|---|---|---|---|
| passive · llm · tour_named | 1.159 | 1.090 | 0.070 | {'hyp4': 4, 'hyp3': 5, 'stat': 13, 'hyp2': 1, 'hyp1': 7, 'hyp5': 5} |
| passive · llm_fixed · tour_named | 1.159 | 1.039 | 0.119 | {'hyp1': 12, 'hyp3': 2, 'stat': 15, 'hyp2': 2, 'hyp5': 2, 'hyp4': 2} |
