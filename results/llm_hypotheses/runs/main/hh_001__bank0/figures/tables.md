# Tour start + re-asking — hh_001

Scoring: top-1 and log-loss are EXACT (ON_PERSON and OUT_OF_HOUSE distinct); the merged number (ON_PERSON ≡ OUT_OF_HOUSE, the older rule) follows in brackets. ± is one standard error.

## Passive protocol (fixed patrol, no policy)

| arm | n | top-1 (merged) | log-loss (merged) |
|---|---|---|---|
| graph_fixed · graph_anonymized | 2472 | 0.708 ± 0.009 (0.708) | 1.092 ± 0.026 (1.092) |
| graph_fixed · graph_named | 2472 | 0.709 ± 0.009 (0.709) | 1.089 ± 0.026 (1.089) |
| llm · tour_anonymized | 2472 | 0.711 ± 0.009 (0.711) | 1.080 ± 0.026 (1.080) |
| llm · tour_named | 2472 | 0.704 ± 0.009 (0.704) | 1.083 ± 0.026 (1.083) |
| llm_fixed · tour_anonymized | 2472 | 0.710 ± 0.009 (0.710) | 1.078 ± 0.026 (1.078) |
| llm_fixed · tour_named | 2472 | 0.704 ± 0.009 (0.704) | 1.092 ± 0.026 (1.092) |
| longleaf_fixed · longleaf_anonymized | 2472 | 0.712 ± 0.009 (0.712) | 1.091 ± 0.026 (1.091) |
| longleaf_fixed · longleaf_named | 2472 | 0.713 ± 0.009 (0.713) | 1.093 ± 0.026 (1.093) |
| mostfreq72 | 2472 | 0.721 ± 0.009 (0.721) | 1.102 ± 0.030 (1.102) |
| routine_posterior | 2472 | 0.758 ± 0.009 (0.758) | 0.714 ± 0.023 (0.714) |
| tree · tree_anonymized | 2472 | 0.709 ± 0.009 (0.709) | 1.093 ± 0.026 (1.093) |
| tree · tree_named | 2472 | 0.714 ± 0.009 (0.714) | 1.076 ± 0.026 (1.076) |
| tree_fixed · tree_anonymized | 2472 | 0.708 ± 0.009 (0.708) | 1.093 ± 0.026 (1.093) |
| tree_fixed · tree_named | 2472 | 0.710 ± 0.009 (0.710) | 1.084 ± 0.026 (1.084) |

## Tour-absent accuracy (objects the installation tour did not see, apart from the tour-visible stratum)

