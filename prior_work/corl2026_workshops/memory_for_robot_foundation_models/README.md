# Memory for Robot Foundation Models (CoRL 2026 workshop)

- Workshop: "Memory for Robot Foundation Models", half-day workshop at CoRL 2026
- URL: https://corl2026-memory.github.io/
- Page limit: up to 4 pages excluding references (CoRL 2026 template, double-anonymised; appendices do not count)
- Deadline: 30 September 2026, anywhere on earth
- Status in the project memory (2026-10-01): "FM-memory workshop paper (2026-09-21, due 24 Sep) ... Submitted."

Everything in this folder is a copy. Nothing was moved. The originals are where the table below says.

## Two bodies of work sit here

There are two drafts in this folder and they are different studies.

1. `fm_memory_draft/` is the study written on the `fm-memory` git worktree
   (`/home/oliver/robot/dynamic_home_eqa_fm`, branch `fm-memory`), runs final on 2026-09-22. Its draft
   says in its own first line: "Draft for the CoRL 2026 workshop 'Memory for Robot Foundation Models'
   (4 pages excl. references)". This is the memory-workshop paper beyond doubt.

2. `memoryWorkshop_pdf_and_checks/` is a copy of `results/memoryWorkshop/` from the main repo: a
   10-page LaTeX PDF built 2026-09-29 titled "How Should a Home Robot Update Its Memories When Human
   Routines Change?", plus two markdown files that check it. See the next section for what it is.

### What `DRAFT_CorlMemoryWorkshop_1.pdf` is, and why it is also copied into the CSIR folder

Facts checked:

- `pdftotext` of page 1: the abstract describes simulated households where "a resident falls ill,
  recovers, and later falls ill again", the robot "sees only the rooms it opens and is never told
  that anyone is ill", and compares "a simple rule that searches where an object was last seen",
  "several language-model memories that store only written summaries", and "the same summaries
  paired with the raw record of sightings". That is the self-improve study (`src/self_improve/`,
  runs under `results/self_improve/wave_*` and `overnight_wave*`), not the fm_memory study (which
  has a replay buffer, a nightly routine table, counters, and a "she is home sick today" message,
  on a fixed sighting stream with no searching).
- `CHECKS_ON_THE_DRAFT.md` checks the PDF's numbers against `results/self_improve/paper/scripts/*.py`
  and `results/self_improve/paper/*.txt` (Table 1 reproduces from `table1_ten_homes.py`, and so on).
  `OVERNIGHT_REPORT.md` (30 September) reports five jobs run with those same scripts.
- `pdfinfo`: 10 pages, "LaTeX with hyperref", created 29 September 2026 16:30 PDT. Sections 1 to 6
  and the conclusion run to page 7; references start on page 7; the appendix fills pages 8 to 10.
  About six and a half pages of main text.
- The memory workshop allows 4 pages; CSIR allows 8. The CSIR deadline (28 September) had passed
  when this PDF was built; the memory-workshop deadline (30 September) had not.
- The file name and folder name both say "memory workshop", and the paper's last sentence asks that
  "how a memory applies past experience to a situation that returns should be an evaluation
  criterion for robot memory".

Decision: this PDF is the memory-workshop write-up of the self-improve illness study, that is, a
second memory-workshop draft, distinct from `fm_memory_draft/`. The name, title, folder and build
date all point at this workshop. Its length (about 6.5 pages of main text) does not fit the 4-page
limit, so either it was cut before submission or it was prepared for CSIR under a misleading name;
the repo does not record which. Because its content, figures and every numeric check come from the
CSIR study's code and analysis folder, the same three files are also copied into
`../csir_continually_self_improving_robots/draft_pdf_from_results_memoryWorkshop/`, so whichever
workshop it was sent to, the folder for that workshop has it. No `.tex` or `.bib` for it exists
anywhere on this machine (`CHECKS_ON_THE_DRAFT.md` says the same; a `find` over `~/robot` on
2026-10-02 found no `.tex` newer than 22 September).

## The claim of each draft

**fm_memory draft** (from `fm_memory_draft/paper/draft.md`, abstract, quoted in part):

