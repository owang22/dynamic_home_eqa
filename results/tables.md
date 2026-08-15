# Budgeted whole-house belief tracking on HOMER+

Every number below is derived from `results/raw_results.csv` by `beliefsim.report` through `beliefsim.scoring.aggregate_ratio`. No number in this file is computed by a second code path.

**Aggregation: MACRO over household** unless a table says otherwise — each of the three households weighs equally, whatever its object count. Micro-averages over instants are available from the same CSV by changing one argument; they differ from these by <0.01 because the households are of similar size.

## Scale of the displaced slice

The displaced slice is the primary metric, so its size is reported before any conclusion is drawn from it.

| household | objects | receptacles | scored instants | displaced | share |
|---|---|---|---|---|---|
| HH-A | 50 | 26 | 8500 | 663 | 0.078 |
| HH-B | 49 | 29 | 8330 | 625 | 0.075 |
| HH-C | 39 | 25 | 6630 | 560 | 0.084 |

Per household-day the displaced count runs 38-100. That is enough to separate methods at the household level, which is the unit of analysis; it is NOT enough to read a single household-day.

## Primary results

### Displaced-instant accuracy

Top-1 accuracy restricted to instants where the object is NOT at its learning-period modal receptacle. This is where the signal is: the all-instant number is dominated by inertia and compresses every method into the top few points.

| belief | policy | B=0 | B=1 | B=2 | B=5 | B=10 | B=25 | B=50 | B=all |
|---|---|---|---|---|---|---|---|---|---|
| last_observation | random | 0.037 | 0.195 | 0.252 | 0.229 | 0.278 | 0.299 | 0.361 | 1.000 |
| last_observation | round_robin | 0.037 | 0.257 | 0.254 | 0.260 | 0.256 | 0.339 | 0.330 | 1.000 |
| last_observation | staleness_first | 0.037 | 0.227 | 0.258 | 0.208 | 0.291 | 0.299 | 0.338 | 1.000 |
| last_observation | entropy_first | 0.037 | 0.258 | 0.235 | 0.234 | 0.269 | 0.341 | 0.346 | 1.000 |
| most_frequent | random | 0.036 | 0.149 | 0.208 | 0.134 | 0.111 | 0.097 | 0.085 | 1.000 |
| most_frequent | round_robin | 0.036 | 0.226 | 0.188 | 0.128 | 0.170 | 0.177 | 0.189 | 1.000 |
| most_frequent | staleness_first | 0.036 | 0.260 | 0.246 | 0.141 | 0.173 | 0.207 | 0.145 | 1.000 |
| most_frequent | entropy_first | 0.036 | 0.208 | 0.244 | 0.210 | 0.231 | 0.276 | 0.389 | 1.000 |
| timetable | random | 0.039 | 0.224 | 0.225 | 0.274 | 0.422 | 0.536 | 0.580 | 1.000 |
| timetable | round_robin | 0.039 | 0.251 | 0.267 | 0.285 | 0.402 | 0.441 | 0.478 | 1.000 |
| timetable | staleness_first | 0.039 | 0.272 | 0.285 | 0.324 | 0.343 | 0.439 | 0.499 | 1.000 |
| timetable | entropy_first | 0.039 | 0.269 | 0.343 | 0.448 | 0.506 | 0.638 | 0.719 | 1.000 |
| fremen | random | 0.035 | 0.200 | 0.187 | 0.144 | 0.161 | 0.170 | 0.210 | 1.000 |
| fremen | round_robin | 0.035 | 0.260 | 0.232 | 0.176 | 0.167 | 0.274 | 0.247 | 1.000 |
| fremen | staleness_first | 0.035 | 0.343 | 0.250 | 0.162 | 0.172 | 0.207 | 0.224 | 1.000 |
| fremen | entropy_first | 0.035 | 0.253 | 0.287 | 0.290 | 0.193 | 0.344 | 0.321 | 1.000 |
| pooled_class | random | 0.035 | 0.171 | 0.266 | 0.280 | 0.374 | 0.502 | 0.553 | 1.000 |
| pooled_class | round_robin | 0.035 | 0.222 | 0.238 | 0.322 | 0.386 | 0.417 | 0.426 | 1.000 |
| pooled_class | staleness_first | 0.035 | 0.233 | 0.257 | 0.291 | 0.330 | 0.454 | 0.447 | 1.000 |
| pooled_class | entropy_first | 0.035 | 0.208 | 0.231 | 0.481 | 0.545 | 0.604 | 0.692 | 1.000 |
| uniform | random | 0.036 | 0.035 | 0.037 | 0.035 | 0.040 | 0.038 | 0.037 | 0.041 |
| uniform | round_robin | 0.036 | 0.039 | 0.038 | 0.036 | 0.037 | 0.039 | 0.038 | 0.036 |
| uniform | staleness_first | 0.036 | 0.036 | 0.037 | 0.037 | 0.038 | 0.035 | 0.035 | 0.041 |
| uniform | entropy_first | 0.036 | 0.035 | 0.038 | 0.035 | 0.037 | 0.038 | 0.043 | 0.039 |

### All-instant accuracy

Top-1 accuracy over every object at every scored timestep. Reported for completeness; a predictor that always guesses each object's habitual receptacle scores ~0.92 here.

