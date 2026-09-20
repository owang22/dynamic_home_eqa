# LLM agents vs classical agents, 4 h patrol, households: hh_s0 hh_s1 hh_s2 hh_s3 hh_s4 hh_s5 hh_s6 hh_s7 hh_s8 hh_s9 

10 households (hh_s0, hh_s1, hh_s2, hh_s3, hh_s4, hh_s5, hh_s6, hh_s7, hh_s8, hh_s9), 22 agents, patrol every [4] h, look on/off = ['llm', 'off', 'voi']. 71680 agent-question records. Shift days per household: hh_s0: [1, 2, 4, 5]; hh_s1: [3, 4, 5]; hh_s2: [4, 5, 7]; hh_s3: [4, 5]; hh_s4: [4, 5, 6, 7]; hh_s5: [2, 4, 5]; hh_s6: [4, 5]; hh_s7: [4, 5]; hh_s8: [1, 3, 4, 5, 7]; hh_s9: [3, 4, 5, 6].

Records per household: hh_s0 7168, hh_s1 7168, hh_s2 7168, hh_s3 7168, hh_s4 7168, hh_s5 7168, hh_s6 7168, hh_s7 7168, hh_s8 7168, hh_s9 7168

## 1. Accuracy per day per agent (no abstaining; shift days marked *)

### patrol every 4 h, look llm

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| llm_naive/not_told/look_on | 84% | 81% | 81% | 82% | 88% | 77% | 77% | 81% | 83% | 80% | 90% | 31% | 7% |
| llm_naive/told/look_on | 84% | 81% | 80% | 82% | 89% | 77% | 78% | 82% | 83% | 80% | 90% | 31% | 8% |
| llm_recent/not_told/look_on | 82% | 81% | 79% | 82% | 87% | 78% | 78% | 81% | 82% | 80% | 89% | 24% | 6% |
| llm_recent/told/look_on | 82% | 81% | 79% | 81% | 87% | 78% | 79% | 81% | 82% | 80% | 89% | 21% | 8% |
| llm_summary/not_told/look_on | 84% | 87% | 88% | 84% | 89% | 82% | 84% | 85% | 86% | 85% | 90% | 55% | 43% |
| llm_summary/told/look_on | 83% | 86% | 87% | 85% | 92% | 83% | 84% | 86% | 88% | 84% | 91% | 69% | 35% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| llm_naive/not_told/look_on | 1451 | 71% | 789 | 100% |
| llm_naive/told/look_on | 1451 | 72% | 789 | 100% |
| llm_recent/not_told/look_on | 1451 | 71% | 789 | 100% |
| llm_recent/told/look_on | 1451 | 71% | 789 | 100% |
| llm_summary/not_told/look_on | 1451 | 78% | 789 | 99% |
| llm_summary/told/look_on | 1451 | 78% | 789 | 100% |

Questions by truth type: on_person 29, out_of_house 206, spot 2005
(* every household shifts that day; ° some households do)

### patrol every 4 h, look off

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 79% | 79% | 77% | 73% | 83% | 71% | 65% | 75% | 77% | 74% | 84% | 0% | 0% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 79% | 79% | 79% | 81% | 88% | 76% | 77% | 80% | 82% | 78% | 89% | 0% | 0% |
| LastObservation | 79% | 79% | 79% | 81% | 88% | 76% | 78% | 80% | 82% | 78% | 89% | 0% | 0% |
| Markov1(a=1,cut=24h,hl=24h) | 82% | 83% | 81% | 80% | 87% | 79% | 80% | 82% | 83% | 81% | 88% | 21% | 33% |
| MostFrequentLocation | 81% | 79% | 79% | 81% | 87% | 76% | 77% | 80% | 82% | 78% | 89% | 0% | 3% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 81% | 80% | 79% | 81% | 88% | 76% | 78% | 80% | 82% | 79% | 89% | 7% | 4% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 79% | 79% | 78% | 80% | 83% | 71% | 75% | 78% | 80% | 76% | 87% | 0% | 0% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 79% | 79% | 79% | 80% | 86% | 71% | 75% | 79% | 81% | 77% | 88% | 0% | 0% |
| SmoothedRecency(hl=6h,freq=24h) | 79% | 79% | 79% | 81% | 88% | 76% | 78% | 80% | 82% | 78% | 89% | 3% | 0% |
| TimetableLookup(bin=1h,days=all) | 82% | 79% | 80% | 81% | 85% | 75% | 77% | 80% | 82% | 78% | 88% | 0% | 10% |
| llm_naive/not_told/look_off | 81% | 81% | 79% | 82% | 88% | 76% | 76% | 80% | 83% | 78% | 89% | 28% | 3% |
| llm_naive/told/look_off | 81% | 81% | 78% | 82% | 88% | 76% | 77% | 80% | 82% | 78% | 89% | 31% | 4% |
| llm_recent/not_told/look_off | 80% | 80% | 78% | 81% | 87% | 76% | 77% | 80% | 82% | 78% | 88% | 24% | 6% |
| llm_recent/told/look_off | 80% | 80% | 78% | 80% | 87% | 75% | 78% | 80% | 82% | 78% | 88% | 24% | 5% |
| llm_summary/not_told/look_off | 82% | 81% | 81% | 80% | 85% | 77% | 73% | 80% | 81% | 79% | 86% | 38% | 24% |
| llm_summary/told/look_off | 82% | 82% | 79% | 80% | 87% | 74% | 72% | 79% | 82% | 77% | 87% | 34% | 15% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 1451 | 63% | 789 | 99% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 1451 | 69% | 789 | 100% |
| LastObservation | 1451 | 69% | 789 | 100% |
| Markov1(a=1,cut=24h,hl=24h) | 1451 | 72% | 789 | 100% |
| MostFrequentLocation | 1451 | 69% | 789 | 100% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 1451 | 70% | 789 | 100% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 1451 | 66% | 789 | 99% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 1451 | 67% | 789 | 100% |
| SmoothedRecency(hl=6h,freq=24h) | 1451 | 69% | 789 | 100% |
| TimetableLookup(bin=1h,days=all) | 1451 | 69% | 789 | 100% |
| llm_naive/not_told/look_off | 1451 | 70% | 789 | 100% |
| llm_naive/told/look_off | 1451 | 70% | 789 | 100% |
| llm_recent/not_told/look_off | 1451 | 69% | 789 | 100% |
| llm_recent/told/look_off | 1451 | 69% | 789 | 100% |
| llm_summary/not_told/look_off | 1451 | 69% | 789 | 100% |
| llm_summary/told/look_off | 1451 | 69% | 789 | 99% |

Questions by truth type: on_person 29, out_of_house 206, spot 2005
(* every household shifts that day; ° some households do)

### patrol every 4 h, look voi

