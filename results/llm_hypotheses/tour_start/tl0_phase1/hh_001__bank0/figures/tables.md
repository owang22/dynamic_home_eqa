# Tour start + re-asking — hh_001

Scoring: ON_PERSON ≡ OUT_OF_HOUSE. ± is one standard error.

## Passive protocol (fixed patrol, no policy)

| arm | n | top-1 | log-loss |
|---|---|---|---|
| graph · graph_anonymized | 2472 | 0.706 ± 0.009 | 1.045 ± 0.027 |
| graph · graph_named | 2472 | 0.727 ± 0.009 | 1.007 ± 0.027 |
| graph_fixed · graph_anonymized | 2472 | 0.706 ± 0.009 | 1.047 ± 0.027 |
| graph_fixed · graph_named | 2472 | 0.722 ± 0.009 | 1.018 ± 0.027 |
| llm · tour_named | 2472 | 0.701 ± 0.009 | 1.096 ± 0.028 |
| llm_fixed · tour_named | 2472 | 0.715 ± 0.009 | 1.081 ± 0.027 |
| mostfreq72 | 2472 | 0.721 ± 0.009 | 1.102 ± 0.030 |
| oracle | 2472 | 0.758 ± 0.009 | 0.714 ± 0.023 |

## Late-discovery accuracy (objects first sighted after day 0, apart from the tour-visible stratum)

| arm | late n | late top-1 | late log-loss | tour-visible n | tour-visible top-1 |
|---|---|---|---|---|---|
| active · graph · graph_named · f0 | 698 | 0.630 ± 0.018 | 1.287 ± 0.060 | 1774 | 0.866 ± 0.008 |
| active · graph_fixed · graph_named · f0 | 698 | 0.695 ± 0.017 | 1.074 ± 0.056 | 1774 | 0.866 ± 0.008 |
| active · graph_fixed · graph_named · f0.1 | 698 | 0.663 ± 0.018 | 1.167 ± 0.058 | 1774 | 0.869 ± 0.008 |
| active · graph_fixed · graph_named · f0 · b0 | 698 | 0.698 ± 0.017 | 1.064 ± 0.056 | 1774 | 0.866 ± 0.008 |
| active · graph_fixed · graph_named · f0 · b0.5 | 698 | 0.698 ± 0.017 | 1.056 ± 0.056 | 1774 | 0.870 ± 0.008 |
| active · graph_fixed · graph_named · f0 · b2 | 698 | 0.693 ± 0.017 | 1.081 ± 0.057 | 1774 | 0.867 ± 0.008 |
| active · llm · tour_named · f0 | 698 | 0.552 ± 0.019 | 1.455 ± 0.059 | 1774 | 0.864 ± 0.008 |
| active · llm_fixed · tour_named · f0 | 698 | 0.577 ± 0.019 | 1.394 ± 0.058 | 1774 | 0.855 ± 0.008 |
| active · mostfreq72 · f0 | 698 | 0.573 ± 0.019 | 1.384 ± 0.060 | 1774 | 0.868 ± 0.008 |
| active · oracle · f0 | 698 | 0.673 ± 0.018 | 1.481 ± 0.088 | 1774 | 0.846 ± 0.009 |
| passive · graph · graph_anonymized | 698 | 0.463 ± 0.019 | 1.705 ± 0.058 | 1774 | 0.802 ± 0.009 |
| passive · graph · graph_named | 698 | 0.520 ± 0.019 | 1.606 ± 0.057 | 1774 | 0.808 ± 0.009 |
| passive · graph_fixed · graph_anonymized | 698 | 0.450 ± 0.019 | 1.708 ± 0.058 | 1774 | 0.806 ± 0.009 |
| passive · graph_fixed · graph_named | 698 | 0.523 ± 0.019 | 1.607 ± 0.057 | 1774 | 0.800 ± 0.009 |
| passive · llm · tour_named | 698 | 0.476 ± 0.019 | 1.799 ± 0.057 | 1774 | 0.789 ± 0.010 |
| passive · llm_fixed · tour_named | 698 | 0.464 ± 0.019 | 1.762 ± 0.055 | 1774 | 0.814 ± 0.009 |
| passive · mostfreq72 | 698 | 0.477 ± 0.019 | 1.853 ± 0.062 | 1774 | 0.817 ± 0.009 |
| passive · oracle | 698 | 0.632 ± 0.018 | 1.155 ± 0.055 | 1774 | 0.807 ± 0.009 |

