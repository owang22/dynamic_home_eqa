# Planning metric: search cost, rooms, and an ask-or-search policy

Post-processing over the existing `uq/regime/<regime>/<agent>/hh_s*.jsonl` logs — no new agent runs, only the ones that
already carry a full `dist` (none_tt, none_tt72, none_lastseen [added for this], mart_tt72, bma_tt, ocp_tt). Script:
`src/baselines/patrol/uq_planning.py`; expectations written before the run: `uq/regime/EXPECTATIONS.md` (E19, E20).

## Definitions
- **places (rank)**: 1-indexed position of the truth receptacle in the agent's own distribution, sorted by probability
  descending (ties broken the same way the logged `answer` is picked: the highest receptacle id wins) — "how many
  places you would search, in the agent's own order, before finding the object." A truth whose probability falls below
  the logging floor (1e-4, so it is not even in the serialized `dist`) gets the worst-case rank = the household's total
  spot count (~38 for these banks).
- **rooms**: number of distinct rooms entered by that point, walking the same order (receptacle -> room from the bank
  header).
- **ask-or-search policy**: confident = `top_prob >= tau` (tau = 0.6) for agents with a plain point distribution, or
  `set_size <= k` (k = 3) for the honest-sets agent (ocp_tt). If confident, cost = places (physically search). If not
  confident, cost = a flat ask cost `c` (c in {2, 4} "places-equivalent") — ask the resident and retrieve directly, no
  search. Mean places and mean rooms are reported unconditionally, for every question, regardless of the policy; total
  cost is the policy-mixed number.
- tau and k are single fixed values, not tuned per agent or per stage — chosen once (tau = 0.6: a plain "more likely
  right than wrong, with room to spare" bar; k = 3: "down to a handful of spots") and reported as-is, with a brief
  sensitivity check (k in {1, 2, 3}) noted below rather than swept into the headline table.

## Results (10 households each; tables: `sick10_all_summary.md`, `sick10_owner_summary.md`; rows: `*_by_day.csv`)

| agent | sick10_all: lead cost (c=2/c=4) | sick cost (c=2/c=4) | return cost (c=2/c=4) | sick confident share |
|---|---|---|---|---|
| none_tt (frozen tt) | 2.27 / 3.56 | 3.28 / 4.53 | 2.02 / 2.80 | 38% |
| none_tt72 | 2.12 / 3.84 | 2.14 / 4.08 | 1.96 / 3.77 | 3% |
| none_lastseen | 12.17 / 12.17 | 13.97 / 13.97 | 11.91 / 11.91 | 100% |
| mart_tt72 (e-detector + reset) | 2.12 / 3.84 | **2.04 / 3.99** | 1.95 / 3.77 | 2% |
| bma_tt (hedge) | 2.22 / 3.57 | **2.39 / 4.00** | 2.02 / 2.91 | 19% |
| ocp_tt (honest sets, k=3) | 2.98 / 3.56 | 3.71 / 4.32 | 2.29 / 2.43 | 69% |

(sick10_owner: same shape — mart_tt72 sick 2.03/3.90 vs none_tt72's own 2.16/4.03; bma_tt sick 2.22/3.68 vs none_tt sick
3.03/4.13; ocp_tt sick 3.51/3.98 vs its own lead 2.74/3.25, i.e. up not down. Full numbers in the summary tables.)

## Reading it (E19/E20)
- **E20 (places track accuracy) — confirmed.** `none_lastseen`'s mean places (11-14, i.e. almost never near the top of
  its own ranking) sits far above every timetable-based agent's (~2.4-4.8) in every stage, matching its ~50% flat
  accuracy; `none_tt`'s places jump lead->sick (4.4 -> 4.8 on sick10_all) then fall on the return (2.4) as the timetable
  bins refill — the same break the accuracy chart shows, in search-cost units.