| agent | Wed° | Thu° | Fri° | Sat* | Sun* | Mon° | Tue° | all | shift | non-shift | spot | on_person | out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 93% | 92% | 91% | 91% | 92% | 84% | 86% | 90% | 91% | 89% | 95% | 38% | 45% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 86% | 91% | 88% | 95% | 97% | 88% | 88% | 90% | 93% | 88% | 99% | 10% | 20% |
| LastObservation | 90% | 92% | 92% | 90% | 94% | 88% | 89% | 91% | 91% | 90% | 96% | 41% | 50% |
| Markov1(a=1,cut=24h,hl=24h) | 84% | 90% | 91% | 89% | 92% | 90% | 88% | 89% | 90% | 88% | 95% | 55% | 41% |
| MostFrequentLocation | 90% | 91% | 92% | 95% | 97% | 90% | 92% | 92% | 94% | 91% | 98% | 28% | 43% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 91% | 91% | 91% | 92% | 95% | 88% | 89% | 91% | 92% | 90% | 97% | 17% | 41% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 82% | 87% | 87% | 93% | 96% | 83% | 85% | 88% | 91% | 84% | 98% | 0% | 0% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 83% | 87% | 87% | 93% | 96% | 83% | 85% | 88% | 91% | 85% | 98% | 0% | 0% |
| SmoothedRecency(hl=6h,freq=24h) | 89% | 92% | 91% | 95% | 97% | 89% | 88% | 91% | 93% | 90% | 98% | 24% | 36% |
| TimetableLookup(bin=1h,days=all) | 88% | 88% | 90% | 90% | 88% | 82% | 82% | 87% | 88% | 86% | 92% | 45% | 43% |

Objects that moved in the 24 h before the question vs. objects that did not:

| agent | moved: n | moved: acc | still: n | still: acc |
|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 1451 | 85% | 789 | 99% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 1451 | 85% | 789 | 100% |
| LastObservation | 1451 | 86% | 789 | 100% |
| Markov1(a=1,cut=24h,hl=24h) | 1451 | 83% | 789 | 100% |
| MostFrequentLocation | 1451 | 88% | 789 | 100% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 1451 | 86% | 789 | 100% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 1451 | 81% | 789 | 100% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 1451 | 81% | 789 | 100% |
| SmoothedRecency(hl=6h,freq=24h) | 1451 | 87% | 789 | 100% |
| TimetableLookup(bin=1h,days=all) | 1451 | 80% | 789 | 99% |

Questions by truth type: on_person 29, out_of_house 206, spot 2005
(* every household shifts that day; ° some households do)

## 2. Accuracy vs patrol density (all days, no abstaining)

### look llm

| agent | every 4 h |
|---|---|
| llm_naive/not_told/look_on | 81% |
| llm_naive/told/look_on | 82% |
| llm_recent/not_told/look_on | 81% |
| llm_recent/told/look_on | 81% |
| llm_summary/not_told/look_on | 85% |
| llm_summary/told/look_on | 86% |

### look off

| agent | every 4 h |
|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 75% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 80% |
| LastObservation | 80% |
| Markov1(a=1,cut=24h,hl=24h) | 82% |
| MostFrequentLocation | 80% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 80% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 78% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 79% |
| SmoothedRecency(hl=6h,freq=24h) | 80% |
| TimetableLookup(bin=1h,days=all) | 80% |
| llm_naive/not_told/look_off | 80% |
| llm_naive/told/look_off | 80% |
| llm_recent/not_told/look_off | 80% |
| llm_recent/told/look_off | 80% |
| llm_summary/not_told/look_off | 80% |
| llm_summary/told/look_off | 79% |

### look voi

| agent | every 4 h |
|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 90% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 90% |
| LastObservation | 91% |
| Markov1(a=1,cut=24h,hl=24h) | 89% |
| MostFrequentLocation | 92% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 91% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 88% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 88% |
| SmoothedRecency(hl=6h,freq=24h) | 91% |
| TimetableLookup(bin=1h,days=all) | 87% |

## 3. What the free look is worth (all densities pooled)

| agent | look off | look voi | look top | before-look answer (voi runs) | found by voi look | found by top look |
|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 75% | 90% | - | 78% | 51% | - |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 80% | 90% | - | 82% | 52% | - |
| LastObservation | 80% | 91% | - | 83% | 43% | - |
| Markov1(a=1,cut=24h,hl=24h) | 82% | 89% | - | 86% | 42% | - |
| MostFrequentLocation | 80% | 92% | - | 82% | 52% | - |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 80% | 91% | - | 83% | 47% | - |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 78% | 88% | - | 82% | 48% | - |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 79% | 88% | - | 82% | 48% | - |
| SmoothedRecency(hl=6h,freq=24h) | 80% | 91% | - | 83% | 46% | - |
| TimetableLookup(bin=1h,days=all) | 80% | 87% | - | 78% | 44% | - |
| llm_naive/not_told/look_off | 80% | - | - | - | - | - |
| llm_naive/not_told/look_on | - | - | - | - | - | - |
| llm_naive/told/look_off | 80% | - | - | - | - | - |
| llm_naive/told/look_on | - | - | - | - | - | - |
| llm_recent/not_told/look_off | 80% | - | - | - | - | - |
| llm_recent/not_told/look_on | - | - | - | - | - | - |
| llm_recent/told/look_off | 80% | - | - | - | - | - |
| llm_recent/told/look_on | - | - | - | - | - | - |
| llm_summary/not_told/look_off | 80% | - | - | - | - | - |
| llm_summary/not_told/look_on | - | - | - | - | - | - |
| llm_summary/told/look_off | 79% | - | - | - | - | - |
| llm_summary/told/look_on | - | - | - | - | - | - |

Look gain by confidence before the look (pooled over agents, look-on runs):

| top prob before look | n | acc before look | acc after look |
|---|---|---|---|
| [0.00, 0.40) | 2018 | 54% | 67% |
| [0.40, 0.60) | 1493 | 54% | 75% |
| [0.60, 0.80) | 2199 | 64% | 82% |
| [0.80, 0.95) | 5518 | 73% | 84% |
| [0.95, 1.01) | 24612 | 89% | 91% |

## 4. Abstain rate and answered-accuracy per day (look voi for classical agents, look on for LLM agents; all densities pooled)

### outright ABSTAIN answers only (LLM direct route)

