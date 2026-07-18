# Active probe — per-scene gate

## ep049w  (n_rooms=11, chance=0.0833, max_looks=6, targets=28 {'static': 8, 'occasional': 8, 'dynamic': 12})

| tier | policy | acc [95% CI] | looks | looks: stable/occ/dyn | absten P/R/F1 |
|---|---|---|---|---|---|
| b3_perpetua_star(schedule_prior) | answer_now | 0.825 [0.761,0.885] | 0.00 | 0.0/0.0/0.0 | 0.807/0.897/0.85 |
| b3_perpetua_star(schedule_prior) | voi_predictive | 0.944 [0.895,0.982] | 0.97 | 0.087/1.421/1.253 | 0.957/0.954/0.955 |
| b2_classdecay | answer_now | 0.812 [0.745,0.874] | 0.00 | 0.0/0.0/0.0 | 0.762/0.914/0.831 |
| b2_classdecay | voi_predictive | 0.867 [0.805,0.926] | 0.22 | 0.0/0.067/0.458 | 0.83/0.94/0.882 |
| b0_lastseen | answer_now | 0.812 [0.745,0.874] | 0.00 | 0.0/0.0/0.0 | 0.762/0.914/0.831 |
| b3_perpetua_star(fremen) | answer_now | 0.824 [0.758,0.885] | 0.00 | 0.0/0.0/0.0 | 0.786/0.914/0.845 |
| b3_perpetua_star(fremen) | voi_predictive | 0.931 [0.879,0.974] | 0.68 | 0.1/0.854/0.939 | 0.938/0.954/0.946 |
| b3_perpetua_star(fremen) | sense_until_confident | 1.000 [1.000,1.000] | 2.93 | 2.825/3.871/2.381 | 1.0/1.0/1.0 |

**Named-cell gaps (paired per-object, C2):**
- **voi_b3f − sense_until_conf_b3f (re-prediction vs elimination)**: -0.069 [-0.121,-0.027] (CI-sep) (n_obj=28)
- **voi_b3f − answer_now_b3f (value of acting)**: +0.107 [+0.059,+0.163] (CI-sep) (n_obj=28)
- **voi_b3f − voi_b2 (does predictive belief matter)**: +0.064 [+0.018,+0.123] (CI-sep) (n_obj=28)
- **answer_now_b3f − answer_now_b2 (routine vs decay, passive)**: +0.012 [+0.001,+0.025] (CI-sep) (n_obj=28)
- **answer_now_b3s − answer_now_b3f (LLM prior, passive)**: +0.001 [-0.007,+0.010] (n_obj=28)
- **voi_b3s − voi_b3f (LLM prior, active)**: +0.013 [+0.001,+0.026] (CI-sep) (n_obj=28)

