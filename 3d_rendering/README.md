# 3d_rendering

Simulated lived-in homes for testing a robot's memory, and pictures of them.

- **lived_home generator** (`src/lived_home/`): language-model residents live day by day in an
  HSSD home. A rule engine holds where every object is; an object moves only when a resident
  carries it. Every 2 hours (08:00-22:00) the run writes a snapshot of every position.
- **Renders** (`results/vlm_night/render/`): household A's snapshots placed in its HSSD scene
  (habitat-sim), photographed from fixed robot viewpoints, with true pixel counts per object.
- **VLM night** (`results/vlm_night/questions/`): question trials on those pictures with the
  local Qwen3.8-27B vision model.
- **Render-methods trial** (`results/render_methods/`): Habitat+HSSD, OmniGibson and EnvDreamer
  on one test; the reports recommend Habitat+HSSD, which the renders use.

## Layout

```
src/lived_home/      generator, world rules, placement rules, play task, baselines, checkers
tests/               98 tests of the generator (no model, no GPU)
results/lived_home/  one folder per run, plus dated notes (*_2026-10-*.md) and spend_ledger.json
results/vlm_night/   render/ (picture code, README.md), questions/ (trial code and results)
results/render_methods/  TEST_SPEC.md, one REPORT.md per method, gallery/
results/hssd_survey.json output of `python -m lived_home.hssd_layout --survey`
critic/              brief and dated notes of the skeptic reviewer
(the first draft, examples/lived_home_draft/, moved to /home/oliver/robot/dynamic_home_eqa_archive/ on 2026-10-19)
```

## How to run

From the repo root, with `PYTHONPATH=3d_rendering/src` and the `dynamic_eqa` conda env:

```
python -m pytest 3d_rendering/tests -q                       # tests
python -m lived_home.run_pilot --scene <hssd scene> --days 14 --out <run>   # paid; --fake: offline
python -m lived_home.run_pilot --household <run>/household.json --fake --days 2 --out <tmp>
python -m lived_home.play <run>              # play task page -> <run>/play/
python -m lived_home.play_baselines <run>    # simple methods on every play question
python -m lived_home.baselines <run>         # predictors from patrol notes -> baselines_notes.md
python -m lived_home.check_placement <run>   # positions the placement rules forbid
python -m lived_home.drift <run>             # clutter over the days -> drift.json
python -m lived_home.read_pilot <run>        # replay.md, report.md   (build_page: viewer page)
```

Paid runs: set `HOSTED_SPEND_LEDGER` to `results/lived_home/spend_ledger.json` (default is in
/tmp) and `HOSTED_SPEND_CAP` (dollars, total over the ledger).
Renders: `results/vlm_night/render/README.md`. Question trials: each script's header.
Tested: world and placement rules, household checks, HSSD layout reading, the day loop, the
play task. Not tested: model calls, render scripts, question trials, render-methods scripts.

## Runs and write-ups

| run | home | days | write-up |
|---|---|---|---|
| `hssd_a` (household A) | HSSD 107734254_176000121 | 14 | `report.md`, `baselines_notes.md` |
| `hssd_b` (household B) | HSSD 104862621_172226772 | 14 | `report.md`, `baselines_notes.md` |
| `hssd_a2` (A again, placement rules on) | as A | 14 | `NOTES.md` (code in `code_frozen/`) |
| `hssd_luna` | HSSD 105515337_173104347 | 7 | `PILOT_WRITEUP.md` |
| `pilot_luna` | invented home | 7 | superseded (`hssd_luna_check`, a 2-day check, moved to the archive 2026-10-19) |

Dated notes: `results/lived_home/FIXES_2026-10-13.md` (placement rules, search scoring),
`results/vlm_night/NIGHT_2026-10-13.md` (+ `AUDIT_`), `vlm_night/questions/placed/RESULTS.md`
and `GRADING.md`; older: `results/lived_home/NIGHT_2026-10-10.md`, `MORNING_2026-10-09.md`.

Superseded, kept for provenance: `stale_*/` folders in runs (not in git), `questions/old_v1/`
(answers before the parse fix and the audit), the v2 render code (`*_v2.py`), and
`examples/lived_home_draft/`. Never edit a `code_frozen/` folder.
