# LLM agents vs patrol density (look on), households: hh_s0 hh_s1 hh_s2 hh_s3 hh_s4 

5 households (hh_s0, hh_s1, hh_s2, hh_s3, hh_s4), 14 agents, patrol every [1, 4, 8] h, look on/off = ['llm', 'off', 'voi']. 73472 agent-question records. Shift days per household: hh_s0: [1, 2, 4, 5]; hh_s1: [3, 4, 5]; hh_s2: [4, 5, 7]; hh_s3: [4, 5]; hh_s4: [4, 5, 6, 7].

Records per household: hh_s0 14784, hh_s1 14784, hh_s2 14784, hh_s3 14560, hh_s4 14560

## 1. Accuracy per day per agent (no abstaining; shift days marked *)

### patrol every 1 h, look llm

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| llm_naive/not_told/look_on | 80% | 86% | 88% | 91% | 91% | 80% | 81% | 85% | 87% | 84% | 95% | 31% | 3% |
| llm_naive/told/look_on | 81% | 86% | 88% | 92% | 91% | 80% | 81% | 86% | 88% | 84% | 95% | 38% | 4% |
| llm_recent/not_told/look_on | 81% | 88% | 89% | 91% | 92% | 85% | 81% | 87% | 89% | 85% | 95% | 54% | 14% |
| llm_recent/told/look_on | 81% | 88% | 90% | 91% | 92% | 81% | 81% | 86% | 88% | 85% | 95% | 62% | 7% |
| llm_summary/not_told/look_on | 88% | 96% | 94% | 91% | 93% | 87% | 94% | 92% | 92% | 91% | 96% | 31% | 62% |
| llm_summary/told/look_on | 91% | 97% | 96% | 93% | 95% | 91% | 94% | 94% | 95% | 93% | 96% | 85% | 75% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| llm_naive/not_told/look_on | 738 | 78% | 382 | 100% |
| llm_naive/told/look_on | 738 | 78% | 382 | 100% |
| llm_recent/not_told/look_on | 738 | 80% | 382 | 100% |
| llm_recent/told/look_on | 738 | 79% | 382 | 100% |
| llm_summary/not_told/look_on | 738 | 87% | 382 | 100% |
| llm_summary/told/look_on | 738 | 91% | 382 | 100% |

Questions by truth type: on_person 13, out_of_house 109, spot 998
(* every household shifts that day; ° some households do)

### patrol every 1 h, look off

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 78% | 86% | 81% | 85% | 82% | 77% | 71% | 80% | 81% | 79% | 90% | 0% | 2% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 78% | 86% | 88% | 91% | 90% | 80% | 81% | 85% | 87% | 83% | 95% | 0% | 0% |
| LastObservation | 78% | 86% | 88% | 91% | 90% | 80% | 81% | 85% | 87% | 83% | 95% | 0% | 1% |
| Markov1(a=1,cut=24h,hl=24h) | 81% | 92% | 92% | 91% | 89% | 85% | 89% | 88% | 89% | 88% | 94% | 23% | 40% |
| MostFrequentLocation | 81% | 86% | 88% | 91% | 90% | 79% | 81% | 85% | 87% | 84% | 95% | 8% | 5% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 80% | 86% | 88% | 91% | 90% | 81% | 81% | 85% | 87% | 84% | 95% | 15% | 4% |
| SmoothedRecency(hl=6h,freq=24h) | 78% | 86% | 88% | 91% | 90% | 80% | 81% | 85% | 87% | 83% | 95% | 0% | 0% |
| TimetableLookup(bin=1h,days=all) | 81% | 88% | 91% | 91% | 89% | 85% | 88% | 87% | 89% | 86% | 95% | 0% | 28% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 738 | 70% | 382 | 99% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 738 | 77% | 382 | 100% |
| LastObservation | 738 | 77% | 382 | 100% |
| Markov1(a=1,cut=24h,hl=24h) | 738 | 82% | 382 | 100% |
| MostFrequentLocation | 738 | 78% | 382 | 100% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 738 | 78% | 382 | 100% |
| SmoothedRecency(hl=6h,freq=24h) | 738 | 77% | 382 | 100% |
| TimetableLookup(bin=1h,days=all) | 738 | 81% | 382 | 100% |

Questions by truth type: on_person 13, out_of_house 109, spot 998
(* every household shifts that day; ° some households do)

### patrol every 1 h, look voi

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 92% | 93% | 94% | 96% | 95% | 88% | 91% | 93% | 94% | 92% | 98% | 31% | 49% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 88% | 92% | 95% | 96% | 98% | 87% | 88% | 92% | 95% | 90% | 100% | 15% | 31% |
| LastObservation | 90% | 93% | 95% | 96% | 96% | 89% | 90% | 93% | 94% | 92% | 98% | 31% | 53% |
| Markov1(a=1,cut=24h,hl=24h) | 84% | 91% | 94% | 96% | 96% | 91% | 91% | 92% | 94% | 90% | 98% | 54% | 41% |
| MostFrequentLocation | 92% | 92% | 93% | 98% | 96% | 92% | 92% | 94% | 96% | 92% | 99% | 38% | 49% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 92% | 89% | 95% | 98% | 95% | 90% | 88% | 92% | 94% | 91% | 98% | 38% | 44% |
| SmoothedRecency(hl=6h,freq=24h) | 91% | 94% | 93% | 96% | 97% | 90% | 88% | 93% | 95% | 91% | 99% | 31% | 39% |
| TimetableLookup(bin=1h,days=all) | 89% | 92% | 95% | 98% | 95% | 88% | 89% | 92% | 94% | 91% | 98% | 38% | 42% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 738 | 89% | 382 | 100% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 738 | 88% | 382 | 100% |
| LastObservation | 738 | 89% | 382 | 100% |
| Markov1(a=1,cut=24h,hl=24h) | 738 | 88% | 382 | 100% |
| MostFrequentLocation | 738 | 90% | 382 | 100% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 738 | 89% | 382 | 100% |
| SmoothedRecency(hl=6h,freq=24h) | 738 | 89% | 382 | 100% |
| TimetableLookup(bin=1h,days=all) | 738 | 88% | 382 | 100% |

