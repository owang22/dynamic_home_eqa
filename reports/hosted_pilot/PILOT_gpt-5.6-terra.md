# Hosted-generation pilot — hh4 on gpt-5.6-terra

Snapshot: `gpt-5.6-terra` — spend ledger: hosted spend $4.9084 of $5.00 cap across 265 call(s) [gpt-5.6-luna: $0.2933 (138 calls), gpt-5.6-terra: $4.6152 (127 calls)]

## Per stage

| stage | calls | attempts | failed attempts | prompt tok | completion tok | (of which reasoning) | $ | wall s |
|---|---|---|---|---|---|---|---|---|
| L2 calendar | 2 | 2 | 0 | 11630 | 16372 | 8250 | $0.2093 | — |
| L2 objects | 6 | 6 | 5 | 103836 | 40913 | 3080 | $0.5740 | — |
| L2 special events | 2 | — | 0 | 6490 | 12880 | 11774 | $0.1617 | — |
| story calendar (21d) | 84 | — | 0 | 761390 | 57980 | 0 | $2.2185 | 228 |
| bind pass | 1 | — | 0 | 13302 | 5367 | 0 | $0.0910 | — |

### Escalation (gpt-5.6-terra)

| stage | calls | attempts | failed attempts | prompt tok | completion tok | (of which reasoning) | $ | wall s |
|---|---|---|---|---|---|---|---|---|
| L2 calendar | 2 | 2 | 0 | 11630 | 16372 | 8250 | $0.2093 | — |
| L2 objects | 6 | 6 | 5 | 103836 | 40913 | 3080 | $0.5740 | — |
| L2 special events | 2 | — | 0 | 6490 | 12880 | 11774 | $0.1617 | — |
- L2 objects failure: `{"attempt": 0, "failures": ["reachability: at-home activity 'get_ready' is scheduled by weekly_blocks but appears in no object rule (and carries no reset_all) \u2014 a home block that touches no", "reachability: at-home activity 'shower' is scheduled by weekly_blocks but appears in no object rule (a`
- L2 objects failure: `{"attempt": 1, "failures": ["reachability: at-home activity 'meal_prep' is scheduled by weekly_blocks but appears in no object rule (and carries no reset_all) \u2014 a home block that touches no", "reachability: at-home activity 'shower' is scheduled by weekly_blocks but appears in no object rule (a`
- L2 objects failure: `{"attempt": 2, "failures": ["reachability: at-home activity 'meal_prep' is scheduled by weekly_blocks but appears in no object rule (and carries no reset_all) \u2014 a home block that touches no"]}`
- L2 objects failure: `{"attempt": 0, "failures": ["reachability: at-home activity 'meal_prep' is scheduled by weekly_blocks but appears in no object rule (and carries no reset_all) \u2014 a home block that touches no"]}`
- L2 objects failure: `{"attempt": 1, "failures": ["reachability: at-home activity 'meal_prep' is scheduled by weekly_blocks but appears in no object rule (and carries no reset_all) \u2014 a home block that touches no"]}`

### Wall-clock (CLI stages, from timings.txt)

- schema probe: 19 s
- L2 stage (gpt-5.6-luna): 121 s
- story calendar (21d): 228 s
- realism panel: 0 s
- L2 stage (gpt-5.6-terra): 1 s

## Extrapolation (x10 households)

- measured hh4 total on gpt-5.6-terra: **$3.2546** -> x10 ~= **$32.55**
- escalated stage on gpt-5.6-terra: $0.9450 -> x10 ~= $9.45

  (Straight multiplication; hh4 is the 4-resident hard case, so this is an upper-leaning estimate for the set.)

## Quality

| model | household | n_events | events_per_day | moves_per_object_day | hour_entropy | daily_fano | fano_all | carry_frac | top2 | dead_days | twin_pairs | never_move |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt-5.6-terra | hh_004 | 2941 | 140.05 | 4.24 | 0.864 | 7.13 | 6.98 | 0.117 | 0.192 | 0 | 0 | 1/33 |
| qwen3.8-27b | hh_004 | 7119 | 339.0 | 10.27 | 0.767 | 2.92 | 2.74 | 0.021 | 0.141 | 0 | 0 | 0/33 |

- attempt burn per stage (legend: attempt burn is the model-quality signal here — a model that needs more resamples to satisfy the same contracts is the weaker generator for THIS pipeline, whatever its benchmarks say):
  - gpt-5.6-terra: {'L2 calendar': 2, 'L2 objects': 6}
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


## The reasoning finding (why terra's L2 was "blocked")

Every hosted call in this pilot ran with **reasoning_effort=none** — the
brief pinned "minimal", the gpt-5.6 API retired that value, and `none`
was taken as its floor. Measured across every cached response of both
models: **0 reasoning tokens out of 225,233 completion tokens.** Terra is
a reasoning model that was run with its reasoning switched off.

The failing invariant is NOT missing from the prompt. OBJECT_RULES states
it verbatim: "every AT-HOME activity in your weekly_blocks must appear in
at least one object rule phase." It is a PROSE constraint (the schema
pins the activity enum one way only — a rule cannot name an unscheduled
activity, but nothing forces every scheduled at-home activity to get a
rule), and cross-checking 19 at-home activities against 33 objects'
rules is exactly the bookkeeping reasoning tokens exist for. Compare
[[feedback-generator-capability-ceiling]]: grammar-enforced constraints
are obeyed, prose ones are not.

Single objects call, same calendar / prompt / schema / seed, effort swept:

| reasoning_effort | reasoning tok | at-home activities left unbound | verdict |
|---|---|---|---|
| none | 0 | meal_prep, socialise_home, wash_dishes | FAIL |
| medium | 98 | meal_prep | FAIL |
| high | 1473 | none — full coverage | **PASS** |

Rerun of the full L2 at effort=high (fresh cache dir; the tag does not
fold reasoning effort, so reasoning and non-reasoning responses must
never share a cache): **hh_004 OK**, accepted on calendar attempt 2 /
objects attempt 3, 14,912 reasoning tokens. Terra's L2 is NOT blocked —
the earlier verdict was an artifact of the reasoning setting, and
`reports/hosted_pilot/build_log_terra_reasoning-none_FAILED.json`
preserves the reasoning-off evidence.

Second conditional API behavior probed here: `temperature` is accepted
ONLY with reasoning off; at any non-zero effort the API rejects a
non-default temperature outright. The adapter drops sampling params
whenever effort != none.