## Assumption recovery (final graph holds a value matching the bank's ground-truth premise)

| arm | premises | matched | rate |
|---|---|---|---|
| active · graph · graph_named · f0 | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': 'household_size=solo', 'work_pattern': 'weekday_presence=away'} | 1.00 |
| active · graph_fixed · graph_named · f0 | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': 'household_size=solo', 'work_pattern': 'weekday_presence=away'} | 1.00 |
| active · graph_fixed · graph_named · f0.1 | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': 'household_size=solo', 'work_pattern': 'weekday_presence=away'} | 1.00 |
| active · graph_fixed · graph_named · f0 · b0 | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': 'household_size=solo', 'work_pattern': 'weekday_presence=away'} | 1.00 |
| active · graph_fixed · graph_named · f0 · b0.5 | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': 'household_size=solo', 'work_pattern': 'weekday_presence=away'} | 1.00 |
| active · graph_fixed · graph_named · f0 · b2 | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': 'household_size=solo', 'work_pattern': 'weekday_presence=away'} | 1.00 |
| active · llm · tour_named · f0 | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': None, 'work_pattern': None} | 0.00 |
| active · llm_fixed · tour_named · f0 | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': None, 'work_pattern': None} | 0.00 |
| passive · graph · graph_anonymized | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': 'weekday_presence=present', 'work_pattern': 'weekday_presence=away'} | 1.00 |
| passive · graph · graph_named | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': 'household_size=solo', 'work_pattern': 'weekday_presence=away'} | 1.00 |
| passive · graph_fixed · graph_anonymized | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': 'weekday_presence=present', 'work_pattern': 'weekday_presence=away'} | 1.00 |
| passive · graph_fixed · graph_named | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': 'household_size=solo', 'work_pattern': 'weekday_presence=away'} | 1.00 |
| passive · llm · tour_named | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': None, 'work_pattern': None} | 0.00 |
| passive · llm_fixed · tour_named | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': None, 'work_pattern': None} | 0.00 |

## Active protocol (myopic VoI λ=0.05, random slice f)

