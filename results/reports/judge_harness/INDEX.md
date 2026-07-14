# Judge harness index

Higher Spearman + monotonically increasing mean-by-band = better. `over` is the fraction the judge scored above the human (its known failure).

| config | style | ctx | fs | think | k | Spearman | exact | over | mean@band 0/1/2/3 |
|---|---|---|---|---|---|---|---|---|---|
| strict_ctx_fs_k3 | strict | ✓ | ✓ | True | 3 | 0.83 | 0.62 | 0.23 | 0.18/0.41/0.55/0.80 |
| strict_ctx_fs | strict | ✓ | ✓ | False | 1 | 0.79 | 0.67 | 0.15 | 0.11/0.36/0.50/0.80 |
| strict_thinking | strict | · | · | True | 1 | 0.79 | 0.46 | 0.48 | 0.32/0.55/0.73/0.85 |
| strict | strict | · | · | False | 1 | 0.75 | 0.58 | 0.29 | 0.23/0.38/0.55/0.82 |
| strict_fs | strict | · | ✓ | False | 1 | 0.73 | 0.50 | 0.33 | 0.26/0.43/0.57/0.83 |
| strict_ctx | strict | ✓ | · | False | 1 | 0.73 | 0.54 | 0.38 | 0.27/0.50/0.65/0.83 |
| moe_strict_thinking | strict | · | · | True | 1 | 0.66 | 0.52 | 0.29 | 0.34/0.39/0.58/0.83 |
| asis | asis | · | · | False | 1 | 0.64 | 0.54 | 0.35 | 0.45/0.40/0.60/0.88 |
