# casas/ — real ADL grounding (CASAS free-living data)

Grounds our object-routine machinery in **real** activities of daily living,
to compare against the invented schedules in `profiles/revamp_v1/`. One home
so far: **aruba**, the classic CASAS single-resident testbed (an older adult
living alone, 2010–2011).

## Data source and what we keep

Zenodo record **17180309** — "CASAS Smart Home dataset (aruba, cairo, milan,
tulum) — free living, motion, door, temperature, activity labels"
(33 MB zip, one raw file per home; the CASAS community also hosts multi-GB
smartwatch IMU sets — record 20349208 is one of those, not this).

Raw CASAS format is one ambient-sensor event per line, with activity
annotations riding on some lines:

    2010-11-04 00:03:50.209589 M003 ON Sleeping begin
    2010-11-04 00:03:57.399391 M003 OFF
    2010-11-04 00:15:08.984841 T002 21.5

Per the standing space rule, we keep **only the labeled activities and their
timestamps** — every motion/door/temperature reading is discarded, and the
raw files are not stored in the repo (they live in session scratch during
extraction). What is stored: `aruba/activities.csv` (475 KB — 6,477
intervals over 220 days, 11 activities, zero begin/end pairing anomalies)
and `aruba/summary.json`.

## Pipeline

    extract_activities.py  raw CASAS txt -> activities.csv + summary.json
    aruba_profile.yaml     extrapolated resident + object inventory
                           (CASAS gives activities, not objects — the
                           inventory/rooms layer is our invention, flagged
                           per-line as (from data) vs (extrapolated))
    aruba_binding.yaml     activity -> during/after object rules; same
                           mechanics as revamp_v1 specs, plus p/only_from
                           on `during` (real activities repeat ~28x/day;
                           not every bout touches every object)
    simulate_from_casas.py replays the REAL intervals through the binding;
                           emits the standard timeline format
                           (events.jsonl / hourly.csv / meta.json), real
                           calendar day names (aruba day 0 = Thu 2010-11-04)

    python extract_activities.py <raw>/aruba.txt --out aruba
    python simulate_from_casas.py aruba_binding.yaml --days 14 --seed 0 \
        --out aruba/timeline_14d

Spatialized into the SAME HSSD suite as hh_001
(`visualization/configs/casas_aruba_102343992.yaml`, identical anchors) so
both traces render in the same viewer on the same floor plan:
`/visualization/viewer/index.html?trace=/casas/aruba/timeline_14d/trace.json`

## What the real grounding changes (aruba vs hh_001, 14 days, same house)

| | hh_001 (invented) | casas_aruba (real ADLs) |
|---|---|---|
| activity intervals/day | ~11 blocks | 28 median (p10 22, p90 37) |
| day-to-day timing spread | jitter ±5–15 min | σ = 75–117 min on daily anchors |
| object moves /object/day | 1.25 | ~3.1 |
| busiest object | phone 2.9 moves/d | remote 7.3 moves/d |
| within-room shuffles | 20% of moves | 38% of moves |
| tidy-up sweeps | invented weekly reset | real Housekeeping bouts, ~2-day gaps, bursty |
| dish cycle | invented per-day rules | real Wash_Dishes every ~2 days; pile peaks 5/5 out |
| away time | 444 obj-hours (work shifts) | 144 obj-hours (~2 brief outings/day) |

**Fragmentation caveat (2026-08-09):** the raw bout counts overstate
behavioral fragmentation. 41% of within-day gaps between consecutive
same-activity bouts are under 10 minutes — the annotator closes an interval
whenever the resident briefly steps away, so one "making breakfast" becomes
2–3 labeled bouts. Merging bouts <30 min apart into sessions: 28 raw
intervals/day → **16 sessions/day**; Meal_Preparation 7.3 → **4.1 kitchen
sessions/day** (a normal breakfast/lunch/dinner + snack pattern, tri-modal
by hour); Relax 13.3 → 3.9. Calibrate any bout-count model on merged
sessions and treat sub-session splitting as observation noise, not
behavior.

Reading: real routines are far more fragmented and far less punctual than
our authored specs — many short bouts with hour-scale day-to-day drift,
producing ~2.5× the object churn, more within-room shuffling, and
irregular-but-recurrent tidy/wash cycles that our clean weekly reset only
approximates. The revamp_v1 authoring lessons that transfer directly:
`only_from` gating matters even more here (repeated bouts would otherwise
re-trigger constantly), and the reachability lint caught a frozen-object bug
in this binding too (notebook_1, then mug_2/plate_2 gated behind
never-reached `only_from` states — the lint cannot see through gates, so
check `meta.json` move counts after simulating).

