# atus/ — reading an IPUMS ATUS time-use extract

Tools for pulling one respondent's 24-hour diary (ACTIVITY, START, STOP,
WHERE) out of an IPUMS ATUS hierarchical extract and rendering it.

The microdata itself is **not** in the repo (IPUMS terms of use; see
`.gitignore`). Drop your extract at `atus/atus_00001.dat.gz` and both tools
work; a re-download reproduces everything.

    python atus/read_extract.py --list                    # candidate diaries
    python atus/read_extract.py --caseid <CASEID>         # the table
    python atus/read_extract.py --caseid <CASEID> --csv out.csv
    python atus/plot_diary.py  --caseid <CASEID> --out out.png

## No codebook: how the layout was established

The extract arrived without its DDI (`.xml`/`.cbk`), so column offsets were
inferred from the data and then validated against ATUS's structural
guarantees — **all 6,146 respondent-days pass**:

| check | result |
|---|---|
| every diary's first activity starts at 04:00 | 6146 / 6146 |
| activities tile the day contiguously (stop == next start) | 6146 / 6146 |
| durations sum to 1440 min (final record clipped at the 04:00 boundary) | 6146 / 6146 |
| every activity code's major category is in the ATUS lexicon | 6146 / 6146 |

One ATUS convention matters for the arithmetic: the **last** record of a
diary keeps the respondent's real reported stop time, which usually runs
past the 04:00 cutoff (5,353 of 6,146 diaries here — e.g. "21:00 → 07:00"
sleeping). Clip it to the window and the day tiles exactly 1440 minutes.

`WHERE` labels were assigned from the raw TEWHERE ordering and then checked
against what each code actually hosts in this extract (990 grocery-shopping
records at 106, 51 banking at 111, 116 workouts at 112, sleeping at 9999).
Three low-volume codes — 113, 115, 9998 — are marked `(inferred)` and are
the ones a codebook should settle.

## Home-collapsed view (`--home-only`)

`home_blocks()` reduces a diary to what the object-tracking task cares
about: full activity detail INSIDE the home, and everything else merged
into single "out of house" spans however fragmented the diary was out
there — the same way the simulated households model absence as one
ELSEWHERE. Rules:

* location is the respondent's home or yard → **home**;
* location was not asked AND the activity is personal care (asleep,
  washing, dressing) → **home** (ATUS never asks WHERE for these);
* a not-asked record that is *not* personal care is a diary gap or data
  code — the location **carries forward** from the previous block and the
  row is flagged `*` / `location_imputed`, so the imputation is visible;
* everything else → **out of house**, with consecutive spans merged.

The commuter example goes from 25 records to 11 blocks: home until 06:53,
out for 10.8 h, home for the evening with one 44-minute errand, asleep
from 21:00.

## Two extracts, one reader

Column offsets are keyed to the **activity-record width**, so both extracts
parse without a flag:

| extract | respondents | activity records | years | diary date? |
|---|---|---|---|---|
| `atus_00001.dat.gz` (55-char activity) | 6,146 | 114,151 | 2025 | no |
| `atus_00002.dat.gz` (82-char activity) | 198,090 | 3,778,113 | 2006–2025 | **yes** |

`DEFAULT_EXTRACT` is the larger one. Validation on it: all 198,090 diaries
start at 04:00, tile contiguously, and use in-lexicon codes; 16 diaries
(0.008%) do not sum to 1440 minutes. The richer layout also carries its own
duration field, which matches `stop - start` on **199,999 of 200,000**
sampled records — an independent confirmation of the inferred offsets.

The larger extract adds RECTYPE 5 (35,303 records, first seen in year 2011)
— the eldercare module, not used here.

## Activity labels: three-tier fallback

ATUS codes are hierarchical (2-digit major → 4-digit subcategory → 6-digit
detail) and this extract uses **461 distinct detail codes**. Labels resolve
6 → 4 → 2, so every record reads as something meaningful:

* **83.2%** of records have an exact 6-digit label;
* **16.8%** fall back to their 4-digit subcategory (e.g. code 180704 shows
  as "Travel: consumer purchases");
* **0%** are unlabeled.

The subcategory tier is the published lexicon's second level and is stated
with confidence. The exact 6-digit meanings of the high-volume codes in the
fallback group are the one thing worth confirming against the ATUS coding
lexicon — the biggest are 180704 (81k records), 180302 (52k), 180703 (38k),
020602 (37k), 030112 (27k).

## Day-of-week: present in the second extract only

The person record of `atus_00002` carries the diary date as `YYYYMMDD` at
offset 40. That was confirmed, not assumed: reading it as a date yields
Sat 24.2% / Sun 25.8% / weekdays ~10% each — ATUS's deliberate weekend
oversampling. (The first extract has no such field: no person-record
column showed that signature, CASEID encodes year and month but not a
day-of-month, and the survey weights are continuous with no bimodal split
to exploit.)

One structural limit remains whatever the extract: ATUS interviews each
respondent for a **single** day, so a weekday *and* a weekend diary for
the same household does not exist. Day-type comparisons are always across
respondents — which is why `plot_occupancy.py` exists.

## Two views

* `plot_diary.py` — individual days as timelines. Answers "what did this
  day look like". With one diary per cell it cannot show a weekday/weekend
  *effect*: individual variation swamps it.
* `plot_occupancy.py` — the population curve: share of respondents at home
  by clock time, weekday against weekend, split by household type read
  from diary content. This is where the day-of-week effect is visible
  (families with children: 43% home at midday on a weekday vs 55% on a
  weekend, and the weekday exodus is ~90 minutes earlier).

## Relationship to the rest of the repo

This is the real-data counterpart to `casas/` (CASAS gives labeled
activities with no location; ATUS gives activity **and** location, but a
single day per respondent and no object information). Neither carries
objects, so an ATUS diary cannot drive the object-trace viewer — the
timeline figure from `plot_diary.py` is its visualization.