| agent | Wed abstain / acc | Thu abstain / acc | Fri abstain / acc | Sat abstain / acc | Sun abstain / acc | Mon abstain / acc | Tue abstain / acc | shift abstain / acc | non-shift abstain / acc | mean score |
|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0% / 93% | 0% / 92% | 0% / 91% | 0% / 91% | 0% / 92% | 0% / 84% | 0% / 86% | 0% / 91% | 0% / 89% | +0.80 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0% / 86% | 0% / 91% | 0% / 88% | 0% / 95% | 0% / 97% | 0% / 88% | 0% / 88% | 0% / 93% | 0% / 88% | +0.81 |
| LastObservation | 0% / 90% | 0% / 92% | 0% / 92% | 0% / 90% | 0% / 94% | 0% / 88% | 0% / 89% | 0% / 91% | 0% / 90% | +0.81 |
| Markov1(a=1,cut=24h,hl=24h) | 0% / 84% | 0% / 90% | 0% / 91% | 0% / 89% | 0% / 92% | 0% / 90% | 0% / 88% | 0% / 90% | 0% / 88% | +0.78 |
| MostFrequentLocation | 0% / 90% | 0% / 91% | 0% / 92% | 0% / 95% | 0% / 97% | 0% / 90% | 0% / 92% | 0% / 94% | 0% / 91% | +0.85 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0% / 91% | 0% / 91% | 0% / 91% | 0% / 92% | 0% / 95% | 0% / 88% | 0% / 89% | 0% / 92% | 0% / 90% | +0.82 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 0% / 82% | 0% / 87% | 0% / 87% | 0% / 93% | 0% / 96% | 0% / 83% | 0% / 85% | 0% / 91% | 0% / 84% | +0.75 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 0% / 83% | 0% / 87% | 0% / 87% | 0% / 93% | 0% / 96% | 0% / 83% | 0% / 85% | 0% / 91% | 0% / 85% | +0.75 |
| SmoothedRecency(hl=6h,freq=24h) | 0% / 89% | 0% / 92% | 0% / 91% | 0% / 95% | 0% / 97% | 0% / 89% | 0% / 88% | 0% / 93% | 0% / 90% | +0.83 |
| TimetableLookup(bin=1h,days=all) | 0% / 88% | 0% / 88% | 0% / 90% | 0% / 90% | 0% / 88% | 0% / 82% | 0% / 82% | 0% / 88% | 0% / 86% | +0.74 |
| llm_naive/not_told/look_on | 3% / 86% | 3% / 84% | 5% / 85% | 1% / 83% | 1% / 89% | 6% / 81% | 2% / 79% | 2% / 85% | 4% / 83% | +0.66 |
| llm_naive/told/look_on | 3% / 86% | 3% / 84% | 5% / 84% | 1% / 82% | 0% / 89% | 6% / 82% | 2% / 80% | 2% / 85% | 4% / 84% | +0.66 |
| llm_recent/not_told/look_on | 3% / 85% | 2% / 82% | 4% / 83% | 0% / 82% | 1% / 87% | 5% / 82% | 3% / 81% | 2% / 84% | 3% / 82% | +0.65 |
| llm_recent/told/look_on | 3% / 85% | 2% / 82% | 4% / 83% | 0% / 81% | 0% / 87% | 6% / 82% | 2% / 81% | 2% / 84% | 3% / 82% | +0.64 |
| llm_summary/not_told/look_on | 4% / 87% | 1% / 87% | 1% / 88% | 1% / 84% | 0% / 89% | 1% / 83% | 2% / 86% | 1% / 86% | 2% / 87% | +0.72 |
| llm_summary/told/look_on | 4% / 86% | 2% / 87% | 2% / 88% | 1% / 86% | 0% / 92% | 1% / 84% | 2% / 86% | 1% / 88% | 2% / 86% | +0.73 |

### threshold 0.4 on the top probability / stated confidence, plus outright ABSTAIN answers

| agent | Wed abstain / acc | Thu abstain / acc | Fri abstain / acc | Sat abstain / acc | Sun abstain / acc | Mon abstain / acc | Tue abstain / acc | shift abstain / acc | non-shift abstain / acc | mean score |
|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 12% / 96% | 9% / 97% | 9% / 96% | 5% / 92% | 2% / 94% | 10% / 90% | 11% / 90% | 6% / 94% | 10% / 93% | +0.80 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 10% / 93% | 7% / 94% | 6% / 93% | 2% / 96% | 1% / 97% | 8% / 93% | 7% / 93% | 4% / 96% | 8% / 93% | +0.83 |
| LastObservation | 12% / 95% | 9% / 96% | 11% / 98% | 6% / 94% | 2% / 94% | 10% / 93% | 10% / 93% | 6% / 94% | 11% / 95% | +0.82 |
| Markov1(a=1,cut=24h,hl=24h) | 48% / 95% | 36% / 95% | 35% / 100% | 36% / 96% | 28% / 98% | 31% / 95% | 33% / 95% | 33% / 96% | 37% / 96% | +0.60 |
| MostFrequentLocation | 12% / 96% | 9% / 95% | 10% / 97% | 5% / 98% | 2% / 98% | 8% / 95% | 9% / 95% | 5% / 96% | 10% / 96% | +0.85 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 13% / 97% | 9% / 96% | 9% / 96% | 5% / 96% | 2% / 96% | 8% / 92% | 8% / 93% | 5% / 95% | 10% / 95% | +0.83 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 0% / 82% | 0% / 87% | 0% / 87% | 0% / 93% | 0% / 96% | 0% / 83% | 0% / 85% | 0% / 91% | 0% / 85% | +0.75 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 0% / 83% | 0% / 87% | 0% / 87% | 0% / 93% | 0% / 96% | 0% / 83% | 0% / 85% | 0% / 91% | 0% / 85% | +0.75 |
| SmoothedRecency(hl=6h,freq=24h) | 12% / 94% | 9% / 95% | 8% / 95% | 4% / 97% | 2% / 98% | 10% / 93% | 9% / 94% | 5% / 96% | 10% / 94% | +0.83 |
| TimetableLookup(bin=1h,days=all) | 16% / 95% | 17% / 96% | 16% / 96% | 13% / 97% | 14% / 95% | 18% / 94% | 20% / 93% | 14% / 95% | 18% / 95% | +0.76 |
| llm_naive/not_told/look_on | 3% / 87% | 3% / 84% | 5% / 85% | 1% / 83% | 1% / 89% | 7% / 82% | 2% / 79% | 2% / 85% | 4% / 84% | +0.66 |
| llm_naive/told/look_on | 3% / 87% | 3% / 84% | 5% / 84% | 1% / 82% | 0% / 89% | 6% / 82% | 3% / 81% | 2% / 85% | 4% / 84% | +0.66 |
| llm_recent/not_told/look_on | 3% / 85% | 2% / 82% | 4% / 83% | 0% / 82% | 1% / 87% | 5% / 82% | 3% / 81% | 2% / 84% | 3% / 82% | +0.65 |
| llm_recent/told/look_on | 3% / 85% | 2% / 82% | 4% / 83% | 0% / 81% | 0% / 87% | 6% / 82% | 2% / 81% | 2% / 84% | 3% / 82% | +0.64 |
| llm_summary/not_told/look_on | 4% / 87% | 1% / 87% | 1% / 88% | 1% / 84% | 0% / 89% | 1% / 83% | 2% / 86% | 1% / 86% | 2% / 87% | +0.72 |
| llm_summary/told/look_on | 4% / 86% | 2% / 87% | 2% / 88% | 1% / 85% | 0% / 92% | 2% / 84% | 3% / 87% | 1% / 88% | 3% / 86% | +0.73 |

