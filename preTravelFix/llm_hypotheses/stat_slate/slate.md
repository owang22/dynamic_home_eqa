# Statistical slate, passive protocol, ON_PERSON ≡ OUT_OF_HOUSE (sorted by pooled log-loss)

| model | hh_001 top-1 | hh_001 log-loss | hh_002 top-1 | hh_002 log-loss | both top-1 | both log-loss |
|---|---|---|---|---|---|---|
| MostFrequentLocation(hl=72h) | 0.644 | 1.317 | 0.583 | 1.715 | 0.613 | 1.516 |
| MostFrequentLocation | 0.586 | 1.472 | 0.546 | 1.692 | 0.566 | 1.582 |
| SmoothedRecency(hl=6h,freq=24h) | 0.650 | 1.411 | 0.590 | 1.932 | 0.620 | 1.671 |
| MostFrequentLocation(hl=24h) | 0.638 | 1.408 | 0.597 | 2.012 | 0.618 | 1.710 |
| TimetableLookup(bin=1h,days=weekday_weekend,hl=72h) | 0.559 | 1.596 | 0.529 | 1.952 | 0.544 | 1.774 |
| HierarchyBackoff(po=5,pc=5,hl=24h) | 0.612 | 1.879 | 0.570 | 2.157 | 0.591 | 2.018 |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.621 | 1.909 | 0.587 | 2.298 | 0.604 | 2.104 |
| TimetableLookup(bin=1h,days=all,hl=24h) | 0.491 | 1.845 | 0.475 | 2.379 | 0.483 | 2.112 |
| PerpetuaStar(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 0.553 | 2.359 | 0.500 | 2.561 | 0.526 | 2.460 |
| PerpetuaStarFlat(lognormal,K<=3,pm=0.01,a0=0.01/h,g=0.99) | 0.550 | 2.375 | 0.496 | 2.595 | 0.523 | 2.485 |
| Markov1(a=1,cut=24h,hl=24h) | 0.446 | 2.169 | 0.357 | 2.802 | 0.402 | 2.486 |
| DaytypeMixture(K=3,bin=2h,hl=24h) | 0.561 | 2.287 | 0.523 | 2.701 | 0.542 | 2.494 |
| Perpetua(lognormal,K<=3,pm=0.01,steps=10) | 0.539 | 2.433 | 0.490 | 2.598 | 0.514 | 2.516 |
| LastObservation | 0.611 | 2.331 | 0.572 | 2.779 | 0.592 | 2.555 |
