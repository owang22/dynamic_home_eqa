# Writing this paper — read before you write a sentence

You are writing an uncertainty paper, not a robot-memory paper. Everything below follows from that.

## The claim

**Accuracy and uncertainty are separate axes, and a change in the household's routine moves one and not the
other.**

That accuracy does not imply calibration is not news to this audience. Two things here are:

1. **An embodied instance.** Not a benchmark shift — a home where one resident is off sick for ten days and
   then comes back, and a robot that has to answer "where is my mug?" through it.
2. **It is worst exactly at the shift.** The failure is not a general property of these methods. It is
   localised to the days the routine changes, and it recovers afterwards. That is the contribution.

And there is a positive result with a mechanism behind it, which is the part a model designer can act on:

3. **Whether a method's uncertainty survives a shift follows from what its confidence is a function of.**
   Frequency-based confidence cannot see a regime change. Age-of-evidence confidence must.

## What you must not write

- **Do not lead on accuracy.** "Every method breaks on the first sick day" is the setup, not the finding.
- **Do not turn this into a league table.** The survival-time model is the *least accurate* classical method
  while the household is stable. If a reader finishes thinking "use Perpetua", you have written the wrong
  paper. The claim is about a design property, not a product.
- **Do not describe the timetable results as a discovery.** A stale-window frequency estimator failing at a
  distribution shift is standard. Present it as the yardstick it is. Being coy about that will cost you a
  reviewer.
- **Do not say "swept per day"** about any of the decision figures, or any other phrase implying a threshold
  was refitted on held-out data. None was. See "Exact wording" below.
- **Do not quote a number without saying which household set and which window it came from.**

## Figure order

| Order | Figure | Why it is here |
|---|---|---|
| 1 | **F8** decision score per day | Opens the paper. The ranking inverts under a score a user feels; the survival-time model sits *below* both timetables while stable and wins at the shift. A separate axis can only be shown by a method that loses on one and wins on the other. |
| 2 | **F5** confidence against accuracy | The claim in its simplest form: accuracy collapses, stated confidence does not move. |
| 3 | **F11** whose confidence survives | The positive result. Four methods' confidence-vs-correctness across the month; the timetables hit zero at the shift, the survival-time model does not. **The mechanism section attaches here.** |
| 4 | **F10** the same test one day at a time | The localisation. Works in every window except the shift, and again a week later. |
| 5 | **F6** the inversion | What miscalibration costs: at the shift the rule answers what it gets wrong and defers what it would have got right. |
| 6 | **F7** sets break rather than widen | The uncertainty apparatus keeps its shape while its promise fails. Best thesis-fit in the set — and only three households. Flag that in the caption. |
| setup | **F1** learn, break, relearn | One panel establishing that there is a disruption and how big. Not a section. |
| support | **F4**, **F9** | F4 rules out "it could just decline more". F9 is the rigour behind F10. |
| out | **F2**, **F3** | Accuracy results. See below. |

Every figure folder now contains a `claims.md` whose first section is **"Its job in the argument"**. If what
you are writing about a figure disagrees with that section, one of the two is wrong — resolve it before
writing, do not paper over it.

## F3 is the hard call

F3 (what one sentence buys) contains the largest effect in the project: an instruction that nobody retracted
leaves the same-hour-lookup memory **18 points worse than saying nothing** on the return days, still 13 down a
week later — larger than the 12 points the instruction bought at the shift.

It is an **accuracy** result. It belongs in this paper only if someone measures the confidence half: does an
arm carrying an instruction that has silently lapsed stay confident while getting worse? **That check has not
been run.** If it comes back positive, F3 becomes the third instance of the thesis — an instruction is evidence
with no expiry attached, so a model with no representation of staleness cannot discount it — and it should move
into the main sequence after F11. If nobody runs the check, leave F3 out and write it up elsewhere.

## The mechanism paragraph

This is the part most likely to be written vaguely. It is not vague; it is arithmetic. Both confidence numbers
are the probability the method puts on its own answer, so they are directly comparable.

**Timetable.** The reported number is the Dirichlet posterior mean of the sighting histogram for the bin
matching the query's hour and day-kind:

    p(r) = (count_r + α) / (Σ_r count_r + α·L)

`L` is the number of locations, `α` a smoothing constant; counts are raw (never-forgets) or weighted
`2^(−age/72h)` (three-day). **This is a ratio of counts.** Scale every count by the same factor and it does not
move. Its only sensitivity to evidence age comes through the fixed `α` in the denominator, which pulls toward
uniform once counts get small — and that is weak. Source: `src/baselines/beliefs/timetable.py`,
`src/baselines/beliefs/base.py` (`dirichlet_mean`, `_weighted_counts`).

**Perpetua\*.** Per (object, location) edge, a two-state Markov chain with fitted leave rate `μ` and arrive
rate `η`, advanced in closed form from the last sighting:

    p_r(t) = p_eq,r + (p_r(t_anchor) − p_eq,r) · exp(−(μ_r + η_r)·F(t_anchor, t))

