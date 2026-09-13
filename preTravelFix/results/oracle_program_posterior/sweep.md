# OracleBelief weighting sweep: eps x forgetting half-life, passive diet, 20 fleet banks

Every setting replays NeverSense at each bank's own budget on all 20 banks (800 realizations). ESS is ``1 / sum(w_i^2)`` after each question. The setting is chosen on the 10 calibration households only: the largest passive accuracy among settings whose calibration median ESS is at least 5. The 10 test households are shown for the record and were not consulted. The routine oracle's no-observation answer (same realizations, uniform weights) scores 0.703 on calibration and 0.714 on test. Per-question rows per setting in `sweep/<setting>/ess_passive.csv`; this table in `sweep.csv`.

| eps | half-life | cal median ESS | cal p10 / p90 | cal accuracy | gate | test median ESS | test accuracy |
|---|---|---|---|---|---|---|---|
| 0.05 | none | 1.00 | 1.00 / 1.11 | 0.646 | STOP | 1.00 | 0.649 |
| 0.05 | 96 h | 1.01 | 1.00 / 1.76 | 0.660 | STOP | 1.03 | 0.665 |
| 0.05 | 48 h | 1.06 | 1.00 / 2.13 | 0.677 | STOP | 1.11 | 0.678 |
| 0.05 | 24 h | 1.25 | 1.00 / 2.77 | 0.697 | STOP | 1.31 | 0.692 |
| 0.05 | 12 h | 1.84 | 1.02 / 4.68 | 0.716 | STOP | 2.04 | 0.710 |
| 0.05 | 6 h | 3.80 | 1.15 / 17.07 | 0.736 | STOP | 4.85 | 0.736 |
| 0.2 | none | 1.00 | 1.00 / 1.57 | 0.646 | STOP | 1.02 | 0.649 |
| 0.2 | 96 h | 1.10 | 1.00 / 2.27 | 0.662 | STOP | 1.28 | 0.670 |
| 0.2 | 48 h | 1.44 | 1.00 / 3.33 | 0.683 | STOP | 1.67 | 0.686 |
| 0.2 | 24 h | 2.15 | 1.05 / 5.27 | 0.709 | STOP | 2.40 | 0.705 |
| 0.2 | 12 h | 4.51 | 1.36 / 15.21 | 0.740 | STOP | 5.80 | 0.735 |
| 0.2 | 6 h | 17.97 | 2.63 / 101.70 | 0.761 | pass | 27.49 | 0.756 |
| 0.4 | none | 1.05 | 1.00 / 2.18 | 0.646 | STOP | 1.15 | 0.650 |
| 0.4 | 96 h | 1.56 | 1.02 / 3.83 | 0.670 | STOP | 2.04 | 0.681 |
| 0.4 | 48 h | 2.58 | 1.13 / 6.53 | 0.699 | STOP | 3.19 | 0.704 |
| 0.4 | 24 h | 5.76 | 1.70 / 16.31 | 0.737 | pass | 7.71 | 0.732 |
| 0.4 | 12 h | 23.05 | 4.67 / 74.95 | 0.764 | pass | 33.24 | 0.758 **(selected)** |
| 0.4 | 6 h | 107.90 | 15.88 / 338.46 | 0.760 | pass | 152.16 | 0.755 |
| 0.6 | none | 1.42 | 1.00 / 3.49 | 0.651 | STOP | 1.77 | 0.658 |
| 0.6 | 96 h | 3.38 | 1.31 / 10.16 | 0.692 | STOP | 5.00 | 0.706 |
| 0.6 | 48 h | 9.19 | 2.68 / 23.58 | 0.733 | pass | 13.48 | 0.736 |
| 0.6 | 24 h | 36.22 | 10.30 / 84.80 | 0.762 | pass | 54.14 | 0.755 |
| 0.6 | 12 h | 151.25 | 46.60 / 296.30 | 0.758 | pass | 199.71 | 0.752 |
| 0.6 | 6 h | 368.44 | 128.45 / 588.94 | 0.741 | pass | 429.69 | 0.742 |
| 0.8 | none | 3.86 | 1.18 / 20.93 | 0.678 | STOP | 5.35 | 0.690 |
| 0.8 | 96 h | 44.25 | 11.66 / 89.79 | 0.738 | pass | 69.41 | 0.739 |
| 0.8 | 48 h | 142.39 | 67.34 / 222.25 | 0.743 | pass | 192.83 | 0.740 |
| 0.8 | 24 h | 342.04 | 225.44 / 441.60 | 0.738 | pass | 398.49 | 0.737 |
| 0.8 | 12 h | 550.15 | 402.66 / 645.91 | 0.727 | pass | 589.20 | 0.731 |
| 0.8 | 6 h | 679.30 | 530.07 / 751.36 | 0.720 | pass | 701.35 | 0.725 |
| 0.9 | none | 28.44 | 4.54 / 205.59 | 0.714 | pass | 47.51 | 0.720 |
| 0.9 | 96 h | 326.14 | 219.79 / 426.78 | 0.726 | pass | 391.59 | 0.726 |
| 0.9 | 48 h | 513.72 | 432.18 / 574.80 | 0.722 | pass | 560.48 | 0.723 |
| 0.9 | 24 h | 654.03 | 593.96 / 695.50 | 0.718 | pass | 679.67 | 0.721 |
| 0.9 | 12 h | 733.69 | 683.16 / 761.66 | 0.713 | pass | 745.19 | 0.719 |
| 0.9 | 6 h | 770.58 | 727.06 / 788.68 | 0.710 | pass | 776.14 | 0.717 |

**Selection.** Selected: eps 0.4 per disagreement, forgetting half-life 12 h (calibration median ESS 23.05, passive accuracy 0.764 vs routine 0.703). Written to `selected.json`; `ess_gate`, `grid` and `report` use it unless `--eps`/`--half-life-h` override.