| belief | policy | B=0 | B=1 | B=2 | B=5 | B=10 | B=25 | B=50 | B=all |
|---|---|---|---|---|---|---|---|---|---|
| last_observation | random | 0.038 | 0.702 | 0.834 | 0.890 | 0.886 | 0.896 | 0.897 | 1.000 |
| last_observation | round_robin | 0.038 | 0.889 | 0.883 | 0.880 | 0.888 | 0.893 | 0.899 | 1.000 |
| last_observation | staleness_first | 0.038 | 0.887 | 0.886 | 0.892 | 0.886 | 0.895 | 0.897 | 1.000 |
| last_observation | entropy_first | 0.038 | 0.892 | 0.884 | 0.898 | 0.892 | 0.895 | 0.900 | 1.000 |
| most_frequent | random | 0.037 | 0.724 | 0.847 | 0.912 | 0.916 | 0.921 | 0.925 | 1.000 |
| most_frequent | round_robin | 0.037 | 0.881 | 0.898 | 0.912 | 0.912 | 0.911 | 0.915 | 1.000 |
| most_frequent | staleness_first | 0.037 | 0.881 | 0.900 | 0.910 | 0.910 | 0.909 | 0.916 | 1.000 |
| most_frequent | entropy_first | 0.037 | 0.898 | 0.890 | 0.897 | 0.888 | 0.911 | 0.912 | 1.000 |
| timetable | random | 0.038 | 0.692 | 0.867 | 0.917 | 0.930 | 0.941 | 0.951 | 1.000 |
| timetable | round_robin | 0.038 | 0.885 | 0.905 | 0.914 | 0.917 | 0.927 | 0.930 | 1.000 |
| timetable | staleness_first | 0.038 | 0.881 | 0.903 | 0.912 | 0.922 | 0.927 | 0.930 | 1.000 |
| timetable | entropy_first | 0.038 | 0.890 | 0.911 | 0.936 | 0.944 | 0.950 | 0.962 | 1.000 |
| fremen | random | 0.037 | 0.705 | 0.867 | 0.910 | 0.912 | 0.917 | 0.925 | 1.000 |
| fremen | round_robin | 0.037 | 0.884 | 0.899 | 0.905 | 0.909 | 0.904 | 0.913 | 1.000 |
| fremen | staleness_first | 0.037 | 0.877 | 0.898 | 0.911 | 0.910 | 0.913 | 0.914 | 1.000 |
| fremen | entropy_first | 0.037 | 0.882 | 0.899 | 0.899 | 0.900 | 0.908 | 0.926 | 1.000 |
| pooled_class | random | 0.038 | 0.792 | 0.880 | 0.923 | 0.929 | 0.945 | 0.953 | 1.000 |
| pooled_class | round_robin | 0.038 | 0.898 | 0.913 | 0.915 | 0.922 | 0.930 | 0.935 | 1.000 |
| pooled_class | staleness_first | 0.038 | 0.900 | 0.906 | 0.916 | 0.922 | 0.929 | 0.935 | 1.000 |
| pooled_class | entropy_first | 0.038 | 0.910 | 0.924 | 0.941 | 0.952 | 0.963 | 0.972 | 1.000 |
| uniform | random | 0.037 | 0.038 | 0.037 | 0.037 | 0.038 | 0.037 | 0.038 | 0.038 |
| uniform | round_robin | 0.037 | 0.038 | 0.038 | 0.039 | 0.037 | 0.038 | 0.038 | 0.037 |
| uniform | staleness_first | 0.037 | 0.039 | 0.038 | 0.037 | 0.038 | 0.038 | 0.037 | 0.037 |
| uniform | entropy_first | 0.037 | 0.037 | 0.037 | 0.037 | 0.037 | 0.037 | 0.039 | 0.038 |

## Calibration

### Brier score (lower is better)

Multiclass Brier over the full receptacle set, per scored instant. An uncertainty-driven policy is only as good as the uncertainty it reads, and top-1 cannot show that.

| belief | policy | B=0 | B=1 | B=2 | B=5 | B=10 | B=25 | B=50 | B=all |
|---|---|---|---|---|---|---|---|---|---|
| last_observation | random | 0.962 | 0.391 | 0.267 | 0.220 | 0.227 | 0.208 | 0.206 | 0.000 |
| last_observation | round_robin | 0.962 | 0.223 | 0.233 | 0.241 | 0.224 | 0.214 | 0.201 | 0.000 |
| last_observation | staleness_first | 0.962 | 0.226 | 0.228 | 0.215 | 0.227 | 0.210 | 0.207 | 0.000 |
| last_observation | entropy_first | 0.962 | 0.216 | 0.233 | 0.203 | 0.217 | 0.209 | 0.200 | 0.000 |
| most_frequent | random | 0.962 | 0.337 | 0.208 | 0.132 | 0.123 | 0.116 | 0.111 | 0.000 |
| most_frequent | round_robin | 0.962 | 0.204 | 0.162 | 0.143 | 0.135 | 0.136 | 0.134 | 0.000 |
| most_frequent | staleness_first | 0.962 | 0.206 | 0.156 | 0.146 | 0.143 | 0.138 | 0.131 | 0.000 |
| most_frequent | entropy_first | 0.962 | 0.199 | 0.218 | 0.202 | 0.223 | 0.177 | 0.175 | 0.000 |
| timetable | random | 0.962 | 0.368 | 0.197 | 0.134 | 0.115 | 0.097 | 0.076 | 0.000 |
| timetable | round_robin | 0.962 | 0.202 | 0.160 | 0.147 | 0.143 | 0.124 | 0.114 | 0.000 |
| timetable | staleness_first | 0.962 | 0.208 | 0.161 | 0.148 | 0.135 | 0.125 | 0.114 | 0.000 |
| timetable | entropy_first | 0.962 | 0.215 | 0.175 | 0.126 | 0.110 | 0.099 | 0.076 | 0.000 |
| fremen | random | 0.962 | 0.358 | 0.194 | 0.137 | 0.133 | 0.127 | 0.117 | 0.000 |
| fremen | round_robin | 0.962 | 0.195 | 0.167 | 0.150 | 0.140 | 0.157 | 0.144 | 0.000 |
| fremen | staleness_first | 0.962 | 0.212 | 0.164 | 0.142 | 0.142 | 0.140 | 0.139 | 0.000 |
| fremen | entropy_first | 0.962 | 0.233 | 0.202 | 0.201 | 0.199 | 0.183 | 0.148 | 0.000 |
| pooled_class | random | 0.962 | 0.371 | 0.228 | 0.129 | 0.108 | 0.086 | 0.072 | 0.000 |
| pooled_class | round_robin | 0.962 | 0.262 | 0.172 | 0.137 | 0.124 | 0.114 | 0.108 | 0.000 |
| pooled_class | staleness_first | 0.962 | 0.257 | 0.178 | 0.138 | 0.125 | 0.113 | 0.102 | 0.000 |
| pooled_class | entropy_first | 0.962 | 0.255 | 0.164 | 0.108 | 0.086 | 0.069 | 0.053 | 0.000 |
| uniform | random | 0.962 | 0.962 | 0.962 | 0.962 | 0.962 | 0.962 | 0.962 | 0.962 |
| uniform | round_robin | 0.962 | 0.962 | 0.962 | 0.962 | 0.962 | 0.962 | 0.962 | 0.962 |
| uniform | staleness_first | 0.962 | 0.962 | 0.962 | 0.962 | 0.962 | 0.962 | 0.962 | 0.962 |
| uniform | entropy_first | 0.962 | 0.962 | 0.962 | 0.962 | 0.962 | 0.962 | 0.962 | 0.962 |

