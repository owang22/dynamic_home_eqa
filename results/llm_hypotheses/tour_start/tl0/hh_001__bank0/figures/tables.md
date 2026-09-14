# Tour start + re-asking — hh_001

Scoring: ON_PERSON ≡ OUT_OF_HOUSE. ± is one standard error.

## Passive protocol (fixed patrol, no policy)

| arm | n | top-1 | log-loss |
|---|---|---|---|
| graph · graph_anonymized | 2472 | 0.706 ± 0.009 | 1.102 ± 0.028 |
| graph · graph_named | 2472 | 0.728 ± 0.009 | 0.977 ± 0.026 |
| graph_fixed · graph_anonymized | 2472 | 0.703 ± 0.009 | 1.096 ± 0.028 |
| graph_fixed · graph_named | 2472 | 0.713 ± 0.009 | 1.032 ± 0.027 |
| llm · tour_anonymized | 2472 | 0.713 ± 0.009 | 1.109 ± 0.028 |
| llm · tour_named | 2472 | 0.701 ± 0.009 | 1.096 ± 0.028 |
| llm_fixed · tour_anonymized | 2472 | 0.711 ± 0.009 | 1.121 ± 0.028 |
| llm_fixed · tour_named | 2472 | 0.715 ± 0.009 | 1.081 ± 0.027 |
| mostfreq | 2472 | 0.740 ± 0.009 | 1.184 ± 0.026 |
| mostfreq72 | 2472 | 0.721 ± 0.009 | 1.102 ± 0.030 |
| oracle | 2472 | 0.758 ± 0.009 | 0.714 ± 0.023 |
| periodic | 2472 | 0.727 ± 0.009 | 1.501 ± 0.047 |

## Late-discovery accuracy (objects first sighted after day 0, apart from the tour-visible stratum)

| arm | late n | late top-1 | late log-loss | tour-visible n | tour-visible top-1 |
|---|---|---|---|---|---|
| active · graph · graph_named · f0 | 698 | 0.662 ± 0.018 | 1.191 ± 0.058 | 1774 | 0.869 ± 0.008 |
| active · graph_fixed · graph_named · f0 | 698 | 0.660 ± 0.018 | 1.130 ± 0.055 | 1774 | 0.868 ± 0.008 |
| active · graph_fixed · graph_named · f0.1 | 698 | 0.638 ± 0.018 | 1.215 ± 0.056 | 1774 | 0.865 ± 0.008 |
| active · graph_fixed · graph_named · f0 · b0 | 698 | 0.653 ± 0.018 | 1.147 ± 0.054 | 1774 | 0.860 ± 0.008 |
| active · graph_fixed · graph_named · f0 · b0.5 | 698 | 0.653 ± 0.018 | 1.165 ± 0.055 | 1774 | 0.864 ± 0.008 |
| active · graph_fixed · graph_named · f0 · b2 | 698 | 0.653 ± 0.018 | 1.160 ± 0.055 | 1774 | 0.860 ± 0.008 |
| active · llm · tour_named · f0 | 698 | 0.552 ± 0.019 | 1.455 ± 0.059 | 1774 | 0.864 ± 0.008 |
| active · llm · tour_named · f0.1 | 698 | 0.556 ± 0.019 | 1.473 ± 0.060 | 1774 | 0.868 ± 0.008 |
| active · llm_fixed · tour_named · f0 | 698 | 0.577 ± 0.019 | 1.394 ± 0.058 | 1774 | 0.855 ± 0.008 |
| active · llm_fixed · tour_named · f0.1 | 698 | 0.583 ± 0.019 | 1.385 ± 0.057 | 1774 | 0.850 ± 0.008 |
| active · mostfreq72 · f0 | 698 | 0.573 ± 0.019 | 1.384 ± 0.060 | 1774 | 0.868 ± 0.008 |
| active · mostfreq72 · f0.1 | 698 | 0.563 ± 0.019 | 1.466 ± 0.063 | 1774 | 0.866 ± 0.008 |
| active · oracle · f0 | 698 | 0.673 ± 0.018 | 1.481 ± 0.088 | 1774 | 0.846 ± 0.009 |
| passive · graph · graph_anonymized | 698 | 0.446 ± 0.019 | 1.849 ± 0.055 | 1774 | 0.808 ± 0.009 |
| passive · graph · graph_named | 698 | 0.532 ± 0.019 | 1.523 ± 0.056 | 1774 | 0.806 ± 0.009 |
| passive · graph_fixed · graph_anonymized | 698 | 0.447 ± 0.019 | 1.828 ± 0.055 | 1774 | 0.804 ± 0.009 |
| passive · graph_fixed · graph_named | 698 | 0.486 ± 0.019 | 1.646 ± 0.054 | 1774 | 0.802 ± 0.009 |
| passive · llm · tour_anonymized | 698 | 0.457 ± 0.019 | 1.842 ± 0.056 | 1774 | 0.814 ± 0.009 |
| passive · llm · tour_named | 698 | 0.476 ± 0.019 | 1.799 ± 0.057 | 1774 | 0.789 ± 0.010 |
| passive · llm_fixed · tour_anonymized | 698 | 0.451 ± 0.019 | 1.874 ± 0.056 | 1774 | 0.813 ± 0.009 |
| passive · llm_fixed · tour_named | 698 | 0.464 ± 0.019 | 1.762 ± 0.055 | 1774 | 0.814 ± 0.009 |
| passive · mostfreq | 698 | 0.507 ± 0.019 | 1.871 ± 0.054 | 1774 | 0.832 ± 0.009 |
| passive · mostfreq72 | 698 | 0.477 ± 0.019 | 1.853 ± 0.062 | 1774 | 0.817 ± 0.009 |
| passive · oracle | 698 | 0.632 ± 0.018 | 1.155 ± 0.055 | 1774 | 0.807 ± 0.009 |
| passive · periodic | 698 | 0.474 ± 0.019 | 2.717 ± 0.104 | 1774 | 0.826 ± 0.009 |