### threshold 0.5 on the top probability / stated confidence, plus outright ABSTAIN answers

| agent | Wed abstain / acc | Thu abstain / acc | Fri abstain / acc | Sat abstain / acc | Sun abstain / acc | Mon abstain / acc | Tue abstain / acc | shift abstain / acc | non-shift abstain / acc | mean score |
|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 14% / 97% | 12% / 98% | 11% / 97% | 5% / 93% | 2% / 94% | 14% / 93% | 13% / 91% | 7% / 94% | 13% / 95% | +0.80 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 11% / 94% | 8% / 95% | 8% / 95% | 3% / 97% | 1% / 97% | 11% / 94% | 8% / 94% | 5% / 97% | 9% / 94% | +0.84 |
| LastObservation | 14% / 96% | 12% / 98% | 12% / 98% | 6% / 94% | 2% / 94% | 14% / 95% | 13% / 95% | 8% / 95% | 13% / 96% | +0.82 |
| Markov1(a=1,cut=24h,hl=24h) | 57% / 100% | 49% / 99% | 49% / 100% | 44% / 98% | 38% / 98% | 45% / 98% | 45% / 97% | 44% / 98% | 49% / 99% | +0.52 |
| MostFrequentLocation | 16% / 98% | 12% / 97% | 11% / 97% | 5% / 98% | 2% / 98% | 11% / 95% | 11% / 96% | 7% / 98% | 12% / 97% | +0.85 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 16% / 98% | 11% / 97% | 10% / 96% | 5% / 96% | 2% / 96% | 12% / 94% | 9% / 93% | 6% / 96% | 12% / 96% | +0.83 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 0% / 82% | 0% / 87% | 1% / 87% | 1% / 94% | 0% / 96% | 0% / 83% | 1% / 85% | 0% / 92% | 0% / 85% | +0.75 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 0% / 83% | 0% / 87% | 1% / 87% | 1% / 94% | 0% / 96% | 1% / 84% | 1% / 86% | 1% / 92% | 0% / 85% | +0.76 |
| SmoothedRecency(hl=6h,freq=24h) | 12% / 94% | 10% / 96% | 9% / 96% | 4% / 97% | 2% / 98% | 11% / 94% | 10% / 95% | 6% / 97% | 11% / 95% | +0.84 |
| TimetableLookup(bin=1h,days=all) | 25% / 98% | 24% / 97% | 24% / 98% | 19% / 97% | 19% / 96% | 26% / 95% | 27% / 94% | 21% / 96% | 26% / 97% | +0.71 |
| llm_naive/not_told/look_on | 4% / 87% | 3% / 84% | 5% / 85% | 1% / 83% | 1% / 89% | 7% / 82% | 2% / 79% | 2% / 85% | 4% / 84% | +0.66 |
| llm_naive/told/look_on | 3% / 87% | 3% / 84% | 5% / 84% | 1% / 83% | 1% / 89% | 7% / 83% | 3% / 81% | 2% / 85% | 4% / 84% | +0.67 |
| llm_recent/not_told/look_on | 3% / 85% | 2% / 82% | 4% / 83% | 1% / 83% | 1% / 88% | 5% / 82% | 3% / 81% | 2% / 84% | 3% / 82% | +0.65 |
| llm_recent/told/look_on | 3% / 85% | 2% / 82% | 4% / 83% | 1% / 82% | 1% / 87% | 6% / 82% | 2% / 81% | 2% / 84% | 3% / 82% | +0.65 |
| llm_summary/not_told/look_on | 4% / 87% | 1% / 87% | 1% / 88% | 1% / 84% | 1% / 89% | 1% / 83% | 2% / 86% | 1% / 86% | 2% / 87% | +0.72 |
| llm_summary/told/look_on | 4% / 87% | 2% / 87% | 2% / 88% | 1% / 85% | 1% / 92% | 2% / 84% | 3% / 87% | 1% / 88% | 3% / 86% | +0.73 |

### threshold 0.6 on the top probability / stated confidence, plus outright ABSTAIN answers

| agent | Wed abstain / acc | Thu abstain / acc | Fri abstain / acc | Sat abstain / acc | Sun abstain / acc | Mon abstain / acc | Tue abstain / acc | shift abstain / acc | non-shift abstain / acc | mean score |
|---|---|---|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 14% / 97% | 12% / 98% | 11% / 97% | 6% / 93% | 2% / 95% | 15% / 94% | 13% / 92% | 8% / 95% | 13% / 95% | +0.81 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 13% / 96% | 8% / 95% | 9% / 96% | 3% / 97% | 2% / 98% | 12% / 95% | 9% / 94% | 6% / 97% | 10% / 95% | +0.84 |
| LastObservation | 14% / 96% | 12% / 98% | 12% / 98% | 6% / 94% | 2% / 94% | 14% / 95% | 13% / 95% | 8% / 95% | 13% / 96% | +0.82 |
| Markov1(a=1,cut=24h,hl=24h) | 58% / 100% | 53% / 100% | 55% / 100% | 51% / 99% | 46% / 99% | 53% / 100% | 52% / 99% | 51% / 99% | 54% / 100% | +0.47 |
| MostFrequentLocation | 17% / 98% | 13% / 98% | 12% / 98% | 6% / 98% | 3% / 98% | 13% / 96% | 11% / 96% | 7% / 98% | 14% / 97% | +0.85 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 16% / 98% | 12% / 97% | 11% / 97% | 5% / 96% | 2% / 96% | 13% / 95% | 10% / 94% | 7% / 96% | 13% / 96% | +0.83 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 1% / 84% | 1% / 88% | 4% / 90% | 1% / 94% | 0% / 96% | 2% / 85% | 3% / 87% | 1% / 92% | 2% / 86% | +0.77 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 1% / 84% | 0% / 87% | 4% / 90% | 1% / 94% | 0% / 96% | 3% / 86% | 2% / 87% | 1% / 92% | 2% / 86% | +0.77 |
| SmoothedRecency(hl=6h,freq=24h) | 13% / 95% | 11% / 97% | 9% / 96% | 4% / 98% | 2% / 98% | 12% / 95% | 11% / 95% | 6% / 97% | 11% / 96% | +0.84 |
| TimetableLookup(bin=1h,days=all) | 29% / 98% | 30% / 98% | 32% / 97% | 26% / 98% | 26% / 97% | 32% / 96% | 34% / 96% | 28% / 97% | 32% / 97% | +0.66 |
| llm_naive/not_told/look_on | 4% / 87% | 3% / 84% | 5% / 85% | 1% / 83% | 1% / 89% | 7% / 82% | 2% / 79% | 2% / 85% | 4% / 84% | +0.66 |
| llm_naive/told/look_on | 3% / 87% | 3% / 84% | 5% / 84% | 1% / 83% | 1% / 89% | 7% / 83% | 3% / 81% | 2% / 85% | 4% / 84% | +0.67 |
| llm_recent/not_told/look_on | 3% / 85% | 2% / 82% | 4% / 83% | 1% / 83% | 1% / 88% | 5% / 82% | 3% / 81% | 2% / 84% | 3% / 82% | +0.65 |
| llm_recent/told/look_on | 3% / 85% | 2% / 82% | 4% / 83% | 1% / 82% | 1% / 87% | 6% / 82% | 2% / 81% | 2% / 84% | 3% / 82% | +0.65 |
| llm_summary/not_told/look_on | 4% / 87% | 1% / 87% | 1% / 88% | 1% / 84% | 1% / 89% | 1% / 83% | 2% / 86% | 1% / 86% | 2% / 87% | +0.72 |
| llm_summary/told/look_on | 4% / 87% | 2% / 87% | 2% / 88% | 1% / 85% | 1% / 92% | 2% / 84% | 3% / 87% | 1% / 88% | 3% / 86% | +0.73 |

