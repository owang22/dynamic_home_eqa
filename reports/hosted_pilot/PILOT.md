# Hosted-generation pilot — hh4 on gpt-5.6-luna

Snapshot: `gpt-5.6-luna` — spend ledger: hosted spend $1.4067 of $5.00 cap across 168 call(s) [gpt-5.6-luna: $0.2933 (138 calls), gpt-5.6-terra: $1.1135 (30 calls)]

## Per stage

| stage | calls | attempts | failed attempts | prompt tok | completion tok | (of which reasoning) | $ | wall s |
|---|---|---|---|---|---|---|---|---|
| L2 calendar | 3 | 3 | 0 | 17445 | 7386 | 0 | $0.0103 | — |
| L2 objects | 3 | 3 | 2 | 49821 | 12195 | 0 | $0.0246 | — |
| L2 special events | 1 | — | 0 | 2528 | 1043 | 0 | $0.0018 | — |
| story calendar (21d) | 84 | — | 0 | 806710 | 63560 | 0 | $0.2376 | 228 |
| bind pass | 1 | — | 0 | 13295 | 2507 | 0 | $0.0057 | — |

### Escalation (gpt-5.6-terra)

| stage | calls | attempts | failed attempts | prompt tok | completion tok | (of which reasoning) | $ | wall s |
|---|---|---|---|---|---|---|---|---|
| L2 calendar | 0 | 3 | 0 | 0 | 0 | 0 | $0.0000 | — |
| L2 objects | 0 | 9 | 9 | 0 | 0 | 0 | $0.0000 | — |
| L2 special events | 0 | — | 0 | 0 | 0 | 0 | $0.0000 | — |
- L2 objects failure: `{"attempt": 0, "failures": ["reachability: at-home activity 'reading' is scheduled by weekly_blocks but appears in no object rule (and carries no reset_all) \u2014 a home block that touches noth", "reachability: at-home activity 'wash_dishes' is scheduled by weekly_blocks but appears in no object ru`
- L2 objects failure: `{"attempt": 0, "failures": ["reachability: at-home activity 'get_ready' is scheduled by weekly_blocks but appears in no object rule (and carries no reset_all) \u2014 a home block that touches no"]}`

### Wall-clock (CLI stages, from timings.txt)

- schema probe: 19 s
- L2 stage (gpt-5.6-luna): 121 s
- story calendar (21d): 228 s
- realism panel: 0 s
- L2 stage (gpt-5.6-terra): 1 s

## Extrapolation (x10 households)

- measured hh4 total on gpt-5.6-luna: **$0.2799** -> x10 ~= **$2.80**
- escalated stage on gpt-5.6-terra: $0.0000 -> x10 ~= $0.00

  (Straight multiplication; hh4 is the 4-resident hard case, so this is an upper-leaning estimate for the set.)

## Quality

| model | household | n_events | events_per_day | moves_per_object_day | hour_entropy | daily_fano | fano_all | carry_frac | top2 | dead_days | twin_pairs | never_move |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt-5.6-luna | hh_004 | 2146 | 102.19 | 3.1 | 0.848 | 3.15 | 3.0 | 0.03 | 0.216 | 0 | 1 | 4/33 |
| qwen3.8-27b | hh_004 | 7119 | 339.0 | 10.27 | 0.767 | 2.92 | 2.74 | 0.021 | 0.141 | 0 | 0 | 0/33 |

- attempt burn per stage (legend: attempt burn is the model-quality signal here — a model that needs more resamples to satisfy the same contracts is the weaker generator for THIS pipeline, whatever its benchmarks say):
  - gpt-5.6-luna: {'L2 calendar': 3, 'L2 objects': 3}
  - qwen3.8-27b: {'calendar': 1, 'objects': 1, 'persona': 5}

## Caveats

- hosted `seed` is best-effort: sent (it improves stability) but not a determinism guarantee — the ResponseCache is the source of truth for reproducing this run.
- the model alias is pinned to the snapshot above from the first response; a mid-run change aborts. NOTE: the API echoes the ALIAS itself in the response `model` field (every cached record says `gpt-5.6-luna`, no dated id), so the pin detects mid-run changes but cannot name a dated snapshot — replay-level reproducibility rides the ResponseCache alone.
- sampling params (`temperature`/`top_p`) pass through unchanged (probed accepted — see the behavior probes in schema_compat.md); `reasoning_effort: minimal` no longer exists on gpt-5.6 and maps to its successor `none`.
- schema `persona` lost to the transform: const+=type (coverage in schema_compat.md)
- schema `l2_calendar` lost to the transform: const+=type, enum-dedup->$defs, items=false, optional->required+nullable (coverage in schema_compat.md)
- schema `l2_objects` lost to the transform: const+=type, enum-dedup->$defs, items=false, optional->required+nullable (coverage in schema_compat.md)
- schema `l2_special_events` lost to the transform: enum-dedup->$defs, optional->required+nullable (coverage in schema_compat.md)
- schema `bind_pass` lost to the transform: const+=type, enum-dedup->$defs, items=false, optional->required+nullable (coverage in schema_compat.md)

## Verdict

(per stage: works as-is / works with transform / needs gpt-5.6-terra / blocked)

- L2 calendar: works with transform
- L2 objects: works with transform
- L2 special events: works with transform
- story calendar: works as-is
- bind pass: works with transform

(Auto-derived from the run records; edit only with evidence.)
