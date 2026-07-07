# Generation diversity and dwell-time instrumentation

**VERDICT: real, substantial variation exists — categories are not
degenerate or flat — but the mean-dwell distribution is closer to a
continuum than to two cleanly separated clusters, so the volatile/stable
median-split is real signal cut at a somewhat arbitrary point, not a
fabricated distinction.** Pure counting over all 211 currently-validated
generation folders — no rendering, no model calls, reuses
`embodied.belief.dwell_events` unchanged.

## The load-bearing check: do categories separate on dwell time?

21 location categories, mean dwell time ranges from **0.85h (cup) to
15.24h (chair)** — an 18x spread, computed from 1,152 to as few as 1
dwell samples per category (see full table,
`generation_diversity_dwell.csv`). This is not a flat or degenerate
distribution: cups, drinkware, and screens (tv/oven power state) dwell
under 1.2h on average; keys, wallets, bottles, vases, and chairs dwell
4-15h. The ordering itself is intuitively sensible — frequently-handled
kitchen items and mobile electronics cluster at the volatile end,
furniture-adjacent and rarely-touched items at the stable end — which is
a real (if informal) plausibility check the numbers pass.

**But the spread is closer to continuous than bimodal.** Sorted mean
dwell times step up mostly smoothly (0.85, 1.08, 1.14, 1.18, ... 4.41,
4.44) with only two visible larger jumps — wallet(4.44h)->bottle(5.87h)
and bottle(5.87h)->vase(10.15h) — not a clean gap separating two
natural groups. `embodied.policy.classify_hazard`'s median-split
("volatile" if fitted lambda >= median, else "stable") is therefore
cutting through a real but largely continuous distribution at its
midpoint, not separating two pre-existing clusters. This is a nuanced
finding, not a pass/fail: **the underlying variation is real** (ruling
out "the strata are fake" in the strong sense of "there's no real signal
here"), but **the binary stable/volatile framing is a modeling choice
imposed on a continuum**, not a natural kind the data itself suggests.
Worth stating precisely for any report that treats "volatile" and
"stable" as qualitatively different regimes rather than two ends of one
spectrum.

**A second, independent observation worth flagging:** several categories
show mean dwell far above median dwell (`bottle`: mean 5.87h vs. median
0.69h; `fridge::door`: mean 2.01h vs. median 0.37h; `bowl`: mean 3.97h
vs. median 0.55h) — heavily right-skewed distributions, a few very long
dwell events pulling the mean well above where most individual events
actually sit. Kernel fitting (`embodied/posterior.py`'s
`fit_transition_kernels`) derives `lambda_per_hour` from mean dwell, not
median — for these skewed categories, that mean-based rate may
understate how often a "typical" (median) dwell interval actually ends,
relative to what a median-based rate would imply. Not acted on here —
flagged as a real property of the data a future kernel-fitting
refinement should be aware of.

## Move counts and anchor diversity

Move counts range from 1,537 (`bowl`) down to single digits for
categories that only appear in a few scenes (`wardrobe`, `fridge` as
bare location-moving categories — most of their events are in the
`::power`/`::door` state-change stream instead, counted separately).
Distinct-anchor counts (`generation_diversity_categories.csv`) run
30-48 for the high-volume clutter categories — real spatial variety, not
every object collapsing onto one favorite slot. Anchor-level object
counts (`generation_diversity_anchors.csv`) show the expected pattern:
room-level anchors (`kitchen`, `bedroom`, `living_room`, 27-29 distinct
objects each) and major furniture (`dining.table`, `bedroom.bed`,
`kitchen.fridge`, 27-28 each) are the most shared destinations, which is
physically sensible — these are exactly the places a household's mobile
objects would concentrate.

## Per-profile differences

Household profile visibly changes category behavior — not a
rounding-error effect. `candle`'s mean dwell time alone ranges from
**1.12h (single_parent_young_kids) to 4.34h (single_retiree)**, a 4x
spread across profiles for the identical category
(`generation_diversity_by_profile.csv` has the full breakdown for every
category x profile pair with at least one dwell sample). This is the
right direction and the right rough magnitude for face validity — a
retiree living alone plausibly interacts with a candle far less often
than a household actively raising young children — though this report
does not claim more than "profiles produce visibly different behavior
for the same category," not a validated claim that the SPECIFIC
magnitudes are realistic (that question is exactly what the render tool
and eventual human-correlation study are for).

## What this does and does not establish

**Establishes:** categories separate on dwell time by a real, large
margin (18x range); household profile measurably changes a category's
own dwell behavior; anchor/object diversity is broad, not collapsed onto
a handful of favorites. None of these are consistent with a degenerate
or template-collapsed generator.

**Does not establish:** whether the SPECIFIC dwell times, or the
specific volatile/stable cutoff, are behaviorally realistic in an
absolute sense (a candle dwelling 2 hours vs. 20 minutes vs. 8 hours —
which is "right" for a real household — is not something a self-
consistency check like this one can answer). That is exactly the
render-tool + human-correlation gap `realism_score_trace.md` already
names.

**Traceability:** `scripts/generation_diversity_report.py`, pure Python,
no habitat_sim, no model calls. Reads all 211 currently-validated
folders under `generation_out/` (validated via
`scripts/scene_validation.py`'s existing `validate_folder`). Raw CSVs:
`generation_diversity_categories.csv`, `generation_diversity_anchors.csv`,
`generation_diversity_dwell.csv`, `generation_diversity_by_profile.csv`.
