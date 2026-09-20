# Classical agents, 20 households, 4 patrol densities, look off / voi / top

20 households (hh_s0, hh_s1, hh_s10, hh_s11, hh_s12, hh_s13, hh_s14, hh_s15, hh_s16, hh_s17, hh_s18, hh_s19, hh_s2, hh_s3, hh_s4, hh_s5, hh_s6, hh_s7, hh_s8, hh_s9), 10 agents, patrol every [1, 2, 4, 8] h, look on/off = ['off', 'top', 'voi']. 537600 agent-question records. Shift days per household: hh_s0: [1, 2, 4, 5]; hh_s1: [3, 4, 5]; hh_s10: [4, 5]; hh_s11: [3, 4, 5]; hh_s12: [4, 5, 7]; hh_s13: [4, 5]; hh_s14: [2, 4, 5]; hh_s15: [1, 3, 4, 5]; hh_s16: [4, 5]; hh_s17: [4, 5, 6]; hh_s18: [4, 5]; hh_s19: [4, 5]; hh_s2: [4, 5, 7]; hh_s3: [4, 5]; hh_s4: [4, 5, 6, 7]; hh_s5: [2, 4, 5]; hh_s6: [4, 5]; hh_s7: [4, 5]; hh_s8: [1, 3, 4, 5, 7]; hh_s9: [3, 4, 5, 6].

Records per household: hh_s0 26880, hh_s1 26880, hh_s10 26880, hh_s11 26880, hh_s12 26880, hh_s13 26880, hh_s14 26880, hh_s15 26880, hh_s16 26880, hh_s17 26880, hh_s18 26880, hh_s19 26880, hh_s2 26880, hh_s3 26880, hh_s4 26880, hh_s5 26880, hh_s6 26880, hh_s7 26880, hh_s8 26880, hh_s9 26880

## 1. Accuracy per day per agent (no abstaining; shift days marked *)

### patrol every 1 h, look off

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 83% | 84% | 79% | 82% | 86% | 77% | 76% | 81% | 82% | 80% | 90% | 0% | 2% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 82% | 84% | 84% | 92% | 92% | 82% | 84% | 86% | 89% | 83% | 95% | 4% | 0% |
| LastObservation | 83% | 84% | 84% | 91% | 92% | 82% | 84% | 86% | 89% | 83% | 96% | 0% | 2% |
| Markov1(a=1,cut=24h,hl=24h) | 86% | 90% | 89% | 92% | 92% | 88% | 89% | 90% | 92% | 88% | 95% | 41% | 45% |
| MostFrequentLocation | 84% | 85% | 84% | 91% | 92% | 82% | 84% | 86% | 89% | 83% | 95% | 5% | 3% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 84% | 85% | 84% | 92% | 92% | 82% | 85% | 86% | 90% | 84% | 96% | 12% | 5% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 82% | 83% | 80% | 87% | 87% | 78% | 80% | 83% | 86% | 80% | 92% | 0% | 0% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 82% | 84% | 81% | 88% | 90% | 80% | 81% | 84% | 87% | 81% | 93% | 0% | 0% |
| SmoothedRecency(hl=6h,freq=24h) | 82% | 84% | 84% | 91% | 92% | 82% | 84% | 86% | 89% | 83% | 96% | 3% | 1% |
| TimetableLookup(bin=1h,days=all) | 84% | 85% | 86% | 92% | 92% | 87% | 90% | 88% | 91% | 86% | 95% | 7% | 28% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 2891 | 71% | 1589 | 99% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 2891 | 78% | 1589 | 100% |
| LastObservation | 2891 | 78% | 1589 | 100% |
| Markov1(a=1,cut=24h,hl=24h) | 2891 | 84% | 1589 | 100% |
| MostFrequentLocation | 2891 | 78% | 1589 | 100% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 2891 | 79% | 1589 | 100% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 2891 | 73% | 1589 | 99% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 2891 | 75% | 1589 | 100% |
| SmoothedRecency(hl=6h,freq=24h) | 2891 | 78% | 1589 | 100% |
| TimetableLookup(bin=1h,days=all) | 2891 | 81% | 1589 | 100% |

Questions by truth type: on_person 75, out_of_house 390, spot 4015
(* every household shifts that day; ° some households do)

### patrol every 1 h, look top

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 95% | 95% | 94% | 95% | 97% | 88% | 90% | 93% | 95% | 92% | 98% | 23% | 57% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 90% | 91% | 91% | 97% | 98% | 93% | 91% | 93% | 95% | 91% | 99% | 19% | 43% |
| LastObservation | 92% | 92% | 94% | 97% | 97% | 92% | 92% | 94% | 96% | 93% | 99% | 35% | 57% |
| Markov1(a=1,cut=24h,hl=24h) | 91% | 90% | 91% | 98% | 98% | 92% | 92% | 93% | 96% | 91% | 99% | 65% | 41% |
| MostFrequentLocation | 92% | 93% | 92% | 97% | 98% | 90% | 91% | 93% | 96% | 92% | 99% | 32% | 46% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 94% | 93% | 91% | 97% | 98% | 91% | 90% | 94% | 96% | 92% | 99% | 31% | 49% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 85% | 87% | 86% | 95% | 95% | 84% | 86% | 88% | 93% | 85% | 99% | 0% | 0% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 86% | 87% | 86% | 95% | 96% | 85% | 86% | 89% | 93% | 85% | 99% | 0% | 0% |
| SmoothedRecency(hl=6h,freq=24h) | 91% | 90% | 91% | 97% | 98% | 92% | 91% | 93% | 95% | 91% | 99% | 37% | 39% |
| TimetableLookup(bin=1h,days=all) | 92% | 92% | 93% | 97% | 98% | 93% | 93% | 94% | 96% | 92% | 99% | 39% | 53% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 2891 | 90% | 1589 | 100% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 2891 | 89% | 1589 | 100% |
| LastObservation | 2891 | 91% | 1589 | 100% |
| Markov1(a=1,cut=24h,hl=24h) | 2891 | 89% | 1589 | 100% |
| MostFrequentLocation | 2891 | 90% | 1589 | 100% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 2891 | 90% | 1589 | 100% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 2891 | 82% | 1589 | 100% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 2891 | 82% | 1589 | 100% |
| SmoothedRecency(hl=6h,freq=24h) | 2891 | 89% | 1589 | 100% |
| TimetableLookup(bin=1h,days=all) | 2891 | 91% | 1589 | 100% |

Questions by truth type: on_person 75, out_of_house 390, spot 4015
(* every household shifts that day; ° some households do)

### patrol every 1 h, look voi

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 94% | 93% | 92% | 95% | 95% | 89% | 90% | 93% | 94% | 91% | 98% | 39% | 49% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 91% | 92% | 91% | 97% | 97% | 89% | 90% | 92% | 95% | 90% | 99% | 21% | 33% |
| LastObservation | 93% | 92% | 92% | 97% | 97% | 92% | 92% | 94% | 96% | 92% | 98% | 48% | 55% |
| Markov1(a=1,cut=24h,hl=24h) | 89% | 91% | 94% | 97% | 97% | 93% | 92% | 93% | 96% | 92% | 98% | 67% | 47% |
| MostFrequentLocation | 93% | 93% | 92% | 97% | 98% | 92% | 93% | 94% | 96% | 92% | 99% | 45% | 48% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 94% | 91% | 92% | 97% | 97% | 92% | 90% | 93% | 95% | 92% | 99% | 35% | 47% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 85% | 87% | 85% | 95% | 96% | 85% | 86% | 88% | 93% | 85% | 98% | 0% | 0% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 85% | 87% | 85% | 95% | 96% | 85% | 86% | 88% | 93% | 85% | 99% | 0% | 0% |
| SmoothedRecency(hl=6h,freq=24h) | 93% | 92% | 91% | 97% | 98% | 90% | 90% | 93% | 96% | 91% | 99% | 28% | 43% |
| TimetableLookup(bin=1h,days=all) | 91% | 91% | 93% | 97% | 97% | 91% | 92% | 93% | 96% | 91% | 99% | 39% | 47% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 2891 | 89% | 1589 | 100% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 2891 | 88% | 1589 | 100% |
| LastObservation | 2891 | 90% | 1589 | 100% |
| Markov1(a=1,cut=24h,hl=24h) | 2891 | 90% | 1589 | 100% |
| MostFrequentLocation | 2891 | 91% | 1589 | 100% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 2891 | 89% | 1589 | 100% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 2891 | 82% | 1589 | 100% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 2891 | 82% | 1589 | 100% |
| SmoothedRecency(hl=6h,freq=24h) | 2891 | 89% | 1589 | 100% |
| TimetableLookup(bin=1h,days=all) | 2891 | 89% | 1589 | 100% |

Questions by truth type: on_person 75, out_of_house 390, spot 4015
(* every household shifts that day; ° some households do)

