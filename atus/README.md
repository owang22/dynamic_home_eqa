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

## No day-of-week in this extract

`plot_diary.py` cannot split weekday from weekend: **the extract has no
diary-day variable.** Checked three ways — no column in the person record
carries the 1-7 field with ATUS's characteristic weekend oversampling
(Sat and Sun each ~25% of diary days); CASEID encodes year and month but
not a day-of-month (its chars 7-8 only ever run 01-12, and reading them
as a date yields a weekday distribution nothing like the design); and the
survey weights are continuous, with no bimodal split to exploit.

To get it, add **DAY** (TUDIARYDAY) to the IPUMS extract and re-download —
then the day-of-week is one field away and the weekday/weekend panels
become trivial. Note that even then, ATUS interviews each respondent for a
SINGLE day, so a weekday *and* weekend diary for the same household does
not exist in ATUS at all; comparisons across day types are always across
respondents.

## Relationship to the rest of the repo

This is the real-data counterpart to `casas/` (CASAS gives labeled
activities with no location; ATUS gives activity **and** location, but a
single day per respondent and no object information). Neither carries
objects, so an ATUS diary cannot drive the object-trace viewer — the
timeline figure from `plot_diary.py` is its visualization.
