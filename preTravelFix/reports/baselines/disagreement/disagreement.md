# Belief disagreement measurement

## family panel (9 beliefs)

  last_observation, most_frequent, timetable, daytype_mixture, markov1, periodic_persistence, hierarchy_backoff, smoothed_recency, perpetua_star

  questions            4500
  unanimous argmax     0.482
  mean pairwise JSD    0.304
  median pairwise JSD  0.296

  by_volatility_tercile
      bucket      n  unanimous  mean JSD
           0   1497      0.579     0.279
           1   1539      0.502     0.304
           2   1464      0.363     0.328

  by_hour
      bucket      n  unanimous  mean JSD
           0     22      0.318     0.349
           3      6      0.500     0.360
           4     81      0.531     0.303
           5    151      0.430     0.328
           6    203      0.527     0.293
           7    244      0.459     0.295
           8    262      0.427     0.321
           9    248      0.448     0.314
          10    251      0.378     0.320
          11    254      0.480     0.305
          12    248      0.504     0.302
          13    238      0.462     0.306
          14    247      0.522     0.298
          15    265      0.396     0.322
          16    263      0.521     0.294
          17    266      0.568     0.281
          18    248      0.391     0.327
          19    269      0.465     0.313
          20    273      0.604     0.278
          21    182      0.577     0.288
          22    169      0.408     0.302
          23    110      0.691     0.246

## parameter panel (6 beliefs)

  smoothed_recency(smoothing_half_life_h=1), smoothed_recency(smoothing_half_life_h=3), smoothed_recency(smoothing_half_life_h=6), smoothed_recency(smoothing_half_life_h=12), smoothed_recency(smoothing_half_life_h=24), smoothed_recency(smoothing_half_life_h=48)

  questions            4500
  unanimous argmax     0.923
  mean pairwise JSD    0.085
  median pairwise JSD  0.082

  by_volatility_tercile
      bucket      n  unanimous  mean JSD
           0   1497      0.955     0.089
           1   1539      0.910     0.080
           2   1464      0.903     0.087

  by_hour
      bucket      n  unanimous  mean JSD
           0     22      0.909     0.079
           3      6      0.833     0.080
           4     81      0.889     0.094
           5    151      0.947     0.086
           6    203      0.956     0.079
           7    244      0.955     0.090
           8    262      0.950     0.089
           9    248      0.895     0.088
          10    251      0.888     0.087
          11    254      0.906     0.085
          12    248      0.911     0.082
          13    238      0.878     0.084
          14    247      0.915     0.086
          15    265      0.902     0.084
          16    263      0.939     0.082
          17    266      0.932     0.091
          18    248      0.940     0.092
          19    269      0.903     0.085
          20    273      0.927     0.085
          21    182      0.951     0.088
          22    169      0.941     0.072
          23    110      0.955     0.070