Questions by truth type: on_person 13, out_of_house 109, spot 998
(* every household shifts that day; ° some households do)

### patrol every 4 h, look llm

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| llm_naive/not_told/look_on | 84% | 84% | 81% | 86% | 86% | 76% | 74% | 82% | 83% | 81% | 90% | 38% | 6% |
| llm_naive/told/look_on | 84% | 84% | 79% | 85% | 87% | 76% | 75% | 82% | 83% | 80% | 90% | 31% | 7% |
| llm_recent/not_told/look_on | 81% | 84% | 80% | 84% | 83% | 78% | 76% | 81% | 82% | 80% | 90% | 31% | 7% |
| llm_recent/told/look_on | 81% | 84% | 80% | 84% | 84% | 77% | 76% | 81% | 82% | 80% | 90% | 23% | 9% |
| llm_summary/not_told/look_on | 86% | 89% | 88% | 88% | 90% | 81% | 86% | 87% | 86% | 87% | 92% | 46% | 46% |
| llm_summary/told/look_on | 85% | 89% | 86% | 88% | 92% | 81% | 86% | 87% | 89% | 86% | 92% | 69% | 39% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| llm_naive/not_told/look_on | 738 | 72% | 382 | 100% |
| llm_naive/told/look_on | 738 | 72% | 382 | 100% |
| llm_recent/not_told/look_on | 738 | 71% | 382 | 100% |
| llm_recent/told/look_on | 738 | 71% | 382 | 100% |
| llm_summary/not_told/look_on | 738 | 80% | 382 | 99% |
| llm_summary/told/look_on | 738 | 80% | 382 | 100% |

Questions by truth type: on_person 13, out_of_house 109, spot 998
(* every household shifts that day; ° some households do)

### patrol every 4 h, look off

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 78% | 83% | 75% | 80% | 82% | 72% | 66% | 77% | 78% | 75% | 86% | 0% | 0% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 78% | 83% | 79% | 85% | 85% | 76% | 74% | 80% | 82% | 79% | 90% | 0% | 0% |
| LastObservation | 78% | 83% | 79% | 85% | 85% | 76% | 74% | 80% | 82% | 79% | 90% | 0% | 0% |
| Markov1(a=1,cut=24h,hl=24h) | 81% | 88% | 81% | 85% | 83% | 78% | 78% | 82% | 82% | 82% | 88% | 31% | 31% |
| MostFrequentLocation | 80% | 83% | 79% | 85% | 85% | 76% | 74% | 80% | 82% | 79% | 90% | 0% | 4% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 80% | 85% | 80% | 85% | 85% | 76% | 74% | 81% | 82% | 79% | 90% | 8% | 5% |
| SmoothedRecency(hl=6h,freq=24h) | 78% | 83% | 79% | 85% | 85% | 76% | 74% | 80% | 82% | 79% | 90% | 0% | 0% |
| TimetableLookup(bin=1h,days=all) | 80% | 84% | 81% | 84% | 84% | 74% | 75% | 80% | 82% | 79% | 89% | 0% | 10% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 738 | 65% | 382 | 99% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 738 | 70% | 382 | 100% |
| LastObservation | 738 | 70% | 382 | 100% |
| Markov1(a=1,cut=24h,hl=24h) | 738 | 73% | 382 | 100% |
| MostFrequentLocation | 738 | 70% | 382 | 100% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 738 | 71% | 382 | 100% |
| SmoothedRecency(hl=6h,freq=24h) | 738 | 70% | 382 | 100% |
| TimetableLookup(bin=1h,days=all) | 738 | 70% | 382 | 100% |

Questions by truth type: on_person 13, out_of_house 109, spot 998
(* every household shifts that day; ° some households do)

### patrol every 4 h, look voi

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 91% | 92% | 92% | 92% | 91% | 82% | 83% | 89% | 90% | 89% | 95% | 31% | 43% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 86% | 91% | 90% | 96% | 96% | 88% | 88% | 91% | 93% | 89% | 99% | 15% | 23% |
| LastObservation | 88% | 92% | 91% | 92% | 92% | 87% | 88% | 90% | 91% | 89% | 95% | 46% | 49% |
| Markov1(a=1,cut=24h,hl=24h) | 82% | 91% | 91% | 92% | 90% | 90% | 84% | 88% | 89% | 88% | 94% | 54% | 38% |
| MostFrequentLocation | 89% | 91% | 94% | 98% | 96% | 91% | 90% | 93% | 95% | 91% | 99% | 38% | 43% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 91% | 91% | 92% | 94% | 92% | 87% | 89% | 91% | 92% | 90% | 97% | 8% | 43% |
| SmoothedRecency(hl=6h,freq=24h) | 87% | 91% | 94% | 96% | 96% | 88% | 87% | 91% | 93% | 89% | 98% | 15% | 33% |
| TimetableLookup(bin=1h,days=all) | 87% | 88% | 92% | 92% | 85% | 78% | 84% | 87% | 87% | 86% | 92% | 54% | 45% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 738 | 84% | 382 | 99% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 738 | 86% | 382 | 100% |
| LastObservation | 738 | 85% | 382 | 100% |
| Markov1(a=1,cut=24h,hl=24h) | 738 | 83% | 382 | 100% |
| MostFrequentLocation | 738 | 89% | 382 | 100% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 738 | 86% | 382 | 100% |
| SmoothedRecency(hl=6h,freq=24h) | 738 | 86% | 382 | 100% |
| TimetableLookup(bin=1h,days=all) | 738 | 80% | 382 | 98% |

Questions by truth type: on_person 13, out_of_house 109, spot 998
(* every household shifts that day; ° some households do)

