# CoRL 2026 workshop submissions: the paper-facing material in one place

Gathered 2026-10-02. Every file here is a **copy**; nothing was moved or deleted. The run outputs,
caches, banks and code that the papers depend on stay where the scripts expect them, and each
subfolder's README lists those paths. Copies were taken with `cp -p`, so the timestamps are the
originals'.

| folder | workshop | URL | pages | deadline | size |
|---|---|---|---|---|---|
| `memory_for_robot_foundation_models/` | Memory for Robot Foundation Models | https://corl2026-memory.github.io/ | 4 excl. references | 30 Sep 2026 AoE | 3.7 MB |
| `csir_continually_self_improving_robots/` | CSIR: Continually Self-Improving Robots | https://csircorl.github.io/website/ | 8 excl. references and appendix | 28 Sep 2026 AoE | 2.9 MB |
| `uncertainty_workshop/` | CoRL 2026 uncertainty workshop (Oliver: "uncertainty"; URL not recorded) | not recorded | not recorded | not recorded | 11 MB |

Page limits and deadlines for the first two were read from the workshop pages on 2026-10-02.

## What each folder holds, in one line

- **memory_for_robot_foundation_models/**: the `fm-memory` worktree's draft (`draft.md`, the
  results page, four figures, three README notes, two configs), and a copy of
  `results/memoryWorkshop/` (the 10-page PDF "How Should a Home Robot Update Its Memories When
  Human Routines Change?" with its two check files).
- **csir_continually_self_improving_robots/**: `results/self_improve/paper/` minus its code and run
  output (11 notes, 37 analysis outputs, the figures directory), the study-level notes from
  `results/self_improve/*.md`, and a second copy of the `results/memoryWorkshop/` PDF and checks.
- **uncertainty_workshop/**: the confidence-shift study's reports, question lists, ledgers and
  driver folder; the uncertainty-methods sub-strand's narrative, writing instructions, reports and
  eleven figures; the SOTA-memory night's expectations, results and surveys; the regime-search
  notes; `results/closed_loop/QUESTIONS.md`.

## Files I was unsure about, and what I did

1. **`results/memoryWorkshop/DRAFT_CorlMemoryWorkshop_1.pdf`** (and its two check files). Named
   for the memory workshop, built 29 September, but its content is the CSIR study
   (`src/self_improve/`), its checks run the CSIR analysis scripts, and its 6.5 pages of main text
   fit CSIR's 8-page limit and not the memory workshop's 4. Copied into **both** folders. The
   reasoning is written out in `memory_for_robot_foundation_models/README.md`.
2. **`results/self_improve/*.md`** (eleven study-level notes such as `THE_MAIN_POINTS.md`,
   `WHAT_COUNTS_AS_A_LEAD.md`, `EXPECTATIONS.md`). Not in the task's list, but the paper notes cite
   them. Copied into `csir_continually_self_improving_robots/study_notes/`.
3. **`results/self_improve/paper/household_mode/`** (252 JSON files, 35 MB). Run output written by
   `run_household_mode.py` and read by two other scripts. Not copied.
4. **`results/self_improve/paper/scripts/`** (45 Python files). Code. Not copied; listed as a
   dependency.
5. **`fm_memory/tools/*.py` and `*.sh`** in the worktree. Code. Not copied, except
   `README_gotchas.md`. Note that `results/fm_memory/` is untracked in the worktree and the harness
   files it used carry uncommitted edits there, so if the worktree is removed that code is lost;
   the folder README says so.
6. **`confidence_shift_2026-09-20/driver/`**. Holds five small scripts and two tables. The task
   listed it by name, so it was copied whole (60 KB), against the general rule of not copying code.
7. **`confidence_shift_2026-09-20/uq/`**. Not in the task's list, but it is where the uncertainty
   paper's narrative, writing instructions, claim audit and all eleven figures live. Copied its
   markdown files and `figures/` (2.9 MB); left its 3.2 GB of runs.
8. **`regime_search/FROZEN_REGIME.md` and `NOTES.md`** (archive). Not in the task's list; the
   figure manifest says the figures are generated from that strand. Copied the two notes only.
9. **`sota_memory/SURVEY2.md`, `EXPIRY.md`, `REINSTATEMENT.md`, `HARNESS_AUDIT.md`,
   `four_arm.txt`**. The task named `EXPECTATIONS.md`, `RESULTS.md`, `SURVEY.md`; these five sit
   beside them and are notes of the same kind, so they were copied too.
10. **`confidence_shift_2026-09-20/overnight_status.md`, `tuning_log.md`, `ledger_live_fb.html`**.
    Same reasoning as 9; copied.
11. **The uncertainty workshop's identity.** Searched both memory directories, the archive's
    markdown and the repo for "uncertaintywm", "uncertainty workshop", "workshop". Only two files
    name it, both as "the uncertainty workshop". Recorded as "name not recorded".

## Missing everywhere

- No LaTeX source or `.bib` for any of the three papers is on this machine (`main_v3.tex` for CSIR
  is presumably on Overleaf).
- No submitted PDF for the fm_memory draft or for the CSIR paper; the only PDF is the one in item 1.
- No draft at all for the uncertainty paper.

## Scripts that write into the source folders (why copy, not move)

- `results/self_improve/paper/`: `paper_figures.py`, `make_figures.py`, `day_curves.py`,
  `write_captions.py`, `plot_the_chooser.py` write `figures/`; `write_appendix_material.py` writes
  `appendix_material.md`; `night31_audit.py` writes `night31_audit.json`; `run_household_mode.py`
  writes `household_mode/`. All live in `results/self_improve/paper/scripts/`. Nothing in `src/`
  references the folder.
- `results/memoryWorkshop/`: no writer in code; one prose reference at
  `results/self_improve/paper/scripts/write_appendix_material.py:420`.
- `fm_memory/figs/` and `fm_memory/paper/`: written by `tools/figs.py` and `tools/build_page.py`
  in the worktree.
- The archive strands: written by `src/baselines/patrol/confshift*.py`, `hyp.py`, `uq_*.py` (still
  in the main repo) at their pre-archive relative paths.