| arm | tour-absent n | tour-absent top-1 (merged) | tour-absent log-loss | tour-visible n | tour-visible top-1 (merged) |
|---|---|---|---|---|---|
| active · graph_fixed · graph_anonymized · f0 | 765 | 0.493 ± 0.018 (0.539) | 1.657 ± 0.059 | 1707 | 0.875 ± 0.008 (0.879) |
| active · graph_fixed · graph_named · f0 | 765 | 0.499 ± 0.018 (0.545) | 1.644 ± 0.059 | 1707 | 0.882 ± 0.008 (0.882) |
| active · llm · tour_anonymized · f0 | 765 | 0.490 ± 0.018 (0.533) | 1.667 ± 0.060 | 1707 | 0.889 ± 0.008 (0.889) |
| active · llm · tour_named · f0 | 765 | 0.497 ± 0.018 (0.558) | 1.617 ± 0.059 | 1707 | 0.881 ± 0.008 (0.884) |
| active · llm_fixed · tour_anonymized · f0 | 765 | 0.498 ± 0.018 (0.539) | 1.651 ± 0.059 | 1707 | 0.887 ± 0.008 (0.888) |
| active · llm_fixed · tour_named · f0 | 765 | 0.502 ± 0.018 (0.552) | 1.667 ± 0.059 | 1707 | 0.880 ± 0.008 (0.880) |
| active · log_reader · named · f0 | 765 | 0.525 ± 0.018 (0.525) | 2.515 ± 0.092 | 1707 | 0.883 ± 0.008 (0.883) |
| active · log_reader_aided · named · f0 | 765 | 0.566 ± 0.018 (0.567) | 2.359 ± 0.091 | 1707 | 0.837 ± 0.009 (0.837) |
| active · longleaf_fixed · longleaf_anonymized · f0 | 765 | 0.495 ± 0.018 (0.542) | 1.619 ± 0.058 | 1707 | 0.882 ± 0.008 (0.883) |
| active · longleaf_fixed · longleaf_named · f0 | 765 | 0.495 ± 0.018 (0.544) | 1.644 ± 0.059 | 1707 | 0.882 ± 0.008 (0.883) |
| active · mostfreq72 · f0 | 765 | 0.493 ± 0.018 (0.622) | 1.497 ± 0.058 | 1707 | 0.873 ± 0.008 (0.882) |
| active · routine_posterior · f0 | 765 | 0.731 ± 0.016 (0.731) | 0.880 ± 0.046 | 1707 | 0.845 ± 0.009 (0.845) |
| active · tree · tree_anonymized · f0 | 765 | 0.495 ± 0.018 (0.542) | 1.630 ± 0.058 | 1707 | 0.876 ± 0.008 (0.879) |
| active · tree · tree_named · f0 | 765 | 0.498 ± 0.018 (0.540) | 1.678 ± 0.060 | 1707 | 0.886 ± 0.008 (0.886) |
| active · tree_fixed · tree_anonymized · f0 | 765 | 0.498 ± 0.018 (0.544) | 1.640 ± 0.058 | 1707 | 0.875 ± 0.008 (0.878) |
| active · tree_fixed · tree_named · f0 | 765 | 0.495 ± 0.018 (0.536) | 1.663 ± 0.059 | 1707 | 0.888 ± 0.008 (0.889) |
| active · tree_fixed · tree_named · f0 · b0.5 | 765 | 0.505 ± 0.018 (0.550) | 1.647 ± 0.059 | 1707 | 0.883 ± 0.008 (0.885) |
| passive · graph_fixed · graph_anonymized | 765 | 0.459 ± 0.018 (0.459) | 1.878 ± 0.052 | 1707 | 0.820 ± 0.009 (0.820) |
| passive · graph_fixed · graph_named | 765 | 0.459 ± 0.018 (0.459) | 1.878 ± 0.052 | 1707 | 0.821 ± 0.009 (0.821) |
| passive · llm · tour_anonymized | 765 | 0.458 ± 0.018 (0.458) | 1.879 ± 0.052 | 1707 | 0.824 ± 0.009 (0.824) |
| passive · llm · tour_named | 765 | 0.456 ± 0.018 (0.456) | 1.865 ± 0.053 | 1707 | 0.815 ± 0.009 (0.815) |
| passive · llm_fixed · tour_anonymized | 765 | 0.459 ± 0.018 (0.459) | 1.878 ± 0.052 | 1707 | 0.823 ± 0.009 (0.823) |
| passive · llm_fixed · tour_named | 765 | 0.459 ± 0.018 (0.459) | 1.878 ± 0.052 | 1707 | 0.814 ± 0.009 (0.814) |
| passive · longleaf_fixed · longleaf_anonymized | 765 | 0.459 ± 0.018 (0.459) | 1.878 ± 0.052 | 1707 | 0.825 ± 0.009 (0.825) |
| passive · longleaf_fixed · longleaf_named | 765 | 0.459 ± 0.018 (0.459) | 1.878 ± 0.052 | 1707 | 0.827 ± 0.009 (0.827) |
| passive · mostfreq72 | 765 | 0.482 ± 0.018 (0.482) | 1.837 ± 0.058 | 1707 | 0.828 ± 0.009 (0.828) |
| passive · routine_posterior | 765 | 0.648 ± 0.017 (0.648) | 1.104 ± 0.052 | 1707 | 0.807 ± 0.010 (0.807) |
| passive · tree · tree_anonymized | 765 | 0.458 ± 0.018 (0.458) | 1.881 ± 0.052 | 1707 | 0.821 ± 0.009 (0.821) |
| passive · tree · tree_named | 765 | 0.461 ± 0.018 (0.461) | 1.880 ± 0.053 | 1707 | 0.827 ± 0.009 (0.827) |
| passive · tree_fixed · tree_anonymized | 765 | 0.459 ± 0.018 (0.459) | 1.878 ± 0.052 | 1707 | 0.820 ± 0.009 (0.820) |
| passive · tree_fixed · tree_named | 765 | 0.459 ± 0.018 (0.459) | 1.878 ± 0.052 | 1707 | 0.822 ± 0.009 (0.822) |