### Log loss, nats (lower is better)

Floored at 1e-6, so a confident-and-wrong belief costs at most 13.8 nats. One-hot beliefs (last-observation) are punished hardest here and that is the intended reading.

| belief | policy | B=0 | B=1 | B=2 | B=5 | B=10 | B=25 | B=50 | B=all |
|---|---|---|---|---|---|---|---|---|---|
| last_observation | random | 3.281 | 1.979 | 1.623 | 1.517 | 1.570 | 1.436 | 1.420 | 0.000 |
| last_observation | round_robin | 3.281 | 1.539 | 1.613 | 1.663 | 1.547 | 1.479 | 1.389 | 0.000 |
| last_observation | staleness_first | 3.281 | 1.565 | 1.574 | 1.487 | 1.568 | 1.454 | 1.429 | 0.000 |
| last_observation | entropy_first | 3.281 | 1.490 | 1.607 | 1.405 | 1.497 | 1.444 | 1.381 | 0.000 |
| most_frequent | random | 3.281 | 1.507 | 0.937 | 0.436 | 0.322 | 0.239 | 0.215 | 0.000 |
| most_frequent | round_robin | 3.281 | 1.245 | 0.713 | 0.615 | 0.470 | 0.449 | 0.470 | 0.000 |
| most_frequent | staleness_first | 3.281 | 1.263 | 0.708 | 0.577 | 0.522 | 0.414 | 0.372 | 0.000 |
| most_frequent | entropy_first | 3.281 | 1.339 | 1.475 | 1.368 | 1.524 | 1.215 | 1.210 | 0.000 |
| timetable | random | 3.281 | 1.596 | 0.979 | 0.605 | 0.546 | 0.486 | 0.315 | 0.000 |
| timetable | round_robin | 3.281 | 1.259 | 0.830 | 0.735 | 0.754 | 0.653 | 0.501 | 0.000 |
| timetable | staleness_first | 3.281 | 1.291 | 0.787 | 0.745 | 0.702 | 0.638 | 0.512 | 0.000 |
| timetable | entropy_first | 3.281 | 1.450 | 1.176 | 0.848 | 0.724 | 0.672 | 0.519 | 0.000 |
| fremen | random | 3.281 | 1.602 | 0.904 | 0.459 | 0.380 | 0.337 | 0.303 | 0.000 |
| fremen | round_robin | 3.281 | 1.160 | 0.781 | 0.602 | 0.488 | 0.637 | 0.565 | 0.000 |
| fremen | staleness_first | 3.281 | 1.288 | 0.775 | 0.556 | 0.534 | 0.515 | 0.499 | 0.000 |
| fremen | entropy_first | 3.281 | 1.570 | 1.375 | 1.370 | 1.364 | 1.262 | 1.019 | 0.000 |
| pooled_class | random | 3.281 | 1.193 | 0.701 | 0.363 | 0.257 | 0.193 | 0.156 | 0.000 |
| pooled_class | round_robin | 3.281 | 0.802 | 0.536 | 0.394 | 0.356 | 0.328 | 0.351 | 0.000 |
| pooled_class | staleness_first | 3.281 | 0.796 | 0.540 | 0.405 | 0.379 | 0.309 | 0.305 | 0.000 |
| pooled_class | entropy_first | 3.281 | 0.770 | 0.526 | 0.317 | 0.243 | 0.206 | 0.165 | 0.000 |
| uniform | random | 3.281 | 3.281 | 3.281 | 3.281 | 3.281 | 3.281 | 3.281 | 3.281 |
| uniform | round_robin | 3.281 | 3.281 | 3.281 | 3.281 | 3.281 | 3.281 | 3.281 | 3.281 |
| uniform | staleness_first | 3.281 | 3.281 | 3.281 | 3.281 | 3.281 | 3.281 | 3.281 | 3.281 |
| uniform | entropy_first | 3.281 | 3.281 | 3.281 | 3.281 | 3.281 | 3.281 | 3.281 | 3.281 |

## Per-household detail

### Displaced-instant accuracy by household

Policy: staleness_first. The household is the unit of analysis (n=3), so per-household columns are the result and the mean is descriptive.