### patrol every 2 h, look off

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 81% | 82% | 76% | 78% | 83% | 74% | 72% | 78% | 80% | 77% | 87% | 0% | 1% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 81% | 82% | 82% | 88% | 90% | 79% | 82% | 84% | 87% | 81% | 93% | 3% | 0% |
| LastObservation | 81% | 82% | 82% | 88% | 90% | 80% | 82% | 84% | 87% | 81% | 93% | 0% | 1% |
| Markov1(a=1,cut=24h,hl=24h) | 85% | 86% | 88% | 89% | 90% | 84% | 86% | 87% | 89% | 86% | 92% | 41% | 42% |
| MostFrequentLocation | 82% | 82% | 82% | 87% | 89% | 80% | 81% | 83% | 86% | 81% | 93% | 4% | 2% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 83% | 84% | 83% | 88% | 90% | 80% | 82% | 84% | 88% | 82% | 93% | 7% | 6% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 81% | 82% | 80% | 85% | 84% | 75% | 78% | 81% | 83% | 79% | 90% | 0% | 0% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 81% | 82% | 79% | 87% | 86% | 76% | 79% | 82% | 85% | 79% | 91% | 0% | 0% |
| SmoothedRecency(hl=6h,freq=24h) | 81% | 82% | 82% | 88% | 90% | 80% | 82% | 84% | 87% | 81% | 93% | 4% | 1% |
| TimetableLookup(bin=1h,days=all) | 83% | 83% | 83% | 88% | 89% | 82% | 83% | 85% | 88% | 83% | 93% | 9% | 16% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 2891 | 67% | 1589 | 99% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 2891 | 74% | 1589 | 100% |
| LastObservation | 2891 | 75% | 1589 | 100% |
| Markov1(a=1,cut=24h,hl=24h) | 2891 | 80% | 1589 | 100% |
| MostFrequentLocation | 2891 | 74% | 1589 | 100% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 2891 | 75% | 1589 | 100% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 2891 | 71% | 1589 | 99% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 2891 | 71% | 1589 | 100% |
| SmoothedRecency(hl=6h,freq=24h) | 2891 | 75% | 1589 | 100% |
| TimetableLookup(bin=1h,days=all) | 2891 | 76% | 1589 | 100% |

Questions by truth type: on_person 75, out_of_house 390, spot 4015
(* every household shifts that day; ° some households do)

### patrol every 2 h, look top

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 95% | 95% | 93% | 95% | 96% | 88% | 90% | 93% | 94% | 92% | 98% | 19% | 57% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 90% | 91% | 90% | 96% | 97% | 92% | 92% | 92% | 95% | 90% | 99% | 15% | 38% |
| LastObservation | 93% | 92% | 93% | 96% | 97% | 91% | 92% | 94% | 95% | 92% | 98% | 32% | 56% |
| Markov1(a=1,cut=24h,hl=24h) | 90% | 90% | 90% | 97% | 98% | 92% | 91% | 93% | 95% | 91% | 98% | 65% | 39% |
| MostFrequentLocation | 92% | 94% | 92% | 96% | 98% | 90% | 90% | 93% | 95% | 91% | 99% | 36% | 45% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 93% | 93% | 92% | 96% | 98% | 90% | 91% | 93% | 96% | 92% | 99% | 36% | 47% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 86% | 87% | 85% | 94% | 95% | 84% | 85% | 88% | 92% | 85% | 98% | 0% | 0% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 86% | 87% | 85% | 94% | 96% | 85% | 85% | 88% | 93% | 85% | 99% | 0% | 0% |
| SmoothedRecency(hl=6h,freq=24h) | 90% | 90% | 91% | 96% | 97% | 91% | 90% | 92% | 95% | 91% | 99% | 32% | 36% |
| TimetableLookup(bin=1h,days=all) | 91% | 92% | 91% | 95% | 96% | 89% | 90% | 92% | 94% | 91% | 97% | 32% | 51% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 2891 | 89% | 1589 | 100% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 2891 | 88% | 1589 | 100% |
| LastObservation | 2891 | 90% | 1589 | 100% |
| Markov1(a=1,cut=24h,hl=24h) | 2891 | 88% | 1589 | 100% |
| MostFrequentLocation | 2891 | 89% | 1589 | 100% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 2891 | 90% | 1589 | 100% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 2891 | 81% | 1589 | 100% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 2891 | 82% | 1589 | 100% |
| SmoothedRecency(hl=6h,freq=24h) | 2891 | 88% | 1589 | 100% |
| TimetableLookup(bin=1h,days=all) | 2891 | 88% | 1589 | 99% |

Questions by truth type: on_person 75, out_of_house 390, spot 4015
(* every household shifts that day; ° some households do)

### patrol every 2 h, look voi

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 94% | 93% | 90% | 93% | 95% | 87% | 90% | 92% | 93% | 91% | 97% | 35% | 49% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 89% | 91% | 91% | 96% | 97% | 88% | 89% | 92% | 95% | 89% | 99% | 13% | 28% |
| LastObservation | 92% | 92% | 91% | 95% | 96% | 91% | 92% | 93% | 94% | 92% | 97% | 53% | 55% |
| Markov1(a=1,cut=24h,hl=24h) | 88% | 91% | 92% | 95% | 96% | 91% | 92% | 92% | 94% | 91% | 97% | 67% | 47% |
| MostFrequentLocation | 92% | 93% | 91% | 97% | 98% | 92% | 92% | 94% | 96% | 92% | 99% | 47% | 47% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 92% | 91% | 91% | 96% | 96% | 90% | 90% | 92% | 94% | 91% | 98% | 27% | 45% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 84% | 87% | 85% | 95% | 95% | 85% | 85% | 88% | 92% | 85% | 98% | 0% | 0% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 84% | 87% | 85% | 95% | 96% | 85% | 85% | 88% | 93% | 85% | 98% | 0% | 0% |
| SmoothedRecency(hl=6h,freq=24h) | 92% | 92% | 91% | 95% | 97% | 90% | 89% | 92% | 95% | 91% | 99% | 25% | 40% |
| TimetableLookup(bin=1h,days=all) | 90% | 90% | 91% | 94% | 95% | 88% | 88% | 91% | 93% | 89% | 96% | 51% | 47% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 2891 | 87% | 1589 | 100% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 2891 | 87% | 1589 | 100% |
| LastObservation | 2891 | 89% | 1589 | 100% |
| Markov1(a=1,cut=24h,hl=24h) | 2891 | 88% | 1589 | 100% |
| MostFrequentLocation | 2891 | 90% | 1589 | 100% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 2891 | 88% | 1589 | 100% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 2891 | 82% | 1589 | 100% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 2891 | 82% | 1589 | 100% |
| SmoothedRecency(hl=6h,freq=24h) | 2891 | 88% | 1589 | 100% |
| TimetableLookup(bin=1h,days=all) | 2891 | 86% | 1589 | 99% |

Questions by truth type: on_person 75, out_of_house 390, spot 4015
(* every household shifts that day; ° some households do)

### patrol every 4 h, look off

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 79% | 79% | 74% | 76% | 81% | 72% | 69% | 76% | 78% | 74% | 85% | 0% | 0% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 79% | 79% | 78% | 83% | 87% | 77% | 78% | 80% | 83% | 78% | 89% | 3% | 0% |
| LastObservation | 79% | 79% | 77% | 83% | 87% | 77% | 78% | 80% | 83% | 78% | 89% | 0% | 0% |
| Markov1(a=1,cut=24h,hl=24h) | 82% | 82% | 81% | 83% | 86% | 81% | 81% | 82% | 84% | 81% | 88% | 39% | 34% |
| MostFrequentLocation | 80% | 80% | 77% | 83% | 86% | 77% | 78% | 80% | 83% | 78% | 89% | 0% | 3% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 80% | 80% | 78% | 83% | 87% | 77% | 78% | 81% | 84% | 78% | 89% | 7% | 4% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 79% | 79% | 77% | 82% | 83% | 73% | 75% | 78% | 82% | 76% | 87% | 0% | 0% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 79% | 79% | 77% | 82% | 85% | 74% | 76% | 79% | 82% | 77% | 88% | 0% | 0% |
| SmoothedRecency(hl=6h,freq=24h) | 79% | 80% | 78% | 83% | 87% | 77% | 78% | 80% | 83% | 78% | 89% | 5% | 0% |
| TimetableLookup(bin=1h,days=all) | 80% | 79% | 78% | 83% | 85% | 77% | 78% | 80% | 83% | 78% | 88% | 1% | 9% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 2891 | 63% | 1589 | 99% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 2891 | 69% | 1589 | 100% |
| LastObservation | 2891 | 69% | 1589 | 100% |
| Markov1(a=1,cut=24h,hl=24h) | 2891 | 73% | 1589 | 100% |
| MostFrequentLocation | 2891 | 69% | 1589 | 100% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 2891 | 70% | 1589 | 100% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 2891 | 67% | 1589 | 99% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 2891 | 68% | 1589 | 100% |
| SmoothedRecency(hl=6h,freq=24h) | 2891 | 69% | 1589 | 100% |
| TimetableLookup(bin=1h,days=all) | 2891 | 69% | 1589 | 99% |

