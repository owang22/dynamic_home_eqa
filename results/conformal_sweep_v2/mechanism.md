# Mechanism table: age of evidence x regime

Sweep `results/conformal_sweep_v2/budget90`; sensing policy `conformal_global_alpha0.3`; passive sets at alpha 0.3 (global). Regimes from bank data. Cells with fewer than 30 questions are listed but not quoted in the verdicts' pooled numbers beyond their weight.

## HierarchyBackoff(po=5,pc=5,hl=24h)

| age_bin | regime | n | share | mean_out_mass | set_contains_out | n_sensed | sensed_share | first_sense_hit_rate | acc_given_sensed | acc_given_memory | acc_passive_new | acc_passive_old | n_old |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-6h | truly_out | 302 | 0.0134 | 0.0008 | 0.0 | 70 | 0.2318 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 302 |
| 0-6h | stale_in_house | 4645 | 0.2064 | 0.0009 | 0.0 | 1012 | 0.2179 | 0.6235 | 0.9387 | 0.9061 | 0.8693 | 0.8693 | 4645 |
| 6-24h | truly_out | 1780 | 0.0791 | 0.0016 | 0.0 | 392 | 0.2202 | 0.0 | 0.0051 | 0.0 | 0.0 | 0.0264 | 1780 |
| 6-24h | came_back | 20 | 0.0009 | 0.0084 | 0.0 | 3 | 0.15 | 0.6667 | 1.0 | 0.9412 | 0.75 | 0.0 | 20 |
| 6-24h | stale_in_house | 9860 | 0.4382 | 0.0009 | 0.0 | 2258 | 0.229 | 0.5868 | 0.8964 | 0.836 | 0.7069 | 0.7041 | 9860 |
| 24-72h | truly_out | 1115 | 0.0496 | 0.0038 | 0.0 | 356 | 0.3193 | 0.0 | 0.0112 | 0.0013 | 0.0 | 0.4574 | 1115 |
| 24-72h | came_back | 1028 | 0.0457 | 0.0029 | 0.0 | 223 | 0.2169 | 0.6502 | 0.9776 | 0.9503 | 0.93 | 0.0 | 1028 |
| 24-72h | stale_in_house | 2548 | 0.1132 | 0.0024 | 0.0 | 924 | 0.3626 | 0.4502 | 0.7825 | 0.6355 | 0.356 | 0.2991 | 2548 |
| 72h+ | truly_out | 381 | 0.0169 | 0.0031 | 0.0 | 99 | 0.2598 | 0.0 | 0.0101 | 0.0 | 0.0 | 0.5144 | 381 |
| 72h+ | came_back | 402 | 0.0179 | 0.0024 | 0.0 | 110 | 0.2736 | 0.5727 | 0.9909 | 0.9041 | 0.8532 | 0.0 | 402 |
| 72h+ | stale_in_house | 419 | 0.0186 | 0.0027 | 0.0 | 143 | 0.3413 | 0.4126 | 0.7343 | 0.5072 | 0.1026 | 0.0788 | 419 |

