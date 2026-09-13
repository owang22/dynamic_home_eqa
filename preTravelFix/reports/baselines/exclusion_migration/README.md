# Exclusion-veto migration: paired replay

Generated 2026-09-08T01:40:03 at commit `ff83c0ba40f5` (dirty tree) by `python -m baselines.exclusion_migration_replay`. 20 seed-0 fleet banks, bank budget, seed 0; beliefs: the frozen panel and PerpetuaStar; policies: NeverSense and SequentialSearch. `old` = the pre-migration hard permanent veto (uniform redistribution, no floor; the `legacy_exclusion_veto` flag); `new` = the floor-mix plus decaying-suppression pipeline. Age bins and regimes come from the bank data (module docstring), never from either rule.

## Headline accuracy

| belief | policy | n | acc_old | acc_new | delta |
|---|---|---|---|---|---|
| LastObservation | NeverSense | 45000 | 0.592 | 0.6184 | 0.0264 |
| LastObservation | SequentialSearch | 45000 | 0.6508 | 0.6712 | 0.0204 |
| MostFrequentLocation(hl=24h) | NeverSense | 45000 | 0.5856 | 0.622 | 0.0364 |
| MostFrequentLocation(hl=24h) | SequentialSearch | 45000 | 0.6355 | 0.6734 | 0.0378 |
| TimetableLookup(bin=1h,days=all,hl=24h) | NeverSense | 45000 | 0.5306 | 0.5604 | 0.0298 |
| TimetableLookup(bin=1h,days=all,hl=24h) | SequentialSearch | 45000 | 0.5783 | 0.598 | 0.0198 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | NeverSense | 45000 | 0.5616 | 0.5616 | 0.0 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | SequentialSearch | 45000 | 0.6286 | 0.6286 | 0.0 |

## By age of the last ambient sighting

| belief | policy | age_bin | n | acc_old | acc_new | delta |
|---|---|---|---|---|---|---|
| LastObservation | NeverSense | 0-6h | 11079 | 0.8335 | 0.8335 | 0.0 |
| LastObservation | NeverSense | 6-24h | 23713 | 0.6293 | 0.6273 | -0.002 |
| LastObservation | NeverSense | 24-72h | 8441 | 0.2548 | 0.3658 | 0.111 |
| LastObservation | NeverSense | 72h+ | 1767 | 0.1885 | 0.3571 | 0.1686 |
| LastObservation | SequentialSearch | 0-6h | 11079 | 0.8389 | 0.8365 | -0.0023 |
| LastObservation | SequentialSearch | 6-24h | 23713 | 0.6782 | 0.6849 | 0.0067 |
| LastObservation | SequentialSearch | 24-72h | 8441 | 0.3956 | 0.4668 | 0.0712 |
| LastObservation | SequentialSearch | 72h+ | 1767 | 0.3243 | 0.4284 | 0.1041 |
| MostFrequentLocation(hl=24h) | NeverSense | 0-6h | 11079 | 0.8167 | 0.8167 | 0.0 |
| MostFrequentLocation(hl=24h) | NeverSense | 6-24h | 23713 | 0.6254 | 0.6271 | 0.0017 |
| MostFrequentLocation(hl=24h) | NeverSense | 24-72h | 8441 | 0.2545 | 0.4046 | 0.1501 |
| MostFrequentLocation(hl=24h) | NeverSense | 72h+ | 1767 | 0.1856 | 0.3724 | 0.1868 |
| MostFrequentLocation(hl=24h) | SequentialSearch | 0-6h | 11079 | 0.78 | 0.7814 | 0.0014 |
| MostFrequentLocation(hl=24h) | SequentialSearch | 6-24h | 23713 | 0.6728 | 0.6946 | 0.0218 |
| MostFrequentLocation(hl=24h) | SequentialSearch | 24-72h | 8441 | 0.4053 | 0.5155 | 0.1102 |
| MostFrequentLocation(hl=24h) | SequentialSearch | 72h+ | 1767 | 0.3299 | 0.4652 | 0.1353 |
| TimetableLookup(bin=1h,days=all,hl=24h) | NeverSense | 0-6h | 11079 | 0.7282 | 0.7192 | -0.009 |
| TimetableLookup(bin=1h,days=all,hl=24h) | NeverSense | 6-24h | 23713 | 0.5648 | 0.5619 | -0.0029 |
| TimetableLookup(bin=1h,days=all,hl=24h) | NeverSense | 24-72h | 8441 | 0.2504 | 0.3889 | 0.1385 |
| TimetableLookup(bin=1h,days=all,hl=24h) | NeverSense | 72h+ | 1767 | 0.1709 | 0.3628 | 0.1919 |
| TimetableLookup(bin=1h,days=all,hl=24h) | SequentialSearch | 0-6h | 11079 | 0.7129 | 0.7002 | -0.0127 |
| TimetableLookup(bin=1h,days=all,hl=24h) | SequentialSearch | 6-24h | 23713 | 0.6063 | 0.6079 | 0.0016 |
| TimetableLookup(bin=1h,days=all,hl=24h) | SequentialSearch | 24-72h | 8441 | 0.3763 | 0.4698 | 0.0936 |
| TimetableLookup(bin=1h,days=all,hl=24h) | SequentialSearch | 72h+ | 1767 | 0.3237 | 0.4375 | 0.1138 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | NeverSense | 0-6h | 11079 | 0.7918 | 0.7918 | 0.0 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | NeverSense | 6-24h | 23713 | 0.5532 | 0.5532 | 0.0 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | NeverSense | 24-72h | 8441 | 0.3394 | 0.3394 | 0.0 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | NeverSense | 72h+ | 1767 | 0.2926 | 0.2926 | 0.0 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | SequentialSearch | 0-6h | 11079 | 0.7717 | 0.7717 | 0.0 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | SequentialSearch | 6-24h | 23713 | 0.6444 | 0.6444 | 0.0 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | SequentialSearch | 24-72h | 8441 | 0.4515 | 0.4515 | 0.0 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | SequentialSearch | 72h+ | 1767 | 0.3667 | 0.3667 | 0.0 |