> "A home robot that answers 'where is my mug?' from what it has seen must remember the
> household's routine, not the last frame. We ask what that memory should store and how it gets
> updated when the routine shifts, on a symbolic household simulator with a scripted shift: 14 days
> of an ordinary routine, ten days with one resident off sick ..., eight days back at work. ... We
> compare two LLM memories practitioners deploy, a replay buffer of dated sightings and a nightly
> consolidated routine table, against counters that never forget, forget with a half-life, or index
> memory by regime. The buffer learns the routine (66% cold, against 73% for a counter) and
> collapses at the shift like everything else, but then does not re-learn from ten days of
> feedback ... A replay buffer is memory without an update rule. The consolidated table never
> learns the routine at all (40% cold) ... One sentence, 'she is home sick today', is what updates
> the buffer: +33.3 cold points inside the spell (se 3.7, 18 households) ... A counter that stores
> each sighting under the regime it was seen in re-learns as fast as the forgetting counter with a
> return drop a fifth the size (-4.7 against -22.9): the shift should be a retrieval key, not a
> caption and not a forgetting trigger."

**memoryWorkshop PDF** (from page 1 of `memoryWorkshop_pdf_and_checks/DRAFT_CorlMemoryWorkshop_1.pdf`,
abstract, quoted in part):

> "We compare a simple rule that searches where an object was last seen, several language-model
> memories that store only written summaries, and the same summaries paired with the raw record of
> sightings. The simple rule outperforms every summary-only memory, and adding the raw record closes
> that gap. The return of the illness reveals the larger difference. All methods drop in accuracy
> when the second illness begins, but methods with the raw record are less wrong than they were at
> the first illness, while summary-only methods are about as wrong as the first time. Their
> summaries record where objects moved but not why. When we tell the model the cause directly, it
> predicts the new locations correctly for a full day, then discards the explanation in its next
> update after one contrary observation. ... Memories for changing homes should keep raw
> observations alongside summaries and represent the state of the household separately from facts
> about objects."

## What is in this folder and where it came from

`FM` below means `/home/oliver/robot/dynamic_home_eqa_fm/results/fm_memory` (the `fm-memory`
worktree). Note: `results/fm_memory/` is **untracked** in that worktree (`git status` shows
`?? results/fm_memory/`), so until now these files existed only on disk, on no branch. This copy
is the first one inside a tracked tree.

| file in this folder | copied from |
|---|---|
| `fm_memory_draft/paper/draft.md` | `FM/paper/draft.md` (the 4-page draft, markdown) |
| `fm_memory_draft/paper/memory_page.html` | `FM/paper/memory_page.html` (the self-contained results page built by `tools/build_page.py`) |
| `fm_memory_draft/figs/fig1_shape.png`, `fig1_shape_cold.png` | `FM/figs/` (Figure 1, all questions and cold questions) |
| `fm_memory_draft/figs/fig2_told.png`, `fig2_told_cold.png` | `FM/figs/` (Figure 2) |
| `fm_memory_draft/figs/stage_means.md`, `stage_means_cold.md` | `FM/figs/` (the stage-mean tables the figures draw) |
| `fm_memory_draft/notes/tools_README_gotchas.md` | `FM/tools/README_gotchas.md` (harness gotchas found while running the study) |
| `fm_memory_draft/notes/v1_weekday_stamps_README.md` | `FM/v1_weekday_stamps/README.md` (why the v1 runs were superseded) |
| `fm_memory_draft/notes/v2_weekend_names_README.md` | `FM/v2_weekend_names/README.md` (why the v2 runs were superseded) |
| `fm_memory_draft/notes/frozen_regime_2026-09-21_person.yaml` | `FM/frozen_regime_2026-09-21_person.yaml` (the frozen regime config) |
| `fm_memory_draft/notes/f1_s10_19.yaml` | `FM/f1_s10_19.yaml` (config for the second bank set, seeds 10 to 19) |
| `memoryWorkshop_pdf_and_checks/DRAFT_CorlMemoryWorkshop_1.pdf` | `results/memoryWorkshop/DRAFT_CorlMemoryWorkshop_1.pdf` (main repo) |
| `memoryWorkshop_pdf_and_checks/CHECKS_ON_THE_DRAFT.md` | `results/memoryWorkshop/CHECKS_ON_THE_DRAFT.md` |
| `memoryWorkshop_pdf_and_checks/OVERNIGHT_REPORT.md` | `results/memoryWorkshop/OVERNIGHT_REPORT.md` |