Caveats: the object layer is still invented — only the activity stream is
real. The default 14-day window (days 0–13) happens to catch a Housekeeping
burst — 10 of the 28 housekeeping days in the whole 220-day dataset — so
`reset:Housekeeping` moves are over-represented vs. the long-run rate;
The short-bout flaw noted here previously is fixed: tidying is now a
sequential nearest-first walk (2–5 min per item) limited by the real
bout's duration, so a 3-minute Housekeeping bout touches ~1 item and only
long bouts sweep the house (14-day window: 26 tidy moves across 14 bouts,
6 bouts cut short by their own real length — vs 49 instantaneous moves
before). Run with `--anchors ../visualization/configs/casas_aruba_102343992.yaml`
for geometric nearest-first ordering. Aruba's actual floor plan is not modeled; anchors reuse hh_001's suite
so motion patterns compare on identical geometry. Interval overlaps in the
annotations are kept as-is.

## Where the sporadicity comes from (decomposition, 2026-08-09)

Question: object motions from real data look far less periodic than
hh_001's — is that the real stream, our binding layer, or this resident?
Experiments: (1) activity-level day-pair similarity across all four homes;
(2) a deterministic-rules variant of the binding (all p→1, dist→argmax, no
misplace) replayed on the same real intervals; (3) seed0-vs-seed1 runs on
identical streams.

Event-timing sporadicity (hour-of-day entropy of move times / Fano factor
of daily move counts — what the slider makes visible):

    hh_001 invented + stochastic rules   0.36 / 0.42   (metronomic)
    aruba  real     + stochastic rules   0.74 / 1.92
    aruba  real     + DETERMINISTIC      0.76 / 2.03   (just as sporadic)

Verdict: **the real activity stream is the cause, not the binding's coin
flips** — deterministic rules on real intervals reproduce the full timing
scatter. The binding's stochasticity only decides *which* bout moves an
object (its per-bout p's set move *volume*, tuned by feel and worth
calibrating) and adds mild seed-to-seed divergence (0.71 hourly agreement
vs hh_001's 0.77). Nor is the resident unusual: activity-level day-pair
similarity is 0.39–0.75 across all four homes (aruba mid-pack at 0.57) vs
~0.95 for our specs by construction, and same-weekday pairs beat other
pairs by ≤0.02 everywhere — real weekly structure is nearly absent in
these (mostly retired) homes. Occupancy-wise the traces are comparable
(0.59 real vs 0.55 invented, statics excluded); the perceived difference
is almost entirely event-timing scatter.

Implication for revamp_v1 stage 2, if realism at this level matters:
periodicity is baked into our generator by construction. The real stream
suggests (a) hour-scale start jitter (σ 60–120 min) for non-anchored
activities, (b) fragmenting activities into a variable number of short
bouts per day (~Poisson), (c) per-day skip probabilities, (d) at most weak
weekday/weekend distinction. These are exactly the parameters
`aruba/activities.csv` (and milan/tulum2/cairo, now also extracted) can
calibrate.

## Jitter calibration (feeds revamp_v1's tiered jitter model)

Day-to-day σ of daily anchor start times (first occurrence in a window;
sleep = evening onset with midnight wrap):

| home | activity | n days | median | σ (min) |
|---|---|---|---|---|
| cairo | Dinner | 42 | 17.8h | **19** |
| cairo | Lunch | 37 | 11.9h | 27 |
| cairo | R2_Sleep / R1_Sleep | 52/50 | ~20.7h | 32 / 38 |
| milan | Sleep | 60 | 22.2h | 48 |
| cairo | R2_Take_Medicine | 44 | 7.3h | 48 |
| cairo | Breakfast | 48 | 7.5h | 51 |
| milan | Morning_Meds | 41 | 8.9h | 55 |
| tulum2 | R1_Sleeping_in_Bed | 129 | 0.1h | 62 |
| aruba | Sleeping | 218 | 23.9h | 67 |
| milan | Eve_Meds | 19 | 20.5h | 76 |
| aruba / tulum2 | first Meal_Preparation | 214/92 | 7–10h | 78 / 78 |
| tulum2 | Work_Table | 50 | 12.3h | 79 |
| cairo | R1_Work (at home) | 18 | 7.6h | 111 |

Two lessons: nothing in these homes is tighter than ~19 min day-to-day —
and the tightest anchor measured is a *dinner* (cairo's punctual couple),
so tier membership is a per-household authoring choice; only the tier
VALUES are calibrated. No employed-outside-the-home resident exists in
these datasets, so the `external` tier (σ 10) remains a domain prior.
These numbers set the defaults in
`profiles/revamp_v1/simulate_schedule.py`:
`{external: 10, routine: 30, flexible: 75, loose: 110}`.
