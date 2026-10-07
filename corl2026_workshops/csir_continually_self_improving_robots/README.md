# CSIR: Continually Self-Improving Robots (CoRL 2026 workshop)

- Workshop: "Continually Self-Improving Robots Workshop" at CoRL 2026
- URL: https://csircorl.github.io/website/
- Page limit: up to 8 pages, references and appendix excluded; any paper template
- Deadline: 28 September 2026, 11:59 PM anywhere on earth
- Status in the project memory (2026-10-01): the overnight-driver session "ended with the CSIR
  draft's checks, figures and appendix"; the submissions are described as done.

Everything in this folder is a copy. Nothing was moved. The LaTeX source (`main_v3.tex`) is not in
the repo and not on this machine; see "What is missing".

## The claim of the paper

There is no draft text of the CSIR paper in the repo (the text is in the LaTeX, which is
elsewhere). The nearest thing is the abstract checked sentence by sentence in
`paper_notes/DOES_THE_ABSTRACT_HOLD.md` (written 2026-09-28), which quotes the abstract's sentences.
Put together from those quotes and the file's verdicts:

> A home robot that learns from its own searches where the household's objects are, with a language
> model writing its memory each night. "The robot learns only from the rooms it searches and is not
> told about the illness." A simple last-seen rule outperforms every memory that stores only written
> summaries. "Giving the same summaries access to the raw sightings closes that gap: this memory is
> competitive with the rule and pulls ahead when the robot observes little" (+3.5 / +1.5 points over
> ten households, neither clearing two standard errors; +4.4 / +5.0 at four questions a day on the
> five wider homes, both clearing). When the illness returns, the memories that keep the raw record
> drop less than they did the first time; the summary-only memories drop about as much as before,
> because their notes record where objects moved but not why. "In one diagnostic case, a language
> model told about the illness predicts useful locations, then retracts the prediction in its next
> update."

The file's own verdict: "the argument holds, three sentences need rewording, and one of those is a
real overstatement." The 10-page PDF in `draft_pdf_from_results_memoryWorkshop/` is the same study
written out in full (its abstract is quoted in `../memory_for_robot_foundation_models/README.md`);
why it sits in both folders is explained there.

## What is in this folder and where it came from

`P` below means `results/self_improve/paper/` in the main repo.

### `paper_notes/` (from `P/*.md`)

| file | what it is |
|---|---|
| `questions_answered.md` | 2026-09-27, "what the code settles about the runs the draft draws on", with file and line for each answer |
| `questions_left_open.md` | the questions that file could not settle |
| `DOES_THE_ABSTRACT_HOLD.md` | the abstract against the measurements, sentence by sentence |
| `FIGURES.md` | the two figure sets (`spec` and `oliver`), what each figure draws, every number drawn |
| `FIGURE_CHECKS_BEFORE_DRAWING.md` | checks run before the figures were drawn |
| `appendix_material.md` | built by `P/scripts/write_appendix_material.py`; appendix text and tables |
| `numbers_check.md` | numbers in the prose checked against the outputs |
| `does_the_chooser_matter.md`, `does_the_log_cap_cost_anything.md`, `household_mode.md`, `the_two_held_cells.md` | one-question analyses (each has a matching `.txt` in `analysis_outputs/`) |

### `analysis_outputs/` (from `P/*.txt` and `P/*.json`)

Thirty-seven files. Each `.txt` is the saved output of the same-named script in `P/scripts/`
(`table1_ten_homes.txt` from `table1_ten_homes.py`, and so on; the `_FIXED` versions were rerun
after the ACE merge-step fix of 2026-09-30, see `OVERNIGHT_REPORT.md` item 1). Exceptions, with no
same-named script: `ace_pairs_share_an_object.txt`, `told_on_both_illnesses.txt` (probably from
`both_illnesses_told.py`), `household_mode_scores.txt` (from `score_household_mode.py`),
`scored_counts_overnight_wave.txt` (from `scored_counts.py`), `evening_threshold.txt/.json` and
`at_home_hours.json` (hand-saved checks). `night31_audit.json` is read back by `paper_figures.py`.