### patrol every 8 h, look llm

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| llm_naive/not_told/look_on | 81% | 85% | 82% | 83% | 87% | 78% | 76% | 82% | 83% | 80% | 90% | 31% | 10% |
| llm_naive/told/look_on | 81% | 86% | 82% | 82% | 87% | 74% | 77% | 81% | 83% | 80% | 90% | 31% | 10% |
| llm_recent/not_told/look_on | 81% | 84% | 80% | 84% | 85% | 76% | 76% | 81% | 84% | 79% | 88% | 38% | 4% |
| llm_recent/told/look_on | 73% | 84% | 77% | 81% | 85% | 75% | 70% | 78% | 81% | 75% | 87% | 22% | 6% |
| llm_summary/not_told/look_on | 82% | 90% | 86% | 86% | 88% | 84% | 86% | 86% | 88% | 85% | 90% | 31% | 61% |
| llm_summary/told/look_on | 82% | 92% | 85% | 88% | 89% | 82% | 89% | 87% | 88% | 86% | 92% | 46% | 46% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| llm_naive/not_told/look_on | 738 | 72% | 382 | 100% |
| llm_naive/told/look_on | 738 | 72% | 382 | 100% |
| llm_recent/not_told/look_on | 587 | 71% | 309 | 100% |
| llm_recent/told/look_on | 605 | 67% | 291 | 100% |
| llm_summary/not_told/look_on | 738 | 79% | 382 | 99% |
| llm_summary/told/look_on | 738 | 80% | 382 | 100% |

Questions by truth type: on_person 12, out_of_house 100, spot 932
(* every household shifts that day; ° some households do)

### patrol every 8 h, look off

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 73% | 81% | 76% | 77% | 78% | 66% | 69% | 74% | 76% | 73% | 83% | 0% | 0% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 74% | 81% | 78% | 82% | 85% | 72% | 74% | 78% | 81% | 76% | 88% | 0% | 0% |
| LastObservation | 73% | 81% | 78% | 82% | 85% | 72% | 74% | 78% | 81% | 76% | 87% | 0% | 0% |
| Markov1(a=1,cut=24h,hl=24h) | 74% | 82% | 74% | 81% | 83% | 71% | 72% | 77% | 79% | 75% | 84% | 23% | 22% |
| MostFrequentLocation | 74% | 81% | 77% | 82% | 83% | 71% | 72% | 77% | 80% | 75% | 86% | 0% | 2% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 74% | 83% | 78% | 82% | 85% | 72% | 74% | 78% | 81% | 76% | 88% | 15% | 3% |
| SmoothedRecency(hl=6h,freq=24h) | 73% | 81% | 78% | 82% | 85% | 73% | 74% | 78% | 81% | 76% | 87% | 0% | 1% |
| TimetableLookup(bin=1h,days=all) | 72% | 83% | 78% | 81% | 82% | 71% | 72% | 77% | 80% | 75% | 86% | 0% | 8% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 738 | 62% | 382 | 98% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 738 | 67% | 382 | 100% |
| LastObservation | 738 | 67% | 382 | 100% |
| Markov1(a=1,cut=24h,hl=24h) | 738 | 65% | 382 | 100% |
| MostFrequentLocation | 738 | 65% | 382 | 99% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 738 | 67% | 382 | 100% |
| SmoothedRecency(hl=6h,freq=24h) | 738 | 67% | 382 | 100% |
| TimetableLookup(bin=1h,days=all) | 738 | 66% | 382 | 99% |

Questions by truth type: on_person 13, out_of_house 109, spot 998
(* every household shifts that day; ° some households do)

### patrol every 8 h, look voi

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 89% | 91% | 89% | 89% | 91% | 76% | 82% | 87% | 88% | 86% | 93% | 31% | 41% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 81% | 89% | 89% | 96% | 97% | 86% | 86% | 89% | 93% | 86% | 98% | 8% | 16% |
| LastObservation | 87% | 91% | 90% | 92% | 89% | 84% | 86% | 89% | 90% | 87% | 94% | 23% | 46% |
| Markov1(a=1,cut=24h,hl=24h) | 82% | 89% | 87% | 91% | 89% | 86% | 84% | 87% | 89% | 85% | 92% | 54% | 39% |
| MostFrequentLocation | 89% | 92% | 93% | 97% | 95% | 90% | 90% | 92% | 95% | 90% | 98% | 54% | 44% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 89% | 88% | 92% | 93% | 91% | 84% | 88% | 89% | 91% | 88% | 96% | 8% | 36% |
| SmoothedRecency(hl=6h,freq=24h) | 86% | 90% | 92% | 96% | 95% | 86% | 84% | 90% | 93% | 88% | 98% | 8% | 25% |
| TimetableLookup(bin=1h,days=all) | 86% | 86% | 89% | 86% | 83% | 79% | 76% | 84% | 83% | 84% | 89% | 46% | 39% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 738 | 81% | 382 | 98% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 738 | 84% | 382 | 100% |
| LastObservation | 738 | 83% | 382 | 100% |
| Markov1(a=1,cut=24h,hl=24h) | 738 | 80% | 382 | 100% |
| MostFrequentLocation | 738 | 88% | 382 | 100% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 738 | 84% | 382 | 100% |
| SmoothedRecency(hl=6h,freq=24h) | 738 | 85% | 382 | 100% |
| TimetableLookup(bin=1h,days=all) | 738 | 76% | 382 | 98% |

Questions by truth type: on_person 13, out_of_house 109, spot 998
(* every household shifts that day; ° some households do)

## 2. Accuracy vs patrol density (all days, no abstaining)

### look llm

| agent | every 1 h | every 4 h | every 8 h |
|---|---|---|---|
| llm_naive/not_told/look_on | 85% | 82% | 82% |
| llm_naive/told/look_on | 86% | 82% | 81% |
| llm_recent/not_told/look_on | 87% | 81% | 81% |
| llm_recent/told/look_on | 86% | 81% | 78% |
| llm_summary/not_told/look_on | 92% | 87% | 86% |
| llm_summary/told/look_on | 94% | 87% | 87% |

### look off

| agent | every 1 h | every 4 h | every 8 h |
|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 80% | 77% | 74% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 85% | 80% | 78% |
| LastObservation | 85% | 80% | 78% |
| Markov1(a=1,cut=24h,hl=24h) | 88% | 82% | 77% |
| MostFrequentLocation | 85% | 80% | 77% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 85% | 81% | 78% |
| SmoothedRecency(hl=6h,freq=24h) | 85% | 80% | 78% |
| TimetableLookup(bin=1h,days=all) | 87% | 80% | 77% |