## 5. Told vs not told, per day (LLM agents; hint message in the prompt from each shift day's first question on)

| agent | Wed° told / not | Thu° told / not | Fri° told / not | Sat* told / not | Sun* told / not | Mon° told / not | Tue° told / not | all told / not | shift told / not | non-shift told / not |
|---|---|---|---|---|---|---|---|---|---|---|
| llm_naive/look_off | 81% / 81% | 81% / 81% | 78% / 79% | 82% / 82% | 88% / 88% | 76% / 76% | 77% / 76% | 80% / 80% | 82% / 83% | 78% / 78% |
| llm_naive/look_on | 84% / 84% | 81% / 81% | 80% / 81% | 82% / 82% | 89% / 88% | 77% / 77% | 78% / 77% | 82% / 81% | 83% / 83% | 80% / 80% |
| llm_recent/look_off | 80% / 80% | 80% / 80% | 78% / 78% | 80% / 81% | 87% / 87% | 75% / 76% | 78% / 77% | 80% / 80% | 82% / 82% | 78% / 78% |
| llm_recent/look_on | 82% / 82% | 81% / 81% | 79% / 79% | 81% / 82% | 87% / 87% | 78% / 78% | 79% / 78% | 81% / 81% | 82% / 82% | 80% / 80% |
| llm_summary/look_off | 82% / 82% | 82% / 81% | 79% / 81% | 80% / 80% | 87% / 85% | 74% / 77% | 72% / 73% | 79% / 80% | 82% / 81% | 77% / 79% |
| llm_summary/look_on | 83% / 84% | 86% / 87% | 87% / 88% | 85% / 84% | 92% / 89% | 83% / 82% | 84% / 84% | 86% / 85% | 88% / 86% | 84% / 85% |

LLM parse fallbacks and look requests:

| agent | n | fallback | asked for a look | look found it | direct ABSTAIN |
|---|---|---|---|---|---|
| llm_naive/not_told/look_off | 2240 | 0% | 0% | 0% | 0% |
| llm_naive/not_told/look_on | 2240 | 0% | 6% | 2% | 3% |
| llm_naive/told/look_off | 2240 | 0% | 0% | 0% | 0% |
| llm_naive/told/look_on | 2240 | 0% | 7% | 2% | 3% |
| llm_recent/not_told/look_off | 2240 | 0% | 0% | 0% | 4% |
| llm_recent/not_told/look_on | 2240 | 0% | 4% | 1% | 3% |
| llm_recent/told/look_off | 2240 | 0% | 0% | 0% | 4% |
| llm_recent/told/look_on | 2240 | 0% | 4% | 1% | 3% |
| llm_summary/not_told/look_off | 2240 | 0% | 0% | 0% | 2% |
| llm_summary/not_told/look_on | 2240 | 0% | 12% | 8% | 1% |
| llm_summary/told/look_off | 2240 | 0% | 0% | 0% | 2% |
| llm_summary/told/look_on | 2240 | 0% | 14% | 9% | 2% |

## 6. Shift effect paired by household

For every household and agent: accuracy on the household's own shift days minus accuracy on its own non-shift days (`shift - non`), then the mean and the count of households where the difference is negative. Also aligned on each household's first major-event day (guests or illness, weekend days excluded): accuracy on the day before, the day, and the day after, mean over households that have such a day. Spot-only columns use in-house truths only, so the OUT_OF_HOUSE mix cannot drive the difference.

### look llm

| agent | mean(shift - non) | households with a drop | mean(shift - non), spot only | drop, spot only | event day -1 / 0 / +1 | event day -1 / 0 / +1, spot only | households with an event day |
|---|---|---|---|---|---|---|---|
| llm_naive/not_told/look_on | +3.1 | 4/10 | -2.9 | 7/10 | 80% / 81% / 80% | 90% / 90% / 89% | 7 |
| llm_naive/told/look_on | +3.4 | 4/10 | -2.6 | 8/10 | 80% / 81% / 81% | 90% / 90% / 88% | 7 |
| llm_recent/not_told/look_on | +2.8 | 3/10 | -2.9 | 7/10 | 79% / 80% / 82% | 88% / 90% / 90% | 7 |
| llm_recent/told/look_on | +3.0 | 3/10 | -3.0 | 7/10 | 79% / 81% / 82% | 88% / 89% / 90% | 7 |
| llm_summary/not_told/look_on | +0.5 | 5/10 | -2.2 | 8/10 | 82% / 83% / 86% | 89% / 90% / 88% | 7 |
| llm_summary/told/look_on | +3.5 | 3/10 | -0.7 | 6/10 | 82% / 85% / 87% | 91% / 91% / 92% | 7 |

### look off

