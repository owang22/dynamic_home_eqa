# atypicals_report.md — atyp_v2 bank (addendum v2 transformations)

All atypical households are DETERMINISTIC registered transforms of VERIFIED
typical profiles. Object bindings + placements are inherited byte-for-byte;
only schedule timing changes. Provenance is inherited from the (VERIFIED)
base; V6a/V6b (ATUS/HOMER) gate the base only, V1–V5 + V6c-integrity gate the
transform. Reportable = 0 FAIL on the transformed profile.

Bank reportable: True.  Envelope hash: `d7cdf419c00016cb`.

| household | transform | params | base | dist | V1–V5 | coverage | reportable |
|---|---|---|---|---|---|---|---|
| single_adult_typ_v1__atyp_t1_night_2300-0700 | night_shift_reversion | {'work_block_start': '23:00', 'work_block_end': '07:00', 'workdays': None, 'transition_block': True, 'shift_activity': None} | single_adult_typ_v1 | 0.14028 | PASS | 0.458 | yes |
| single_adult_typ_v1__atyp_t2_three_twelves | workday_pattern | {'pattern': 'three_twelves'} | single_adult_typ_v1 | 0.10986 | PASS | 0.4911 | yes |
| family4_typ_v1__atyp_t2_weekend_worker | workday_pattern | {'pattern': 'weekend_worker'} | family4_typ_v1 | 0.11643 | PASS | 0.3997 | yes |

## W1 observation-coverage confound check

- mean coverage: typ_v1 = 0.481, atyp_v2 = 0.450
- relative difference = 6.6% (OK (<10%))
  (24h-spread jittered snapshots prevent systematic under-observation of night-active homes.)

## W2 day-type movement structure (per household, in the bank manifest)

- **single_adult_typ_v1__atyp_t1_night_2300-0700** workdays=[0, 1, 2, 3, 4] (n_work=22/n_off=8): phone 5.636/2.0 (wk/off), water_glass 3.045/0.375 (wk/off), fork 2.591/0.0 (wk/off), knife 2.545/2.5 (wk/off)
- **single_adult_typ_v1__atyp_t2_three_twelves** workdays=[0, 1, 2] (n_work=14/n_off=16): phone 4.214/1.938 (wk/off), water_glass 2.857/3.062 (wk/off), knife 2.643/2.562 (wk/off), bowl 2.571/0.0 (wk/off)
- **family4_typ_v1__atyp_t2_weekend_worker** workdays=[1, 2, 3, 4, 5] (n_work=21/n_off=9): phone 10.81/4.333 (wk/off), backpack 7.19/0.111 (wk/off), bowl 4.19/2.778 (wk/off), glasses 3.952/1.889 (wk/off)

## Notes
- W4: the periodic belief B3 (fremen) has BOTH a 24h and a 168h (weekly) component
  (`fremen.py` Section C); T1/T2 households are only learnable with the weekly
  component — E2/E3 configs MUST enable `f_source=fremen_weekly`, not the daily default.
- T2.weekend_worker(roommates) is NOT in the reportable bank: it produces a V1 FAIL
  (the roommates share one game_controller, which the day-realignment forces into
  concurrent use in two rooms — a real conflict, reported not silenced). weekend_worker
  was applied to family4 instead. T3/T4 are registered + unit-tested but excluded from
  reportable banks (T4 by design; T3 pending a packer refinement).
- Superseded: the hand-authored night_shift_typ_v1 profile was retired in favor of the
  T1(single_adult) output (archive/hssd_generation/superseded_profiles/).