Questions by truth type: on_person 75, out_of_house 390, spot 4015
(* every household shifts that day; ° some households do)

### patrol every 4 h, look top

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 94% | 95% | 90% | 93% | 95% | 88% | 89% | 92% | 93% | 91% | 97% | 20% | 52% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 88% | 90% | 89% | 95% | 96% | 90% | 91% | 91% | 94% | 89% | 99% | 8% | 31% |
| LastObservation | 92% | 92% | 93% | 96% | 96% | 91% | 90% | 93% | 95% | 92% | 98% | 33% | 54% |
| Markov1(a=1,cut=24h,hl=24h) | 90% | 89% | 90% | 94% | 96% | 90% | 89% | 91% | 94% | 89% | 97% | 57% | 38% |
| MostFrequentLocation | 92% | 95% | 91% | 96% | 96% | 89% | 90% | 92% | 95% | 91% | 99% | 31% | 41% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 93% | 93% | 90% | 96% | 97% | 89% | 90% | 92% | 95% | 91% | 98% | 23% | 44% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 85% | 87% | 85% | 94% | 94% | 84% | 85% | 88% | 92% | 85% | 98% | 0% | 0% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 86% | 87% | 85% | 95% | 95% | 84% | 85% | 88% | 92% | 85% | 98% | 0% | 0% |
| SmoothedRecency(hl=6h,freq=24h) | 90% | 90% | 91% | 96% | 97% | 90% | 90% | 92% | 94% | 90% | 99% | 31% | 35% |
| TimetableLookup(bin=1h,days=all) | 91% | 90% | 89% | 92% | 92% | 88% | 88% | 90% | 92% | 89% | 95% | 28% | 47% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 2891 | 88% | 1589 | 100% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 2891 | 87% | 1589 | 100% |
| LastObservation | 2891 | 89% | 1589 | 100% |
| Markov1(a=1,cut=24h,hl=24h) | 2891 | 86% | 1589 | 100% |
| MostFrequentLocation | 2891 | 88% | 1589 | 100% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 2891 | 88% | 1589 | 100% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 2891 | 81% | 1589 | 100% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 2891 | 82% | 1589 | 100% |
| SmoothedRecency(hl=6h,freq=24h) | 2891 | 88% | 1589 | 100% |
| TimetableLookup(bin=1h,days=all) | 2891 | 85% | 1589 | 99% |

Questions by truth type: on_person 75, out_of_house 390, spot 4015
(* every household shifts that day; ° some households do)

### patrol every 4 h, look voi

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 94% | 92% | 89% | 92% | 92% | 83% | 86% | 90% | 91% | 89% | 95% | 35% | 46% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 86% | 91% | 89% | 96% | 97% | 89% | 89% | 91% | 94% | 88% | 99% | 9% | 24% |
| LastObservation | 92% | 91% | 89% | 92% | 93% | 90% | 90% | 91% | 92% | 90% | 96% | 41% | 53% |
| Markov1(a=1,cut=24h,hl=24h) | 86% | 89% | 88% | 92% | 92% | 90% | 89% | 89% | 91% | 88% | 95% | 59% | 42% |
| MostFrequentLocation | 91% | 91% | 92% | 96% | 97% | 91% | 91% | 93% | 95% | 91% | 99% | 35% | 44% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 92% | 91% | 90% | 94% | 95% | 89% | 89% | 91% | 93% | 90% | 97% | 24% | 43% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 84% | 87% | 84% | 94% | 95% | 84% | 85% | 88% | 92% | 84% | 98% | 0% | 0% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 84% | 87% | 85% | 94% | 96% | 84% | 86% | 88% | 93% | 85% | 98% | 0% | 0% |
| SmoothedRecency(hl=6h,freq=24h) | 90% | 91% | 90% | 96% | 96% | 89% | 89% | 92% | 94% | 90% | 98% | 23% | 36% |
| TimetableLookup(bin=1h,days=all) | 91% | 88% | 88% | 90% | 87% | 84% | 84% | 87% | 88% | 87% | 92% | 44% | 44% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 2891 | 85% | 1589 | 99% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 2891 | 86% | 1589 | 100% |
| LastObservation | 2891 | 86% | 1589 | 100% |
| Markov1(a=1,cut=24h,hl=24h) | 2891 | 84% | 1589 | 100% |
| MostFrequentLocation | 2891 | 89% | 1589 | 100% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 2891 | 87% | 1589 | 100% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 2891 | 81% | 1589 | 100% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 2891 | 81% | 1589 | 100% |
| SmoothedRecency(hl=6h,freq=24h) | 2891 | 87% | 1589 | 100% |
| TimetableLookup(bin=1h,days=all) | 2891 | 81% | 1589 | 99% |

Questions by truth type: on_person 75, out_of_house 390, spot 4015
(* every household shifts that day; ° some households do)

### patrol every 8 h, look off

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 76% | 77% | 72% | 75% | 77% | 69% | 70% | 74% | 76% | 72% | 82% | 0% | 0% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 76% | 77% | 76% | 80% | 83% | 74% | 76% | 77% | 80% | 75% | 86% | 1% | 0% |
| LastObservation | 76% | 77% | 76% | 80% | 83% | 74% | 76% | 77% | 80% | 75% | 86% | 0% | 0% |
| Markov1(a=1,cut=24h,hl=24h) | 76% | 78% | 75% | 79% | 82% | 75% | 77% | 77% | 80% | 76% | 83% | 37% | 25% |
| MostFrequentLocation | 76% | 77% | 75% | 79% | 82% | 73% | 75% | 77% | 80% | 75% | 86% | 3% | 2% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 77% | 78% | 77% | 80% | 83% | 75% | 76% | 78% | 81% | 76% | 86% | 9% | 7% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 76% | 77% | 75% | 78% | 80% | 72% | 72% | 76% | 78% | 74% | 84% | 0% | 0% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 76% | 77% | 74% | 79% | 80% | 72% | 73% | 76% | 79% | 74% | 85% | 0% | 0% |
| SmoothedRecency(hl=6h,freq=24h) | 76% | 77% | 76% | 80% | 83% | 74% | 76% | 77% | 80% | 75% | 86% | 4% | 0% |
| TimetableLookup(bin=1h,days=all) | 76% | 77% | 75% | 80% | 81% | 73% | 74% | 77% | 79% | 74% | 85% | 3% | 7% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 2891 | 60% | 1589 | 98% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 2891 | 65% | 1589 | 100% |
| LastObservation | 2891 | 65% | 1589 | 100% |
| Markov1(a=1,cut=24h,hl=24h) | 2891 | 65% | 1589 | 100% |
| MostFrequentLocation | 2891 | 64% | 1589 | 100% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 2891 | 66% | 1589 | 100% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 2891 | 63% | 1589 | 99% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 2891 | 63% | 1589 | 100% |
| SmoothedRecency(hl=6h,freq=24h) | 2891 | 65% | 1589 | 100% |
| TimetableLookup(bin=1h,days=all) | 2891 | 64% | 1589 | 99% |

Questions by truth type: on_person 75, out_of_house 390, spot 4015
(* every household shifts that day; ° some households do)

### patrol every 8 h, look top

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 93% | 94% | 91% | 94% | 95% | 87% | 89% | 92% | 93% | 91% | 97% | 24% | 49% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 86% | 89% | 87% | 95% | 96% | 89% | 90% | 90% | 93% | 88% | 98% | 7% | 23% |
| LastObservation | 91% | 92% | 92% | 95% | 96% | 90% | 90% | 92% | 94% | 91% | 98% | 31% | 48% |
| Markov1(a=1,cut=24h,hl=24h) | 88% | 88% | 88% | 93% | 94% | 87% | 89% | 90% | 92% | 88% | 95% | 49% | 37% |
| MostFrequentLocation | 92% | 94% | 91% | 96% | 96% | 87% | 89% | 92% | 94% | 91% | 98% | 32% | 38% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 92% | 93% | 90% | 95% | 97% | 89% | 90% | 92% | 94% | 91% | 98% | 23% | 43% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 85% | 87% | 85% | 94% | 95% | 84% | 86% | 88% | 92% | 85% | 98% | 0% | 0% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 85% | 87% | 85% | 94% | 95% | 85% | 85% | 88% | 92% | 85% | 98% | 0% | 0% |
| SmoothedRecency(hl=6h,freq=24h) | 90% | 90% | 91% | 96% | 97% | 91% | 89% | 92% | 94% | 90% | 99% | 36% | 34% |
| TimetableLookup(bin=1h,days=all) | 89% | 89% | 88% | 91% | 89% | 85% | 87% | 88% | 90% | 87% | 94% | 29% | 43% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 2891 | 88% | 1589 | 99% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 2891 | 85% | 1589 | 100% |
| LastObservation | 2891 | 88% | 1589 | 100% |
| Markov1(a=1,cut=24h,hl=24h) | 2891 | 84% | 1589 | 100% |
| MostFrequentLocation | 2891 | 88% | 1589 | 100% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 2891 | 88% | 1589 | 100% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 2891 | 81% | 1589 | 100% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 2891 | 82% | 1589 | 100% |
| SmoothedRecency(hl=6h,freq=24h) | 2891 | 88% | 1589 | 100% |
| TimetableLookup(bin=1h,days=all) | 2891 | 83% | 1589 | 99% |