with `p_eq = η/(μ+η)` the long-run occupancy and `F` elapsed time under a switching prior. Then normalised
across locations, remainder to "elsewhere". **This is explicitly a function of how long ago the object was
seen**, relaxing from certainty toward the base rate at a speed fitted per object — so it is least confident
about exactly the objects that historically move most. Source:
`src/dynbelief/beliefs/perpetua.py`.

**The argument in one sentence:** a change in routine makes old evidence wrong *without changing historical
frequencies*, so it is invisible to the first number by construction and visible to the second by
construction. The measured correlations (0.35 → −0.12 for the never-forgets timetable; 0.37 → 0.43 for the
survival-time model) are what that algebra predicts.

**Two honest limits on this paragraph.** (a) Our Perpetua is implemented "from the brief's operational
definition" of arXiv 2605.00121 — neither the paper nor that brief is in this repository, and steps like the
class-pooled rate smoothing and the occupancy pinning look like our engineering rather than theirs. Say
"our implementation of" and cite the file. (b) The prediction that the advantage decays once the disruption
outlasts `1/(μ+η)` is only partly borne out: largest right after each change (2.25 at the first sick days,
1.05 on the first days back), smallest mid-spell (0.59), but 1.55 a week after the return, which does not fit.
Do not present it as confirmed.

## Exact wording that matters

**Hindsight.** Three figures use three different amounts, and each must be described with words that match:

- **F8** — one threshold per method for the *whole run*, then scored per day. Tightest.
- **F9** — one threshold per method per *window*, and one per household.
- **F10** — one threshold per method per *day*.

None is refitted on held-out data. Every one is chosen knowing the outcomes it is then scored on, which is what
makes all three upper bounds rather than policies. The full paragraph is in every one of those folders'
`caption.md` under "How much hindsight this figure uses" — copy it, do not paraphrase it.

**The claim bar.** An effect is claimed when its average is at least twice its own standard error across
households. Below six households the old spread bar governs instead. Both are printed wherever they disagree.

**Household counts.** F1–F6 and F8–F11 are ten. **F7 is three.** F9 is ten except the first-days-back window,
which is eight — a household needs twenty answered questions inside a window to enter it, and that window is
three days long. Say so wherever you quote a first-days-back number from F9.

**The rerun floor.** Running the same arm again over the same data does not give the same answers: identical
prompts at temperature zero are not reproducible on this server, and the arms match before their message
because those prompts are cache hits. About 3% of answers change for the recent-sightings list, about 5% for
the whole-log memory, none at all for the counting methods (one household's classical arm was re-run and came
back byte-identical, as did its question bank). **Across all days accuracy moves 0 to 2 points; inside one
window of one household it has moved 10.** Every result here is stated per window, so it is the per-window
figure that governs. Never apply one arm's floor to another arm. Full paragraph in every folder's
`caption.md`; the single source is `results/regime_search/tools/rerun_floor.py`.

## Things to check before submission

- [ ] **Run the F3 confidence check** and decide F3's fate on the result, not on how good the number is.
- [ ] **Pull the reasoning traces.** Every LLM run logs a `reasoning` field per question. They show the model
      inferring object dependencies from the routine — e.g. *"Yuki is at home working from 9:00 to 17:30, and
      her work items (mug, water bottle) were last seen at her desk before being moved to the kitchen at
      03:00…"*. That is the evidence for any claim that the LLM derives structure from the instruction, and it
      is currently unused. An appendix table of four or five traces, chosen before looking at whether they
      flatter us.
- [ ] **The reliability picture.** There is still no figure showing a calibration curve deforming at the
      shift. For an audience that already accepts accuracy ≠ calibration, showing the familiar object break is
      the cheapest way to buy attention. The confidence-bin data exists and has been deprioritised twice.
- [ ] **F7 on more than three households**, if there is any compute at all. It is the best thesis-fit figure
      and the weakest-powered.

## Where things are

- Figures: `results/confidence_shift_2026-09-20/uq/figures/<FOLDER>/` — each holds the PNG, SVG and PDF plus
  `caption.md` (caption, population, households, data notes), `claims.md` (job in the argument, the claim,
  what demonstrates it, what it does NOT show) and `numbers.md` (every number behind it).
- `MANIFEST.json` / `MANIFEST.md` — all eleven, with rendered width and whether each is single, 1.5 or double
  column. **Reproduce each at its stated width.** Do not squeeze a 1.5-column figure into one column; the
  labels are set for that width and shrinking puts the smallest text near 4pt.
- Builder: `results/regime_search/tools/paper_figures.py`. Regenerate with `python3 tools/paper_figures.py`
  from `results/regime_search`. It refuses to ship a figure whose prose contains a number its own table does
  not produce, so if you change a claim by hand it will tell you.
- Method: `METHODS.md`. Known faults and their fixes: `problems_found.md` — read the last five entries before
  writing anything about reproducibility.

## One rule that has caught four errors here

**Anywhere one artifact quotes another's number, compute the quote from the source rather than copying it.**
A table beside a chart is computed from the drawn series. Prose reads its own table by key. The rerun floor is
imported from one file. If you find yourself typing a number into the paper that also appears in a figure,
you are doing the thing that produced every numerical error in this project.