## Assumption recovery (final graph holds a value matching the bank's ground-truth premise)

| arm | premises | matched | rate |
|---|---|---|---|
| active · graph · graph_named · f0 | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': None, 'work_pattern': 'weekday_presence=out'} | 0.50 |
| active · graph_fixed · graph_named · f0 | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': None, 'work_pattern': 'weekday_presence=out'} | 0.50 |
| active · graph_fixed · graph_named · f0.1 | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': None, 'work_pattern': 'weekday_presence=out'} | 0.50 |
| active · graph_fixed · graph_named · f0 · b0 | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': None, 'work_pattern': 'weekday_presence=out'} | 0.50 |
| active · graph_fixed · graph_named · f0 · b0.5 | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': None, 'work_pattern': 'weekday_presence=out'} | 0.50 |
| active · graph_fixed · graph_named · f0 · b2 | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': None, 'work_pattern': 'weekday_presence=out'} | 0.50 |
| active · llm · tour_named · f0 | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': None, 'work_pattern': None} | 0.00 |
| active · llm · tour_named · f0.1 | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': None, 'work_pattern': None} | 0.00 |
| active · llm_fixed · tour_named · f0 | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': None, 'work_pattern': None} | 0.00 |
| active · llm_fixed · tour_named · f0.1 | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': None, 'work_pattern': None} | 0.00 |
| passive · graph · graph_anonymized | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': 'household_size=one_adult', 'work_pattern': None} | 0.50 |
| passive · graph · graph_named | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': None, 'work_pattern': 'weekday_presence=out'} | 0.50 |
| passive · graph_fixed · graph_anonymized | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': 'household_size=one_adult', 'work_pattern': None} | 0.50 |
| passive · graph_fixed · graph_named | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': None, 'work_pattern': 'weekday_presence=out'} | 0.50 |
| passive · llm · tour_anonymized | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': None, 'work_pattern': None} | 0.00 |
| passive · llm · tour_named | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': None, 'work_pattern': None} | 0.00 |
| passive · llm_fixed · tour_anonymized | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': None, 'work_pattern': None} | 0.00 |
| passive · llm_fixed · tour_named | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': None, 'work_pattern': None} | 0.00 |

## Active protocol (myopic VoI λ=0.05, random slice f)

