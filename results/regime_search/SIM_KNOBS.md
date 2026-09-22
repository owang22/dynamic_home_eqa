# Simulator knobs for the regime search (2026-09-21)

Everything here is config-driven and off by default: with no `calendar` in the config the generator's
output is byte-identical to before (checked with `cmp` on seed 10 at 8 and 28 days, all four files).

## 1. `calendar` — scripted stages (situation_sim.situation.sample_situations)

A list of stages; a day belongs to the last stage whose `days: [a, b]` (inclusive) covers it, or to no
stage. Per stage:

| field | meaning | default |
|---|---|---|
| `name` | the stage tag carried into hidden_state.json days, bank header `stages`, every question row and run-log row (`stage`) | `stageN` |
| `days: [a, b]` | inclusive day indices (day 0 = the walkthrough day, `day0` names its weekday) | required |
| `day_kind: weekday \| weekend` | overrides the day's schedule kind and event/episode rates; the weekday *name* stays the calendar's (a "holiday Tuesday" runs the weekend schedule) | calendar |
| `force_events` | list of `{event, resident}`; added as the same Cause objects the random roll makes (`sick_day:resident_1`, household scope `guest_visit`); `resident` = id, name, or `household`/omitted | none |
| `suppress_random_events` | drop the day's randomly rolled events (the rolls are still drawn, so internal states / episodes are identical with or without it) | false |
| `roles: {resident: role}` | the resident follows that role's daily schedule template for the stage (`worker_out`, `worker_home`, `student`, `shift_worker`, `retired`); the walkthrough placement keeps the base role | none |

Events available: `sick_day` (resident), `late_work` (resident, working roles), `guest_visit`, `rain`,
`grocery_delivery`, `laundry_day` (household). Episodes (moods) and internal states are not scripted; set
`events:` rates in the config to 0 and use `suppress_random_events` for a clean lead-up.

CLI: `python3 -m situation_sim.run --seed S --out DIR --days 28 --day0 Monday --calendar cal.yaml`
(`cal.yaml` = `{calendar: [...]}`); the determinism check regenerates with the same calendar.

## 2. Through the harness (baselines.patrol.confshift)

Config keys: `days` (any length), `day0`, `calendar` (as above). `ensure_households` writes
`<sim_dir>/calendar.yaml`, passes it to the generator and stamps it into `rates.json`, so editing the
calendar regenerates every requested seed on the next run. `per_day` up to 96 works (`oversample` ≥ 4×);
`classes: [..]` restricts questions to object classes as before.

Bank header additions when a calendar is present: `stages` (day → stage), `day_kinds` (day → weekday|weekend
as scheduled); `shift_days` counts a `day_kind: weekend` day and forced major events as shift days.
Question rows and classical run-log rows carry `stage`.

Cost: one household, 28 days × 96 questions, five classical agents ≈ 4 min.

## 3. Worked example — `configs/regime_example.yaml`

```yaml
day0: Monday
days: 28
events: {sick_day: {weekday: 0.10, weekend: 0.02}, guest_visit: {weekday: 0.10, weekend: 0.14}}
calendar:
  - {name: lead,    days: [0, 13],  suppress_random_events: true}
  - {name: holiday, days: [14, 14], day_kind: weekend, suppress_random_events: true}
  - {name: sick,    days: [15, 18], force_events: [{event: sick_day, resident: resident_1}], suppress_random_events: true}
  - {name: shifts,  days: [19, 25], roles: {resident_1: shift_worker}, suppress_random_events: true}
  - {name: return,  days: [26, 27], suppress_random_events: true}
per_day: 96
oversample: 384
```

`python3 -m baselines.patrol.confshift classical --config ../configs/regime_example.yaml --seeds 10 --out OUT`
gives, on hh_s10 (all questions, timetable per day): lead 51 46 70 69 56 55 71 53 64 75 68 71 69 · holiday 64 ·
sick 49 69 65 74 · shifts 67 68 57 59 70 65 72 · return 79 57; last seen 42-65 flat. The timetable re-learns a
4-day regime by its second day, so with 2 h bins the breaks are one-day dips.

Verification done for this example: `data/situation_sim/regime/hh_s10_cal/trace.md` — lead Tuesday
"leaves for work 08:21 (back 17:51)", holiday Tuesday on the weekend schedule, sick days "off sick, resting
on the couch all day", shift week "leaves for the shift 13:54 (back 22:54)"; `hidden_state.json` days carry
`stage`/`roles`; bank questions per stage lead 1248 / holiday 96 / sick 384 / shifts 672 / return 192.

## Reverse direction (home → work)

`- {name: home, days: [0, 13], day_kind: weekend, suppress_random_events: true}` then
`- {name: work, days: [14, 27], suppress_random_events: true}` (or `roles: {resident_1: worker_out}` on a
`worker_home` household). Residents at home all day move fewer things; the work week starts the trips.