| arm | top-1 (answer) | log-loss (belief at answer time, after that question's senses) | senses/day | random senses |
|---|---|---|---|---|
| graph · graph_named · f0 | 0.800 ± 0.008 | 0.760 ± 0.026 | 24.0 | 0 |
| graph_fixed · graph_named · f0 | 0.818 ± 0.008 | 0.693 ± 0.024 | 24.0 | 0 |
| graph_fixed · graph_named · f0.1 | 0.811 ± 0.008 | 0.723 ± 0.025 | 23.8 | 56 |
| graph_fixed · graph_named · f0 · b0 | 0.819 ± 0.008 | 0.692 ± 0.024 | 23.9 | None |
| graph_fixed · graph_named · f0 · b0.5 | 0.822 ± 0.008 | 0.680 ± 0.024 | 23.5 | None |
| graph_fixed · graph_named · f0 · b2 | 0.818 ± 0.008 | 0.689 ± 0.024 | 23.5 | None |
| llm · tour_named · f0 | 0.776 ± 0.008 | 0.828 ± 0.027 | 23.4 | 0 |
| llm_fixed · tour_named · f0 | 0.777 ± 0.008 | 0.823 ± 0.026 | 23.2 | 0 |
| mostfreq72 · f0 | 0.784 ± 0.008 | 0.783 ± 0.027 | 24.0 | 0 |
| oracle · f0 | 0.797 ± 0.008 | 0.845 ± 0.036 | 23.7 | 0 |

## Paired comparisons (A − B over the same questions, 95% bootstrap CI)

| comparison | top-1 | log-loss |
|---|---|---|
| re-asking − fixed (named) | -0.015 [-0.024, -0.005]* | +0.015 [-0.001, +0.030] |
| LLM named − MostFreq72 (no-LLM) | -0.021 [-0.028, -0.013]* | -0.006 [-0.022, +0.011] |
| LLM named − MostFreq72 (active, f0) | -0.008 [-0.017, -0.000]* | +0.044 [+0.026, +0.064]* |

## Re-asking: calls, timing, outcome

| arm | re-asks | live LLM calls | generation s | events |
|---|---|---|---|---|
| active · graph · graph_named · f0 | 2 | 2 | 1495.4 | d3 scheduled → revised; d7 scheduled → revised |
| active · graph_fixed · graph_named · f0 | 0 | None | None |  |
| active · graph_fixed · graph_named · f0.1 | 0 | None | None |  |
| active · graph_fixed · graph_named · f0 · b0 | 0 | None | None |  |
| active · graph_fixed · graph_named · f0 · b0.5 | 0 | None | None |  |
| active · graph_fixed · graph_named · f0 · b2 | 0 | None | None |  |
| active · llm · tour_named · f0 | 3 | 3 | 1862.9 | d0 uncovered → revised; d3 scheduled → revised; d7 scheduled → revised |
| active · llm_fixed · tour_named · f0 | 0 | None | None |  |
| passive · graph · graph_anonymized | 2 | 2 | 1036.8 | d3 scheduled → revised; d7 scheduled → revised |
| passive · graph · graph_named | 2 | 2 | 1323.1 | d3 scheduled → revised; d7 scheduled → revised |
| passive · graph_fixed · graph_anonymized | 0 | None | None |  |
| passive · graph_fixed · graph_named | 0 | None | None |  |
| passive · llm · tour_named | 3 | 3 | 1591.2 | d0 uncovered → revised; d3 scheduled → revised; d7 scheduled → revised |
| passive · llm_fixed · tour_named | 0 | None | None |  |

## Graph arm: leaves, edits, prunes, births, rejections, checks

| arm | leaves by day (first → last) | applied ops | rejected ops | prunes | born / skipped | checks resolved (in favour) | weight spread presence / absence | settled at end |
|---|---|---|---|---|---|---|---|---|
| active · graph · graph_named · f0 | 4 → 3 | 4 | 0  | 1 | 0 / 0 | 23 (6) | 71.3 / 151.7 | weekday_presence=away |
| active · graph_fixed · graph_named · f0 | 4 → 3 | 0 | 0  | 1 | 0 / 0 | 22 (8) | 172.1 / 396.5 | weekday_presence=away |
| active · graph_fixed · graph_named · f0.1 | 4 → 3 | 0 | 0  | 1 | 0 / 0 | 21 (8) | 161.5 / 357.1 | weekday_presence=away |
| active · graph_fixed · graph_named · f0 · b0 | 4 → 3 | 0 | 0  | 1 | 0 / 0 | 22 (8) | 170.9 / 384.3 | weekday_presence=away |
| active · graph_fixed · graph_named · f0 · b0.5 | 4 → 3 | 0 | 0  | 1 | 0 / 0 | 21 (7) | 181.4 / 416.6 | weekday_presence=away |
| active · graph_fixed · graph_named · f0 · b2 | 4 → 3 | 0 | 0  | 1 | 0 / 0 | 20 (7) | 183.1 / 411.7 | weekday_presence=away |
| passive · graph · graph_anonymized | 4 → 3 | 4 | 0  | 1 | 0 / 0 | 18 (2) | 8.8 / 3.8 |  |
| passive · graph · graph_named | 4 → 3 | 4 | 0  | 1 | 0 / 0 | 16 (7) | 68.0 / 176.2 | weekday_presence=away |
| passive · graph_fixed · graph_anonymized | 4 → 3 | 0 | 0  | 1 | 0 / 0 | 18 (3) | 2.9 / 7.4 |  |
| passive · graph_fixed · graph_named | 4 → 3 | 0 | 0  | 1 | 0 / 0 | 16 (7) | 99.4 / 226.9 | weekday_presence=away |

Tour-start elicitation (last elicit run): hh_001 tour_named 612s, 16267 tokens, 122.31s/hypothesis; hh_001 tour_anonymized 384s, 10148 tokens, 76.75s/hypothesis


## Per-object oracle gap

| arm | mixture log-loss | per-object oracle | gain | best-particle counts |
|---|---|---|---|---|
| passive · llm · tour_named | 1.096 | 0.996 | 0.100 | {'hyp3': 6, 'hyp4': 3, 'stat': 12, 'hyp1': 12, 'hyp2': 2} |
| passive · llm_fixed · tour_named | 1.081 | 1.023 | 0.058 | {'hyp3': 8, 'stat': 15, 'hyp1': 12} |
