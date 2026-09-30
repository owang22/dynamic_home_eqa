# What was moved out of this repository, 2026-09-29

The repository had grown to **190,024 tracked files and 9.0 GB**, which is more than a language
model's sandbox can walk. It is now **7,058 tracked files and 1.36 GB**. Nothing was deleted.

Everything below was **moved**, not removed, to

    /home/oliver/robot/dynamic_home_eqa_archive/

under the **same relative paths**, so `results/llm_hypotheses/cache/abc.json` is now
`/home/oliver/robot/dynamic_home_eqa_archive/results/llm_hypotheses/cache/abc.json`. Every file is
also still in this repository's git history: `git log --all -- <path>` finds it and
`git show <commit>:<path>` reads it back without touching the archive at all.

| path | tracked files | files on disk | size |
|---|---|---|---|
| `results/confidence_shift_2026-09-20` | 63,779 | 64,140 | 4.3G |
| `results/llm_hypotheses` | 62,758 | 64,613 | 752M |
| `results/overnight_2026-09-20` | 40,449 | 40,529 | 788M |
| `results/sota_memory` | 8,261 | 8,341 | 423M |
| `results/regime_search` | 383 | 644 | 1.5G |
| `preTravelFix` | 972 | 972 | 1.3G |
| `scratch_runs` | 5,194 | 5,194 | 35M |
| `old_profiles` | 681 | 681 | 81M |
| `data/objects/external_props` | 271 | 271 | 275M |
| `data/objects/external_props_candidates` | 219 | 219 | 15M |
| `results/self_improve/archive` | 0 | 4,040 | 2.5G |
| `src/.mypy_cache` | 0 | 15,271 | 336M |
| **total** | **182,967** | **204,915** | **9.6 GB** |

## Why each one

- **`results/confidence_shift_2026-09-20`**, **`results/llm_hypotheses`**,
  **`results/overnight_2026-09-20`**, **`results/sota_memory`**, **`results/regime_search`** -
  finished or superseded run strands. Their only readers are the scripts that wrote them
  (`src/baselines/patrol/uq_*.py`, `src/baselines/llm_hypotheses/*.py`), which are themselves part
  of those strands. Nothing in the current paper pipeline reads any of them.
- **`preTravelFix/`**, **`scratch_runs/`** - no reference anywhere in `src/` or the paper scripts.
- **`old_profiles/`** - five mentions in `src/`, every one of them prose in a docstring saying the
  new code does *not* read it. No code path loads it.
- **`data/objects/external_props`** and **`external_props_candidates`** - 3D render assets, some
  `.glb` files 18 MB each. Referenced only in a docstring about asset binding. The small file the
  code does load, `data/objects/clutter_room_map.json`, **stayed**.
- **`results/self_improve/archive`** - already untracked, already named archive, 2.5 GB.
- **`src/.mypy_cache`** - type-checker cache, 15,271 files, regenerable. This one is genuinely
  disposable; it was moved rather than deleted only for consistency.

`__pycache__` directories were deleted rather than moved: compiled bytecode, already ignored,
regenerated on the next import.

## What deliberately stayed

- **`results/self_improve`** - the live paper. 15 GB on disk, 598 files tracked; the run cells
  every number comes from are untracked but must stay where the analysis scripts read them.
- **`results/rendered_look`** - another session was editing it the same day.
- **`data/situation_sim`** - kept on request.
- **`llm_prior_cache/`** (181,060 files, 754 MB) - **do not move this.** It is the model-response
  cache that `run_one_cell.py`, `search_driven.py` and `overnight_wave.py` read and write, and
  180,453 of its files are from the current paper's runs. Moving it means every future run misses
  the cache and has to call the model again. It is gitignored, so it costs a clone nothing.
- **`third_party/`** (6,465 files, 5.9 GB) - gitignored by a hard rule already, and `src/` imports
  from it.

## If the sandbox still struggles

A git-aware sandbox is now fine: a clone is 7,058 files. A sandbox that copies the **directory**
still sees 22 GB, because the live run cells and the model cache have to stay. Exclude these two
and it drops to about 1.5 GB:

    llm_prior_cache/
    third_party/

`git clone --depth 1` also avoids the 2.6 GB of history, which was left intact on purpose:
rewriting it would change every commit hash and break every other working copy.

## Putting something back

    mv /home/oliver/robot/dynamic_home_eqa_archive/results/regime_search results/

then remove its line from `.gitignore` if it should be tracked again. To run one of the old
strands in place, point its scripts at the archive root rather than moving it back.