| agent | mean(shift - non) | households with a drop | mean(shift - non), spot only | drop, spot only | event day -1 / 0 / +1 | event day -1 / 0 / +1, spot only | households with an event day |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | +3.6 | 2/10 | -2.5 | 7/10 | 74% / 78% / 79% | 86% / 89% / 87% | 7 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | +4.1 | 3/10 | -2.4 | 7/10 | 76% / 79% / 81% | 88% / 89% / 90% | 7 |
| LastObservation | +4.0 | 3/10 | -2.4 | 7/10 | 76% / 79% / 81% | 88% / 89% / 90% | 7 |
| Markov1(a=1,cut=24h,hl=24h) | +2.0 | 4/10 | -1.9 | 6/10 | 78% / 81% / 83% | 87% / 87% / 88% | 7 |
| MostFrequentLocation | +3.2 | 3/10 | -3.1 | 9/10 | 76% / 79% / 82% | 88% / 89% / 90% | 7 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | +4.0 | 4/10 | -2.6 | 7/10 | 78% / 80% / 82% | 88% / 89% / 90% | 7 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | +3.5 | 3/10 | -2.8 | 6/10 | 74% / 79% / 81% | 86% / 89% / 89% | 7 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | +4.6 | 2/10 | -1.7 | 6/10 | 76% / 78% / 81% | 88% / 88% / 89% | 7 |
| SmoothedRecency(hl=6h,freq=24h) | +4.1 | 3/10 | -2.4 | 7/10 | 76% / 79% / 81% | 88% / 89% / 90% | 7 |
| TimetableLookup(bin=1h,days=all) | +3.3 | 4/10 | -2.7 | 7/10 | 77% / 81% / 83% | 87% / 89% / 90% | 7 |
| llm_naive/not_told/look_off | +4.5 | 3/10 | -1.8 | 7/10 | 78% / 80% / 81% | 89% / 89% / 90% | 7 |
| llm_naive/told/look_off | +4.3 | 3/10 | -2.2 | 8/10 | 78% / 80% / 81% | 89% / 89% / 89% | 7 |
| llm_recent/not_told/look_off | +3.8 | 3/10 | -1.8 | 7/10 | 78% / 79% / 80% | 87% / 88% / 89% | 7 |
| llm_recent/told/look_off | +3.5 | 3/10 | -2.3 | 8/10 | 78% / 78% / 81% | 87% / 88% / 89% | 7 |
| llm_summary/not_told/look_off | +1.7 | 5/10 | -2.6 | 7/10 | 77% / 79% / 82% | 87% / 85% / 87% | 7 |
| llm_summary/told/look_off | +4.7 | 5/10 | -0.6 | 6/10 | 76% / 80% / 82% | 86% / 86% / 89% | 7 |

### look voi

| agent | mean(shift - non) | households with a drop | mean(shift - non), spot only | drop, spot only | event day -1 / 0 / +1 | event day -1 / 0 / +1, spot only | households with an event day |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | +2.5 | 2/10 | -1.8 | 8/10 | 90% / 90% / 91% | 96% / 95% / 94% | 7 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | +5.3 | 2/10 | -0.3 | 7/10 | 88% / 89% / 93% | 98% / 98% / 99% | 7 |
| LastObservation | +1.2 | 3/10 | -2.8 | 8/10 | 89% / 90% / 92% | 96% / 95% / 96% | 7 |
| Markov1(a=1,cut=24h,hl=24h) | +1.7 | 3/10 | -2.2 | 8/10 | 88% / 88% / 88% | 94% / 94% / 93% | 7 |
| MostFrequentLocation | +4.0 | 2/10 | -0.6 | 7/10 | 89% / 93% / 93% | 97% / 98% / 99% | 7 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | +2.8 | 2/10 | -1.1 | 7/10 | 90% / 91% / 93% | 96% / 97% / 97% | 7 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | +7.0 | 2/10 | +0.3 | 4/10 | 84% / 86% / 90% | 97% / 97% / 99% | 7 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | +7.0 | 2/10 | +0.2 | 5/10 | 84% / 87% / 90% | 97% / 98% / 99% | 7 |
| SmoothedRecency(hl=6h,freq=24h) | +4.2 | 2/10 | -0.6 | 7/10 | 89% / 91% / 92% | 97% / 97% / 98% | 7 |
| TimetableLookup(bin=1h,days=all) | +2.3 | 3/10 | -1.2 | 4/10 | 88% / 88% / 90% | 94% / 94% / 95% | 7 |

### Per-household accuracy per day (look voi / llm; `*` = that household's shift day)

**hh_s0** (shift days: Wed, Thu, Sat, Sun)

| agent | Wed* | Thu* | Fri | Sat* | Sun* | Mon | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 97% | 100% | 97% | 84% | 88% | 75% | 88% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 88% | 100% | 94% | 91% | 97% | 94% | 84% |
| LastObservation | 91% | 100% | 100% | 94% | 97% | 88% | 91% |
| Markov1(a=1,cut=24h,hl=24h) | 84% | 97% | 100% | 91% | 97% | 88% | 84% |
| MostFrequentLocation | 94% | 97% | 97% | 97% | 100% | 91% | 97% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 97% | 97% | 97% | 91% | 97% | 91% | 88% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 88% | 97% | 94% | 91% | 97% | 81% | 81% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 88% | 97% | 94% | 91% | 97% | 81% | 84% |
| SmoothedRecency(hl=6h,freq=24h) | 94% | 97% | 100% | 94% | 97% | 88% | 88% |
| TimetableLookup(bin=1h,days=all) | 88% | 91% | 94% | 91% | 84% | 75% | 91% |
| llm_naive/not_told/look_on | 88% | 97% | 94% | 91% | 94% | 66% | 78% |
| llm_naive/told/look_on | 88% | 97% | 88% | 91% | 94% | 66% | 78% |
| llm_recent/not_told/look_on | 84% | 97% | 91% | 91% | 88% | 69% | 78% |
| llm_recent/told/look_on | 84% | 97% | 91% | 91% | 88% | 66% | 78% |
| llm_summary/not_told/look_on | 91% | 88% | 94% | 91% | 94% | 72% | 91% |
| llm_summary/told/look_on | 88% | 100% | 88% | 91% | 97% | 75% | 88% |

**hh_s1** (shift days: Fri, Sat, Sun)

| agent | Wed | Thu | Fri* | Sat* | Sun* | Mon | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 97% | 84% | 94% | 94% | 91% | 91% | 75% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 88% | 81% | 88% | 100% | 94% | 91% | 81% |
| LastObservation | 91% | 81% | 94% | 94% | 88% | 91% | 84% |
| Markov1(a=1,cut=24h,hl=24h) | 81% | 84% | 91% | 91% | 81% | 94% | 81% |
| MostFrequentLocation | 91% | 78% | 97% | 100% | 94% | 91% | 81% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 94% | 88% | 88% | 94% | 88% | 88% | 78% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 78% | 72% | 84% | 97% | 94% | 81% | 75% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 78% | 72% | 84% | 97% | 94% | 84% | 75% |
| SmoothedRecency(hl=6h,freq=24h) | 88% | 84% | 91% | 97% | 91% | 91% | 75% |
| TimetableLookup(bin=1h,days=all) | 94% | 81% | 100% | 94% | 81% | 81% | 78% |
| llm_naive/not_told/look_on | 84% | 72% | 84% | 84% | 78% | 84% | 69% |
| llm_naive/told/look_on | 84% | 72% | 81% | 84% | 78% | 84% | 69% |
| llm_recent/not_told/look_on | 88% | 78% | 81% | 84% | 78% | 84% | 69% |
| llm_recent/told/look_on | 88% | 78% | 81% | 84% | 78% | 84% | 69% |
| llm_summary/not_told/look_on | 84% | 78% | 88% | 88% | 91% | 88% | 84% |
| llm_summary/told/look_on | 84% | 78% | 91% | 88% | 91% | 84% | 88% |

**hh_s2** (shift days: Sat, Sun, Tue)

