# Budget grid: accuracy against senses per question

Figure: `frontier.png` (one panel per belief; marker size = daily budget). Rows below: the most accurate policy per belief and budget, and the most accurate one that spends no more than SequentialSearch.

| belief | budget/day | best policy | acc | senses/q | best at or below search cost | acc | senses/q | search acc | search senses/q |
|---|---|---|---|---|---|---|---|---|---|
| LastObservation | 24 | ResolvableMassSense(alpha=0.3,tau=0.8,global) | 0.655 | 0.24 | ResolvableMassSense(alpha=0.3,tau=0.8,global) | 0.655 | 0.24 | 0.641 | 0.27 |
| LastObservation | 45 | ConformalSense(alpha=0.5,global) | 0.718 | 0.48 | ConformalSense(alpha=0.5,global) | 0.718 | 0.48 | 0.666 | 0.50 |
| LastObservation | 90 | ResolvableMassSense(alpha=0.2,tau=0.6,global) | 0.804 | 0.78 | ResolvableMassSense(alpha=0.2,tau=0.6,global) | 0.804 | 0.78 | 0.707 | 1.00 |
| MostFrequentLocation | 24 | ACISense(alpha=0.3,gamma=0,oracle) | 0.686 | 0.23 | ACISense(alpha=0.3,gamma=0,oracle) | 0.686 | 0.23 | 0.647 | 0.27 |
| MostFrequentLocation | 45 | ConformalSense(alpha=0.5,global) | 0.739 | 0.48 | ConformalSense(alpha=0.5,global) | 0.739 | 0.48 | 0.672 | 0.50 |
| MostFrequentLocation | 90 | ConformalSense(alpha=0.5,age_binned) | 0.835 | 0.87 | ConformalSense(alpha=0.5,age_binned) | 0.835 | 0.87 | 0.711 | 1.00 |
| TimetableLookup | 24 | ConformalSense(alpha=0.05,age_binned) | 0.586 | 0.27 | ConformalSense(alpha=0.05,age_binned) | 0.586 | 0.27 | 0.583 | 0.27 |
| TimetableLookup | 45 | ResolvableMassSense(alpha=0.2,tau=0.6,global) | 0.629 | 0.50 | ResolvableMassSense(alpha=0.2,tau=0.6,global) | 0.629 | 0.50 | 0.606 | 0.50 |
| TimetableLookup | 90 | ResolvableMassSense(alpha=0.2,tau=0.6,global) | 0.741 | 1.00 | ResolvableMassSense(alpha=0.2,tau=0.6,global) | 0.741 | 1.00 | 0.648 | 1.00 |
| PeriodicPersistence | 24 | ResolvableMassSense(alpha=0.3,tau=0.4,global) | 0.692 | 0.20 | ResolvableMassSense(alpha=0.3,tau=0.4,global) | 0.692 | 0.20 | 0.654 | 0.27 |
| PeriodicPersistence | 45 | ConformalSense(alpha=0.5,global) | 0.762 | 0.48 | ConformalSense(alpha=0.5,global) | 0.762 | 0.48 | 0.681 | 0.50 |
| PeriodicPersistence | 90 | ResolvableMassSense(alpha=0.2,tau=0.6,global) | 0.854 | 0.96 | ResolvableMassSense(alpha=0.2,tau=0.6,global) | 0.854 | 0.96 | 0.719 | 1.00 |
| HierarchyBackoff | 24 | ResolvableMassSense(alpha=0.3,tau=0.4,global) | 0.687 | 0.24 | ResolvableMassSense(alpha=0.3,tau=0.4,global) | 0.687 | 0.24 | 0.646 | 0.27 |
| HierarchyBackoff | 45 | ConformalSense(alpha=0.5,global) | 0.725 | 0.48 | ConformalSense(alpha=0.5,global) | 0.725 | 0.48 | 0.673 | 0.50 |
| HierarchyBackoff | 90 | ConformalSense(alpha=0.5,age_binned) | 0.820 | 0.85 | ConformalSense(alpha=0.5,age_binned) | 0.820 | 0.85 | 0.714 | 1.00 |