| belief | B=0 | B=1 | B=2 | B=5 | B=10 | B=25 | B=50 | B=all |
|---|---|---|---|---|---|---|---|---|
| last_observation / HH-A | 0.042 | 0.282 | 0.270 | 0.245 | 0.287 | 0.206 | 0.286 | 1.000 |
| last_observation / HH-B | 0.034 | 0.195 | 0.239 | 0.163 | 0.307 | 0.354 | 0.375 | 1.000 |
| last_observation / HH-C | 0.036 | 0.204 | 0.266 | 0.217 | 0.278 | 0.336 | 0.353 | 1.000 |
| most_frequent / HH-A | 0.036 | 0.211 | 0.292 | 0.189 | 0.255 | 0.357 | 0.260 | 1.000 |
| most_frequent / HH-B | 0.035 | 0.235 | 0.217 | 0.109 | 0.116 | 0.155 | 0.095 | 1.000 |
| most_frequent / HH-C | 0.038 | 0.333 | 0.229 | 0.126 | 0.149 | 0.110 | 0.081 | 1.000 |
| timetable / HH-A | 0.040 | 0.220 | 0.257 | 0.272 | 0.190 | 0.227 | 0.347 | 1.000 |
| timetable / HH-B | 0.034 | 0.239 | 0.279 | 0.301 | 0.339 | 0.454 | 0.472 | 1.000 |
| timetable / HH-C | 0.041 | 0.357 | 0.320 | 0.397 | 0.501 | 0.638 | 0.679 | 1.000 |
| fremen / HH-A | 0.045 | 0.405 | 0.299 | 0.253 | 0.282 | 0.147 | 0.272 | 1.000 |
| fremen / HH-B | 0.026 | 0.335 | 0.225 | 0.092 | 0.102 | 0.103 | 0.109 | 1.000 |
| fremen / HH-C | 0.035 | 0.291 | 0.225 | 0.142 | 0.133 | 0.369 | 0.291 | 1.000 |
| pooled_class / HH-A | 0.034 | 0.170 | 0.239 | 0.233 | 0.192 | 0.305 | 0.250 | 1.000 |
| pooled_class / HH-B | 0.036 | 0.204 | 0.294 | 0.268 | 0.290 | 0.448 | 0.450 | 1.000 |
| pooled_class / HH-C | 0.035 | 0.327 | 0.239 | 0.372 | 0.508 | 0.610 | 0.643 | 1.000 |
| uniform / HH-A | 0.036 | 0.037 | 0.034 | 0.041 | 0.041 | 0.038 | 0.041 | 0.041 |
| uniform / HH-B | 0.035 | 0.030 | 0.036 | 0.034 | 0.036 | 0.026 | 0.030 | 0.038 |
| uniform / HH-C | 0.036 | 0.043 | 0.041 | 0.036 | 0.038 | 0.041 | 0.035 | 0.044 |

## Diagnostics

### Diagnostics

`just-sensed` is the accuracy on objects observed at the scored instant itself (trivially 1.000 for every method — the short-circuit is shared, see `beliefsim.beliefs._ExactSighting`); `not-sensed` is the accuracy on everything else, i.e. the inference the experiment is actually about. `staleness` is the mean hours since last observation over objects ever observed. `value/sense` is (accuracy - never-sense accuracy) / budget, in accuracy points per daily look.