| agent | Wed | Thu | Fri | Sat* | Sun* | Mon | Tue* |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 78% | 97% | 97% | 97% | 84% | 84% | 88% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 81% | 97% | 100% | 97% | 94% | 88% | 97% |
| LastObservation | 75% | 100% | 97% | 91% | 88% | 88% | 94% |
| Markov1(a=1,cut=24h,hl=24h) | 72% | 100% | 97% | 94% | 88% | 94% | 84% |
| MostFrequentLocation | 78% | 97% | 97% | 97% | 91% | 91% | 94% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 78% | 97% | 100% | 94% | 88% | 88% | 94% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 72% | 97% | 97% | 97% | 94% | 84% | 88% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 72% | 97% | 94% | 97% | 94% | 84% | 91% |
| SmoothedRecency(hl=6h,freq=24h) | 78% | 97% | 100% | 97% | 94% | 91% | 97% |
| TimetableLookup(bin=1h,days=all) | 78% | 94% | 88% | 88% | 69% | 88% | 78% |
| llm_naive/not_told/look_on | 72% | 94% | 78% | 91% | 78% | 78% | 72% |
| llm_naive/told/look_on | 72% | 94% | 78% | 88% | 78% | 78% | 72% |
| llm_recent/not_told/look_on | 69% | 94% | 78% | 88% | 78% | 78% | 78% |
| llm_recent/told/look_on | 69% | 94% | 78% | 88% | 78% | 75% | 78% |
| llm_summary/not_told/look_on | 75% | 97% | 91% | 91% | 81% | 81% | 69% |
| llm_summary/told/look_on | 75% | 97% | 91% | 91% | 81% | 81% | 81% |

**hh_s3** (shift days: Sat, Sun)

| agent | Wed | Thu | Fri | Sat* | Sun* | Mon | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 94% | 94% | 94% | 94% | 97% | 94% | 91% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 91% | 88% | 97% | 94% | 97% | 94% | 97% |
| LastObservation | 97% | 94% | 91% | 91% | 94% | 88% | 94% |
| Markov1(a=1,cut=24h,hl=24h) | 97% | 88% | 88% | 94% | 91% | 91% | 94% |
| MostFrequentLocation | 94% | 97% | 94% | 97% | 100% | 94% | 97% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 94% | 91% | 91% | 94% | 94% | 91% | 97% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 91% | 84% | 94% | 91% | 97% | 91% | 97% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 91% | 84% | 94% | 91% | 97% | 91% | 97% |
| SmoothedRecency(hl=6h,freq=24h) | 91% | 91% | 97% | 94% | 100% | 94% | 97% |
| TimetableLookup(bin=1h,days=all) | 91% | 91% | 94% | 94% | 94% | 75% | 94% |
| llm_naive/not_told/look_on | 100% | 78% | 88% | 78% | 88% | 91% | 88% |
| llm_naive/told/look_on | 100% | 78% | 88% | 81% | 94% | 91% | 88% |
| llm_recent/not_told/look_on | 97% | 75% | 84% | 81% | 84% | 91% | 91% |
| llm_recent/told/look_on | 97% | 75% | 84% | 81% | 88% | 91% | 91% |
| llm_summary/not_told/look_on | 97% | 94% | 97% | 81% | 94% | 94% | 94% |
| llm_summary/told/look_on | 97% | 84% | 88% | 84% | 100% | 94% | 91% |

**hh_s4** (shift days: Sat, Sun, Mon, Tue)

| agent | Wed | Thu | Fri | Sat* | Sun* | Mon* | Tue* |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 91% | 84% | 81% | 94% | 97% | 69% | 75% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 84% | 88% | 72% | 97% | 100% | 75% | 78% |
| LastObservation | 88% | 88% | 75% | 94% | 94% | 81% | 78% |
| Markov1(a=1,cut=24h,hl=24h) | 75% | 84% | 81% | 91% | 94% | 84% | 75% |
| MostFrequentLocation | 91% | 84% | 84% | 100% | 97% | 88% | 81% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 94% | 81% | 88% | 97% | 94% | 78% | 88% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 75% | 84% | 72% | 94% | 100% | 72% | 69% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 75% | 84% | 72% | 94% | 100% | 72% | 69% |
| SmoothedRecency(hl=6h,freq=24h) | 84% | 88% | 81% | 97% | 97% | 75% | 78% |
| TimetableLookup(bin=1h,days=all) | 84% | 81% | 88% | 97% | 97% | 72% | 78% |
| llm_naive/not_told/look_on | 78% | 81% | 62% | 84% | 91% | 62% | 62% |
| llm_naive/told/look_on | 78% | 81% | 62% | 81% | 91% | 62% | 69% |
| llm_recent/not_told/look_on | 69% | 78% | 66% | 78% | 88% | 66% | 62% |
| llm_recent/told/look_on | 69% | 78% | 66% | 78% | 88% | 69% | 66% |
| llm_summary/not_told/look_on | 81% | 91% | 69% | 88% | 91% | 69% | 91% |
| llm_summary/told/look_on | 81% | 88% | 75% | 88% | 94% | 72% | 84% |

**hh_s5** (shift days: Thu, Sat, Sun)

| agent | Wed | Thu* | Fri | Sat* | Sun* | Mon | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 91% | 91% | 91% | 88% | 91% | 72% | 84% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 75% | 84% | 88% | 97% | 100% | 78% | 81% |
| LastObservation | 91% | 84% | 91% | 78% | 97% | 91% | 84% |
| Markov1(a=1,cut=24h,hl=24h) | 78% | 91% | 84% | 81% | 94% | 88% | 91% |
| MostFrequentLocation | 88% | 91% | 94% | 91% | 100% | 84% | 84% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 91% | 91% | 94% | 81% | 97% | 81% | 84% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 72% | 81% | 84% | 91% | 100% | 78% | 81% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 72% | 81% | 84% | 91% | 100% | 75% | 81% |
| SmoothedRecency(hl=6h,freq=24h) | 84% | 91% | 91% | 94% | 100% | 84% | 81% |
| TimetableLookup(bin=1h,days=all) | 84% | 94% | 91% | 78% | 88% | 81% | 75% |
| llm_naive/not_told/look_on | 75% | 81% | 72% | 75% | 91% | 75% | 78% |
| llm_naive/told/look_on | 75% | 81% | 72% | 69% | 91% | 75% | 78% |
| llm_recent/not_told/look_on | 75% | 81% | 81% | 69% | 91% | 75% | 78% |
| llm_recent/told/look_on | 75% | 81% | 81% | 66% | 91% | 72% | 78% |
| llm_summary/not_told/look_on | 69% | 88% | 84% | 75% | 91% | 75% | 66% |
| llm_summary/told/look_on | 69% | 88% | 78% | 72% | 91% | 78% | 56% |

**hh_s6** (shift days: Sat, Sun)