| arm | top-1 (answer) | log-loss (belief at answer time, after that question's senses) | senses/day | random senses |
|---|---|---|---|---|
| graph · graph_named · f0 | 0.811 ± 0.008 | 0.721 ± 0.025 | 23.2 | 0 |
| graph_fixed · graph_named · f0 | 0.809 ± 0.008 | 0.717 ± 0.025 | 23.2 | 0 |
| graph_fixed · graph_named · f0.1 | 0.801 ± 0.008 | 0.745 ± 0.025 | 23.3 | 56 |
| graph_fixed · graph_named · f0 · b0 | 0.802 ± 0.008 | 0.724 ± 0.024 | 23.2 | None |
| graph_fixed · graph_named · f0 · b0.5 | 0.804 ± 0.008 | 0.726 ± 0.025 | 23.2 | None |
| graph_fixed · graph_named · f0 · b2 | 0.802 ± 0.008 | 0.727 ± 0.025 | 23.2 | None |
| llm · tour_named · f0 | 0.776 ± 0.008 | 0.828 ± 0.027 | 23.4 | 0 |
| llm · tour_named · f0.1 | 0.780 ± 0.008 | 0.839 ± 0.027 | 23.4 | 56 |
| llm_fixed · tour_named · f0 | 0.777 ± 0.008 | 0.823 ± 0.026 | 23.2 | 0 |
| llm_fixed · tour_named · f0.1 | 0.775 ± 0.008 | 0.846 ± 0.027 | 23.3 | 56 |
| mostfreq72 · f0 | 0.784 ± 0.008 | 0.783 ± 0.027 | 24.0 | 0 |
| mostfreq72 · f0.1 | 0.781 ± 0.008 | 0.820 ± 0.028 | 24.0 | 56 |
| oracle · f0 | 0.797 ± 0.008 | 0.845 ± 0.036 | 23.7 | 0 |

## Paired comparisons (A − B over the same questions, 95% bootstrap CI)

| comparison | top-1 | log-loss |
|---|---|---|
| named − anonymized (re-asking) | -0.013 [-0.021, -0.004]* | -0.013 [-0.026, -0.001]* |
| named − anonymized (fixed set) | +0.004 [-0.004, +0.013] | -0.039 [-0.056, -0.023]* |
| re-asking − fixed (named) | -0.015 [-0.024, -0.005]* | +0.015 [-0.001, +0.030] |
| re-asking − fixed (anonymized) | +0.002 [-0.000, +0.006] | -0.011 [-0.017, -0.006]* |
| LLM named − MostFreq72 (no-LLM) | -0.021 [-0.028, -0.013]* | -0.006 [-0.022, +0.011] |
| LLM named − MostFreq | -0.040 [-0.051, -0.028]* | -0.088 [-0.108, -0.066]* |
| random slice 0.1 − 0 (re-asking) | +0.004 [-0.004, +0.011] | +0.011 [-0.004, +0.027] |
| random slice 0.1 − 0 (fixed set) | -0.002 [-0.010, +0.005] | +0.023 [+0.005, +0.041]* |
| random slice 0.1 − 0 (MostFreq72) | -0.004 [-0.011, +0.004] | +0.037 [+0.019, +0.055]* |
| LLM named − MostFreq72 (active, f0) | -0.008 [-0.017, -0.000]* | +0.044 [+0.026, +0.064]* |

## Re-asking: calls, timing, outcome

| arm | re-asks | live LLM calls | generation s | events |
|---|---|---|---|---|
| active · graph · graph_named · f0 | 2 | 2 | 923.0 | d3 scheduled → revised; d7 scheduled → revised |
| active · graph_fixed · graph_named · f0 | 0 | None | None |  |
| active · graph_fixed · graph_named · f0.1 | 0 | None | None |  |
| active · graph_fixed · graph_named · f0 · b0 | 0 | None | None |  |
| active · graph_fixed · graph_named · f0 · b0.5 | 0 | None | None |  |
| active · graph_fixed · graph_named · f0 · b2 | 0 | None | None |  |
| active · llm · tour_named · f0 | 3 | 3 | 1862.9 | d0 uncovered → revised; d3 scheduled → revised; d7 scheduled → revised |
| active · llm · tour_named · f0.1 | 3 | 3 | 1678.8 | d0 uncovered → revised; d3 scheduled → revised; d7 scheduled → revised |
| active · llm_fixed · tour_named · f0 | 0 | None | None |  |
| active · llm_fixed · tour_named · f0.1 | 0 | None | None |  |
| passive · graph · graph_anonymized | 2 | 2 | 1277.9 | d3 scheduled → revised; d7 scheduled → revised |
| passive · graph · graph_named | 2 | 2 | 849.2 | d3 scheduled → revised; d7 scheduled → revised |
| passive · graph_fixed · graph_anonymized | 0 | None | None |  |
| passive · graph_fixed · graph_named | 0 | None | None |  |
| passive · llm · tour_anonymized | 3 | 3 | 1976.5 | d0 uncovered → revised; d3 scheduled → revised; d7 scheduled → revised |
| passive · llm · tour_named | 3 | 3 | 1591.2 | d0 uncovered → revised; d3 scheduled → revised; d7 scheduled → revised |
| passive · llm_fixed · tour_anonymized | 0 | None | None |  |
| passive · llm_fixed · tour_named | 0 | None | None |  |

## Graph arm: leaves, edits, prunes, births

| arm | leaves by day (first → last) | edits | prunes | born / skipped | final assumptions |
|---|---|---|---|---|---|
| active · graph · graph_named · f0 | 8 → 1 | 12 | 0 | 0 / 0 | weekday_presence, weekend_activity, suitcase_status |
| active · graph_fixed · graph_named · f0 | 8 → 3 | 0 | 5 | 0 / 0 | weekday_presence, weekend_activity, suitcase_status |
| active · graph_fixed · graph_named · f0.1 | 8 → 3 | 0 | 5 | 0 / 0 | weekday_presence, weekend_activity, suitcase_status |
| active · graph_fixed · graph_named · f0 · b0 | 8 → 3 | 0 | 5 | 0 / 0 | weekday_presence, weekend_activity, suitcase_status |
| active · graph_fixed · graph_named · f0 · b0.5 | 8 → 3 | 0 | 5 | 0 / 0 | weekday_presence, weekend_activity, suitcase_status |
| active · graph_fixed · graph_named · f0 · b2 | 8 → 3 | 0 | 5 | 0 / 0 | weekday_presence, weekend_activity, suitcase_status |
| passive · graph · graph_anonymized | 8 → 3 | 6 | 4 | 0 / 0 | household_size, weekday_presence, evening_meal |
| passive · graph · graph_named | 8 → 2 | 8 | 4 | 0 / 0 | weekday_presence, weekend_activity, suitcase_status |
| passive · graph_fixed · graph_anonymized | 8 → 3 | 0 | 5 | 0 / 0 | household_size, weekday_presence, evening_meal |
| passive · graph_fixed · graph_named | 8 → 3 | 0 | 5 | 0 / 0 | weekday_presence, weekend_activity, suitcase_status |

Tour-start elicitation (last elicit run): hh_001 tour_named 612s, 16267 tokens, 122.31s/hypothesis; hh_001 tour_anonymized 384s, 10148 tokens, 76.75s/hypothesis


## Per-object oracle gap

| arm | mixture log-loss | per-object oracle | gain | best-particle counts |
|---|---|---|---|---|
| passive · llm · tour_named | 1.096 | 0.996 | 0.100 | {'hyp3': 6, 'hyp4': 3, 'stat': 12, 'hyp1': 12, 'hyp2': 2} |
| passive · llm · tour_anonymized | 1.109 | 1.049 | 0.060 | {'hyp4': 3, 'stat': 21, 'hyp1': 4, 'hyp2': 6, 'hyp5': 1} |
| passive · llm_fixed · tour_named | 1.081 | 1.023 | 0.058 | {'hyp3': 8, 'stat': 15, 'hyp1': 12} |
| passive · llm_fixed · tour_anonymized | 1.121 | 1.052 | 0.069 | {'hyp4': 2, 'stat': 21, 'hyp1': 8, 'hyp2': 3, 'hyp5': 1} |