Questions by truth type: on_person 75, out_of_house 390, spot 4015
(* every household shifts that day; ° some households do)

### patrol every 8 h, look voi

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 92% | 90% | 87% | 89% | 90% | 80% | 82% | 87% | 89% | 86% | 93% | 25% | 43% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 83% | 88% | 89% | 95% | 96% | 88% | 89% | 90% | 94% | 87% | 98% | 5% | 19% |
| LastObservation | 89% | 89% | 88% | 91% | 91% | 87% | 87% | 89% | 90% | 88% | 94% | 41% | 50% |
| Markov1(a=1,cut=24h,hl=24h) | 84% | 86% | 85% | 89% | 89% | 87% | 86% | 87% | 89% | 86% | 92% | 49% | 42% |
| MostFrequentLocation | 90% | 90% | 91% | 95% | 96% | 90% | 91% | 92% | 95% | 90% | 98% | 40% | 44% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 89% | 90% | 89% | 93% | 94% | 87% | 87% | 90% | 92% | 88% | 96% | 19% | 38% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 82% | 87% | 84% | 94% | 95% | 85% | 85% | 87% | 92% | 84% | 97% | 0% | 0% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 82% | 87% | 84% | 94% | 95% | 85% | 85% | 87% | 92% | 84% | 97% | 0% | 0% |
| SmoothedRecency(hl=6h,freq=24h) | 88% | 89% | 90% | 95% | 95% | 89% | 87% | 90% | 93% | 88% | 97% | 17% | 30% |
| TimetableLookup(bin=1h,days=all) | 89% | 85% | 84% | 85% | 83% | 79% | 79% | 83% | 84% | 83% | 89% | 35% | 39% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 2891 | 81% | 1589 | 98% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 2891 | 84% | 1589 | 100% |
| LastObservation | 2891 | 83% | 1589 | 100% |
| Markov1(a=1,cut=24h,hl=24h) | 2891 | 80% | 1589 | 100% |
| MostFrequentLocation | 2891 | 88% | 1589 | 100% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 2891 | 84% | 1589 | 100% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 2891 | 80% | 1589 | 100% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 2891 | 80% | 1589 | 100% |
| SmoothedRecency(hl=6h,freq=24h) | 2891 | 85% | 1589 | 100% |
| TimetableLookup(bin=1h,days=all) | 2891 | 76% | 1589 | 98% |

Questions by truth type: on_person 75, out_of_house 390, spot 4015
(* every household shifts that day; ° some households do)

## 2. Accuracy vs patrol density (all days, no abstaining)

### look off

| agent | every 1 h | every 2 h | every 4 h | every 8 h |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 81% | 78% | 76% | 74% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 86% | 84% | 80% | 77% |
| LastObservation | 86% | 84% | 80% | 77% |
| Markov1(a=1,cut=24h,hl=24h) | 90% | 87% | 82% | 77% |
| MostFrequentLocation | 86% | 83% | 80% | 77% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 86% | 84% | 81% | 78% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 83% | 81% | 78% | 76% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 84% | 82% | 79% | 76% |
| SmoothedRecency(hl=6h,freq=24h) | 86% | 84% | 80% | 77% |
| TimetableLookup(bin=1h,days=all) | 88% | 85% | 80% | 77% |

### look top

| agent | every 1 h | every 2 h | every 4 h | every 8 h |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 93% | 93% | 92% | 92% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 93% | 92% | 91% | 90% |
| LastObservation | 94% | 94% | 93% | 92% |
| Markov1(a=1,cut=24h,hl=24h) | 93% | 93% | 91% | 90% |
| MostFrequentLocation | 93% | 93% | 92% | 92% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 94% | 93% | 92% | 92% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 88% | 88% | 88% | 88% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 89% | 88% | 88% | 88% |
| SmoothedRecency(hl=6h,freq=24h) | 93% | 92% | 92% | 92% |
| TimetableLookup(bin=1h,days=all) | 94% | 92% | 90% | 88% |

### look voi

| agent | every 1 h | every 2 h | every 4 h | every 8 h |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 93% | 92% | 90% | 87% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 92% | 92% | 91% | 90% |
| LastObservation | 94% | 93% | 91% | 89% |
| Markov1(a=1,cut=24h,hl=24h) | 93% | 92% | 89% | 87% |
| MostFrequentLocation | 94% | 94% | 93% | 92% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 93% | 92% | 91% | 90% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 88% | 88% | 88% | 87% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 88% | 88% | 88% | 87% |
| SmoothedRecency(hl=6h,freq=24h) | 93% | 92% | 92% | 90% |
| TimetableLookup(bin=1h,days=all) | 93% | 91% | 87% | 83% |

## 3. What the free look is worth (all densities pooled)

| agent | look off | look voi | look top | before-look answer (voi runs) | found by voi look | found by top look |
|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 77% | 90% | 93% | 79% | 55% | 87% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 82% | 91% | 92% | 84% | 57% | 87% |
| LastObservation | 82% | 92% | 93% | 84% | 50% | 88% |
| Markov1(a=1,cut=24h,hl=24h) | 84% | 90% | 92% | 87% | 50% | 87% |
| MostFrequentLocation | 82% | 93% | 93% | 83% | 57% | 87% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 82% | 92% | 93% | 85% | 53% | 88% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 79% | 88% | 88% | 82% | 50% | 88% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 80% | 88% | 88% | 83% | 50% | 88% |
| SmoothedRecency(hl=6h,freq=24h) | 82% | 92% | 92% | 84% | 53% | 88% |
| TimetableLookup(bin=1h,days=all) | 82% | 89% | 91% | 81% | 51% | 85% |

Look gain by confidence before the look (pooled over agents, look-on runs):

| top prob before look | n | acc before look | acc after look |
|---|---|---|---|
| [0.00, 0.40) | 25110 | 57% | 71% |
| [0.40, 0.60) | 21336 | 52% | 74% |
| [0.60, 0.80) | 26523 | 64% | 82% |
| [0.80, 0.95) | 70304 | 81% | 92% |
| [0.95, 1.01) | 215127 | 92% | 96% |

## 4. Abstain rate and answered-accuracy per day (look voi for classical agents, look on for LLM agents; all densities pooled)

### outright ABSTAIN answers only (LLM direct route)

| agent | Wed abstain / acc | Thu abstain / acc | Fri abstain / acc | Sat abstain / acc | Sun abstain / acc | Mon abstain / acc | Tue abstain / acc | shift abstain / acc | non-shift abstain / acc | mean score |
|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0% / 94% | 0% / 92% | 0% / 90% | 0% / 92% | 0% / 93% | 0% / 85% | 0% / 87% | 0% / 92% | 0% / 89% | +0.81 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0% / 87% | 0% / 90% | 0% / 90% | 0% / 96% | 0% / 97% | 0% / 89% | 0% / 89% | 0% / 95% | 0% / 89% | +0.82 |
| LastObservation | 0% / 92% | 0% / 91% | 0% / 90% | 0% / 94% | 0% / 94% | 0% / 90% | 0% / 90% | 0% / 93% | 0% / 91% | +0.83 |
| Markov1(a=1,cut=24h,hl=24h) | 0% / 87% | 0% / 89% | 0% / 90% | 0% / 93% | 0% / 94% | 0% / 90% | 0% / 90% | 0% / 92% | 0% / 89% | +0.81 |
| MostFrequentLocation | 0% / 91% | 0% / 92% | 0% / 91% | 0% / 96% | 0% / 97% | 0% / 91% | 0% / 92% | 0% / 95% | 0% / 91% | +0.86 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0% / 92% | 0% / 91% | 0% / 90% | 0% / 95% | 0% / 95% | 0% / 90% | 0% / 89% | 0% / 94% | 0% / 90% | +0.83 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 0% / 84% | 0% / 87% | 0% / 85% | 0% / 94% | 0% / 95% | 0% / 85% | 0% / 85% | 0% / 92% | 0% / 85% | +0.76 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 0% / 84% | 0% / 87% | 0% / 85% | 0% / 94% | 0% / 96% | 0% / 85% | 0% / 85% | 0% / 92% | 0% / 85% | +0.76 |
| SmoothedRecency(hl=6h,freq=24h) | 0% / 91% | 0% / 91% | 0% / 91% | 0% / 96% | 0% / 96% | 0% / 89% | 0% / 89% | 0% / 94% | 0% / 90% | +0.84 |
| TimetableLookup(bin=1h,days=all) | 0% / 90% | 0% / 89% | 0% / 89% | 0% / 91% | 0% / 91% | 0% / 85% | 0% / 86% | 0% / 90% | 0% / 87% | +0.77 |