### `figures/` (from `P/figures/`, whole directory)

| path | what it is |
|---|---|
| `figures/spec/<name>/` | the figure set drawn to the written specification: `figure2_both_illnesses`, `figure3_told_the_cause`, `figure4_one_notes_life`, `figureA1_first_illness`, `figureA2_what_the_notes_held`, each a vector PDF plus `caption.md`; `figure2_both_illnesses_ACE_fixed/` is the post-fix redraw |
| `figures/oliver/<name>/` | the same five figures drawn to the verbal guidance (two or three lines, no bands, bold text, legend below) |
| `figures/household_mode/` | `household_mode.pdf` and its caption |
| `figures/NUMBERS_DRAWN.txt` | every number `paper_figures.py` drew |
| `figures/superseded_by_the_two_style_sets/` | four earlier PDFs and `WHY_THESE_ARE_HERE.md` |

### `draft_pdf_from_results_memoryWorkshop/` (from `results/memoryWorkshop/`)

| file | what it is |
|---|---|
| `DRAFT_CorlMemoryWorkshop_1.pdf` | 10-page LaTeX PDF, 2026-09-29, "How Should a Home Robot Update Its Memories When Human Routines Change?"; the full write-up of this study |
| `CHECKS_ON_THE_DRAFT.md` | eighteen checks of that PDF against `P/scripts/` outputs; six things to change |
| `OVERNIGHT_REPORT.md` | 2026-09-30, five jobs; the ACE merge-step bug and its fix, the log-only arm, the told-cause pattern across eight runs |

### `study_notes/` (from `results/self_improve/*.md`)

The study-level notes one directory above `paper/`: `THE_MAIN_POINTS.md` (what can be said, as of
2026-09-25), `EXPECTATIONS.md`, `WHAT_COUNTS_AS_A_LEAD.md`, `WHAT_WAS_SET_ASIDE.md`,
`THE_TWO_ACE_RUNS_ARE_THE_SAME_RUN.md`, `FAULTS_IN_SHARED_CODE.md`,
`HOW_OTHER_MEMORIES_BOUND_THEIR_GROWTH.md`, `IT_REPEATS_THE_FACT_AND_REASONS_PAST_IT.md`,
`A_PRIOR_OVER_A_SITUATION_IT_HAS_NEVER_SEEN.md`, `RICH_LOOKS_AND_THE_QUIZ_LIST.md`,
`WHAT_HAPPENS_TO_THE_SENTENCE.md`. These were not in the task's list; they are included because the
paper notes cite them (for example `WHAT_COUNTS_AS_A_LEAD.md` is the bar every lead was judged
against). Listed in the index README as a judgement call.

## Scripts that write into `results/self_improve/paper/`

This is why the folder was copied and not moved. Found by `grep -rn "self_improve/paper" src/
results/self_improve/paper/scripts/`:

- Nothing in `src/` references `results/self_improve/paper`.
- Forty-one scripts in `P/scripts/` reference the path, nearly all in their own usage line. The ones
  that **write** there:
  - `paper_figures.py`, `make_figures.py`, `day_curves.py`, `write_captions.py` write to
    `P/figures/` (`OUT = pathlib.Path("results/self_improve/paper/figures")`);
    `plot_the_chooser.py` writes `P/figures/the_chooser_by_day.pdf`.
  - `write_appendix_material.py` writes `P/appendix_material.md`.
  - `night31_audit.py` writes `P/night31_audit.json`; `paper_figures.py` reads it back.
  - `run_household_mode.py` writes `P/household_mode/` (default `--out`); `score_household_mode.py`
    and `day_curves.py` read it.
  - Every other analysis script prints to stdout and its output was redirected by hand to
    `P/<name>.txt` (the usage lines say `-> results/self_improve/paper/<name>.txt`).
- `results/memoryWorkshop/`: no writer in code; one prose reference in
  `write_appendix_material.py:420`.

## What the paper depends on and was left in place

Nothing below was copied. Paths are relative to the main repo unless absolute.