## By regime (from data)

truly_out = truth OUT_OF_HOUSE at t_query; came_back = truth equals the last-seen receptacle and an ambient visit saw that receptacle empty of the object after the last sighting; stale_in_house = the rest.

| belief | policy | regime | n | acc_old | acc_new | delta |
|---|---|---|---|---|---|---|
| LastObservation | NeverSense | truly_out | 6195 | 0.205 | 0.0006 | -0.2044 |
| LastObservation | NeverSense | came_back | 2633 | 0.0 | 1.0 | 1.0 |
| LastObservation | NeverSense | stale_in_house | 36172 | 0.7014 | 0.6964 | -0.0049 |
| LastObservation | SequentialSearch | truly_out | 6195 | 0.2575 | 0.019 | -0.2384 |
| LastObservation | SequentialSearch | came_back | 2633 | 0.2298 | 0.7406 | 0.5108 |
| LastObservation | SequentialSearch | stale_in_house | 36172 | 0.7488 | 0.7779 | 0.029 |
| MostFrequentLocation(hl=24h) | NeverSense | truly_out | 6195 | 0.205 | 0.0005 | -0.2045 |
| MostFrequentLocation(hl=24h) | NeverSense | came_back | 2633 | 0.0 | 0.9544 | 0.9544 |
| MostFrequentLocation(hl=24h) | NeverSense | stale_in_house | 36172 | 0.6935 | 0.7043 | 0.0108 |
| MostFrequentLocation(hl=24h) | SequentialSearch | truly_out | 6195 | 0.2512 | 0.0205 | -0.2307 |
| MostFrequentLocation(hl=24h) | SequentialSearch | came_back | 2633 | 0.2541 | 0.8287 | 0.5746 |
| MostFrequentLocation(hl=24h) | SequentialSearch | stale_in_house | 36172 | 0.7291 | 0.7739 | 0.0447 |
| TimetableLookup(bin=1h,days=all,hl=24h) | NeverSense | truly_out | 6195 | 0.21 | 0.0002 | -0.2098 |
| TimetableLookup(bin=1h,days=all,hl=24h) | NeverSense | came_back | 2633 | 0.0 | 0.8845 | 0.8845 |
| TimetableLookup(bin=1h,days=all,hl=24h) | NeverSense | stale_in_house | 36172 | 0.6242 | 0.6327 | 0.0086 |
| TimetableLookup(bin=1h,days=all,hl=24h) | SequentialSearch | truly_out | 6195 | 0.245 | 0.0153 | -0.2297 |
| TimetableLookup(bin=1h,days=all,hl=24h) | SequentialSearch | came_back | 2633 | 0.2484 | 0.7953 | 0.5469 |
| TimetableLookup(bin=1h,days=all,hl=24h) | SequentialSearch | stale_in_house | 36172 | 0.6594 | 0.6835 | 0.0241 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | NeverSense | truly_out | 6195 | 0.0 | 0.0 | 0.0 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | NeverSense | came_back | 2633 | 0.6335 | 0.6335 | 0.0 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | NeverSense | stale_in_house | 36172 | 0.6525 | 0.6525 | 0.0 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | SequentialSearch | truly_out | 6195 | 0.0 | 0.0 | 0.0 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | SequentialSearch | came_back | 2633 | 0.6521 | 0.6521 | 0.0 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | SequentialSearch | stale_in_house | 36172 | 0.7346 | 0.7346 | 0.0 |

