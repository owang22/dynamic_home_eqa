# Household summary — realized timings + intrinsic dynamics

ATUS survey columns: NEEDS_DATA (bls.gov blocks scripted downloads; see module docstring for the manual path).

NOTE: specs encode absences two ways — `at: ELSEWHERE` blocks (hh_001 style) or named depart/return pairs (hh_002 style). Only the former feeds the exporter's person-away projection; depart/return-pair households keep carried phones ON_PERSON during absences. Standardization candidate.

## Realized timing marginals (median [p10–p90], from 28-day block realizations)

| household | resident | wake | first departure | return | meal starts |
|---|---|---|---|---|---|
| hh_001 | resident_1 | 17:03 [16:44–17:28] | 22:13 [18:06–22:25] | 07:04 [06:44–20:36] | 07:24 [07:09–07:36] |
| hh_002 | resident_1 | 06:52 [06:11–19:03] | 07:51 [07:39–09:59] | 17:44 [11:31–17:55] | — |
| hh_002 | resident_2 | 07:02 [06:00–12:53] | 07:40 [07:28–07:53] | 15:15 [12:08–15:31] | 17:24 [06:24–18:16] |
| hh_002 | resident_3 | 07:23 [06:42–15:49] | — | — | 07:11 [06:21–07:43] |
| hh_002 | resident_4 | 06:51 [06:14–07:38] | — | — | — |

## Bank-intrinsic dynamics (28-day uniform banks)

| household | objects | modal share (time) | at query times | moves/day | stint med/p90 h | stationarity |
|---|---|---|---|---|---|---|
| hh_001 | 17 | 0.571 | 0.612 | 23.0 | 12.1 / 47.2 | PASS |
| hh_002 | 40 | 0.586 | 0.527 | 61.9 | 12.2 / 36.1 | PASS |
