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

## Relationship to the rest of the repo

This is the real-data counterpart to `casas/` (CASAS gives labeled
activities with no location; ATUS gives activity **and** location, but a
single day per respondent and no object information). Neither carries
objects, so an ATUS diary cannot drive the object-trace viewer — the
timeline figure from `plot_diary.py` is its visualization.
