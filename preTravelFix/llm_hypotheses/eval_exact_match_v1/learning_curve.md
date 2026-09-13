# Learning curve: accuracy by history preceding the question

| model | d0-3 | d4-7 | d8-14 | d15-27 |
|---|---|---|---|---|
| LLMHyp(anonymized) | 0.639 (n=180) | 0.568 (n=720) | 0.540 (n=1260) | 0.532 (n=2340) |
| LLMHyp(named) | 0.622 (n=180) | 0.599 (n=720) | 0.597 (n=1260) | 0.569 (n=2340) |
| LLMHyp(named,decay=1.0) | 0.594 (n=180) | 0.599 (n=720) | 0.596 (n=1260) | 0.547 (n=2340) |
| MostFrequentLocation(hl=24h) | 0.661 (n=180) | 0.604 (n=720) | 0.613 (n=1260) | 0.567 (n=2340) |
| OracleBelief(eps=0.4,hl=12h) | 0.739 (n=180) | 0.728 (n=720) | 0.744 (n=1260) | 0.735 (n=2340) |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.672 (n=180) | 0.604 (n=720) | 0.614 (n=1260) | 0.580 (n=2340) |
