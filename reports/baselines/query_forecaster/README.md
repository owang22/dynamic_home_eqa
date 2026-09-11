# Query forecaster — figures for approval (STOP point)

`baselines/query_forecaster.py`: `QueryForecaster.expected_queries(t,
horizon_hours) -> {object_id: rate}`, fit as empirical per-object query
counts binned by hour of day and day type (weekday/weekend, day 0 =
Monday), divided by the number of training days of that type; a horizon
integrates the hourly rates with fractional slots pro-rated. The
interface is fixed so a learned forecaster can drop in later.

## Evaluation

Fit on the first 60% of question days (3-17) of each routine-driven
bank, scored on the held-out days (18-27):

- `forecast_heatmaps.png` — predicted vs observed held-out totals,
  object class x hour, same layout as the query stream's heatmap. The
  predicted panels reproduce the observed structure (wake-up spike,
  dinner-hour mass, phone spread) in all three households.
- `forecast_scatter.png` — per (object, hour) cell, predicted vs
  observed totals: r = 0.84 (hh_001), 0.74 (hh_003), 0.86 (hh_009).
  The forecaster clearly tracks the routine; residual spread comes from
  the background floor and day-to-day activity jitter.

hh_003 (rotating shift) is the weakest fit, as expected — its schedule
varies across weeks, which a two-day-type table cannot capture. One
line, not investigated further.

## Waiting on the owner

Per the brief this STOPS here: no policies are built on the forecaster
until these figures are confirmed.