### look voi

| agent | every 1 h | every 4 h | every 8 h |
|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 93% | 89% | 87% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 92% | 91% | 89% |
| LastObservation | 93% | 90% | 89% |
| Markov1(a=1,cut=24h,hl=24h) | 92% | 88% | 87% |
| MostFrequentLocation | 94% | 93% | 92% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 92% | 91% | 89% |
| SmoothedRecency(hl=6h,freq=24h) | 93% | 91% | 90% |
| TimetableLookup(bin=1h,days=all) | 92% | 87% | 84% |

## 3. What the free look is worth (all densities pooled)

| agent | look off | look voi | look top | before-look answer (voi runs) | found by voi look | found by top look |
|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 77% | 90% | - | 79% | 53% | - |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 81% | 91% | - | 83% | 56% | - |
| LastObservation | 81% | 91% | - | 83% | 47% | - |
| Markov1(a=1,cut=24h,hl=24h) | 82% | 89% | - | 86% | 46% | - |
| MostFrequentLocation | 81% | 93% | - | 83% | 55% | - |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 82% | 91% | - | 84% | 51% | - |
| SmoothedRecency(hl=6h,freq=24h) | 81% | 91% | - | 83% | 52% | - |
| TimetableLookup(bin=1h,days=all) | 82% | 87% | - | 81% | 48% | - |
| llm_naive/not_told/look_on | - | - | - | - | - | - |
| llm_naive/told/look_on | - | - | - | - | - | - |
| llm_recent/not_told/look_on | - | - | - | - | - | - |
| llm_recent/told/look_on | - | - | - | - | - | - |
| llm_summary/not_told/look_on | - | - | - | - | - | - |
| llm_summary/told/look_on | - | - | - | - | - | - |

Look gain by confidence before the look (pooled over agents, look-on runs):

| top prob before look | n | acc before look | acc after look |
|---|---|---|---|
| [0.00, 0.40) | 2921 | 54% | 65% |
| [0.40, 0.60) | 1800 | 57% | 75% |
| [0.60, 0.80) | 2517 | 59% | 80% |
| [0.80, 0.95) | 6790 | 71% | 82% |
| [0.95, 1.01) | 32564 | 91% | 93% |

## 4. Abstain rate and answered-accuracy per day (look voi for classical agents, look on for LLM agents; all densities pooled)

### outright ABSTAIN answers only (LLM direct route)

| agent | Wed abstain / acc | Thu abstain / acc | Fri abstain / acc | Sat abstain / acc | Sun abstain / acc | Mon abstain / acc | Tue abstain / acc | shift abstain / acc | non-shift abstain / acc | mean score |
|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0% / 91% | 0% / 92% | 0% / 92% | 0% / 92% | 0% / 92% | 0% / 82% | 0% / 85% | 0% / 91% | 0% / 89% | +0.79 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0% / 85% | 0% / 90% | 0% / 91% | 0% / 96% | 0% / 97% | 0% / 87% | 0% / 87% | 0% / 93% | 0% / 88% | +0.81 |
| LastObservation | 0% / 88% | 0% / 92% | 0% / 92% | 0% / 94% | 0% / 92% | 0% / 87% | 0% / 88% | 0% / 92% | 0% / 89% | +0.81 |
| Markov1(a=1,cut=24h,hl=24h) | 0% / 82% | 0% / 90% | 0% / 91% | 0% / 93% | 0% / 92% | 0% / 89% | 0% / 86% | 0% / 91% | 0% / 88% | +0.78 |
| MostFrequentLocation | 0% / 90% | 0% / 92% | 0% / 93% | 0% / 98% | 0% / 96% | 0% / 91% | 0% / 91% | 0% / 95% | 0% / 91% | +0.86 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0% / 91% | 0% / 89% | 0% / 93% | 0% / 95% | 0% / 93% | 0% / 87% | 0% / 88% | 0% / 92% | 0% / 90% | +0.82 |
| SmoothedRecency(hl=6h,freq=24h) | 0% / 88% | 0% / 92% | 0% / 93% | 0% / 96% | 0% / 96% | 0% / 88% | 0% / 86% | 0% / 93% | 0% / 89% | +0.82 |
| TimetableLookup(bin=1h,days=all) | 0% / 87% | 0% / 89% | 0% / 92% | 0% / 92% | 0% / 88% | 0% / 82% | 0% / 83% | 0% / 88% | 0% / 87% | +0.75 |
| llm_naive/not_told/look_on | 4% / 85% | 4% / 89% | 3% / 87% | 1% / 88% | 2% / 89% | 6% / 83% | 5% / 81% | 3% / 87% | 4% / 85% | +0.69 |
| llm_naive/told/look_on | 5% / 86% | 4% / 89% | 4% / 87% | 1% / 87% | 1% / 89% | 7% / 83% | 5% / 82% | 3% / 87% | 4% / 85% | +0.69 |
| llm_recent/not_told/look_on | 5% / 86% | 3% / 88% | 3% / 86% | 1% / 87% | 1% / 88% | 4% / 83% | 3% / 80% | 2% / 87% | 3% / 84% | +0.69 |
| llm_recent/told/look_on | 6% / 83% | 3% / 88% | 3% / 85% | 0% / 86% | 0% / 87% | 5% / 82% | 4% / 79% | 3% / 86% | 3% / 83% | +0.67 |
| llm_summary/not_told/look_on | 4% / 89% | 1% / 93% | 1% / 90% | 1% / 89% | 1% / 91% | 1% / 85% | 3% / 91% | 1% / 90% | 2% / 90% | +0.78 |
| llm_summary/told/look_on | 4% / 90% | 1% / 94% | 1% / 90% | 0% / 90% | 1% / 93% | 2% / 86% | 1% / 91% | 1% / 91% | 2% / 90% | +0.80 |

### threshold 0.4 on the top probability / stated confidence, plus outright ABSTAIN answers