| belief | policy | budget | all | just-sensed | not-sensed | displaced, not-sensed | staleness h | value/sense |
|---|---|---|---|---|---|---|---|---|
| last_observation | random | 0 | 0.038 | -- | 0.038 | 0.037 | -- | -- |
| last_observation | random | 1 | 0.702 | 1.000 | 0.702 | 0.194 | 640.0 | 0.6645 |
| last_observation | random | 2 | 0.834 | 1.000 | 0.834 | 0.250 | 449.8 | 0.3983 |
| last_observation | random | 5 | 0.890 | 1.000 | 0.889 | 0.224 | 222.6 | 0.1705 |
| last_observation | random | 10 | 0.886 | 1.000 | 0.885 | 0.268 | 107.3 | 0.0849 |
| last_observation | random | 25 | 0.896 | 1.000 | 0.893 | 0.277 | 43.5 | 0.0343 |
| last_observation | random | 50 | 0.897 | 1.000 | 0.890 | 0.316 | 20.9 | 0.0172 |
| last_observation | random | all | 1.000 | 1.000 | -- | -- | 0.0 | -- |
| last_observation | round_robin | 0 | 0.038 | -- | 0.038 | 0.037 | -- | -- |
| last_observation | round_robin | 1 | 0.889 | 1.000 | 0.888 | 0.256 | 551.7 | 0.8510 |
| last_observation | round_robin | 2 | 0.883 | 1.000 | 0.883 | 0.252 | 274.6 | 0.4228 |
| last_observation | round_robin | 5 | 0.880 | 1.000 | 0.879 | 0.254 | 109.6 | 0.1684 |
| last_observation | round_robin | 10 | 0.888 | 1.000 | 0.887 | 0.247 | 54.5 | 0.0850 |
| last_observation | round_robin | 25 | 0.893 | 1.000 | 0.889 | 0.315 | 21.4 | 0.0342 |
| last_observation | round_robin | 50 | 0.899 | 1.000 | 0.892 | 0.287 | 10.3 | 0.0172 |
| last_observation | round_robin | all | 1.000 | 1.000 | -- | -- | 0.0 | -- |
| last_observation | staleness_first | 0 | 0.038 | -- | 0.038 | 0.037 | -- | -- |
| last_observation | staleness_first | 1 | 0.887 | 1.000 | 0.887 | 0.226 | 551.4 | 0.8492 |
| last_observation | staleness_first | 2 | 0.886 | 1.000 | 0.886 | 0.256 | 275.7 | 0.4242 |
| last_observation | staleness_first | 5 | 0.892 | 1.000 | 0.892 | 0.204 | 109.7 | 0.1709 |
| last_observation | staleness_first | 10 | 0.886 | 1.000 | 0.885 | 0.281 | 54.5 | 0.0849 |
| last_observation | staleness_first | 25 | 0.895 | 1.000 | 0.891 | 0.277 | 21.4 | 0.0343 |
| last_observation | staleness_first | 50 | 0.897 | 1.000 | 0.889 | 0.292 | 10.3 | 0.0172 |
| last_observation | staleness_first | all | 1.000 | 1.000 | -- | -- | 0.0 | -- |
| last_observation | entropy_first | 0 | 0.038 | -- | 0.038 | 0.037 | -- | -- |
| last_observation | entropy_first | 1 | 0.892 | 1.000 | 0.892 | 0.257 | 758.0 | 0.8545 |
| last_observation | entropy_first | 2 | 0.884 | 1.000 | 0.883 | 0.232 | 513.8 | 0.4230 |
| last_observation | entropy_first | 5 | 0.898 | 1.000 | 0.898 | 0.229 | 219.7 | 0.1721 |
| last_observation | entropy_first | 10 | 0.892 | 1.000 | 0.890 | 0.259 | 107.6 | 0.0854 |
| last_observation | entropy_first | 25 | 0.895 | 1.000 | 0.892 | 0.319 | 42.7 | 0.0343 |
| last_observation | entropy_first | 50 | 0.900 | 1.000 | 0.893 | 0.298 | 20.7 | 0.0172 |
| last_observation | entropy_first | all | 1.000 | 1.000 | -- | -- | 0.0 | -- |
| most_frequent | random | 0 | 0.037 | -- | 0.037 | 0.036 | -- | -- |
| most_frequent | random | 1 | 0.724 | 1.000 | 0.724 | 0.148 | 628.6 | 0.6870 |
| most_frequent | random | 2 | 0.847 | 1.000 | 0.847 | 0.205 | 460.6 | 0.4052 |
| most_frequent | random | 5 | 0.912 | 1.000 | 0.912 | 0.129 | 217.9 | 0.1751 |
| most_frequent | random | 10 | 0.916 | 1.000 | 0.915 | 0.101 | 108.2 | 0.0879 |
| most_frequent | random | 25 | 0.921 | 1.000 | 0.918 | 0.066 | 41.9 | 0.0354 |
| most_frequent | random | 50 | 0.925 | 1.000 | 0.919 | 0.024 | 20.5 | 0.0178 |
| most_frequent | random | all | 1.000 | 1.000 | -- | -- | 0.0 | -- |
| most_frequent | round_robin | 0 | 0.037 | -- | 0.037 | 0.036 | -- | -- |
| most_frequent | round_robin | 1 | 0.881 | 1.000 | 0.881 | 0.225 | 550.5 | 0.8443 |
| most_frequent | round_robin | 2 | 0.898 | 1.000 | 0.897 | 0.185 | 275.3 | 0.4303 |
| most_frequent | round_robin | 5 | 0.912 | 1.000 | 0.912 | 0.123 | 109.8 | 0.1750 |
| most_frequent | round_robin | 10 | 0.912 | 1.000 | 0.911 | 0.160 | 54.5 | 0.0875 |
| most_frequent | round_robin | 25 | 0.911 | 1.000 | 0.908 | 0.151 | 21.4 | 0.0349 |
| most_frequent | round_robin | 50 | 0.915 | 1.000 | 0.910 | 0.129 | 10.3 | 0.0176 |
| most_frequent | round_robin | all | 1.000 | 1.000 | -- | -- | 0.0 | -- |
| most_frequent | staleness_first | 0 | 0.037 | -- | 0.037 | 0.036 | -- | -- |
| most_frequent | staleness_first | 1 | 0.881 | 1.000 | 0.881 | 0.259 | 551.2 | 0.8444 |
| most_frequent | staleness_first | 2 | 0.900 | 1.000 | 0.900 | 0.244 | 275.0 | 0.4316 |
| most_frequent | staleness_first | 5 | 0.910 | 1.000 | 0.909 | 0.135 | 109.7 | 0.1745 |
| most_frequent | staleness_first | 10 | 0.910 | 1.000 | 0.909 | 0.162 | 54.4 | 0.0873 |
| most_frequent | staleness_first | 25 | 0.909 | 1.000 | 0.906 | 0.177 | 21.4 | 0.0349 |
| most_frequent | staleness_first | 50 | 0.916 | 1.000 | 0.911 | 0.083 | 10.3 | 0.0176 |
| most_frequent | staleness_first | all | 1.000 | 1.000 | -- | -- | 0.0 | -- |
| most_frequent | entropy_first | 0 | 0.037 | -- | 0.037 | 0.036 | -- | -- |
| most_frequent | entropy_first | 1 | 0.898 | 1.000 | 0.898 | 0.204 | 1008.3 | 0.8607 |
| most_frequent | entropy_first | 2 | 0.890 | 1.000 | 0.890 | 0.238 | 1303.5 | 0.4264 |
| most_frequent | entropy_first | 5 | 0.897 | 1.000 | 0.897 | 0.194 | 1509.5 | 0.1721 |
| most_frequent | entropy_first | 10 | 0.888 | 1.000 | 0.886 | 0.199 | 1569.9 | 0.0851 |
| most_frequent | entropy_first | 25 | 0.911 | 1.000 | 0.908 | 0.197 | 1568.6 | 0.0350 |
| most_frequent | entropy_first | 50 | 0.912 | 1.000 | 0.906 | 0.245 | 1544.3 | 0.0175 |
| most_frequent | entropy_first | all | 1.000 | 1.000 | -- | -- | 0.0 | -- |
| timetable | random | 0 | 0.038 | -- | 0.038 | 0.039 | -- | -- |
| timetable | random | 1 | 0.692 | 1.000 | 0.692 | 0.223 | 621.5 | 0.6544 |
| timetable | random | 2 | 0.867 | 1.000 | 0.866 | 0.223 | 449.3 | 0.4143 |
| timetable | random | 5 | 0.917 | 1.000 | 0.917 | 0.270 | 211.3 | 0.1758 |
| timetable | random | 10 | 0.930 | 1.000 | 0.929 | 0.416 | 104.8 | 0.0892 |
| timetable | random | 25 | 0.941 | 1.000 | 0.939 | 0.520 | 43.2 | 0.0361 |
| timetable | random | 50 | 0.951 | 1.000 | 0.947 | 0.553 | 20.4 | 0.0183 |
| timetable | random | all | 1.000 | 1.000 | -- | -- | 0.0 | -- |
| timetable | round_robin | 0 | 0.038 | -- | 0.038 | 0.039 | -- | -- |
| timetable | round_robin | 1 | 0.885 | 1.000 | 0.885 | 0.250 | 552.6 | 0.8469 |
| timetable | round_robin | 2 | 0.905 | 1.000 | 0.904 | 0.265 | 276.0 | 0.4333 |
| timetable | round_robin | 5 | 0.914 | 1.000 | 0.914 | 0.280 | 109.8 | 0.1753 |
| timetable | round_robin | 10 | 0.917 | 1.000 | 0.916 | 0.395 | 54.5 | 0.0879 |
| timetable | round_robin | 25 | 0.927 | 1.000 | 0.924 | 0.424 | 21.4 | 0.0355 |
| timetable | round_robin | 50 | 0.930 | 1.000 | 0.926 | 0.439 | 10.3 | 0.0178 |
| timetable | round_robin | all | 1.000 | 1.000 | -- | -- | 0.0 | -- |
| timetable | staleness_first | 0 | 0.038 | -- | 0.038 | 0.039 | -- | -- |
| timetable | staleness_first | 1 | 0.881 | 1.000 | 0.881 | 0.271 | 552.2 | 0.8427 |
| timetable | staleness_first | 2 | 0.903 | 1.000 | 0.903 | 0.284 | 275.4 | 0.4326 |
| timetable | staleness_first | 5 | 0.912 | 1.000 | 0.911 | 0.319 | 109.6 | 0.1748 |
| timetable | staleness_first | 10 | 0.922 | 1.000 | 0.921 | 0.335 | 54.5 | 0.0884 |
| timetable | staleness_first | 25 | 0.927 | 1.000 | 0.925 | 0.421 | 21.4 | 0.0356 |
| timetable | staleness_first | 50 | 0.930 | 1.000 | 0.925 | 0.462 | 10.3 | 0.0178 |
| timetable | staleness_first | all | 1.000 | 1.000 | -- | -- | 0.0 | -- |
| timetable | entropy_first | 0 | 0.038 | -- | 0.038 | 0.039 | -- | -- |
| timetable | entropy_first | 1 | 0.890 | 1.000 | 0.890 | 0.267 | 902.9 | 0.8523 |
| timetable | entropy_first | 2 | 0.911 | 1.000 | 0.911 | 0.338 | 871.7 | 0.4365 |
| timetable | entropy_first | 5 | 0.936 | 1.000 | 0.935 | 0.439 | 354.3 | 0.1796 |
| timetable | entropy_first | 10 | 0.944 | 1.000 | 0.943 | 0.488 | 203.2 | 0.0906 |
| timetable | entropy_first | 25 | 0.950 | 1.000 | 0.948 | 0.591 | 131.7 | 0.0365 |
| timetable | entropy_first | 50 | 0.962 | 1.000 | 0.959 | 0.636 | 71.1 | 0.0185 |
| timetable | entropy_first | all | 1.000 | 1.000 | -- | -- | 0.0 | -- |
| fremen | random | 0 | 0.037 | -- | 0.037 | 0.035 | -- | -- |
| fremen | random | 1 | 0.705 | 1.000 | 0.705 | 0.198 | 646.3 | 0.6680 |
| fremen | random | 2 | 0.867 | 1.000 | 0.866 | 0.185 | 463.6 | 0.4147 |
| fremen | random | 5 | 0.910 | 1.000 | 0.910 | 0.138 | 214.6 | 0.1746 |
| fremen | random | 10 | 0.912 | 1.000 | 0.910 | 0.149 | 109.0 | 0.0874 |
| fremen | random | 25 | 0.917 | 1.000 | 0.914 | 0.146 | 42.4 | 0.0352 |
| fremen | random | 50 | 0.925 | 1.000 | 0.919 | 0.157 | 20.6 | 0.0177 |
| fremen | random | all | 1.000 | 1.000 | -- | -- | 0.0 | -- |
| fremen | round_robin | 0 | 0.037 | -- | 0.037 | 0.035 | -- | -- |
| fremen | round_robin | 1 | 0.884 | 1.000 | 0.883 | 0.258 | 550.7 | 0.8461 |
| fremen | round_robin | 2 | 0.899 | 1.000 | 0.899 | 0.230 | 275.2 | 0.4308 |
| fremen | round_robin | 5 | 0.905 | 1.000 | 0.905 | 0.170 | 109.8 | 0.1736 |
| fremen | round_robin | 10 | 0.909 | 1.000 | 0.908 | 0.157 | 54.6 | 0.0871 |
| fremen | round_robin | 25 | 0.904 | 1.000 | 0.901 | 0.248 | 21.4 | 0.0347 |
| fremen | round_robin | 50 | 0.913 | 1.000 | 0.907 | 0.199 | 10.3 | 0.0175 |
| fremen | round_robin | all | 1.000 | 1.000 | -- | -- | 0.0 | -- |
| fremen | staleness_first | 0 | 0.037 | -- | 0.037 | 0.035 | -- | -- |
| fremen | staleness_first | 1 | 0.877 | 1.000 | 0.877 | 0.343 | 551.3 | 0.8395 |
| fremen | staleness_first | 2 | 0.898 | 1.000 | 0.898 | 0.248 | 274.9 | 0.4303 |
| fremen | staleness_first | 5 | 0.911 | 1.000 | 0.910 | 0.158 | 109.7 | 0.1746 |
| fremen | staleness_first | 10 | 0.910 | 1.000 | 0.909 | 0.161 | 54.5 | 0.0873 |
| fremen | staleness_first | 25 | 0.913 | 1.000 | 0.910 | 0.185 | 21.4 | 0.0350 |
| fremen | staleness_first | 50 | 0.914 | 1.000 | 0.908 | 0.168 | 10.3 | 0.0175 |
| fremen | staleness_first | all | 1.000 | 1.000 | -- | -- | 0.0 | -- |
| fremen | entropy_first | 0 | 0.037 | -- | 0.037 | 0.035 | -- | -- |
| fremen | entropy_first | 1 | 0.882 | 1.000 | 0.881 | 0.250 | 979.7 | 0.8441 |
| fremen | entropy_first | 2 | 0.899 | 1.000 | 0.898 | 0.280 | 1313.8 | 0.4305 |
| fremen | entropy_first | 5 | 0.899 | 1.000 | 0.898 | 0.272 | 1510.3 | 0.1722 |
| fremen | entropy_first | 10 | 0.900 | 1.000 | 0.899 | 0.158 | 1572.1 | 0.0863 |
| fremen | entropy_first | 25 | 0.908 | 1.000 | 0.905 | 0.260 | 1569.8 | 0.0348 |
| fremen | entropy_first | 50 | 0.926 | 1.000 | 0.921 | 0.121 | 1542.6 | 0.0178 |
| fremen | entropy_first | all | 1.000 | 1.000 | -- | -- | 0.0 | -- |
| pooled_class | random | 0 | 0.038 | -- | 0.038 | 0.035 | -- | -- |
| pooled_class | random | 1 | 0.792 | 1.000 | 0.791 | 0.170 | 635.5 | 0.7538 |
| pooled_class | random | 2 | 0.880 | 1.000 | 0.879 | 0.265 | 463.3 | 0.4210 |
| pooled_class | random | 5 | 0.923 | 1.000 | 0.922 | 0.275 | 221.7 | 0.1770 |
| pooled_class | random | 10 | 0.929 | 1.000 | 0.928 | 0.366 | 109.0 | 0.0891 |
| pooled_class | random | 25 | 0.945 | 1.000 | 0.943 | 0.485 | 42.7 | 0.0363 |
| pooled_class | random | 50 | 0.953 | 1.000 | 0.950 | 0.524 | 20.7 | 0.0183 |
| pooled_class | random | all | 1.000 | 1.000 | -- | -- | 0.0 | -- |
| pooled_class | round_robin | 0 | 0.038 | -- | 0.038 | 0.035 | -- | -- |
| pooled_class | round_robin | 1 | 0.898 | 1.000 | 0.898 | 0.221 | 550.6 | 0.8602 |
| pooled_class | round_robin | 2 | 0.913 | 1.000 | 0.913 | 0.237 | 275.5 | 0.4377 |
| pooled_class | round_robin | 5 | 0.915 | 1.000 | 0.915 | 0.317 | 109.7 | 0.1755 |
| pooled_class | round_robin | 10 | 0.922 | 1.000 | 0.921 | 0.378 | 54.5 | 0.0884 |
| pooled_class | round_robin | 25 | 0.930 | 1.000 | 0.928 | 0.400 | 21.4 | 0.0357 |
| pooled_class | round_robin | 50 | 0.935 | 1.000 | 0.930 | 0.389 | 10.3 | 0.0179 |
| pooled_class | round_robin | all | 1.000 | 1.000 | -- | -- | 0.0 | -- |
| pooled_class | staleness_first | 0 | 0.038 | -- | 0.038 | 0.035 | -- | -- |
| pooled_class | staleness_first | 1 | 0.900 | 1.000 | 0.900 | 0.233 | 551.3 | 0.8628 |
| pooled_class | staleness_first | 2 | 0.906 | 1.000 | 0.906 | 0.255 | 275.3 | 0.4342 |
| pooled_class | staleness_first | 5 | 0.916 | 1.000 | 0.915 | 0.287 | 109.8 | 0.1756 |
| pooled_class | staleness_first | 10 | 0.922 | 1.000 | 0.921 | 0.323 | 54.6 | 0.0884 |
| pooled_class | staleness_first | 25 | 0.929 | 1.000 | 0.927 | 0.436 | 21.4 | 0.0357 |
| pooled_class | staleness_first | 50 | 0.935 | 1.000 | 0.931 | 0.411 | 10.3 | 0.0180 |
| pooled_class | staleness_first | all | 1.000 | 1.000 | -- | -- | 0.0 | -- |
| pooled_class | entropy_first | 0 | 0.038 | -- | 0.038 | 0.035 | -- | -- |
| pooled_class | entropy_first | 1 | 0.910 | 1.000 | 0.909 | 0.207 | 725.1 | 0.8718 |
| pooled_class | entropy_first | 2 | 0.924 | 1.000 | 0.923 | 0.228 | 363.6 | 0.4429 |
| pooled_class | entropy_first | 5 | 0.941 | 1.000 | 0.940 | 0.473 | 184.6 | 0.1806 |
| pooled_class | entropy_first | 10 | 0.952 | 1.000 | 0.952 | 0.521 | 179.1 | 0.0915 |
| pooled_class | entropy_first | 25 | 0.963 | 1.000 | 0.961 | 0.525 | 334.5 | 0.0370 |
| pooled_class | entropy_first | 50 | 0.972 | 1.000 | 0.970 | 0.553 | 398.3 | 0.0187 |
| pooled_class | entropy_first | all | 1.000 | 1.000 | -- | -- | 0.0 | -- |
| uniform | random | 0 | 0.037 | -- | 0.037 | 0.036 | -- | -- |
| uniform | random | 1 | 0.038 | 0.033 | 0.038 | 0.035 | 619.7 | 0.0017 |
| uniform | random | 2 | 0.037 | 0.053 | 0.037 | 0.037 | 459.7 | 0.0004 |
| uniform | random | 5 | 0.037 | 0.039 | 0.037 | 0.035 | 215.7 | 0.0001 |
| uniform | random | 10 | 0.038 | 0.035 | 0.038 | 0.040 | 109.0 | 0.0001 |
| uniform | random | 25 | 0.037 | 0.034 | 0.037 | 0.038 | 42.4 | 0.0000 |
| uniform | random | 50 | 0.038 | 0.037 | 0.038 | 0.037 | 20.6 | 0.0000 |
| uniform | random | all | 0.038 | 0.038 | -- | -- | 0.0 | -- |
| uniform | round_robin | 0 | 0.037 | -- | 0.037 | 0.036 | -- | -- |
| uniform | round_robin | 1 | 0.038 | 0.040 | 0.038 | 0.039 | 551.5 | 0.0016 |
| uniform | round_robin | 2 | 0.038 | 0.033 | 0.038 | 0.038 | 275.6 | 0.0007 |
| uniform | round_robin | 5 | 0.039 | 0.039 | 0.039 | 0.035 | 109.6 | 0.0004 |
| uniform | round_robin | 10 | 0.037 | 0.031 | 0.037 | 0.037 | 54.6 | 0.0000 |
| uniform | round_robin | 25 | 0.038 | 0.037 | 0.038 | 0.040 | 21.4 | 0.0001 |
| uniform | round_robin | 50 | 0.038 | 0.038 | 0.038 | 0.038 | 10.3 | 0.0000 |
| uniform | round_robin | all | 0.037 | 0.037 | -- | -- | 0.0 | -- |
| uniform | staleness_first | 0 | 0.037 | -- | 0.037 | 0.036 | -- | -- |
| uniform | staleness_first | 1 | 0.039 | 0.040 | 0.039 | 0.037 | 551.9 | 0.0019 |
| uniform | staleness_first | 2 | 0.038 | 0.037 | 0.038 | 0.037 | 275.3 | 0.0006 |
| uniform | staleness_first | 5 | 0.037 | 0.036 | 0.037 | 0.037 | 109.8 | -0.0000 |
| uniform | staleness_first | 10 | 0.038 | 0.039 | 0.038 | 0.038 | 54.5 | 0.0002 |
| uniform | staleness_first | 25 | 0.038 | 0.034 | 0.038 | 0.035 | 21.4 | 0.0000 |
| uniform | staleness_first | 50 | 0.037 | 0.034 | 0.038 | 0.036 | 10.3 | 0.0000 |
| uniform | staleness_first | all | 0.037 | 0.037 | -- | -- | 0.0 | -- |
| uniform | entropy_first | 0 | 0.037 | -- | 0.037 | 0.036 | -- | -- |
| uniform | entropy_first | 1 | 0.037 | 0.040 | 0.037 | 0.035 | 623.3 | 0.0002 |
| uniform | entropy_first | 2 | 0.037 | 0.030 | 0.037 | 0.038 | 466.5 | 0.0004 |
| uniform | entropy_first | 5 | 0.037 | 0.029 | 0.037 | 0.035 | 216.4 | -0.0000 |
| uniform | entropy_first | 10 | 0.037 | 0.039 | 0.037 | 0.037 | 111.9 | 0.0001 |
| uniform | entropy_first | 25 | 0.037 | 0.036 | 0.037 | 0.038 | 43.6 | 0.0000 |
| uniform | entropy_first | 50 | 0.039 | 0.039 | 0.039 | 0.043 | 20.5 | 0.0000 |
| uniform | entropy_first | all | 0.038 | 0.038 | -- | -- | 0.0 | -- |