## OUT_OF_HOUSE answers: fired / correct

| belief | policy | age_bin | n | truth_out | fired_old | correct_old | fired_over_truth_old | fired_new | correct_new | fired_over_truth_new |
|---|---|---|---|---|---|---|---|---|---|---|
| LastObservation | NeverSense | 0-6h | 11079 | 562 | 0 | 0 | 0.0 | 0 | 0 | 0.0 |
| LastObservation | NeverSense | 6-24h | 23713 | 3158 | 264 | 103 | 0.084 | 1 | 1 | 0.0 |
| LastObservation | NeverSense | 24-72h | 8441 | 1929 | 3234 | 879 | 1.677 | 7 | 3 | 0.004 |
| LastObservation | NeverSense | 72h+ | 1767 | 546 | 897 | 288 | 1.643 | 0 | 0 | 0.0 |
| LastObservation | NeverSense | all | 45000 | 6195 | 4395 | 1270 | 0.709 | 8 | 4 | 0.001 |
| LastObservation | SequentialSearch | 0-6h | 11079 | 562 | 44 | 39 | 0.078 | 14 | 10 | 0.025 |
| LastObservation | SequentialSearch | 6-24h | 23713 | 3158 | 1279 | 511 | 0.405 | 104 | 64 | 0.033 |
| LastObservation | SequentialSearch | 24-72h | 8441 | 1929 | 3081 | 825 | 1.597 | 67 | 38 | 0.035 |
| LastObservation | SequentialSearch | 72h+ | 1767 | 546 | 780 | 220 | 1.429 | 12 | 6 | 0.022 |
| LastObservation | SequentialSearch | all | 45000 | 6195 | 5184 | 1595 | 0.837 | 197 | 118 | 0.032 |
| MostFrequentLocation(hl=24h) | NeverSense | 0-6h | 11079 | 562 | 0 | 0 | 0.0 | 0 | 0 | 0.0 |
| MostFrequentLocation(hl=24h) | NeverSense | 6-24h | 23713 | 3158 | 257 | 99 | 0.081 | 0 | 0 | 0.0 |
| MostFrequentLocation(hl=24h) | NeverSense | 24-72h | 8441 | 1929 | 3268 | 886 | 1.694 | 3 | 3 | 0.002 |
| MostFrequentLocation(hl=24h) | NeverSense | 72h+ | 1767 | 546 | 914 | 285 | 1.674 | 0 | 0 | 0.0 |
| MostFrequentLocation(hl=24h) | NeverSense | all | 45000 | 6195 | 4439 | 1270 | 0.717 | 3 | 3 | 0.0 |
| MostFrequentLocation(hl=24h) | SequentialSearch | 0-6h | 11079 | 562 | 40 | 36 | 0.071 | 16 | 14 | 0.028 |
| MostFrequentLocation(hl=24h) | SequentialSearch | 6-24h | 23713 | 3158 | 1203 | 482 | 0.381 | 84 | 64 | 0.027 |
| MostFrequentLocation(hl=24h) | SequentialSearch | 24-72h | 8441 | 1929 | 2947 | 813 | 1.528 | 59 | 41 | 0.031 |
| MostFrequentLocation(hl=24h) | SequentialSearch | 72h+ | 1767 | 546 | 773 | 225 | 1.416 | 11 | 8 | 0.02 |
| MostFrequentLocation(hl=24h) | SequentialSearch | all | 45000 | 6195 | 4963 | 1556 | 0.801 | 170 | 127 | 0.027 |
| TimetableLookup(bin=1h,days=all,hl=24h) | NeverSense | 0-6h | 11079 | 562 | 41 | 3 | 0.073 | 0 | 0 | 0.0 |
| TimetableLookup(bin=1h,days=all,hl=24h) | NeverSense | 6-24h | 23713 | 3158 | 608 | 131 | 0.193 | 0 | 0 | 0.0 |
| TimetableLookup(bin=1h,days=all,hl=24h) | NeverSense | 24-72h | 8441 | 1929 | 3338 | 910 | 1.73 | 3 | 1 | 0.002 |
| TimetableLookup(bin=1h,days=all,hl=24h) | NeverSense | 72h+ | 1767 | 546 | 872 | 257 | 1.597 | 0 | 0 | 0.0 |
| TimetableLookup(bin=1h,days=all,hl=24h) | NeverSense | all | 45000 | 6195 | 4859 | 1301 | 0.784 | 3 | 1 | 0.0 |
| TimetableLookup(bin=1h,days=all,hl=24h) | SequentialSearch | 0-6h | 11079 | 562 | 74 | 39 | 0.132 | 16 | 9 | 0.028 |
| TimetableLookup(bin=1h,days=all,hl=24h) | SequentialSearch | 6-24h | 23713 | 3158 | 1551 | 493 | 0.491 | 92 | 51 | 0.029 |
| TimetableLookup(bin=1h,days=all,hl=24h) | SequentialSearch | 24-72h | 8441 | 1929 | 2887 | 783 | 1.497 | 57 | 29 | 0.03 |
| TimetableLookup(bin=1h,days=all,hl=24h) | SequentialSearch | 72h+ | 1767 | 546 | 738 | 203 | 1.352 | 9 | 6 | 0.016 |
| TimetableLookup(bin=1h,days=all,hl=24h) | SequentialSearch | all | 45000 | 6195 | 5250 | 1518 | 0.847 | 174 | 95 | 0.028 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | NeverSense | 0-6h | 11079 | 562 | 0 | 0 | 0.0 | 0 | 0 | 0.0 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | NeverSense | 6-24h | 23713 | 3158 | 0 | 0 | 0.0 | 0 | 0 | 0.0 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | NeverSense | 24-72h | 8441 | 1929 | 0 | 0 | 0.0 | 0 | 0 | 0.0 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | NeverSense | 72h+ | 1767 | 546 | 0 | 0 | 0.0 | 0 | 0 | 0.0 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | NeverSense | all | 45000 | 6195 | 0 | 0 | 0.0 | 0 | 0 | 0.0 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | SequentialSearch | 0-6h | 11079 | 562 | 0 | 0 | 0.0 | 0 | 0 | 0.0 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | SequentialSearch | 6-24h | 23713 | 3158 | 0 | 0 | 0.0 | 0 | 0 | 0.0 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | SequentialSearch | 24-72h | 8441 | 1929 | 0 | 0 | 0.0 | 0 | 0 | 0.0 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | SequentialSearch | 72h+ | 1767 | 546 | 0 | 0 | 0.0 | 0 | 0 | 0.0 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | SequentialSearch | all | 45000 | 6195 | 0 | 0 | 0.0 | 0 | 0 | 0.0 |