| agent | Wed abstain / acc | Thu abstain / acc | Fri abstain / acc | Sat abstain / acc | Sun abstain / acc | Mon abstain / acc | Tue abstain / acc | shift abstain / acc | non-shift abstain / acc | mean score |
|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 12% / 95% | 10% / 97% | 9% / 96% | 5% / 94% | 3% / 94% | 10% / 87% | 9% / 89% | 6% / 94% | 10% / 93% | +0.80 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 12% / 93% | 7% / 94% | 7% / 96% | 2% / 98% | 1% / 97% | 6% / 90% | 9% / 92% | 5% / 96% | 8% / 93% | +0.83 |
| LastObservation | 12% / 94% | 10% / 97% | 9% / 97% | 4% / 96% | 1% / 93% | 9% / 91% | 11% / 93% | 6% / 94% | 10% / 94% | +0.81 |
| Markov1(a=1,cut=24h,hl=24h) | 45% / 94% | 37% / 96% | 36% / 99% | 34% / 98% | 29% / 98% | 33% / 95% | 32% / 94% | 32% / 97% | 38% / 96% | +0.60 |
| MostFrequentLocation | 13% / 97% | 9% / 96% | 10% / 99% | 5% / 100% | 2% / 97% | 8% / 93% | 9% / 93% | 6% / 98% | 10% / 95% | +0.85 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 14% / 98% | 9% / 96% | 9% / 97% | 4% / 98% | 1% / 94% | 8% / 91% | 9% / 92% | 5% / 95% | 10% / 95% | +0.83 |
| SmoothedRecency(hl=6h,freq=24h) | 12% / 93% | 10% / 96% | 9% / 97% | 3% / 98% | 3% / 98% | 8% / 92% | 10% / 92% | 6% / 97% | 9% / 94% | +0.84 |
| TimetableLookup(bin=1h,days=all) | 18% / 95% | 16% / 96% | 17% / 98% | 14% / 99% | 15% / 95% | 18% / 92% | 18% / 92% | 15% / 96% | 17% / 95% | +0.75 |
| llm_naive/not_told/look_on | 4% / 85% | 4% / 89% | 3% / 87% | 1% / 88% | 2% / 89% | 6% / 83% | 6% / 81% | 4% / 87% | 4% / 85% | +0.70 |
| llm_naive/told/look_on | 5% / 86% | 4% / 89% | 4% / 87% | 1% / 87% | 1% / 89% | 7% / 83% | 5% / 82% | 4% / 88% | 4% / 85% | +0.70 |
| llm_recent/not_told/look_on | 5% / 86% | 3% / 88% | 3% / 86% | 1% / 87% | 1% / 88% | 4% / 83% | 3% / 80% | 2% / 87% | 3% / 84% | +0.69 |
| llm_recent/told/look_on | 6% / 83% | 3% / 88% | 3% / 85% | 0% / 86% | 0% / 87% | 6% / 83% | 4% / 79% | 3% / 86% | 3% / 83% | +0.67 |
| llm_summary/not_told/look_on | 4% / 89% | 1% / 93% | 1% / 90% | 1% / 89% | 1% / 91% | 2% / 85% | 3% / 91% | 1% / 90% | 2% / 90% | +0.78 |
| llm_summary/told/look_on | 4% / 90% | 1% / 94% | 1% / 90% | 0% / 90% | 1% / 93% | 2% / 86% | 2% / 91% | 1% / 91% | 2% / 90% | +0.80 |

### threshold 0.5 on the top probability / stated confidence, plus outright ABSTAIN answers

| agent | Wed abstain / acc | Thu abstain / acc | Fri abstain / acc | Sat abstain / acc | Sun abstain / acc | Mon abstain / acc | Tue abstain / acc | shift abstain / acc | non-shift abstain / acc | mean score |
|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 15% / 96% | 12% / 98% | 10% / 97% | 5% / 95% | 4% / 95% | 14% / 90% | 14% / 92% | 8% / 95% | 13% / 94% | +0.80 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 15% / 96% | 9% / 96% | 8% / 96% | 2% / 98% | 2% / 98% | 9% / 92% | 11% / 94% | 6% / 97% | 10% / 94% | +0.84 |
| LastObservation | 16% / 96% | 12% / 98% | 10% / 97% | 4% / 96% | 3% / 94% | 14% / 94% | 15% / 96% | 8% / 96% | 13% / 95% | +0.81 |
| Markov1(a=1,cut=24h,hl=24h) | 53% / 100% | 50% / 99% | 45% / 100% | 39% / 98% | 38% / 99% | 45% / 99% | 44% / 98% | 42% / 99% | 48% / 99% | +0.54 |
| MostFrequentLocation | 18% / 97% | 12% / 98% | 11% / 100% | 5% / 100% | 3% / 98% | 12% / 94% | 12% / 95% | 8% / 99% | 12% / 96% | +0.85 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 18% / 98% | 12% / 97% | 10% / 98% | 4% / 98% | 2% / 95% | 13% / 93% | 12% / 94% | 8% / 96% | 12% / 96% | +0.83 |
| SmoothedRecency(hl=6h,freq=24h) | 13% / 94% | 11% / 97% | 9% / 98% | 3% / 98% | 3% / 98% | 10% / 93% | 11% / 93% | 7% / 97% | 11% / 95% | +0.84 |
| TimetableLookup(bin=1h,days=all) | 25% / 97% | 23% / 98% | 25% / 99% | 18% / 98% | 19% / 96% | 26% / 94% | 25% / 95% | 22% / 98% | 24% / 96% | +0.72 |
| llm_naive/not_told/look_on | 5% / 85% | 4% / 89% | 3% / 87% | 2% / 88% | 2% / 89% | 6% / 83% | 6% / 81% | 4% / 87% | 4% / 85% | +0.70 |
| llm_naive/told/look_on | 5% / 86% | 4% / 89% | 4% / 87% | 1% / 88% | 1% / 89% | 7% / 83% | 5% / 82% | 4% / 88% | 4% / 85% | +0.70 |
| llm_recent/not_told/look_on | 5% / 86% | 3% / 88% | 3% / 86% | 2% / 88% | 2% / 88% | 4% / 83% | 3% / 80% | 3% / 87% | 3% / 84% | +0.69 |
| llm_recent/told/look_on | 6% / 83% | 3% / 88% | 3% / 85% | 2% / 87% | 1% / 88% | 6% / 82% | 4% / 79% | 4% / 87% | 3% / 83% | +0.67 |
| llm_summary/not_told/look_on | 5% / 89% | 1% / 93% | 1% / 90% | 1% / 89% | 1% / 91% | 2% / 85% | 3% / 91% | 1% / 90% | 2% / 90% | +0.78 |
| llm_summary/told/look_on | 4% / 90% | 2% / 94% | 1% / 90% | 1% / 90% | 1% / 93% | 2% / 86% | 2% / 91% | 1% / 91% | 2% / 90% | +0.80 |

