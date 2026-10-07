# Uncertainty workshop (CoRL 2026)

- Workshop: **name not recorded.** Oliver called it "the uncertaintywm workshop". No file in the repo,
  the archive, or the memory directories (`~/.claude/projects/-home-oliver/memory/`,
  `~/.claude/projects/-home-oliver-robot-dynamic-home-eqa/memory/`) gives its full name or URL.
  The only mentions are `uq/NARRATIVE.md` ("Narrative outline for the uncertainty workshop
  submission", 2026-09-23) and `uq/WRITING_THE_PAPER.md` ("You are writing an uncertainty paper,
  not a robot-memory paper").
- URL: not recorded.
- Page limit: not recorded.
- Deadline: not recorded.
- Status in the project memory (2026-10-01): the "UQ-methods research agent (2026-09-21)" was
  "superseded 2026-09-24 by the ACE rebuild. Its outputs are the `confidence_shift_2026-09-20`
  strand, now in the archive." No submission of this paper is recorded; the memory lists the memory
  workshop and CSIR as the submissions that were made.

Everything in this folder is a copy. Nothing was moved. The originals are in the archive
(`/home/oliver/robot/dynamic_home_eqa_archive/`) except `closed_loop/QUESTIONS.md`, which is in the
main repo.

## The claim of the paper

From `confidence_shift/uq/NARRATIVE.md`, section "The argument in one paragraph" (2026-09-23),
quoted in full:

> "A home robot answers 'where is X?' from a memory of what it has seen. In a settled household
> every method we tested does this well and knows roughly how well it is doing. When the
> household's routine changes temporarily, one resident is off sick for ten days, then returns,
> every method breaks, and the useful question is not whether it breaks but whether it can tell that
> it has. It cannot. At the moment the routine changes, the confidence these methods report stops
> predicting their own correctness, so a robot deciding when to answer and when to ask for help is
> deciding on a signal that has gone dead exactly when it is needed. The failure is not calibration
> and cannot be fixed by tuning a threshold: the ordering of questions by confidence carries no
> information at that moment, and a threshold chosen with hindsight does no better. One method
> escapes, the one whose confidence models how long a fact stays true rather than how regular the
> past was, and it is the least accurate of the three. Being right and knowing when you are wrong
> come apart."

`confidence_shift/uq/WRITING_THE_PAPER.md` states the same claim in one line: "Accuracy and
uncertainty are separate axes, and a change in the household's routine moves one and not the
other", and adds the mechanism: "Whether a method's uncertainty survives a shift follows from what
its confidence is a function of. Frequency-based confidence cannot see a regime change.
Age-of-evidence confidence must."

## What is in this folder and where it came from

`CS` below means `/home/oliver/robot/dynamic_home_eqa_archive/results/confidence_shift_2026-09-20`;
`SM` means `/home/oliver/robot/dynamic_home_eqa_archive/results/sota_memory`;
`RS` means `/home/oliver/robot/dynamic_home_eqa_archive/results/regime_search`.

### `confidence_shift/` (the 2026-09-20/21 confidence-shift study, from `CS/`)

| file | copied from | what it is |
|---|---|---|
| `report.md` | `CS/report.md` | the assembled report (protocol, findings, tables); built by `CS/make_report.py` |
| `findings.md` | `CS/findings.md` | the findings narrative included first in the report |
| `open_questions.md` | `CS/open_questions.md` | open questions and assumptions |
| `problems_found.md` | `CS/problems_found.md` | numbered problems found in the harness and methods |
| `tuning_log.md` | `CS/tuning_log.md` | every config tried on the tuning seeds |
| `overnight_status.md` | `CS/overnight_status.md` | the driver session's status log |
| `ledger_live.html`, `ledger_live_fb.html` | `CS/` | the live ledger pages (artifact KJPMaPPbgv4UmeVakrDSTA) |
| `driver/` | `CS/driver/` | the driver's small scripts (`build_ledger.sh`, `check_fb.py`, `check_fb_v1.py`, `watch_fb.sh`, `weekend_table.py`) and two weekend tables (`weekend_table_0502.md`, `weekend_table_0650_told_final.md`). Copied whole because the task listed it; it holds 60 KB of code |

### `confidence_shift/uq/` (the uncertainty-methods research agent's work, from `CS/uq/`)

| file | copied from | what it is |
|---|---|---|
| `NARRATIVE.md` | `CS/uq/NARRATIVE.md` | the narrative outline for the submission (the claim above) |
| `WRITING_THE_PAPER.md` | `CS/uq/WRITING_THE_PAPER.md` | instructions for writing the paper: the claim, what not to write |
| `REPORT.md` | `CS/uq/REPORT.md` | "Uncertainty-aware prediction methods on the regime testbench", 2026-09-21 |
| `METHODS.md` | `CS/uq/METHODS.md` | the methods |
| `CLAIM_AUDIT.md` | `CS/uq/CLAIM_AUDIT.md` | each claim against its evidence |
| `RESEARCH_BRIEF.md` | `CS/uq/RESEARCH_BRIEF.md` | the brief the agent worked from |
| `problems_found.md` | `CS/uq/problems_found.md` | problems found in this strand |
| `figures/` | `CS/uq/figures/` (whole, 2.9 MB) | eleven paper figures F1 to F11, each as PDF, PNG and SVG with `caption.md`, `claims.md`, `numbers.md`; plus `MANIFEST.md` and `MANIFEST.json` |
| `llm_strategies/*.md` | `CS/uq/llm_strategies/` | `STORY.md`, `STORY_numbers.md`, `STORY_paired.md`, `STATUS.md`, `SHORTLIST.md`, `EXPECTATIONS.md`, `THE_WATCHER_WAS_STOPPED.md` (the LLM-strategies sub-strand; only its markdown, not its 778 MB of runs) |
| `regime/*.md` | `CS/uq/regime/` | `EXPECTATIONS.md`, `report.md`, `report_auto.md` (only the markdown, not its 2.4 GB of runs) |
| `fb/report.md` | `CS/uq/fb/report.md` | the found-it-feedback sub-strand report |
| `planning/*.md` | `CS/uq/planning/` | `README.md` and six summary tables (the two `by_day.csv` files, 2.7 MB, were left) |

### `sota_memory/` (the 2026-09-23 "SOTA-memory night", from `SM/`)

| file | what it is |
|---|---|
| `EXPECTATIONS.md` | predictions written before each run |
| `RESULTS.md` | results as they landed, against the predictions |
| `SURVEY.md`, `SURVEY2.md` | survey of published memory systems and how they bound growth |
| `EXPIRY.md`, `REINSTATEMENT.md`, `HARNESS_AUDIT.md` | the fact-store failure catalogue and the harness audit |
| `four_arm.txt` | the four-arm table |

### `regime_search_notes/` (from `RS/`)

`FROZEN_REGIME.md` (the frozen testbench shape, 2026-09-21) and `NOTES.md` (the regime-search
running notes). Not in the task's list; included because `uq/figures/MANIFEST.md` says the
figures are "regenerated by `results/regime_search/tools/paper_figures.py` from `story_data.json`",
so the regime-search strand is where the figures come from.

### `closed_loop/`

`QUESTIONS.md`, copied from `results/closed_loop/QUESTIONS.md` in the main repo: the candidate
research questions for the closed-loop strand (2026-09-22). It is the only file in that directory.

## Scripts that write into the source folders

None of the source folders is written by anything in the main repo's `src/` now. The archive
manifest (`ARCHIVE_MANIFEST.md`) says of `results/confidence_shift_2026-09-20`, `results/sota_memory`
and `results/regime_search`: "Their only readers are the scripts that wrote them
(`src/baselines/patrol/uq_*.py`, `src/baselines/llm_hypotheses/*.py`), which are themselves part
of those strands. Nothing in the current paper pipeline reads any of them." Those scripts
(`src/baselines/patrol/confshift.py`, `confshift_figs.py`, `hyp.py`, `uq_*.py`) still exist in the
main repo and use the pre-archive relative paths, so they would write to
`results/confidence_shift_2026-09-20/` under the repo root if run. Copying rather than moving keeps
the archive consistent with what those scripts expect once pointed at it.

## What the paper depends on and was left in place

| path | what it is |
|---|---|
| `CS/heldout_fb/` (158 MB) | the held-out runs under the frozen found-it-feedback protocol: 20 households classical, LLM on 8; the paper tables come from here |
| `CS/heldout/`, `CS/heldout_p8/` (168 MB, 101 MB) | earlier held-out protocols (`heldout_p8` is the sealed 8-hour-patrol secondary section) |
| `CS/tuning/` (323 MB) | tuning runs on seeds 0 to 9 |
| `CS/followon/` (247 MB) | follow-on shift baselines |
| `CS/probe/`, `CS/llm_cache/` (68 MB) | probes and the LLM prompt cache |
| `CS/uq/regime/<bank>/` (2.4 GB) | the uncertainty-wrapper runs per bank (`sick10_all`, `sick10_owner`, and the earlier banks); `check.md` per bank; `roster.sh` |
| `CS/uq/llm_strategies/` (778 MB) | the LLM-strategy runs |
| `CS/uq/fb/`, `CS/uq/llm_channels/`, `CS/uq/planning/*.csv` | smaller run outputs |
| `CS/uq/shared_state.json`, `CS/uq/windows.json` | the shared state and window definitions the figures use |
| `CS/make_report.py`, `assemble.sh`, `live_affected.py`, `live_progress.py`, `llm_usage.py` | report assembly |
| `RS/` (1.5 GB) | the regime-search runs, `story_data.json`, `story_extra.json`, `page.html`, and `RS/tools/paper_figures.py`, `story_data.py`, `story_page.py` and the rest, which draw the F1 to F11 figures |
| `SM/cache/`, `SM/nottold/`, `SM/nottold_rerun/`, `SM/told/`, `SM/sweeps/`, `SM/smoke/`, `SM/withdrawn/`, `SM/*.log`, `SM/*.pid` | the SOTA-memory runs; `SM/stage_table.py`, `strata.py`, `six.py`, `rerun_noise.py`, `judge_audit.py` the tools |
| `src/baselines/patrol/` in the main repo (`confshift.py`, `confshift_figs.py`, `bank.py`, `run.py`, `llm.py`, `hyp.py`, `uq_agents.py`, `uq_llm*.py`, `uq_report.py`, `uq_windows.py`, `uq_shared_state.py`, ...) | the harness and the uncertainty methods |
| `configs/frozen_2026-09-20.yaml`, `configs/frozen_2026-09-21.yaml`, `configs/frozen_regime_2026-09-21_person.yaml`, `configs/frozen_regime_2026-09-21_household.yaml` | the frozen protocols |
| `data/situation_sim/confshift/ev10/` | the households (per the project memory `confidence-shift-study.md`) |
| `/home/oliver/robot/dynamic_home_eqa_fm/results/fm_memory/banks_f1/` | the banks `SM/EXPECTATIONS.md` names as the SOTA-memory task's input |

## What is missing

- The workshop's name, URL, page limit and deadline.
- Any draft text. There is a narrative outline (`uq/NARRATIVE.md`), writing instructions
  (`uq/WRITING_THE_PAPER.md`), eleven figures with captions, and reports, but no draft, no PDF and
  no LaTeX. Nothing records that this paper was written or submitted; the memory says the strand
  was superseded on 2026-09-24.
- `uq/figures/MANIFEST.md` points at `results/regime_search/tools/paper_figures.py`, which is now in
  the archive at `RS/tools/paper_figures.py`; the figures cannot be regenerated from the main repo
  without pointing that script at the archive.