### threshold 0.4 on the top probability / stated confidence, plus outright ABSTAIN answers

| agent | Wed abstain / acc | Thu abstain / acc | Fri abstain / acc | Sat abstain / acc | Sun abstain / acc | Mon abstain / acc | Tue abstain / acc | shift abstain / acc | non-shift abstain / acc | mean score |
|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 10% / 96% | 9% / 96% | 9% / 94% | 4% / 94% | 3% / 95% | 10% / 90% | 10% / 92% | 5% / 95% | 10% / 94% | +0.81 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 8% / 92% | 7% / 94% | 7% / 94% | 2% / 97% | 2% / 98% | 7% / 93% | 7% / 94% | 3% / 97% | 8% / 93% | +0.84 |
| LastObservation | 10% / 95% | 9% / 95% | 10% / 95% | 4% / 96% | 2% / 95% | 9% / 94% | 9% / 94% | 5% / 95% | 10% / 95% | +0.83 |
| Markov1(a=1,cut=24h,hl=24h) | 39% / 95% | 30% / 95% | 29% / 97% | 27% / 98% | 22% / 98% | 26% / 96% | 26% / 96% | 26% / 97% | 31% / 96% | +0.66 |
| MostFrequentLocation | 11% / 97% | 9% / 96% | 9% / 96% | 4% / 98% | 2% / 98% | 9% / 95% | 9% / 95% | 5% / 97% | 9% / 96% | +0.86 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 11% / 97% | 8% / 95% | 9% / 95% | 4% / 97% | 2% / 96% | 8% / 93% | 8% / 93% | 4% / 96% | 9% / 94% | +0.84 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 0% / 84% | 0% / 87% | 0% / 85% | 0% / 94% | 0% / 95% | 0% / 85% | 1% / 86% | 0% / 92% | 0% / 85% | +0.76 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 0% / 84% | 0% / 87% | 0% / 85% | 0% / 94% | 0% / 96% | 0% / 85% | 1% / 86% | 0% / 93% | 0% / 85% | +0.76 |
| SmoothedRecency(hl=6h,freq=24h) | 11% / 95% | 9% / 95% | 10% / 96% | 3% / 98% | 3% / 98% | 10% / 95% | 9% / 94% | 5% / 97% | 10% / 95% | +0.84 |
| TimetableLookup(bin=1h,days=all) | 13% / 95% | 14% / 95% | 14% / 96% | 11% / 98% | 10% / 96% | 15% / 94% | 16% / 94% | 11% / 96% | 15% / 95% | +0.79 |

### threshold 0.5 on the top probability / stated confidence, plus outright ABSTAIN answers

| agent | Wed abstain / acc | Thu abstain / acc | Fri abstain / acc | Sat abstain / acc | Sun abstain / acc | Mon abstain / acc | Tue abstain / acc | shift abstain / acc | non-shift abstain / acc | mean score |
|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 13% / 98% | 13% / 98% | 12% / 96% | 5% / 95% | 4% / 96% | 14% / 93% | 13% / 94% | 7% / 96% | 13% / 96% | +0.82 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 10% / 94% | 9% / 95% | 9% / 95% | 3% / 98% | 2% / 98% | 10% / 95% | 9% / 95% | 5% / 98% | 10% / 95% | +0.85 |
| LastObservation | 14% / 97% | 13% / 97% | 14% / 97% | 5% / 96% | 3% / 96% | 14% / 96% | 12% / 96% | 7% / 96% | 14% / 97% | +0.83 |
| Markov1(a=1,cut=24h,hl=24h) | 47% / 100% | 43% / 100% | 41% / 99% | 36% / 99% | 31% / 99% | 39% / 99% | 38% / 99% | 36% / 99% | 42% / 99% | +0.60 |
| MostFrequentLocation | 15% / 98% | 12% / 97% | 12% / 98% | 5% / 99% | 3% / 99% | 12% / 97% | 11% / 96% | 6% / 98% | 13% / 97% | +0.86 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 14% / 98% | 12% / 97% | 12% / 97% | 4% / 97% | 3% / 97% | 13% / 95% | 10% / 94% | 6% / 97% | 12% / 96% | +0.84 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 0% / 84% | 0% / 87% | 1% / 85% | 0% / 95% | 1% / 96% | 1% / 85% | 2% / 87% | 0% / 93% | 1% / 85% | +0.76 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 0% / 84% | 0% / 87% | 1% / 86% | 0% / 95% | 0% / 96% | 1% / 86% | 1% / 86% | 0% / 93% | 1% / 85% | +0.76 |
| SmoothedRecency(hl=6h,freq=24h) | 12% / 96% | 10% / 96% | 11% / 96% | 4% / 98% | 3% / 98% | 12% / 96% | 10% / 95% | 5% / 97% | 11% / 96% | +0.85 |
| TimetableLookup(bin=1h,days=all) | 21% / 98% | 22% / 97% | 22% / 97% | 15% / 98% | 15% / 97% | 24% / 97% | 22% / 96% | 17% / 97% | 22% / 97% | +0.76 |

### threshold 0.6 on the top probability / stated confidence, plus outright ABSTAIN answers

| agent | Wed abstain / acc | Thu abstain / acc | Fri abstain / acc | Sat abstain / acc | Sun abstain / acc | Mon abstain / acc | Tue abstain / acc | shift abstain / acc | non-shift abstain / acc | mean score |
|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 13% / 98% | 13% / 98% | 13% / 96% | 5% / 95% | 4% / 96% | 15% / 94% | 14% / 94% | 7% / 96% | 14% / 96% | +0.82 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 11% / 95% | 9% / 96% | 11% / 96% | 3% / 98% | 3% / 99% | 11% / 96% | 10% / 95% | 5% / 98% | 10% / 95% | +0.85 |
| LastObservation | 14% / 97% | 13% / 97% | 14% / 97% | 5% / 96% | 3% / 96% | 14% / 96% | 13% / 96% | 7% / 96% | 14% / 97% | +0.83 |
| Markov1(a=1,cut=24h,hl=24h) | 50% / 100% | 46% / 100% | 47% / 100% | 42% / 99% | 37% / 100% | 46% / 100% | 45% / 99% | 42% / 100% | 47% / 100% | +0.55 |
| MostFrequentLocation | 16% / 98% | 13% / 98% | 13% / 98% | 5% / 99% | 4% / 99% | 13% / 98% | 12% / 97% | 7% / 99% | 14% / 98% | +0.86 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 16% / 98% | 12% / 97% | 12% / 97% | 4% / 97% | 3% / 97% | 13% / 96% | 11% / 95% | 6% / 97% | 13% / 96% | +0.84 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 1% / 84% | 1% / 88% | 2% / 87% | 1% / 95% | 1% / 96% | 2% / 86% | 3% / 88% | 1% / 93% | 2% / 86% | +0.77 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 1% / 84% | 1% / 88% | 3% / 87% | 1% / 95% | 1% / 96% | 3% / 87% | 2% / 87% | 1% / 94% | 2% / 86% | +0.77 |
| SmoothedRecency(hl=6h,freq=24h) | 12% / 96% | 11% / 96% | 12% / 97% | 4% / 98% | 3% / 98% | 12% / 96% | 11% / 95% | 6% / 98% | 12% / 96% | +0.85 |
| TimetableLookup(bin=1h,days=all) | 26% / 99% | 27% / 98% | 28% / 98% | 22% / 98% | 21% / 98% | 29% / 98% | 28% / 97% | 23% / 98% | 28% / 98% | +0.71 |

## 6. Shift effect paired by household

For every household and agent: accuracy on the household's own shift days minus accuracy on its own non-shift days (`shift - non`), then the mean and the count of households where the difference is negative. Also aligned on each household's first major-event day (guests or illness, weekend days excluded): accuracy on the day before, the day, and the day after, mean over households that have such a day. Spot-only columns use in-house truths only, so the OUT_OF_HOUSE mix cannot drive the difference.

### look off