### threshold 0.6 on the top probability / stated confidence, plus outright ABSTAIN answers

| agent | Wed abstain / acc | Thu abstain / acc | Fri abstain / acc | Sat abstain / acc | Sun abstain / acc | Mon abstain / acc | Tue abstain / acc | shift abstain / acc | non-shift abstain / acc | mean score |
|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 15% / 96% | 12% / 98% | 10% / 97% | 5% / 95% | 4% / 96% | 16% / 91% | 15% / 92% | 9% / 95% | 13% / 95% | +0.80 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 15% / 97% | 9% / 96% | 9% / 96% | 2% / 98% | 2% / 98% | 10% / 92% | 11% / 94% | 6% / 97% | 10% / 95% | +0.84 |
| LastObservation | 16% / 96% | 12% / 98% | 10% / 97% | 4% / 96% | 3% / 94% | 14% / 94% | 15% / 96% | 8% / 96% | 13% / 95% | +0.81 |
| Markov1(a=1,cut=24h,hl=24h) | 55% / 100% | 53% / 100% | 50% / 100% | 45% / 99% | 43% / 100% | 51% / 100% | 50% / 99% | 47% / 100% | 52% / 100% | +0.50 |
| MostFrequentLocation | 21% / 98% | 14% / 99% | 12% / 100% | 5% / 100% | 4% / 98% | 13% / 95% | 12% / 95% | 9% / 99% | 14% / 97% | +0.85 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 20% / 98% | 12% / 97% | 10% / 98% | 4% / 98% | 3% / 95% | 14% / 94% | 12% / 94% | 8% / 97% | 13% / 96% | +0.83 |
| SmoothedRecency(hl=6h,freq=24h) | 14% / 95% | 11% / 97% | 10% / 98% | 3% / 98% | 3% / 98% | 11% / 94% | 12% / 94% | 7% / 98% | 11% / 95% | +0.84 |
| TimetableLookup(bin=1h,days=all) | 31% / 98% | 30% / 99% | 31% / 99% | 25% / 99% | 26% / 97% | 32% / 95% | 31% / 96% | 28% / 98% | 31% / 97% | +0.67 |
| llm_naive/not_told/look_on | 5% / 85% | 4% / 89% | 3% / 87% | 2% / 88% | 2% / 89% | 6% / 83% | 6% / 81% | 4% / 87% | 4% / 85% | +0.70 |
| llm_naive/told/look_on | 5% / 86% | 4% / 89% | 4% / 87% | 1% / 88% | 1% / 89% | 7% / 83% | 5% / 82% | 4% / 88% | 4% / 85% | +0.70 |
| llm_recent/not_told/look_on | 5% / 86% | 3% / 88% | 3% / 86% | 2% / 88% | 2% / 88% | 4% / 83% | 3% / 80% | 3% / 87% | 3% / 84% | +0.69 |
| llm_recent/told/look_on | 6% / 83% | 3% / 88% | 3% / 85% | 2% / 87% | 1% / 88% | 6% / 82% | 4% / 79% | 4% / 87% | 3% / 83% | +0.67 |
| llm_summary/not_told/look_on | 5% / 89% | 1% / 93% | 1% / 90% | 1% / 89% | 1% / 91% | 2% / 85% | 3% / 91% | 1% / 90% | 2% / 90% | +0.78 |
| llm_summary/told/look_on | 4% / 90% | 2% / 94% | 1% / 90% | 1% / 90% | 1% / 93% | 2% / 86% | 2% / 91% | 1% / 91% | 2% / 90% | +0.80 |

## 5. Told vs not told, per day (LLM agents; hint message in the prompt from each shift day's first question on)

| agent | Wed° told / not | Thu° told / not | Fri° told / not | Sat* told / not | Sun* told / not | Mon° told / not | Tue° told / not | all told / not | shift told / not | non-shift told / not |
|---|---|---|---|---|---|---|---|---|---|---|
| llm_naive/look_on | 82% / 82% | 85% / 85% | 83% / 84% | 86% / 87% | 88% / 88% | 77% / 78% | 78% / 77% | 83% / 83% | 85% / 84% | 81% / 82% |
| llm_recent/look_on | 79% / 81% | 85% / 85% | 83% / 83% | 86% / 87% | 87% / 87% | 78% / 80% | 76% / 78% | 82% / 83% | 84% / 85% | 80% / 81% |
| llm_summary/look_on | 86% / 85% | 93% / 92% | 89% / 89% | 90% / 88% | 92% / 90% | 85% / 84% | 90% / 89% | 89% / 88% | 90% / 89% | 88% / 88% |

LLM parse fallbacks and look requests:

| agent | n | fallback | asked for a look | look found it | direct ABSTAIN |
|---|---|---|---|---|---|
| llm_naive/not_told/look_on | 3360 | 0% | 7% | 2% | 4% |
| llm_naive/told/look_on | 3360 | 0% | 7% | 2% | 4% |
| llm_recent/not_told/look_on | 3136 | 0% | 5% | 1% | 3% |
| llm_recent/told/look_on | 3136 | 0% | 6% | 1% | 3% |
| llm_summary/not_told/look_on | 3360 | 0% | 14% | 10% | 2% |
| llm_summary/told/look_on | 3360 | 0% | 16% | 11% | 2% |

## 6. Shift effect paired by household

For every household and agent: accuracy on the household's own shift days minus accuracy on its own non-shift days (`shift - non`), then the mean and the count of households where the difference is negative. Also aligned on each household's first major-event day (guests or illness, weekend days excluded): accuracy on the day before, the day, and the day after, mean over households that have such a day. Spot-only columns use in-house truths only, so the OUT_OF_HOUSE mix cannot drive the difference.