## Assumption recovery (final graph holds a value matching the bank's ground-truth premise)

| arm | premises | matched | rate |
|---|---|---|---|
| active · graph_fixed · graph_anonymized · f0 | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': 'household_size=solo', 'work_pattern': 'weekday_presence=commutes'} | 1.00 |
| active · graph_fixed · graph_named · f0 | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': None, 'work_pattern': 'weekday_presence=commutes'} | 0.50 |
| active · llm · tour_anonymized · f0 | {'composition': 'solo', 'work_pattern': 'works_away'} | N/A (no assumptions) | N/A |
| active · llm · tour_named · f0 | {'composition': 'solo', 'work_pattern': 'works_away'} | N/A (no assumptions) | N/A |
| active · llm_fixed · tour_anonymized · f0 | {'composition': 'solo', 'work_pattern': 'works_away'} | N/A (no assumptions) | N/A |
| active · llm_fixed · tour_named · f0 | {'composition': 'solo', 'work_pattern': 'works_away'} | N/A (no assumptions) | N/A |
| active · longleaf_fixed · longleaf_anonymized · f0 | {'composition': 'solo', 'work_pattern': 'works_away'} | N/A (no assumptions) | N/A |
| active · longleaf_fixed · longleaf_named · f0 | {'composition': 'solo', 'work_pattern': 'works_away'} | N/A (no assumptions) | N/A |
| active · tree · tree_anonymized · f0 | {'composition': 'solo', 'work_pattern': 'works_away'} | N/A (no assumptions) | N/A |
| active · tree · tree_named · f0 | {'composition': 'solo', 'work_pattern': 'works_away'} | N/A (no assumptions) | N/A |
| active · tree_fixed · tree_anonymized · f0 | {'composition': 'solo', 'work_pattern': 'works_away'} | N/A (no assumptions) | N/A |
| active · tree_fixed · tree_named · f0 | {'composition': 'solo', 'work_pattern': 'works_away'} | N/A (no assumptions) | N/A |
| active · tree_fixed · tree_named · f0 · b0.5 | {'composition': 'solo', 'work_pattern': 'works_away'} | N/A (no assumptions) | N/A |
| passive · graph_fixed · graph_anonymized | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': 'household_size=solo', 'work_pattern': 'weekday_presence=commutes'} | 1.00 |
| passive · graph_fixed · graph_named | {'composition': 'solo', 'work_pattern': 'works_away'} | {'composition': None, 'work_pattern': 'weekday_presence=commutes'} | 0.50 |
| passive · llm · tour_anonymized | {'composition': 'solo', 'work_pattern': 'works_away'} | N/A (no assumptions) | N/A |
| passive · llm · tour_named | {'composition': 'solo', 'work_pattern': 'works_away'} | N/A (no assumptions) | N/A |
| passive · llm_fixed · tour_anonymized | {'composition': 'solo', 'work_pattern': 'works_away'} | N/A (no assumptions) | N/A |
| passive · llm_fixed · tour_named | {'composition': 'solo', 'work_pattern': 'works_away'} | N/A (no assumptions) | N/A |
| passive · longleaf_fixed · longleaf_anonymized | {'composition': 'solo', 'work_pattern': 'works_away'} | N/A (no assumptions) | N/A |
| passive · longleaf_fixed · longleaf_named | {'composition': 'solo', 'work_pattern': 'works_away'} | N/A (no assumptions) | N/A |
| passive · tree · tree_anonymized | {'composition': 'solo', 'work_pattern': 'works_away'} | N/A (no assumptions) | N/A |
| passive · tree · tree_named | {'composition': 'solo', 'work_pattern': 'works_away'} | N/A (no assumptions) | N/A |
| passive · tree_fixed · tree_anonymized | {'composition': 'solo', 'work_pattern': 'works_away'} | N/A (no assumptions) | N/A |
| passive · tree_fixed · tree_named | {'composition': 'solo', 'work_pattern': 'works_away'} | N/A (no assumptions) | N/A |