| agent | mean(shift - non) | households with a drop | mean(shift - non), spot only | drop, spot only | event day -1 / 0 / +1 | event day -1 / 0 / +1, spot only | households with an event day |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | +3.3 | 7/20 | -3.5 | 15/20 | 74% / 80% / 80% | 86% / 89% / 87% | 12 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | +6.1 | 4/20 | -0.9 | 12/20 | 78% / 83% / 85% | 90% / 92% / 92% | 12 |
| LastObservation | +6.0 | 4/20 | -1.0 | 13/20 | 78% / 82% / 85% | 90% / 92% / 92% | 12 |
| Markov1(a=1,cut=24h,hl=24h) | +3.7 | 4/20 | -0.7 | 10/20 | 81% / 86% / 87% | 89% / 90% / 90% | 12 |
| MostFrequentLocation | +5.4 | 4/20 | -1.5 | 14/20 | 77% / 83% / 85% | 90% / 92% / 92% | 12 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | +5.7 | 4/20 | -1.1 | 13/20 | 79% / 83% / 85% | 90% / 92% / 92% | 12 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | +4.8 | 4/20 | -2.2 | 13/20 | 76% / 82% / 82% | 88% / 91% / 90% | 12 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | +5.7 | 4/20 | -1.2 | 15/20 | 77% / 82% / 83% | 89% / 91% / 90% | 12 |
| SmoothedRecency(hl=6h,freq=24h) | +6.0 | 4/20 | -1.0 | 13/20 | 78% / 83% / 85% | 90% / 92% / 92% | 12 |
| TimetableLookup(bin=1h,days=all) | +5.0 | 4/20 | -1.3 | 13/20 | 79% / 84% / 86% | 90% / 91% / 92% | 12 |

### look top

| agent | mean(shift - non) | households with a drop | mean(shift - non), spot only | drop, spot only | event day -1 / 0 / +1 | event day -1 / 0 / +1, spot only | households with an event day |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | +2.6 | 5/20 | -0.5 | 11/20 | 91% / 93% / 94% | 97% / 98% / 99% | 12 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | +4.9 | 3/20 | -0.0 | 10/20 | 89% / 92% / 94% | 99% / 98% / 100% | 12 |
| LastObservation | +3.2 | 3/20 | +0.2 | 11/20 | 92% / 93% / 96% | 98% / 98% / 99% | 12 |
| Markov1(a=1,cut=24h,hl=24h) | +5.0 | 2/20 | +0.5 | 10/20 | 90% / 91% / 94% | 97% / 97% / 98% | 12 |
| MostFrequentLocation | +4.1 | 3/20 | -0.0 | 11/20 | 92% / 92% / 94% | 99% / 98% / 99% | 12 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | +4.0 | 3/20 | +0.1 | 9/20 | 92% / 92% / 95% | 99% / 98% / 99% | 12 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | +7.3 | 3/20 | -0.2 | 12/20 | 85% / 88% / 92% | 98% / 98% / 100% | 12 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | +7.6 | 3/20 | +0.0 | 8/20 | 85% / 88% / 91% | 99% / 98% / 99% | 12 |
| SmoothedRecency(hl=6h,freq=24h) | +4.5 | 3/20 | +0.0 | 10/20 | 89% / 92% / 93% | 99% / 98% / 99% | 12 |
| TimetableLookup(bin=1h,days=all) | +3.5 | 4/20 | -0.4 | 11/20 | 89% / 91% / 93% | 97% / 97% / 98% | 12 |

### look voi

| agent | mean(shift - non) | households with a drop | mean(shift - non), spot only | drop, spot only | event day -1 / 0 / +1 | event day -1 / 0 / +1, spot only | households with an event day |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | +2.8 | 6/20 | -0.9 | 14/20 | 89% / 91% / 93% | 96% / 96% / 96% | 12 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | +6.2 | 2/20 | +0.3 | 8/20 | 88% / 92% / 93% | 98% / 99% / 99% | 12 |
| LastObservation | +2.6 | 5/20 | -0.7 | 14/20 | 90% / 91% / 93% | 96% / 96% / 97% | 12 |
| Markov1(a=1,cut=24h,hl=24h) | +3.7 | 2/20 | -0.2 | 13/20 | 89% / 91% / 91% | 96% / 95% / 95% | 12 |
| MostFrequentLocation | +4.2 | 3/20 | +0.1 | 13/20 | 91% / 93% / 94% | 98% / 98% / 99% | 12 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | +3.8 | 4/20 | +0.1 | 12/20 | 90% / 92% / 93% | 97% / 97% / 98% | 12 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | +7.8 | 2/20 | +0.4 | 9/20 | 84% / 88% / 91% | 98% / 98% / 99% | 12 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | +8.0 | 2/20 | +0.5 | 7/20 | 85% / 88% / 91% | 98% / 98% / 99% | 12 |
| SmoothedRecency(hl=6h,freq=24h) | +4.8 | 3/20 | +0.1 | 8/20 | 90% / 92% / 93% | 98% / 98% / 99% | 12 |
| TimetableLookup(bin=1h,days=all) | +3.3 | 2/20 | -0.7 | 14/20 | 88% / 90% / 90% | 95% / 95% / 94% | 12 |

### Per-household accuracy per day (look voi / llm; `*` = that household's shift day)

**hh_s0** (shift days: Wed, Thu, Sat, Sun)

| agent | Wed* | Thu* | Fri | Sat* | Sun* | Mon | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 96% | 100% | 95% | 88% | 93% | 80% | 90% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 88% | 99% | 97% | 91% | 98% | 87% | 88% |
| LastObservation | 91% | 100% | 98% | 94% | 97% | 84% | 91% |
| Markov1(a=1,cut=24h,hl=24h) | 85% | 97% | 98% | 91% | 97% | 86% | 88% |
| MostFrequentLocation | 95% | 98% | 97% | 96% | 98% | 89% | 97% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 95% | 97% | 97% | 95% | 97% | 89% | 88% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 87% | 96% | 95% | 91% | 96% | 83% | 84% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 87% | 96% | 95% | 91% | 96% | 83% | 84% |
| SmoothedRecency(hl=6h,freq=24h) | 93% | 98% | 98% | 93% | 98% | 88% | 88% |
| TimetableLookup(bin=1h,days=all) | 90% | 93% | 95% | 92% | 91% | 79% | 86% |

**hh_s1** (shift days: Fri, Sat, Sun)

| agent | Wed | Thu | Fri* | Sat* | Sun* | Mon | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 97% | 86% | 95% | 92% | 90% | 88% | 77% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 84% | 80% | 93% | 100% | 94% | 89% | 79% |
| LastObservation | 91% | 83% | 95% | 96% | 88% | 91% | 85% |
| Markov1(a=1,cut=24h,hl=24h) | 81% | 86% | 90% | 95% | 84% | 92% | 83% |
| MostFrequentLocation | 92% | 81% | 95% | 100% | 92% | 91% | 80% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 92% | 84% | 92% | 98% | 88% | 89% | 78% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 77% | 73% | 86% | 98% | 94% | 84% | 73% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 77% | 73% | 86% | 98% | 94% | 85% | 74% |
| SmoothedRecency(hl=6h,freq=24h) | 90% | 86% | 92% | 99% | 91% | 88% | 75% |
| TimetableLookup(bin=1h,days=all) | 91% | 85% | 95% | 96% | 84% | 84% | 80% |

**hh_s10** (shift days: Sat, Sun)

| agent | Wed | Thu | Fri | Sat* | Sun* | Mon | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 100% | 88% | 92% | 89% | 97% | 72% | 80% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 95% | 84% | 92% | 94% | 98% | 80% | 83% |
| LastObservation | 96% | 90% | 91% | 93% | 95% | 90% | 88% |
| Markov1(a=1,cut=24h,hl=24h) | 92% | 81% | 91% | 95% | 96% | 88% | 92% |
| MostFrequentLocation | 95% | 88% | 92% | 94% | 98% | 90% | 88% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 97% | 86% | 95% | 95% | 97% | 80% | 87% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 89% | 75% | 88% | 88% | 96% | 75% | 75% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 89% | 75% | 88% | 90% | 97% | 75% | 75% |
| SmoothedRecency(hl=6h,freq=24h) | 97% | 85% | 93% | 94% | 98% | 80% | 84% |
| TimetableLookup(bin=1h,days=all) | 98% | 77% | 88% | 91% | 95% | 77% | 85% |

**hh_s11** (shift days: Fri, Sat, Sun)