### look llm

| agent | mean(shift - non) | households with a drop | mean(shift - non), spot only | drop, spot only | event day -1 / 0 / +1 | event day -1 / 0 / +1, spot only | households with an event day |
|---|---|---|---|---|---|---|---|
| llm_naive/not_told/look_on | +3.3 | 1/5 | -3.5 | 4/5 | 81% / 79% / 83% | 93% / 89% / 93% | 4 |
| llm_naive/told/look_on | +4.0 | 1/5 | -3.0 | 4/5 | 81% / 79% / 84% | 92% / 89% / 93% | 4 |
| llm_recent/not_told/look_on | +4.1 | 1/5 | -2.4 | 3/5 | 82% / 80% / 84% | 91% / 89% / 94% | 4 |
| llm_recent/told/look_on | +3.9 | 1/5 | -2.8 | 3/5 | 81% / 79% / 83% | 91% / 88% / 94% | 4 |
| llm_summary/not_told/look_on | +1.3 | 1/5 | -1.7 | 4/5 | 86% / 85% / 92% | 92% / 90% / 92% | 4 |
| llm_summary/told/look_on | +2.4 | 1/5 | -1.1 | 2/5 | 87% / 87% / 92% | 94% / 91% / 96% | 4 |

### look off

| agent | mean(shift - non) | households with a drop | mean(shift - non), spot only | drop, spot only | event day -1 / 0 / +1 | event day -1 / 0 / +1, spot only | households with an event day |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | +3.3 | 2/5 | -3.5 | 4/5 | 74% / 74% / 78% | 86% / 86% / 88% | 4 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | +4.9 | 1/5 | -1.9 | 4/5 | 79% / 76% / 83% | 91% / 88% / 94% | 4 |
| LastObservation | +4.8 | 1/5 | -2.0 | 4/5 | 79% / 76% / 83% | 91% / 88% / 94% | 4 |
| Markov1(a=1,cut=24h,hl=24h) | +3.1 | 1/5 | -2.3 | 4/5 | 82% / 78% / 88% | 89% / 84% / 93% | 4 |
| MostFrequentLocation | +4.7 | 1/5 | -1.9 | 4/5 | 79% / 77% / 83% | 90% / 87% / 93% | 4 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | +4.5 | 1/5 | -2.2 | 4/5 | 81% / 77% / 84% | 91% / 88% / 94% | 4 |
| SmoothedRecency(hl=6h,freq=24h) | +4.8 | 1/5 | -2.0 | 4/5 | 79% / 76% / 83% | 91% / 88% / 94% | 4 |
| TimetableLookup(bin=1h,days=all) | +3.9 | 1/5 | -2.3 | 4/5 | 81% / 79% / 85% | 91% / 87% / 93% | 4 |

### look voi

| agent | mean(shift - non) | households with a drop | mean(shift - non), spot only | drop, spot only | event day -1 / 0 / +1 | event day -1 / 0 / +1, spot only | households with an event day |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | +2.9 | 1/5 | -1.6 | 4/5 | 91% / 88% / 90% | 98% / 94% / 95% | 4 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | +6.0 | 0/5 | +0.1 | 2/5 | 89% / 89% / 92% | 99% / 98% / 100% | 4 |
| LastObservation | +2.9 | 1/5 | -1.3 | 4/5 | 88% / 91% / 91% | 96% / 95% / 97% | 4 |
| Markov1(a=1,cut=24h,hl=24h) | +3.5 | 0/5 | -1.0 | 4/5 | 90% / 88% / 90% | 96% / 93% / 96% | 4 |
| MostFrequentLocation | +5.1 | 0/5 | -0.0 | 2/5 | 90% / 94% / 94% | 99% / 98% / 100% | 4 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | +3.3 | 0/5 | -0.6 | 4/5 | 89% / 90% / 93% | 96% / 97% / 98% | 4 |
| SmoothedRecency(hl=6h,freq=24h) | +5.0 | 0/5 | -0.2 | 2/5 | 91% / 91% / 91% | 99% / 98% / 100% | 4 |
| TimetableLookup(bin=1h,days=all) | +1.7 | 1/5 | -1.7 | 3/5 | 90% / 85% / 88% | 95% / 93% / 94% | 4 |

### Per-household accuracy per day (look voi / llm; `*` = that household's shift day)

**hh_s0** (shift days: Wed, Thu, Sat, Sun)

| agent | Wed* | Thu* | Fri | Sat* | Sun* | Mon | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 96% | 100% | 95% | 86% | 91% | 79% | 90% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 88% | 99% | 96% | 91% | 98% | 86% | 88% |
| LastObservation | 92% | 100% | 98% | 94% | 96% | 83% | 92% |
| Markov1(a=1,cut=24h,hl=24h) | 85% | 97% | 98% | 92% | 96% | 85% | 88% |
| MostFrequentLocation | 95% | 98% | 97% | 96% | 98% | 89% | 97% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 95% | 97% | 97% | 94% | 97% | 89% | 88% |
| SmoothedRecency(hl=6h,freq=24h) | 94% | 98% | 99% | 93% | 98% | 89% | 88% |
| TimetableLookup(bin=1h,days=all) | 90% | 92% | 95% | 91% | 89% | 79% | 84% |
| llm_naive/not_told/look_on | 85% | 95% | 94% | 90% | 96% | 70% | 79% |
| llm_naive/told/look_on | 89% | 95% | 92% | 89% | 96% | 70% | 79% |
| llm_recent/not_told/look_on | 84% | 95% | 92% | 90% | 93% | 71% | 76% |
| llm_recent/told/look_on | 82% | 95% | 92% | 90% | 92% | 71% | 76% |
| llm_summary/not_told/look_on | 91% | 93% | 94% | 91% | 94% | 76% | 95% |
| llm_summary/told/look_on | 92% | 98% | 94% | 93% | 97% | 77% | 89% |

**hh_s1** (shift days: Fri, Sat, Sun)