| agent | Wed | Thu | Fri | Sat* | Sun* | Mon | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 94% | 88% | 84% | 88% | 100% | 81% | 88% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 78% | 91% | 75% | 94% | 100% | 81% | 88% |
| LastObservation | 91% | 91% | 94% | 91% | 97% | 88% | 91% |
| Markov1(a=1,cut=24h,hl=24h) | 81% | 84% | 88% | 94% | 97% | 88% | 94% |
| MostFrequentLocation | 94% | 84% | 88% | 94% | 100% | 88% | 97% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 88% | 91% | 81% | 97% | 100% | 84% | 91% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 75% | 81% | 75% | 94% | 100% | 69% | 84% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 75% | 81% | 75% | 94% | 100% | 69% | 84% |
| SmoothedRecency(hl=6h,freq=24h) | 88% | 97% | 81% | 94% | 100% | 91% | 84% |
| TimetableLookup(bin=1h,days=all) | 84% | 81% | 81% | 91% | 88% | 84% | 78% |
| llm_naive/not_told/look_on | 78% | 66% | 78% | 84% | 94% | 62% | 81% |
| llm_naive/told/look_on | 78% | 66% | 78% | 84% | 97% | 62% | 81% |
| llm_recent/not_told/look_on | 78% | 66% | 75% | 84% | 97% | 69% | 81% |
| llm_recent/told/look_on | 78% | 66% | 75% | 84% | 97% | 72% | 84% |
| llm_summary/not_told/look_on | 75% | 81% | 94% | 84% | 84% | 91% | 88% |
| llm_summary/told/look_on | 75% | 72% | 97% | 88% | 97% | 91% | 88% |

**hh_s7** (shift days: Sat, Sun)

| agent | Wed | Thu | Fri | Sat* | Sun* | Mon | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 94% | 91% | 91% | 88% | 100% | 97% | 91% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 88% | 88% | 91% | 94% | 100% | 97% | 97% |
| LastObservation | 91% | 91% | 91% | 91% | 97% | 97% | 91% |
| Markov1(a=1,cut=24h,hl=24h) | 84% | 88% | 94% | 88% | 97% | 94% | 91% |
| MostFrequentLocation | 88% | 88% | 91% | 94% | 100% | 91% | 97% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 91% | 88% | 91% | 97% | 100% | 94% | 94% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 88% | 84% | 88% | 94% | 97% | 88% | 94% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 88% | 84% | 88% | 94% | 97% | 91% | 94% |
| SmoothedRecency(hl=6h,freq=24h) | 91% | 88% | 88% | 94% | 100% | 100% | 97% |
| TimetableLookup(bin=1h,days=all) | 91% | 78% | 88% | 94% | 94% | 94% | 81% |
| llm_naive/not_told/look_on | 84% | 69% | 91% | 81% | 88% | 84% | 81% |
| llm_naive/told/look_on | 84% | 72% | 91% | 81% | 88% | 84% | 88% |
| llm_recent/not_told/look_on | 81% | 72% | 81% | 81% | 88% | 84% | 84% |
| llm_recent/told/look_on | 81% | 72% | 81% | 81% | 88% | 84% | 84% |
| llm_summary/not_told/look_on | 84% | 72% | 91% | 84% | 88% | 84% | 88% |
| llm_summary/told/look_on | 81% | 69% | 88% | 84% | 91% | 84% | 88% |

**hh_s8** (shift days: Wed, Fri, Sat, Sun, Tue)

| agent | Wed* | Thu | Fri* | Sat* | Sun* | Mon | Tue* |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 100% | 97% | 88% | 94% | 94% | 84% | 94% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 94% | 97% | 84% | 94% | 100% | 91% | 81% |
| LastObservation | 97% | 97% | 97% | 91% | 100% | 88% | 88% |
| Markov1(a=1,cut=24h,hl=24h) | 94% | 91% | 94% | 84% | 97% | 94% | 88% |
| MostFrequentLocation | 94% | 97% | 91% | 94% | 97% | 94% | 91% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 97% | 97% | 88% | 91% | 97% | 91% | 81% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 94% | 97% | 84% | 94% | 94% | 91% | 84% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 94% | 97% | 84% | 94% | 94% | 91% | 84% |
| SmoothedRecency(hl=6h,freq=24h) | 97% | 97% | 88% | 97% | 100% | 91% | 84% |
| TimetableLookup(bin=1h,days=all) | 94% | 97% | 84% | 84% | 97% | 84% | 81% |
| llm_naive/not_told/look_on | 94% | 88% | 75% | 78% | 97% | 84% | 75% |
| llm_naive/told/look_on | 94% | 88% | 75% | 81% | 94% | 88% | 75% |
| llm_recent/not_told/look_on | 94% | 88% | 75% | 84% | 94% | 84% | 75% |
| llm_recent/told/look_on | 94% | 88% | 75% | 78% | 94% | 84% | 75% |
| llm_summary/not_told/look_on | 91% | 88% | 81% | 75% | 94% | 88% | 84% |
| llm_summary/told/look_on | 91% | 91% | 84% | 84% | 94% | 88% | 84% |

**hh_s9** (shift days: Fri, Sat, Sun, Mon)

| agent | Wed | Thu | Fri* | Sat* | Sun* | Mon* | Tue |
|---|---|---|---|---|---|---|---|
| DaytypeMixture(K=3,bin=2h,hl=24h) | 94% | 94% | 91% | 88% | 84% | 91% | 91% |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 94% | 94% | 97% | 94% | 88% | 97% | 97% |
| LastObservation | 91% | 94% | 91% | 91% | 88% | 88% | 94% |
| Markov1(a=1,cut=24h,hl=24h) | 91% | 91% | 91% | 88% | 88% | 88% | 97% |
| MostFrequentLocation | 91% | 94% | 94% | 91% | 88% | 94% | 97% |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 91% | 91% | 94% | 91% | 94% | 91% | 97% |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 94% | 94% | 97% | 94% | 84% | 94% | 94% |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 97% | 94% | 97% | 94% | 88% | 91% | 94% |
| SmoothedRecency(hl=6h,freq=24h) | 94% | 91% | 94% | 94% | 91% | 88% | 97% |
| TimetableLookup(bin=1h,days=all) | 94% | 88% | 94% | 91% | 84% | 91% | 91% |
| llm_naive/not_told/look_on | 88% | 84% | 84% | 78% | 84% | 78% | 88% |
| llm_naive/told/look_on | 88% | 84% | 88% | 78% | 84% | 81% | 88% |
| llm_recent/not_told/look_on | 88% | 78% | 78% | 78% | 81% | 78% | 88% |
| llm_recent/told/look_on | 88% | 78% | 78% | 78% | 81% | 78% | 88% |
| llm_summary/not_told/look_on | 91% | 91% | 88% | 81% | 84% | 84% | 88% |
| llm_summary/told/look_on | 91% | 91% | 88% | 81% | 84% | 81% | 97% |