| path | what it is |
|---|---|
| `src/self_improve/` | the study code: `search_driven.py`, `overnight_wave.py`, `memory_notes.py`, `frozen_household.py`, `household_mode.py`, `the_rerun_noise_floor.py`, `study_settings.py`, `run_one_cell.py` and the rest |
| `src/baselines/` (`types.py` and the harness it imports) | imported by `paper_data.py` |
| `results/self_improve/paper/scripts/` | the 45 analysis and figure scripts (`paper_data.py` is the shared row loader; `figure_style.py` the shared style) |
| `results/self_improve/paper/household_mode/` | 252 JSON files (35 MB), the household-mode baseline outputs written by `run_household_mode.py`; run output, not copied |
| `results/self_improve/overnight_wave/cells/` | `WAVE_10` in `paper_data.py`: the ten-household run at 8 questions a day (Table 1, Figure A1) |
| `results/self_improve/overnight_wave_24_questions/cells/` | the same ten households at 24 a day |
| `results/self_improve/wave_the_second_illness/cells/` | `WAVE_50`: the 50-day run with two illnesses, three households (Figure 2, Tables 2 and 3) |
| `results/self_improve/wave_the_second_illness_ACE_rerun/cells/`, `wave_the_second_illness_ACE_fixed/` | the ACE arm rerun after the merge-step fix (`WAVE_50=...` override) |
| `results/self_improve/wave_the_family_reads_the_log/`, `wave_told_on_the_wider_homes/` | the eight told-cause runs (Figure 3, `the_told_cause_across_runs.txt`) |
| `results/self_improve/wave_wider_five/cells/`, `wave_the_budget_sweep_q4/cells/`, `wave_the_budget_sweep_q8/cells/` | the five wider homes at 4, 8 and 24 questions a day (the observation-budget claim) |
| `results/self_improve/wave_log_only/cells/` | the log-only arm (OVERNIGHT_REPORT job D) |
| `results/self_improve/wave_reasons_first/cells/` | the reason-first prompt order comparison |
| `results/self_improve/wave_last_seen_no_first_illness/` | last-seen with days 14 to 23 deleted (OVERNIGHT_REPORT job B) |
| `results/self_improve/varied_homes/ten_homes/banks/`, `varied_homes/all_generated_v2_twice/banks/`, `varied_homes/headline_five/`, `varied_homes/scenario/` | the question banks and household files (`BANKS_10`, `BANKS_50`) |
| `results/self_improve/runs/`, `three_prompts/`, `search_driven/`, `told_if_right/`, `the_second_illness/`, `ace_as_published/`, `memgpt_as_published/`, `scenario/`, `earlier_work/` | earlier and supporting runs read by `src/self_improve/*.py` |
| `results/self_improve/rerun_noise_floor.json`, `did_it_learn.json`, `room_coverage.json`, `scored_at_both_levels.json`, `nights_vacuous.json`, `never_seen_or_never_written.json`, `which_objects_moved.json`, `what_the_notes_mention_day23.json` | study-level JSON outputs read by the check scripts |
| `results/self_improve/*.py` (`check_classical_curve.py`, `check_scenario.py`, `rebuild_the_artifact.py`, `show_me_the_prompts.py`, ...) | study-level check scripts |
| `/home/oliver/robot/dynamic_home_eqa_archive/results/self_improve/archive/` | 2.5 GB of superseded self_improve runs moved to the archive on 2026-09-29 |

The per-cell LLM prompt caches live inside each `cells/<household>/<arm>/` directory; they are what
makes a rerun replay exactly (`vllm-nondeterminism-rerun-noise` in the project memory).

## What is missing

- `main_v3.tex` and the `.bib`: not in the repo, not anywhere on this machine (`find ~/robot -name
  "*.tex"` newer than 22 September returns nothing). Presumably on Overleaf.
- The submitted PDF of the CSIR paper itself. The only PDF on disk is
  `DRAFT_CorlMemoryWorkshop_1.pdf` (29 September), which may or may not be the submitted CSIR
  version; see the memory-workshop README for the reasoning.
- A record of which figure set (`spec` or `oliver`) went into the submission.