### Seed spread (stochastic policies)

Range of macro DISPLACED-instant accuracy over the five scoring seeds — the primary metric, and the noisiest. Seeds vary the policy's own randomisation and the argmax tie-break; they are not a substitute for the n=3 households.

| belief | policy | budget | min | max | range |
|---|---|---|---|---|---|
| last_observation | random | 1 | 0.162 | 0.248 | 0.0861 |
| last_observation | random | 5 | 0.157 | 0.295 | 0.1380 |
| last_observation | random | 25 | 0.241 | 0.380 | 0.1389 |
| last_observation | entropy_first | 1 | 0.175 | 0.410 | 0.2350 |
| last_observation | entropy_first | 5 | 0.167 | 0.329 | 0.1617 |
| last_observation | entropy_first | 25 | 0.272 | 0.372 | 0.0999 |
| most_frequent | random | 1 | 0.073 | 0.181 | 0.1082 |
| most_frequent | random | 5 | 0.039 | 0.214 | 0.1750 |
| most_frequent | random | 25 | 0.065 | 0.134 | 0.0690 |
| most_frequent | entropy_first | 1 | 0.142 | 0.254 | 0.1115 |
| most_frequent | entropy_first | 5 | 0.130 | 0.257 | 0.1270 |
| most_frequent | entropy_first | 25 | 0.216 | 0.343 | 0.1275 |
| timetable | random | 1 | 0.121 | 0.308 | 0.1867 |
| timetable | random | 5 | 0.199 | 0.344 | 0.1452 |
| timetable | random | 25 | 0.500 | 0.573 | 0.0733 |
| timetable | entropy_first | 1 | 0.148 | 0.341 | 0.1935 |
| timetable | entropy_first | 5 | 0.391 | 0.503 | 0.1111 |
| timetable | entropy_first | 25 | 0.622 | 0.654 | 0.0318 |
| fremen | random | 1 | 0.153 | 0.267 | 0.1139 |
| fremen | random | 5 | 0.068 | 0.198 | 0.1302 |
| fremen | random | 25 | 0.128 | 0.286 | 0.1576 |
| fremen | entropy_first | 1 | 0.099 | 0.394 | 0.2951 |
| fremen | entropy_first | 5 | 0.190 | 0.362 | 0.1722 |
| fremen | entropy_first | 25 | 0.206 | 0.398 | 0.1924 |
| pooled_class | random | 1 | 0.057 | 0.254 | 0.1975 |
| pooled_class | random | 5 | 0.245 | 0.321 | 0.0758 |
| pooled_class | random | 25 | 0.488 | 0.527 | 0.0382 |
| pooled_class | entropy_first | 1 | 0.114 | 0.275 | 0.1610 |
| pooled_class | entropy_first | 5 | 0.441 | 0.504 | 0.0632 |
| pooled_class | entropy_first | 25 | 0.572 | 0.622 | 0.0498 |
| uniform | random | 1 | 0.031 | 0.043 | 0.0117 |
| uniform | random | 5 | 0.031 | 0.040 | 0.0086 |
| uniform | random | 25 | 0.031 | 0.042 | 0.0117 |
| uniform | entropy_first | 1 | 0.027 | 0.042 | 0.0153 |
| uniform | entropy_first | 5 | 0.031 | 0.039 | 0.0081 |
| uniform | entropy_first | 25 | 0.034 | 0.046 | 0.0115 |