| agent | Wed | Thu | Fri* | Sat* | Sun* | Mon | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 97% | 91% | 91% | 95% | 88% | 91% | 77% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 91% | 84% | 91% | 97% | 89% | 88% | 86% |
| LastObservation | 92% | 90% | 91% | 95% | 92% | 94% | 88% |
| Markov1(a=1,cut=24h,hl=24h) | 91% | 87% | 94% | 93% | 91% | 91% | 87% |
| MostFrequentLocation | 91% | 90% | 89% | 98% | 95% | 91% | 86% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 96% | 88% | 88% | 97% | 88% | 93% | 85% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 87% | 80% | 85% | 97% | 88% | 83% | 81% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 87% | 80% | 88% | 97% | 90% | 84% | 82% |
| SmoothedRecency(hl=6h,freq=24h) | 95% | 87% | 91% | 97% | 88% | 90% | 84% |
| TimetableLookup(bin=1h,days=all) | 94% | 80% | 89% | 88% | 85% | 88% | 80% |

**hh_s12** (shift days: Sat, Sun, Tue)

| agent | Wed | Thu | Fri | Sat* | Sun* | Mon | Tue* |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 88% | 91% | 84% | 92% | 91% | 78% | 86% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 75% | 91% | 82% | 94% | 94% | 86% | 90% |
| LastObservation | 87% | 90% | 90% | 93% | 94% | 91% | 88% |
| Markov1(a=1,cut=24h,hl=24h) | 82% | 90% | 85% | 91% | 93% | 91% | 88% |
| MostFrequentLocation | 82% | 95% | 96% | 95% | 94% | 88% | 92% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 81% | 98% | 84% | 94% | 94% | 90% | 88% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 68% | 88% | 73% | 91% | 94% | 80% | 87% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 68% | 88% | 73% | 91% | 94% | 81% | 87% |
| SmoothedRecency(hl=6h,freq=24h) | 80% | 95% | 84% | 91% | 94% | 84% | 94% |
| TimetableLookup(bin=1h,days=all) | 81% | 100% | 80% | 93% | 90% | 84% | 88% |

**hh_s13** (shift days: Sat, Sun)

| agent | Wed | Thu | Fri | Sat* | Sun* | Mon | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 99% | 93% | 80% | 93% | 91% | 84% | 91% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 89% | 91% | 82% | 95% | 98% | 91% | 92% |
| LastObservation | 95% | 86% | 81% | 97% | 92% | 91% | 96% |
| Markov1(a=1,cut=24h,hl=24h) | 91% | 88% | 85% | 98% | 95% | 91% | 95% |
| MostFrequentLocation | 91% | 93% | 80% | 96% | 96% | 96% | 98% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 91% | 90% | 80% | 96% | 98% | 89% | 90% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 88% | 88% | 75% | 94% | 97% | 90% | 87% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 88% | 88% | 75% | 94% | 97% | 90% | 87% |
| SmoothedRecency(hl=6h,freq=24h) | 94% | 91% | 82% | 97% | 96% | 91% | 92% |
| TimetableLookup(bin=1h,days=all) | 95% | 91% | 88% | 95% | 89% | 88% | 88% |

**hh_s14** (shift days: Thu, Sat, Sun)

| agent | Wed | Thu* | Fri | Sat* | Sun* | Mon | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 91% | 95% | 97% | 98% | 100% | 88% | 80% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 85% | 97% | 97% | 97% | 100% | 85% | 81% |
| LastObservation | 90% | 95% | 95% | 96% | 99% | 88% | 83% |
| Markov1(a=1,cut=24h,hl=24h) | 89% | 92% | 91% | 97% | 99% | 89% | 86% |
| MostFrequentLocation | 94% | 96% | 97% | 98% | 100% | 90% | 89% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 88% | 92% | 91% | 98% | 100% | 87% | 83% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 84% | 88% | 94% | 97% | 100% | 81% | 75% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 84% | 88% | 94% | 97% | 100% | 81% | 75% |
| SmoothedRecency(hl=6h,freq=24h) | 91% | 92% | 94% | 98% | 100% | 86% | 83% |
| TimetableLookup(bin=1h,days=all) | 89% | 86% | 90% | 95% | 92% | 88% | 82% |

**hh_s15** (shift days: Wed, Fri, Sat, Sun)

| agent | Wed* | Thu | Fri* | Sat* | Sun* | Mon | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 96% | 95% | 84% | 90% | 88% | 93% | 94% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 97% | 91% | 91% | 100% | 96% | 97% | 95% |
| LastObservation | 98% | 95% | 84% | 93% | 91% | 94% | 91% |
| Markov1(a=1,cut=24h,hl=24h) | 98% | 91% | 85% | 91% | 90% | 96% | 91% |
| MostFrequentLocation | 99% | 92% | 87% | 99% | 97% | 99% | 96% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 98% | 91% | 89% | 97% | 90% | 98% | 95% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 96% | 89% | 81% | 98% | 96% | 97% | 92% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 96% | 89% | 81% | 98% | 96% | 97% | 91% |
| SmoothedRecency(hl=6h,freq=24h) | 97% | 92% | 89% | 97% | 94% | 98% | 95% |
| TimetableLookup(bin=1h,days=all) | 95% | 92% | 92% | 93% | 88% | 88% | 91% |

**hh_s16** (shift days: Sat, Sun)

| agent | Wed | Thu | Fri | Sat* | Sun* | Mon | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 91% | 87% | 93% | 98% | 93% | 82% | 84% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 83% | 89% | 93% | 99% | 96% | 81% | 88% |
| LastObservation | 88% | 86% | 90% | 98% | 94% | 91% | 89% |
| Markov1(a=1,cut=24h,hl=24h) | 79% | 84% | 89% | 96% | 94% | 90% | 88% |
| MostFrequentLocation | 84% | 92% | 91% | 99% | 98% | 86% | 89% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 90% | 85% | 94% | 97% | 97% | 88% | 86% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 79% | 88% | 80% | 100% | 96% | 72% | 85% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 79% | 88% | 81% | 100% | 97% | 70% | 84% |
| SmoothedRecency(hl=6h,freq=24h) | 88% | 86% | 95% | 99% | 98% | 80% | 88% |
| TimetableLookup(bin=1h,days=all) | 90% | 82% | 91% | 91% | 88% | 80% | 80% |

**hh_s17** (shift days: Sat, Sun, Mon)

| agent | Wed | Thu | Fri | Sat* | Sun* | Mon* | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 93% | 97% | 90% | 91% | 89% | 90% | 90% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 84% | 96% | 91% | 96% | 95% | 95% | 95% |
| LastObservation | 95% | 95% | 91% | 95% | 91% | 94% | 96% |
| Markov1(a=1,cut=24h,hl=24h) | 86% | 91% | 93% | 94% | 95% | 92% | 94% |
| MostFrequentLocation | 94% | 97% | 93% | 97% | 97% | 91% | 92% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 97% | 93% | 96% | 95% | 96% | 94% | 94% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 80% | 92% | 88% | 95% | 92% | 92% | 94% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 80% | 94% | 88% | 96% | 94% | 93% | 94% |
| SmoothedRecency(hl=6h,freq=24h) | 89% | 94% | 93% | 98% | 95% | 94% | 92% |
| TimetableLookup(bin=1h,days=all) | 89% | 94% | 88% | 94% | 95% | 94% | 91% |

**hh_s18** (shift days: Sat, Sun)

| agent | Wed | Thu | Fri | Sat* | Sun* | Mon | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 96% | 92% | 81% | 90% | 92% | 88% | 89% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 95% | 91% | 84% | 95% | 97% | 95% | 92% |
| LastObservation | 98% | 93% | 77% | 94% | 95% | 84% | 94% |
| Markov1(a=1,cut=24h,hl=24h) | 98% | 91% | 79% | 93% | 95% | 82% | 93% |
| MostFrequentLocation | 99% | 92% | 93% | 95% | 99% | 95% | 91% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 97% | 94% | 88% | 93% | 95% | 91% | 95% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 94% | 91% | 74% | 94% | 96% | 91% | 88% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 94% | 91% | 77% | 94% | 96% | 91% | 88% |
| SmoothedRecency(hl=6h,freq=24h) | 96% | 91% | 92% | 95% | 96% | 94% | 91% |
| TimetableLookup(bin=1h,days=all) | 99% | 91% | 82% | 88% | 90% | 84% | 87% |

**hh_s19** (shift days: Sat, Sun)

| agent | Wed | Thu | Fri | Sat* | Sun* | Mon | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 94% | 95% | 93% | 95% | 90% | 91% | 95% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 85% | 90% | 93% | 99% | 97% | 97% | 98% |
| LastObservation | 91% | 94% | 91% | 99% | 96% | 95% | 95% |
| Markov1(a=1,cut=24h,hl=24h) | 85% | 96% | 89% | 99% | 92% | 96% | 93% |
| MostFrequentLocation | 91% | 95% | 91% | 99% | 99% | 99% | 95% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 90% | 93% | 93% | 99% | 98% | 99% | 92% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 84% | 88% | 85% | 98% | 92% | 97% | 93% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 84% | 88% | 86% | 98% | 93% | 97% | 92% |
| SmoothedRecency(hl=6h,freq=24h) | 91% | 91% | 95% | 100% | 98% | 99% | 94% |
| TimetableLookup(bin=1h,days=all) | 89% | 91% | 95% | 97% | 95% | 95% | 93% |