| agent | Wed | Thu | Fri* | Sat* | Sun* | Mon | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 97% | 85% | 95% | 93% | 90% | 88% | 76% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 84% | 80% | 92% | 100% | 94% | 90% | 79% |
| LastObservation | 91% | 82% | 95% | 95% | 88% | 92% | 84% |
| Markov1(a=1,cut=24h,hl=24h) | 81% | 85% | 90% | 94% | 83% | 94% | 81% |
| MostFrequentLocation | 93% | 81% | 97% | 100% | 93% | 91% | 79% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 93% | 83% | 92% | 97% | 88% | 90% | 78% |
| SmoothedRecency(hl=6h,freq=24h) | 89% | 85% | 93% | 99% | 91% | 88% | 75% |
| TimetableLookup(bin=1h,days=all) | 93% | 85% | 95% | 95% | 82% | 85% | 78% |
| llm_naive/not_told/look_on | 83% | 73% | 85% | 89% | 81% | 84% | 72% |
| llm_naive/told/look_on | 83% | 73% | 84% | 89% | 82% | 81% | 73% |
| llm_recent/not_told/look_on | 83% | 75% | 82% | 89% | 81% | 83% | 70% |
| llm_recent/told/look_on | 83% | 75% | 83% | 89% | 82% | 84% | 70% |
| llm_summary/not_told/look_on | 83% | 85% | 89% | 91% | 91% | 84% | 84% |
| llm_summary/told/look_on | 83% | 85% | 90% | 89% | 88% | 88% | 91% |

**hh_s2** (shift days: Sat, Sun, Tue)

| agent | Wed | Thu | Fri | Sat* | Sun* | Mon | Tue* |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 78% | 97% | 96% | 97% | 90% | 89% | 93% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 79% | 98% | 99% | 97% | 95% | 88% | 96% |
| LastObservation | 75% | 98% | 95% | 93% | 88% | 85% | 93% |
| Markov1(a=1,cut=24h,hl=24h) | 74% | 97% | 94% | 95% | 90% | 88% | 90% |
| MostFrequentLocation | 80% | 96% | 97% | 97% | 92% | 92% | 96% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 80% | 96% | 97% | 96% | 89% | 86% | 95% |
| SmoothedRecency(hl=6h,freq=24h) | 80% | 97% | 99% | 97% | 95% | 90% | 96% |
| TimetableLookup(bin=1h,days=all) | 78% | 93% | 91% | 86% | 74% | 86% | 81% |
| llm_naive/not_told/look_on | 67% | 94% | 83% | 90% | 81% | 79% | 76% |
| llm_naive/told/look_on | 67% | 94% | 83% | 90% | 81% | 78% | 77% |
| llm_recent/not_told/look_on | 67% | 94% | 80% | 89% | 82% | 79% | 79% |
| llm_recent/told/look_on | 67% | 94% | 80% | 89% | 82% | 78% | 79% |
| llm_summary/not_told/look_on | 72% | 96% | 86% | 91% | 85% | 83% | 80% |
| llm_summary/told/look_on | 74% | 96% | 86% | 94% | 89% | 83% | 86% |

**hh_s3** (shift days: Sat, Sun)

| agent | Wed | Thu | Fri | Sat* | Sun* | Mon | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 94% | 93% | 92% | 91% | 95% | 88% | 91% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 91% | 90% | 96% | 95% | 98% | 93% | 98% |
| LastObservation | 97% | 92% | 94% | 91% | 95% | 91% | 95% |
| Markov1(a=1,cut=24h,hl=24h) | 97% | 83% | 93% | 94% | 94% | 94% | 95% |
| MostFrequentLocation | 96% | 97% | 94% | 96% | 99% | 96% | 97% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 95% | 88% | 94% | 94% | 95% | 93% | 96% |
| SmoothedRecency(hl=6h,freq=24h) | 91% | 91% | 98% | 94% | 98% | 94% | 97% |
| TimetableLookup(bin=1h,days=all) | 93% | 89% | 96% | 94% | 96% | 82% | 95% |
| llm_naive/not_told/look_on | 99% | 80% | 90% | 80% | 89% | 88% | 92% |
| llm_naive/told/look_on | 98% | 81% | 90% | 82% | 90% | 88% | 92% |
| llm_recent/not_told/look_on | 97% | 78% | 89% | 82% | 89% | 89% | 93% |
| llm_recent/told/look_on | 97% | 78% | 89% | 81% | 92% | 89% | 94% |
| llm_summary/not_told/look_on | 98% | 94% | 97% | 82% | 93% | 93% | 92% |
| llm_summary/told/look_on | 98% | 95% | 94% | 84% | 95% | 95% | 93% |

**hh_s4** (shift days: Sat, Sun, Mon, Tue)

| agent | Wed | Thu | Fri | Sat* | Sun* | Mon* | Tue* |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 91% | 85% | 82% | 95% | 98% | 69% | 78% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 84% | 85% | 75% | 97% | 100% | 79% | 76% |
| LastObservation | 88% | 89% | 79% | 97% | 96% | 83% | 77% |
| Markov1(a=1,cut=24h,hl=24h) | 75% | 88% | 80% | 91% | 96% | 85% | 79% |
| MostFrequentLocation | 88% | 86% | 82% | 99% | 98% | 89% | 84% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 91% | 83% | 86% | 95% | 96% | 78% | 84% |
| SmoothedRecency(hl=6h,freq=24h) | 85% | 88% | 76% | 97% | 98% | 80% | 76% |
| TimetableLookup(bin=1h,days=all) | 82% | 84% | 85% | 94% | 98% | 75% | 77% |
| llm_naive/not_told/look_on | 74% | 84% | 68% | 85% | 92% | 69% | 66% |
| llm_naive/told/look_on | 74% | 84% | 68% | 83% | 92% | 68% | 68% |
| llm_recent/not_told/look_on | 72% | 84% | 70% | 84% | 91% | 75% | 67% |
| llm_recent/told/look_on | 71% | 83% | 71% | 80% | 90% | 71% | 67% |
| llm_summary/not_told/look_on | 82% | 91% | 79% | 86% | 90% | 82% | 92% |
| llm_summary/told/look_on | 84% | 90% | 82% | 89% | 93% | 81% | 90% |