There is no file named `EXPECTATIONS.md` under `FM/`; the three README files above are the only
notes of that kind there. The fm_memory study has no PDF and no LaTeX anywhere on this machine; the
markdown draft is the only text.

## What the papers depend on and was left in place

Nothing below was copied. Scripts expect these paths.

### fm_memory draft (all under the `fm-memory` worktree)

| path | what it is |
|---|---|
| `FM/run1/`, `FM/run2_told/`, `FM/run3_toldret/` | the main arms: no message, start message, start + end messages (seeds 0 to 9) |
| `FM/run1_x/`, `FM/run2_told_x/`, `FM/run3_toldret_x/` | the same three arms on the second bank set (seeds 10 to 19), for the 18-household message contrasts |
| `FM/partial/`, `FM/partial_told/` | the partial-shift runs (6 households) |
| `FM/f1_s10_19/` | runs on the second bank set |
| `FM/banks_f1/`, `FM/banks_f1_return/`, `FM/banks_f1_return_s10_19/`, `FM/banks_partial/` | the question banks |
| `FM/classical_tagged/` | the regime-tagged counter runs |
| `FM/cache/` (4.8 MB directory listing; the LLM prompt cache) | needed to replay any LLM arm exactly (see `tools_README_gotchas.md`: "keep the cache with the run") |
| `FM/v1_weekday_stamps/`, `FM/v2_weekend_names/` | superseded runs, kept as a record |
| `FM/server/` | vLLM restart script and log |
| `FM/tools/figs.py`, `paired.py`, `endmsg_contrast.py`, `owner_paired.py`, `stage_table.py`, `build_page.py`, `assay.py`, `class_told.py`, `monitor.py`, `notes_trace.py`, `owner_split.py`, `run_tagged.py`, `*.sh` | the analysis and figure code; the draft's first line says figures and tables regenerate from these |
| `/home/oliver/robot/dynamic_home_eqa_fm/data/situation_sim/fm_memory_f1/` | the household data (untracked in the worktree) |
| `/home/oliver/robot/dynamic_home_eqa_fm/src/baselines/patrol/` (`llm.py`, `bank.py`, `run.py`, `confshift.py`) and `src/situation_sim/` | the harness; these files carry **uncommitted modifications** on the `fm-memory` worktree (`git status` lists them as `M`), so the code that produced the runs is not on any branch either |
| `*.log`, `*.yaml` at the top of `FM/` | run logs and configs |

### memoryWorkshop PDF

Its dependencies are the CSIR study's; see
`../csir_continually_self_improving_robots/README.md`, section "What the paper depends on".

## Scripts that write into the source folders

- `results/memoryWorkshop/`: no script in `src/` or `results/self_improve/paper/scripts/` writes
  there. The one reference is a prose mention in
  `results/self_improve/paper/scripts/write_appendix_material.py:420` (it cites
  `CHECKS_ON_THE_DRAFT.md`, item 6). The folder was hand-made. It was copied rather than moved
  because the appendix text points readers at that path.
- `FM/figs/`, `FM/paper/`: written by `FM/tools/figs.py` and `FM/tools/build_page.py` in the
  worktree. Copied, not moved, for that reason.

## What is missing

- No LaTeX source or `.bib` for either draft on this machine. The fm_memory draft was submitted
  (project memory, 2026-10-01) but no submitted PDF of it is on disk; if one exists it is on
  Overleaf or in email.
- No record in the repo of which version of `DRAFT_CorlMemoryWorkshop_1.pdf` was submitted, or to
  which of the two workshops.
- The fm_memory code and results are uncommitted on the `fm-memory` worktree. If that worktree is
  ever removed, only this folder's copies survive.