## Active protocol (myopic VoI λ=0.05, random slice f)

| arm | top-1 (merged) | log-loss (belief at answer time, after that question's senses) | senses/day | random senses |
|---|---|---|---|---|
| graph_fixed · graph_anonymized · f0 | 0.757 ± 0.009 (0.774) | 0.878 ± 0.027 | 24.0 | 0 |
| graph_fixed · graph_named · f0 | 0.764 ± 0.009 (0.778) | 0.859 ± 0.027 | 24.0 | 0 |
| llm · tour_anonymized · f0 | 0.765 ± 0.009 (0.779) | 0.862 ± 0.027 | 24.0 | 0 |
| llm · tour_named · f0 | 0.762 ± 0.009 (0.783) | 0.862 ± 0.027 | 24.0 | 0 |
| llm_fixed · tour_anonymized · f0 | 0.767 ± 0.009 (0.780) | 0.863 ± 0.027 | 24.0 | 0 |
| llm_fixed · tour_named · f0 | 0.763 ± 0.009 (0.778) | 0.881 ± 0.027 | 24.0 | 0 |
| log_reader · named · f0 | 0.773 ± 0.008 (0.773) | n/a (ranked answer) | 18.9 | None |
| log_reader_aided · named · f0 | 0.753 ± 0.009 (0.753) | n/a (ranked answer) | 22.8 | None |
| longleaf_fixed · longleaf_anonymized · f0 | 0.763 ± 0.009 (0.778) | 0.858 ± 0.027 | 24.0 | 0 |
| longleaf_fixed · longleaf_named · f0 | 0.763 ± 0.009 (0.778) | 0.862 ± 0.027 | 24.0 | 0 |
| mostfreq72 · f0 | 0.755 ± 0.009 (0.801) | 0.837 ± 0.028 | 24.0 | 0 |
| routine_posterior · f0 | 0.809 ± 0.008 (0.810) | 0.592 ± 0.021 | 24.0 | 0 |
| tree · tree_anonymized · f0 | 0.758 ± 0.009 (0.775) | 0.869 ± 0.027 | 24.0 | 0 |
| tree · tree_named · f0 | 0.766 ± 0.009 (0.779) | 0.867 ± 0.027 | 24.0 | 0 |
| tree_fixed · tree_anonymized · f0 | 0.758 ± 0.009 (0.774) | 0.881 ± 0.027 | 24.0 | 0 |
| tree_fixed · tree_named · f0 | 0.766 ± 0.009 (0.780) | 0.865 ± 0.027 | 24.0 | 0 |
| tree_fixed · tree_named · f0 · b0.5 | 0.766 ± 0.009 (0.782) | 0.861 ± 0.027 | 24.0 | None |

## Paired comparisons (A − B over the same questions, 95% bootstrap CI)

| comparison | top-1 | log-loss |
|---|---|---|
| named − anonymized (re-asking) | -0.006 [-0.012, -0.002]* | +0.003 [-0.007, +0.012] |
| named − anonymized (fixed set) | -0.006 [-0.011, -0.002]* | +0.014 [+0.007, +0.020]* |
| re-asking − fixed (named) | +0.000 [-0.004, +0.004] | -0.010 [-0.017, -0.003]* |
| re-asking − fixed (anonymized) | +0.000 [-0.003, +0.004] | +0.002 [-0.003, +0.006] |
| LLM named − MostFreq72 (no-LLM) | -0.017 [-0.025, -0.009]* | -0.019 [-0.035, -0.002]* |
| LLM named − MostFreq72 (active, f0) | +0.007 [-0.002, +0.016] | +0.025 [-0.005, +0.055] |

## Re-asking: calls, timing, outcome

| arm | re-asks | live LLM calls | generation s | events |
|---|---|---|---|---|
| active · graph_fixed · graph_anonymized · f0 | 0 | None | None |  |
| active · graph_fixed · graph_named · f0 | 0 | None | None |  |
| active · llm · tour_anonymized · f0 | 4 | 4 | 2249.3 | d0 uncovered → revised; d0 uncovered → revised; d2 uncovered → revised; d3 scheduled → revised |
| active · llm · tour_named · f0 | 4 | 4 | 2724.2 | d0 uncovered → revised; d2 uncovered → revised; d3 scheduled → revised; d7 scheduled → revised |
| active · llm_fixed · tour_anonymized · f0 | 0 | None | None |  |
| active · llm_fixed · tour_named · f0 | 0 | None | None |  |
| active · longleaf_fixed · longleaf_anonymized · f0 | 0 | None | None |  |
| active · longleaf_fixed · longleaf_named · f0 | 0 | None | None |  |
| active · tree · tree_anonymized · f0 | 2 | 2 | 1124.8 | d3 scheduled → revised; d14 anomaly → revised |
| active · tree · tree_named · f0 | 2 | 4 | 907.0 | d3 scheduled → revised; d14 anomaly → revised |
| active · tree_fixed · tree_anonymized · f0 | 0 | None | None |  |
| active · tree_fixed · tree_named · f0 | 0 | None | None |  |
| active · tree_fixed · tree_named · f0 · b0.5 | 0 | None | None |  |
| passive · graph_fixed · graph_anonymized | 0 | None | None |  |
| passive · graph_fixed · graph_named | 0 | None | None |  |
| passive · llm · tour_anonymized | 4 | 4 | 2210.6 | d1 uncovered → revised; d2 uncovered → revised; d2 uncovered → revised; d3 scheduled → revised |
| passive · llm · tour_named | 4 | 4 | 2484.6 | d1 uncovered → revised; d2 uncovered → revised; d2 uncovered → revised; d3 scheduled → revised |
| passive · llm_fixed · tour_anonymized | 0 | None | None |  |
| passive · llm_fixed · tour_named | 0 | None | None |  |
| passive · longleaf_fixed · longleaf_anonymized | 0 | None | None |  |
| passive · longleaf_fixed · longleaf_named | 0 | None | None |  |
| passive · tree · tree_anonymized | 1 | 1 | 383.5 | d3 scheduled → revised |
| passive · tree · tree_named | 1 | 2 | 455.0 | d3 scheduled → revised |
| passive · tree_fixed · tree_anonymized | 0 | None | None |  |
| passive · tree_fixed · tree_named | 0 | None | None |  |

## Tree arms: label recovery (name-matched: a label whose text carries a synonym of the bank's premise value; its share of node weight in brackets), settled labels, final size

| arm | premises | matched | settled labels | nodes / max depth | revisions applied / rejected |
|---|---|---|---|---|---|
| active · tree · tree_anonymized · f0 | {'composition': 'solo', 'work_pattern': 'works_away'} | composition=single_adult (0.36); work_pattern=both_commute (0.55) | none | 5 / 1 | 2 / 0 |
| active · tree · tree_named · f0 | {'composition': 'solo', 'work_pattern': 'works_away'} | composition=single_resident_mara (1.00); work_pattern=commutes_weekday (0.65) | single_resident_mara | 5 / 1 | 2 / 1 |
| active · tree_fixed · tree_anonymized · f0 | {'composition': 'solo', 'work_pattern': 'works_away'} | composition=single_adult (0.45); work_pattern=both_commute (0.39) | none | 4 / 0 | 0 / 0 |
| active · tree_fixed · tree_named · f0 | {'composition': 'solo', 'work_pattern': 'works_away'} | composition=single_resident_mara (1.00); work_pattern=commutes_weekday (0.67) | single_resident_mara | 4 / 0 | 0 / 0 |
| active · tree_fixed · tree_named · f0 · b0.5 | {'composition': 'solo', 'work_pattern': 'works_away'} | composition=single_resident_mara (1.00); work_pattern=commutes_weekday (0.65) | single_resident_mara | 4 / 0 | 0 / 0 |
| passive · tree · tree_anonymized | {'composition': 'solo', 'work_pattern': 'works_away'} | composition=single_adult (0.26); work_pattern=both_commute (0.74) | none | 5 / 1 | 2 / 0 |
| passive · tree · tree_named | {'composition': 'solo', 'work_pattern': 'works_away'} | composition=single_resident_mara (1.00); work_pattern=commutes_weekday (0.93) | single_resident_mara, commutes_weekday, home_empty_middays | 4 / 1 | 1 / 1 |
| passive · tree_fixed · tree_anonymized | {'composition': 'solo', 'work_pattern': 'works_away'} | composition=single_adult (0.45); work_pattern=both_commute (0.45) | none | 4 / 0 | 0 / 0 |
| passive · tree_fixed · tree_named | {'composition': 'solo', 'work_pattern': 'works_away'} | composition=single_resident_mara (1.00); work_pattern=commutes_weekday (0.76) | single_resident_mara | 3 / 0 | 0 / 0 |

## Graph arm: leaves, edits, prunes, births, rejections, checks

| arm | leaves by day (first → last) | applied ops | rejected ops | prunes | born / skipped | checks resolved (in favour) | weight spread presence / absence | settled at end |
|---|---|---|---|---|---|---|---|---|
| active · graph_fixed · graph_anonymized · f0 | 12 → 11 | 0 | 0  | 1 | 0 / 0 | 47 (20) | 31.2 / 10.6 |  |
| active · graph_fixed · graph_named · f0 | 4 → 4 | 0 | 0  | 0 | 0 / 0 | 29 (16) | 65.6 / 65.3 |  |
| passive · graph_fixed · graph_anonymized | 12 → 7 | 0 | 0  | 5 | 0 / 0 | 27 (13) | 23.8 / 16.4 | weekday_presence=home_all_day |
| passive · graph_fixed · graph_named | 4 → 4 | 0 | 0  | 0 | 0 / 0 | 14 (7) | 37.3 / 44.4 |  |

## Log reader: cost next to accuracy

| arm | top-1 | late top-1 | LLM calls | prompt tokens | completion tokens | live generation s | wall s | invalid decisions | notes versions |
|---|---|---|---|---|---|---|---|---|---|
| active · log_reader · named · f0 | 0.773 ± 0.008 | 0.525 | 2783 | 48627936 | 376036 | 14798.3 | 14801.8 | 119 | 0 |
| active · log_reader_aided · named · f0 | 0.753 ± 0.009 | 0.566 | 2850 | 58229726 | 431817 | 8733.8 | 8739.0 | 153 | 0 |

Tour-start elicitation (last elicit run): hh_001 tour_named 427s, 11207 tokens, 85.35s/hypothesis; hh_001 tour_anonymized 508s, 13270 tokens, 101.55s/hypothesis


## Per-object oracle gap

| arm | mixture log-loss | per-object oracle | gain | best-particle counts |
|---|---|---|---|---|
| passive · llm · tour_named | 1.083 | 1.031 | 0.052 | {'stat': 15, 'hyp3': 5, 'hyp2': 4, 'hyp4': 3, 'hyp5': 5, 'hyp1': 3} |
| passive · llm · tour_anonymized | 1.080 | 1.037 | 0.043 | {'stat': 15, 'hyp2': 1, 'hyp1': 15, 'hyp3': 1, 'hyp5': 3} |
| passive · llm_fixed · tour_named | 1.092 | 1.045 | 0.048 | {'stat': 17, 'hyp3': 2, 'hyp2': 4, 'hyp1': 8, 'hyp5': 3, 'hyp4': 1} |
| passive · llm_fixed · tour_anonymized | 1.078 | 1.037 | 0.042 | {'stat': 14, 'hyp2': 1, 'hyp1': 18, 'hyp3': 1, 'hyp4': 1} |