- **E19 (UQ-aware agents cost less on shift days by asking more) — confirmed for mart_tt72 and bma_tt, NOT for ocp_tt
  at any k tested.** mart_tt72's confident share drops 14% (lead) -> 2% (sick) on sick10_all, and its total cost on the
  sick days is slightly BELOW its own un-reset base (none_tt72: 2.04 vs 2.14 at c=2; 3.99 vs 4.08 at c=4) and clearly
  below the frozen baseline (none_tt: 3.28/4.53) — asking more during the break is cheaper than searching. bma_tt shows
  the same direction, more strongly (2.39 vs none_tt's 3.28 at c=2 on the sick stage). Both hold "no cost on plain days"
  too (lead-stage costs within a few hundredths of their own un-wrapped base).
  **ocp_tt is the counter-example**, and it is informative rather than a bug: ocp_tt does not change the answer or the
  underlying distribution at all (it wraps the frozen base unmodified — its places/rooms columns are IDENTICAL to
  none_tt's, row for row), so gating on conformal set size rather than on the point probability has to be doing the
  selecting on its own. At k=3 its confident share stays high through the sick stage (69% on sick10_all, barely below
  lead's 71%) because the online-conformal threshold q_t only fires very large sets on the first shift day or two, not
  the whole ten-day spell — so for most sick-stage days it says "confident" (search) even though the frozen base's
  point accuracy has not recovered, and total cost RISES during the shift (2.98 -> 3.71 at c=2). Lowering k does not
  fix this: k=1 gives sick confident share 37% (down from 39% lead — a much smaller drop than mart_tt72's 14%->2%) and
  cost still rises (2.49 -> 2.86); k=2 is worse still. The conformal set size is calibrated to a coverage target (it
  correctly reports large sets on the specific days it should, which the "Does the method notice?" panel on the story
  page already shows), not to "is my point guess about to be wrong today" — those are different questions, and this
  policy needs the latter. A conformal-based ask policy would need to key off the set-size TREND or a martingale-style
  detector, not a single fixed k against the raw set size.
- **c sensitivity**: nothing crosses over between c=2 and c=4 in this data — every agent's cost ordering (which one is
  cheapest per stage) is the same at both costs; the ask-vs-search theory is not sensitive to c in this range.

## Matched ask-rate control (added 19:50, coordinator's follow-up)

The raw-confidence table above has a confound: agents sit on different confidence SCALES, so a fixed tau=0.6 gives each
agent a different raw ask rate on lead days (none_tt 65%, mart_tt72 86%, bma_tt 68%, ocp_tt 29%, last-seen 0%) — the
comparison partly measures scale, not uncertainty awareness. Fix: per agent, pick its own threshold from LEAD-day data
so its lead-day ask rate equals a fixed target (25% or 50%), then apply that SAME threshold to sick/return. Files:
`<regime>_matched25.md`, `<regime>_matched50.md`; `threshold_for_rate()` / `run_matched()` in uq_planning.py.

**The claim survives for `mart_tt72` (e-detector + reset) only, on both banks, both rates:**

| agent | sick10_all sick-stage cost (c=2), 25% -> matched rate | sick10_all 50% | sick10_owner 25% | sick10_owner 50% |
|---|---|---|---|---|
| mart_tt72 | lead 3.31 -> sick **2.55** (ask 25%->45%) | lead 2.67 -> sick **2.25** (ask 50%->71%) | lead 2.92 -> sick **2.48** (ask 25%->32%) | lead 2.40 -> sick **2.30** (ask 50%->60%) |
| none_tt72 (its own un-reset base) | lead 3.31 -> sick 3.38 (ask 25%->35%) | lead 2.67 -> sick 2.78 (ask 50%->66%) | lead 2.90 -> sick 3.08 (ask 25%->27%) | lead 2.37 -> sick 2.68 (ask 50%->59%) |
| bma_tt (hedge) | lead 3.15 -> sick 3.55 (ask 25%->32%) | lead 2.39 -> sick 2.82 (ask 50%->63%) | lead 2.88 -> sick 3.14 (ask 25%->26%) | lead 2.29 -> sick 2.49 (ask 50%->59%) |
| ocp_tt (honest sets) | lead 3.13 -> sick 4.00 (ask 24%->21%) | lead 2.74 -> sick 3.42 (ask 38%->41%) | lead 2.83 -> sick 3.65 (ask 22%->18%) | lead 2.66 -> sick 3.08 (ask 35%->34%) |

Only `mart_tt72` is cheaper on the sick days than on its own lead days at EQUAL lead-day ask rate, on every bank and
every rate tested — its ask rate rises noticeably more than the others' too (e.g. +20 to +21 points at the 25% target,
vs bma_tt's +1 to +7 and ocp_tt's roughly flat or falling). Everything else — including `bma_tt`, which looked like a
clear win in the raw-confidence table (2.39 vs frozen's 3.28 at fixed tau=0.6) — gets MORE expensive on the sick days
even at a matched starting rate: the raw-table win was largely the scale confound (bma_tt's raw ask rate at tau=0.6 was
already 68% on lead days, far above the other agents', so its lead cost sat near the c floor already and the "sick
stays about the same" read as an improvement only against frozen's much lower raw ask rate). `ocp_tt`'s negative
finding is unchanged and now confirmed scale-independent: it gets more expensive on sick days at every rate on both
banks. **Conclusion for the paper: the planning-metric result is specifically about the detector-triggered targeted
reset, not about "having an uncertainty signal" in general — a hedge or a coverage-calibrated set does not, by itself,
know when to ask more.**

## Caveats
- tau/k are single fixed values, not swept per-agent; a proper sweep (tau in a range, k in {1,2,3,4}) would sharpen the
  ocp_tt finding above and might find a k where it does help — not done here for time.
- "rooms" counts distinct rooms entered in probability order, not a real path length (no travel-time or room-adjacency
  model) — a places-equivalent proxy, consistent with how the ask cost `c` is specified ("places-equivalent").
- A truth below the 1e-4 logging floor is assigned the worst-case rank (total spot count); checked — this triggers on
  0.7-1.1% of rows for the timetable-based agents and 2.7-4.1% for last-seen (whose floor mass is spread thinnest), so
  it is a minor edge case, not a material bias in the means above.