## Expected signature, and what held

- PerpetuaStar: identical under both semantics by construction (negatives enter its own filters; the base rule never applied to it). Serves as the control.
- OUT_OF_HOUSE over-firing shrinks toward the truth rate at ages of a day and more, LastObservation passive: fired/truth 1.67 old -> 0.00 new (4131 -> 7 answers against 2475 true): **did not hold** (it shrank past the truth rate: passive OUT_OF_HOUSE answers all but vanish; see the pushback recorded in STATUS).
- OUT_OF_HOUSE over-firing shrinks toward the truth rate at ages of a day and more, MostFrequentLocation passive: fired/truth 1.69 old -> 0.00 new (4182 -> 3 answers against 2475 true): **did not hold** (it shrank past the truth rate: passive OUT_OF_HOUSE answers all but vanish; see the pushback recorded in STATUS).
- OUT_OF_HOUSE over-firing shrinks toward the truth rate at ages of a day and more, TimetableLookup passive: fired/truth 1.70 old -> 0.00 new (4210 -> 3 answers against 2475 true): **did not hold** (it shrank past the truth rate: passive OUT_OF_HOUSE answers all but vanish; see the pushback recorded in STATUS).
- came_back accuracy rises for graded models, MostFrequentLocation passive: 0.0 -> 0.9544 (n=2633): **held**
- came_back accuracy rises for graded models, TimetableLookup passive: 0.0 -> 0.8845 (n=2633): **held**
- truly_out passive accuracy may dip where the veto was subsidizing it, LastObservation: 0.205 -> 0.0006 (n=6195): dipped
- truly_out passive accuracy may dip where the veto was subsidizing it, MostFrequentLocation: 0.205 -> 0.0005 (n=6195): dipped
- truly_out passive accuracy may dip where the veto was subsidizing it, TimetableLookup: 0.21 -> 0.0002 (n=6195): dipped
- search-policy accuracy holds or rises, LastObservation + SequentialSearch: 0.6508 -> 0.6712: **held**
- search-policy accuracy holds or rises, MostFrequentLocation + SequentialSearch: 0.6355 -> 0.6734: **held**
- search-policy accuracy holds or rises, TimetableLookup + SequentialSearch: 0.5783 -> 0.598: **held**

Bank hashes and settings: `provenance.json`.
