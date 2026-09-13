# Learning curve: accuracy by history preceding the question

| model | d0-3 | d4-7 | d8-14 | d15-27 |
|---|---|---|---|---|
| LLMHyp(anonymized) | 0.656 (n=180) | 0.581 (n=720) | 0.552 (n=1260) | 0.539 (n=2340) |
| LLMHyp(named) | 0.633 (n=180) | 0.607 (n=720) | 0.606 (n=1260) | 0.577 (n=2340) |
| LLMHyp(named,decay=1.0) | 0.606 (n=180) | 0.601 (n=720) | 0.603 (n=1260) | 0.559 (n=2340) |
| MostFrequentLocation(hl=24h) | 0.667 (n=180) | 0.619 (n=720) | 0.643 (n=1260) | 0.600 (n=2340) |
| OracleBelief(eps=0.4,hl=12h) | 0.744 (n=180) | 0.728 (n=720) | 0.747 (n=1260) | 0.737 (n=2340) |
| PeriodicPersistence(min_dep=2,bin=1h,hl=24h) | 0.683 (n=180) | 0.619 (n=720) | 0.626 (n=1260) | 0.581 (n=2340) |