### Forced held-out ablation

k objects are unobservable to every method, so cross-method comparison is not confounded by different policies leaving different objects unseen. Scored on the held-out objects only, pooled over mask draws. `observable` is the same run's other objects, for reference.

| belief | group | B=1 | B=5 | B=25 | B=all |
|---|---|---|---|---|---|
| last_observation | heldout | 0.041 | 0.035 | 0.039 | 0.035 |
| last_observation | observable | 0.886 | 0.883 | 0.892 | 1.000 |
| most_frequent | heldout | 0.039 | 0.035 | 0.039 | 0.038 |
| most_frequent | observable | 0.884 | 0.917 | 0.921 | 1.000 |
| timetable | heldout | 0.039 | 0.039 | 0.040 | 0.036 |
| timetable | observable | 0.888 | 0.925 | 0.943 | 1.000 |
| fremen | heldout | 0.038 | 0.037 | 0.034 | 0.037 |
| fremen | observable | 0.877 | 0.915 | 0.918 | 1.000 |
| pooled_class | heldout | 0.419 | 0.454 | 0.460 | 0.460 |
| pooled_class | observable | 0.897 | 0.929 | 0.949 | 1.000 |
| uniform | heldout | 0.037 | 0.044 | 0.037 | 0.041 |
| uniform | observable | 0.037 | 0.038 | 0.038 | 0.039 |