**hh_s2** (shift days: Sat, Sun, Tue)

| agent | Wed | Thu | Fri | Sat* | Sun* | Mon | Tue* |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 78% | 96% | 96% | 96% | 91% | 90% | 93% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 80% | 98% | 99% | 97% | 95% | 88% | 96% |
| LastObservation | 75% | 98% | 95% | 92% | 88% | 87% | 92% |
| Markov1(a=1,cut=24h,hl=24h) | 73% | 97% | 95% | 95% | 90% | 88% | 90% |
| MostFrequentLocation | 80% | 96% | 97% | 98% | 92% | 93% | 96% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 80% | 97% | 97% | 97% | 88% | 88% | 94% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 72% | 96% | 96% | 97% | 94% | 84% | 91% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 72% | 95% | 94% | 97% | 94% | 84% | 91% |
| SmoothedRecency(hl=6h,freq=24h) | 80% | 97% | 99% | 98% | 95% | 91% | 95% |
| TimetableLookup(bin=1h,days=all) | 78% | 93% | 91% | 88% | 77% | 88% | 83% |

**hh_s3** (shift days: Sat, Sun)

| agent | Wed | Thu | Fri | Sat* | Sun* | Mon | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 94% | 93% | 92% | 92% | 92% | 89% | 91% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 91% | 91% | 96% | 95% | 98% | 92% | 98% |
| LastObservation | 97% | 92% | 94% | 91% | 95% | 91% | 96% |
| Markov1(a=1,cut=24h,hl=24h) | 97% | 84% | 92% | 95% | 95% | 94% | 95% |
| MostFrequentLocation | 96% | 96% | 94% | 95% | 98% | 97% | 97% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 95% | 88% | 94% | 94% | 95% | 93% | 96% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 91% | 84% | 94% | 90% | 97% | 91% | 97% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 91% | 84% | 94% | 90% | 97% | 91% | 97% |
| SmoothedRecency(hl=6h,freq=24h) | 91% | 91% | 98% | 95% | 98% | 94% | 97% |
| TimetableLookup(bin=1h,days=all) | 92% | 88% | 95% | 94% | 96% | 83% | 95% |

**hh_s4** (shift days: Sat, Sun, Mon, Tue)

| agent | Wed | Thu | Fri | Sat* | Sun* | Mon* | Tue* |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 91% | 85% | 84% | 95% | 98% | 69% | 80% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 85% | 86% | 74% | 98% | 100% | 80% | 76% |
| LastObservation | 88% | 88% | 80% | 97% | 96% | 83% | 77% |
| Markov1(a=1,cut=24h,hl=24h) | 76% | 87% | 82% | 92% | 96% | 84% | 80% |
| MostFrequentLocation | 88% | 86% | 83% | 99% | 98% | 88% | 85% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 91% | 82% | 88% | 95% | 96% | 77% | 84% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 76% | 84% | 72% | 95% | 99% | 72% | 67% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 76% | 84% | 72% | 95% | 100% | 72% | 67% |
| SmoothedRecency(hl=6h,freq=24h) | 86% | 88% | 77% | 97% | 98% | 79% | 77% |
| TimetableLookup(bin=1h,days=all) | 83% | 84% | 88% | 94% | 98% | 76% | 78% |

**hh_s5** (shift days: Thu, Sat, Sun)

| agent | Wed | Thu* | Fri | Sat* | Sun* | Mon | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 90% | 91% | 91% | 89% | 95% | 74% | 79% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 79% | 86% | 88% | 94% | 100% | 81% | 83% |
| LastObservation | 90% | 84% | 92% | 84% | 98% | 90% | 88% |
| Markov1(a=1,cut=24h,hl=24h) | 79% | 91% | 89% | 84% | 95% | 91% | 86% |
| MostFrequentLocation | 88% | 88% | 93% | 91% | 100% | 84% | 86% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 88% | 91% | 91% | 87% | 98% | 83% | 80% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 73% | 81% | 85% | 90% | 100% | 77% | 81% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 73% | 81% | 85% | 90% | 100% | 77% | 80% |
| SmoothedRecency(hl=6h,freq=24h) | 85% | 87% | 89% | 91% | 100% | 82% | 80% |
| TimetableLookup(bin=1h,days=all) | 83% | 94% | 88% | 82% | 91% | 83% | 75% |

**hh_s6** (shift days: Sat, Sun)

| agent | Wed | Thu | Fri | Sat* | Sun* | Mon | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 94% | 88% | 82% | 91% | 100% | 78% | 91% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 80% | 87% | 77% | 95% | 100% | 79% | 89% |
| LastObservation | 91% | 90% | 91% | 94% | 98% | 87% | 88% |
| Markov1(a=1,cut=24h,hl=24h) | 81% | 87% | 89% | 93% | 98% | 91% | 93% |
| MostFrequentLocation | 91% | 86% | 89% | 96% | 100% | 85% | 96% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 87% | 91% | 80% | 95% | 100% | 86% | 90% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 75% | 83% | 75% | 94% | 100% | 69% | 84% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 75% | 83% | 75% | 94% | 100% | 69% | 84% |
| SmoothedRecency(hl=6h,freq=24h) | 91% | 92% | 80% | 95% | 100% | 89% | 87% |
| TimetableLookup(bin=1h,days=all) | 86% | 88% | 80% | 91% | 93% | 83% | 82% |

**hh_s7** (shift days: Sat, Sun)

| agent | Wed | Thu | Fri | Sat* | Sun* | Mon | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 92% | 88% | 91% | 90% | 98% | 93% | 95% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 91% | 89% | 90% | 95% | 100% | 95% | 98% |
| LastObservation | 92% | 90% | 93% | 91% | 96% | 98% | 93% |
| Markov1(a=1,cut=24h,hl=24h) | 86% | 85% | 95% | 90% | 96% | 97% | 92% |
| MostFrequentLocation | 91% | 91% | 90% | 96% | 100% | 91% | 97% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 94% | 87% | 90% | 93% | 98% | 95% | 95% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 88% | 84% | 87% | 94% | 98% | 89% | 96% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 88% | 84% | 86% | 94% | 98% | 91% | 95% |
| SmoothedRecency(hl=6h,freq=24h) | 91% | 86% | 91% | 94% | 100% | 98% | 97% |
| TimetableLookup(bin=1h,days=all) | 91% | 80% | 88% | 91% | 93% | 90% | 90% |

**hh_s8** (shift days: Wed, Fri, Sat, Sun, Tue)

| agent | Wed* | Thu | Fri* | Sat* | Sun* | Mon | Tue* |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 100% | 97% | 91% | 90% | 96% | 91% | 87% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 94% | 96% | 88% | 95% | 97% | 91% | 84% |
| LastObservation | 96% | 97% | 95% | 95% | 97% | 88% | 90% |
| Markov1(a=1,cut=24h,hl=24h) | 93% | 91% | 92% | 88% | 97% | 90% | 89% |
| MostFrequentLocation | 95% | 95% | 89% | 93% | 97% | 91% | 89% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 98% | 97% | 88% | 94% | 99% | 92% | 84% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 93% | 97% | 84% | 94% | 94% | 91% | 83% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 93% | 97% | 84% | 94% | 94% | 91% | 83% |
| SmoothedRecency(hl=6h,freq=24h) | 97% | 96% | 88% | 95% | 98% | 92% | 85% |
| TimetableLookup(bin=1h,days=all) | 97% | 92% | 85% | 87% | 93% | 85% | 87% |

**hh_s9** (shift days: Fri, Sat, Sun, Mon)

| agent | Wed | Thu | Fri* | Sat* | Sun* | Mon* | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 95% | 92% | 93% | 90% | 88% | 91% | 91% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 95% | 93% | 97% | 93% | 90% | 95% | 97% |
| LastObservation | 91% | 92% | 89% | 92% | 91% | 88% | 95% |
| Markov1(a=1,cut=24h,hl=24h) | 92% | 94% | 91% | 91% | 89% | 88% | 95% |
| MostFrequentLocation | 92% | 93% | 94% | 91% | 93% | 92% | 97% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 91% | 91% | 93% | 91% | 93% | 91% | 97% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 94% | 94% | 95% | 94% | 88% | 93% | 95% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 96% | 94% | 95% | 94% | 89% | 93% | 96% |
| SmoothedRecency(hl=6h,freq=24h) | 96% | 91% | 94% | 91% | 91% | 91% | 98% |
| TimetableLookup(bin=1h,days=all) | 95% | 89% | 93% | 90% | 88% | 91% | 91% |

