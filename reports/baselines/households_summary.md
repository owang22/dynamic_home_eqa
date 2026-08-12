# Household summary — realized timings + intrinsic dynamics

ATUS survey columns: NEEDS_DATA (bls.gov blocks scripted downloads; see module docstring for the manual path).

Absences come from `at: ELSEWHERE` activity blocks, which is also what feeds the exporter's person-away projection (a carried object is OUT_OF_HOUSE while its carrier is out). Sleep blocks are excluded from awake time, which is where questions and sightings are drawn from.

## Realized timing marginals (median [p10–p90], from the realized activity blocks)

| household | resident | wake | first departure | return | meal starts |
|---|---|---|---|---|---|
| hh1 | resident_1 | 16:45 [14:52–18:09] | 22:16 [16:19–22:25] | 07:12 [07:00–19:17] | 07:29 [07:09–08:08] |

## Bank-intrinsic dynamics (exported uniform banks)

| household | objects | modal share (time) | at query times | moves/day | stint med/p90 h | stationarity |
|---|---|---|---|---|---|---|
| hh1 | 17 | 0.573 | 0.525 | 25.4 | 15.1 / 36.8 | PASS |
