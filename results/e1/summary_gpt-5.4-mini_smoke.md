# E1 -- adaptation curve (forecasting)

rows: 32  |  model: ['gpt-5.4-mini']  |  prompt_hash: d69077885dc3

## profile_text = False
| bank | D=0 | D=1 | D=3 | D=7 | D=14 | (moved-only D=7) | ECE(D=7) |
|---|---|---|---|---|---|---|---|
| atyp_v1 | 0.750 | - | - | 0.500 | - | 0.000 | 0.350 |
| typ_v1 | 0.250 | - | - | 0.250 | - | 0.000 | 0.325 |

## profile_text = True
| bank | D=0 | D=1 | D=3 | D=7 | D=14 | (moved-only D=7) | ECE(D=7) |
|---|---|---|---|---|---|---|---|
| atyp_v1 | 0.750 | - | - | 0.250 | - | 0.000 | 0.780 |
| typ_v1 | 0.250 | - | - | 0.500 | - | 0.000 | 0.390 |

## C4 controls (D=7)
| slice | atyp_v1 | atyp_shift_v1 |
|---|---|---|
| all | 0.375 | - |
| held-out only | - | - |
| observed only | 0.375 | - |

Interpretation guardrail: numbers only. C1 = atyp accuracy rises with D while typ stays flat; C4 = atyp gains vanish under atyp_shift (per-object phase destroys shared routine). With the MOCK client these are a last-seen baseline, not an LLM result.