**HierarchyBackoff(po=5,pc=5,hl=24h)**
- sensing pays in stale_in_house: accuracy given sensed 0.877 (n=4337) vs answered from memory 0.818: **held** (the policy chose which questions to sense, so this is the policy's own split, not a controlled contrast)
- came_back addressable by graded beliefs, passive accuracy new 0.906 (n=1450) vs old 0.000: **held**
- truly_out near-worthless per single sense: first-sense hit rate 0.000 (n=917): **held**; reachable by passive answering: memory accuracy new 0.000 (n=3578) vs old 0.210: **did not hold**

## LastObservation

| age_bin | regime | n | share | mean_out_mass | set_contains_out | n_sensed | sensed_share | first_sense_hit_rate | acc_given_sensed | acc_given_memory | acc_passive_new | acc_passive_old | n_old |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-6h | truly_out | 302 | 0.0134 | 0.0007 | 0.0 | 40 | 0.1325 | 0.0 | 1.0 | 0.0 | 0.0 | 0.0 | 302 |
| 0-6h | stale_in_house | 4645 | 0.2064 | 0.0007 | 0.0 | 20 | 0.0043 | 0.3 | 1.0 | 0.8971 | 0.8818 | 0.8818 | 4645 |
| 6-24h | truly_out | 1780 | 0.0791 | 0.0024 | 0.0517 | 290 | 0.1629 | 0.0 | 1.0 | 0.0013 | 0.0 | 0.0236 | 1780 |
| 6-24h | came_back | 20 | 0.0009 | 0.0123 | 1.0 | 6 | 0.3 | 1.0 | 1.0 | 0.9286 | 1.0 | 0.0 | 20 |
| 6-24h | stale_in_house | 9860 | 0.4382 | 0.0009 | 0.0094 | 146 | 0.0148 | 0.2808 | 0.9932 | 0.784 | 0.7056 | 0.7062 | 9860 |
| 24-72h | truly_out | 1115 | 0.0496 | 0.0069 | 0.4933 | 235 | 0.2108 | 0.0 | 1.0 | 0.0023 | 0.0027 | 0.4592 | 1115 |
| 24-72h | came_back | 1028 | 0.0457 | 0.0032 | 0.3901 | 76 | 0.0739 | 0.5526 | 1.0 | 0.8036 | 1.0 | 0.0 | 1028 |
| 24-72h | stale_in_house | 2548 | 0.1132 | 0.0043 | 0.3348 | 204 | 0.0801 | 0.049 | 0.9853 | 0.5798 | 0.2747 | 0.2979 | 2548 |
| 72h+ | truly_out | 381 | 0.0169 | 0.0055 | 0.3412 | 62 | 0.1627 | 0.0 | 1.0 | 0.0031 | 0.0 | 0.5249 | 381 |
| 72h+ | came_back | 402 | 0.0179 | 0.0027 | 0.3333 | 29 | 0.0721 | 0.6207 | 0.8966 | 0.8204 | 1.0 | 0.0 | 402 |
| 72h+ | stale_in_house | 419 | 0.0186 | 0.0044 | 0.389 | 33 | 0.0788 | 0.2727 | 1.0 | 0.4689 | 0.0 | 0.0811 | 419 |

**LastObservation**
- sensing pays in stale_in_house: accuracy given sensed 0.990 (n=403) vs answered from memory 0.777: **held** (the policy chose which questions to sense, so this is the policy's own split, not a controlled contrast)
- came_back addressable by graded beliefs, passive accuracy new 1.000 (n=1450) vs old 0.000: one-hot belief, not expected to move
- truly_out near-worthless per single sense: first-sense hit rate 0.000 (n=627): **held**; reachable by passive answering: memory accuracy new 0.001 (n=3578) vs old 0.211: **did not hold**

## MostFrequentLocation(hl=24h)

| age_bin | regime | n | share | mean_out_mass | set_contains_out | n_sensed | sensed_share | first_sense_hit_rate | acc_given_sensed | acc_given_memory | acc_passive_new | acc_passive_old | n_old |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-6h | truly_out | 302 | 0.0134 | 0.0008 | 0.0 | 57 | 0.1887 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 302 |
| 0-6h | stale_in_house | 4645 | 0.2064 | 0.0008 | 0.0 | 947 | 0.2039 | 0.6241 | 0.9345 | 0.9062 | 0.8706 | 0.8706 | 4645 |
| 6-24h | truly_out | 1780 | 0.0791 | 0.002 | 0.0 | 321 | 0.1803 | 0.0 | 0.0218 | 0.0 | 0.0 | 0.0275 | 1780 |
| 6-24h | came_back | 20 | 0.0009 | 0.0103 | 0.0 | 6 | 0.3 | 0.6667 | 1.0 | 0.9286 | 0.85 | 0.0 | 20 |
| 6-24h | stale_in_house | 9860 | 0.4382 | 0.0009 | 0.0 | 2038 | 0.2067 | 0.577 | 0.8871 | 0.8209 | 0.7068 | 0.7044 | 9860 |
| 24-72h | truly_out | 1115 | 0.0496 | 0.0057 | 0.0 | 318 | 0.2852 | 0.0 | 0.022 | 0.0 | 0.0018 | 0.4655 | 1115 |
| 24-72h | came_back | 1028 | 0.0457 | 0.0031 | 0.0 | 179 | 0.1741 | 0.743 | 0.9944 | 0.9635 | 0.9543 | 0.0 | 1028 |
| 24-72h | stale_in_house | 2548 | 0.1132 | 0.003 | 0.0 | 848 | 0.3328 | 0.4446 | 0.7724 | 0.59 | 0.3536 | 0.2959 | 2548 |
| 72h+ | truly_out | 381 | 0.0169 | 0.0047 | 0.0 | 71 | 0.1864 | 0.0 | 0.0282 | 0.0 | 0.0 | 0.4856 | 381 |
| 72h+ | came_back | 402 | 0.0179 | 0.0026 | 0.0 | 57 | 0.1418 | 0.5263 | 0.9825 | 0.9217 | 0.9801 | 0.0 | 402 |
| 72h+ | stale_in_house | 419 | 0.0186 | 0.0032 | 0.0 | 113 | 0.2697 | 0.3274 | 0.5575 | 0.3366 | 0.0692 | 0.0716 | 419 |

**MostFrequentLocation(hl=24h)**
- sensing pays in stale_in_house: accuracy given sensed 0.864 (n=3946) vs answered from memory 0.798: **held** (the policy chose which questions to sense, so this is the policy's own split, not a controlled contrast)
- came_back addressable by graded beliefs, passive accuracy new 0.960 (n=1450) vs old 0.000: **held**
- truly_out near-worthless per single sense: first-sense hit rate 0.000 (n=767): **held**; reachable by passive answering: memory accuracy new 0.001 (n=3578) vs old 0.210: **did not hold**

## PeriodicPersistence(min_dep=2,bin=1h,hl=24h)

| age_bin | regime | n | share | mean_out_mass | set_contains_out | n_sensed | sensed_share | first_sense_hit_rate | acc_given_sensed | acc_given_memory | acc_passive_new | acc_passive_old | n_old |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-6h | truly_out | 302 | 0.0134 | 0.0007 | 0.0 | 33 | 0.1093 | 0.0 | 0.2424 | 0.0 | 0.0 | 0.0 | 302 |
| 0-6h | stale_in_house | 4645 | 0.2064 | 0.0007 | 0.0 | 218 | 0.0469 | 0.5872 | 0.8807 | 0.9056 | 0.8803 | 0.8803 | 4645 |
| 6-24h | truly_out | 1780 | 0.0791 | 0.0022 | 0.0056 | 422 | 0.2371 | 0.0 | 0.3294 | 0.0007 | 0.0006 | 0.0326 | 1780 |
| 6-24h | came_back | 20 | 0.0009 | 0.0116 | 0.0 | 2 | 0.1 | 1.0 | 1.0 | 0.8889 | 0.95 | 0.0 | 20 |
| 6-24h | stale_in_house | 9860 | 0.4382 | 0.0009 | 0.0004 | 1638 | 0.1661 | 0.569 | 0.8333 | 0.8378 | 0.7072 | 0.7059 | 9860 |
| 24-72h | truly_out | 1115 | 0.0496 | 0.0061 | 0.0072 | 402 | 0.3605 | 0.0 | 0.2761 | 0.0014 | 0.0 | 0.4762 | 1115 |
| 24-72h | came_back | 1028 | 0.0457 | 0.0032 | 0.0 | 223 | 0.2169 | 0.5471 | 0.9327 | 0.9106 | 0.9621 | 0.0 | 1028 |
| 24-72h | stale_in_house | 2548 | 0.1132 | 0.0034 | 0.002 | 728 | 0.2857 | 0.4148 | 0.717 | 0.6824 | 0.3281 | 0.2991 | 2548 |
| 72h+ | truly_out | 381 | 0.0169 | 0.0049 | 0.0079 | 101 | 0.2651 | 0.0 | 0.198 | 0.0 | 0.0 | 0.5066 | 381 |
| 72h+ | came_back | 402 | 0.0179 | 0.0027 | 0.0 | 74 | 0.1841 | 0.4459 | 0.8784 | 0.8841 | 0.9701 | 0.0 | 402 |
| 72h+ | stale_in_house | 419 | 0.0186 | 0.0035 | 0.0024 | 117 | 0.2792 | 0.4017 | 0.5983 | 0.5596 | 0.074 | 0.0716 | 419 |

**PeriodicPersistence(min_dep=2,bin=1h,hl=24h)**
- sensing pays in stale_in_house: accuracy given sensed 0.796 (n=2701) vs answered from memory 0.826: **did not hold** (the policy chose which questions to sense, so this is the policy's own split, not a controlled contrast)
- came_back addressable by graded beliefs, passive accuracy new 0.964 (n=1450) vs old 0.000: **held**
- truly_out near-worthless per single sense: first-sense hit rate 0.000 (n=958): **held**; reachable by passive answering: memory accuracy new 0.000 (n=3578) vs old 0.219: **did not hold**

## TimetableLookup(bin=1h,days=all,hl=24h)

| age_bin | regime | n | share | mean_out_mass | set_contains_out | n_sensed | sensed_share | first_sense_hit_rate | acc_given_sensed | acc_given_memory | acc_passive_new | acc_passive_old | n_old |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-6h | truly_out | 302 | 0.0134 | 0.001 | 0.0 | 131 | 0.4338 | 0.0 | 0.8931 | 0.0 | 0.0 | 0.0033 | 302 |
| 0-6h | stale_in_house | 4645 | 0.2064 | 0.0015 | 0.023 | 591 | 0.1272 | 0.6007 | 0.9611 | 0.7432 | 0.7849 | 0.7907 | 4645 |
| 6-24h | truly_out | 1780 | 0.0791 | 0.0025 | 0.0416 | 509 | 0.286 | 0.0 | 0.9489 | 0.0031 | 0.0 | 0.0382 | 1780 |
| 6-24h | came_back | 20 | 0.0009 | 0.0104 | 0.4 | 4 | 0.2 | 1.0 | 1.0 | 0.875 | 0.85 | 0.0 | 20 |
| 6-24h | stale_in_house | 9860 | 0.4382 | 0.0015 | 0.0153 | 1905 | 0.1932 | 0.5612 | 0.9601 | 0.6943 | 0.6506 | 0.644 | 9860 |
| 24-72h | truly_out | 1115 | 0.0496 | 0.0059 | 0.1094 | 299 | 0.2682 | 0.0 | 0.9398 | 0.0025 | 0.0009 | 0.4825 | 1115 |
| 24-72h | came_back | 1028 | 0.0457 | 0.0038 | 0.035 | 123 | 0.1196 | 0.6585 | 0.9512 | 0.8188 | 0.8813 | 0.0 | 1028 |
| 24-72h | stale_in_house | 2548 | 0.1132 | 0.0034 | 0.0471 | 503 | 0.1974 | 0.4533 | 0.9384 | 0.5115 | 0.356 | 0.2786 | 2548 |
| 72h+ | truly_out | 381 | 0.0169 | 0.0049 | 0.0919 | 85 | 0.2231 | 0.0 | 0.9529 | 0.0 | 0.0 | 0.4751 | 381 |
| 72h+ | came_back | 402 | 0.0179 | 0.0033 | 0.0149 | 57 | 0.1418 | 0.6667 | 0.9825 | 0.8058 | 0.9204 | 0.0 | 402 |
| 72h+ | stale_in_house | 419 | 0.0186 | 0.0037 | 0.0286 | 74 | 0.1766 | 0.4595 | 0.8784 | 0.3884 | 0.1002 | 0.0716 | 419 |

**TimetableLookup(bin=1h,days=all,hl=24h)**
- sensing pays in stale_in_house: accuracy given sensed 0.955 (n=3073) vs answered from memory 0.673: **held** (the policy chose which questions to sense, so this is the policy's own split, not a controlled contrast)
- came_back addressable by graded beliefs, passive accuracy new 0.892 (n=1450) vs old 0.000: **held**
- truly_out near-worthless per single sense: first-sense hit rate 0.000 (n=1024): **held**; reachable by passive answering: memory accuracy new 0.000 (n=3578) vs old 0.220: **did not hold**

