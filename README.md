# dynamic_home_eqa

Dynamic Home EQA: LLM-generated household object dynamics on HSSD scenes,
plus embodied resense-policy experiments over the generated worlds.

## Layout

```
dynamic_home_eqa/      the Python package (install with pip install -e .)
  generation/          LLM day-trace generation (persona, activities, displacements)
  env/                 scene state, deltas, replay, inventory
  qa/                  question generation from manifests
  embodied/            embodied agent: world, sensing, belief, policies, runner
  llm_prior/           LLM prior elicitation + FM decision policy
  webapp/realism_eval/ FastAPI human-rating webapp
  scripts/             all CLI entry points (python -m dynamic_home_eqa.scripts.<name>)
  paths.py             single source of truth for every repo/data/output path
tests/                 pytest suite
data/                  pipeline inputs and per-scene caches (admission maps, census,
                       realized days, external prop assets)
generation_out/        generated day traces (the scene pool)
embodied_results/      milestone/experiment result JSONs
results/               reports (results/reports/, indexed by INDEX.md), figures,
                       run outputs (diagnostics/, e0/, e1e4/, realism_eval/)
archive/               superseded outputs, untracked (see .gitignore)
```

## Setup

1. Build the `dynamic_eqa` conda env (see **Environment** below).
2. Install this package into it (no dependency resolution — deps come from the env):

```bash
/path/to/miniconda3/envs/dynamic_eqa/bin/pip install -e . --no-deps
```

After that, every script runs from any working directory.

## Running the pipeline

Fast single-scene smoke test of all four stages:

```bash
./run_pipeline.sh                         # default scene/profile
./run_pipeline.sh 102344022 single_retiree
```

| stage | script | reads | writes |
|---|---|---|---|
| 1. anchor admission map | `scripts/compute_anchor_admission_map.py` | HSSD scene files | `data/anchor_admission_maps/<scene>.json` |
| 2. generate day trace | `scripts/gen_dataset.py` | stage 1's cache (fails open if absent) | `generation_out/<scene>_<profile>/` |
| 3. realized-world artifact | `scripts/build_realized_day.py` | stage 2's output | `data/realized_days/<folder>.realized_day.json` |
| 4. render eval media | `scripts/realism_render_job.py` | stage 3's artifact | `results/reports/realism_eval_media/` |

For real batch runs invoke the stage scripts directly
(`python -m dynamic_home_eqa.scripts.gen_dataset --scenes ... --n ...`);
`run_pipeline.sh` is a smoke-test convenience. Scene-pool expansion
(reachability pre-flight + multi-day generation + qualification) is
`python -m dynamic_home_eqa.scripts.expand_scene_pool`.

Regression check after any change to stages 3/4:

```bash
python -m dynamic_home_eqa.scripts.gold_set     # fixed 8-item render regression set
```

Serve the rating webapp (the app defines no `__main__`; launch through uvicorn):

```bash
python -m uvicorn dynamic_home_eqa.webapp.realism_eval.app:app --host 127.0.0.1 --port 8000
```

It binds to loopback only by design; from another machine, forward the port
(`ssh -L 8000:localhost:8000 <this-machine>`). It reads stage 4's
`render_manifest.json` and auto-creates its SQLite DB
(`results/realism_eval/realism_eval.db`) on first request.

## Tests

```bash
python -m pytest tests/
```

Tests that need habitat-sim/habitat-lab/GPU skip themselves when the
dependency is missing.

## Environment

Everything runs in one conda env, `dynamic_eqa`. Constraints that shape it:

- `python=3.9` — the newest Python with prebuilt `habitat-sim` conda binaries.
- `vllm==0.10.2` — the newest vllm that is 3.9-compatible; also pulls
  `torch==2.8.0+cu128`, required for sm_120 (RTX PRO 6000 Blackwell) GPUs.
- `numpy==1.26.4`, `opencv-python-headless<5`, `pillow==10.4.0` — hard
  requirements of habitat-sim/habitat-lab's compiled extensions. **Any later
  `pip install`/`conda install` can silently bump these; re-pin all three
  whenever a package is (re)installed.** This is the most common way the env
  breaks (`import habitat_sim` fails with `_ARRAY_API not found`).

Build recipe:

```bash
conda create -n dynamic_eqa -c aihabitat -c conda-forge python=3.9 habitat-sim=0.3.3 headless bullet -y
# the "headless bullet" spec can silently resolve to headless_nobullet; force it:
conda install -n dynamic_eqa -c aihabitat -c conda-forge "habitat-sim-mutex=1.0=headless_bullet" "habitat-sim=0.3.3" --force-reinstall -y
PIP=/path/to/miniconda3/envs/dynamic_eqa/bin/pip
(cd /path/to/habitat-lab/habitat-lab && $PIP install -e .)
$PIP install "pillow==10.4.0"
$PIP install "vllm==0.10.2"
$PIP install "numpy==1.26.4" "opencv-python-headless<5" "pillow==10.4.0"   # re-pin after vllm
$PIP install matplotlib "scikit-learn==1.6.1" "pandas==2.3.3" pytest objaverse trimesh
$PIP install -e /path/to/dynamic_home_eqa --no-deps
```

Note `vllm==0.10.2`'s API: `generation/llm_client.py` uses
`GuidedDecodingParams`/`SamplingParams(guided_decoding=...)`, not the
`StructuredOutputsParams` rename from later vllm versions.

## External inputs and env vars

| var | default | meaning |
|---|---|---|
| `HSSD_DIR` | `/mnt/nvme/oliver/robot/datasets/moving-eqa/scene_datasets/hssd-hab` | HSSD scene dataset root |
| `GENERATION_MODEL` | `Qwen/Qwen3-32B` | generation-stage vLLM model (standard HF cache) |
| `DYNAMIC_EQA_HF_HOME` | `/mnt/nvme/oliver/robot/models` | HF_HOME for llm_prior / serve_llm large models |
| `DYNAMIC_EQA_GEN_PYTHON` | this interpreter | interpreter for expand_scene_pool's generation subprocess |
| `DYNAMIC_HOME_EQA_ROOT` | repo checkout | override where data/output dirs are resolved |
| `REALISM_MEDIA_DIR`, `REALISM_DATA_DIR` | see `webapp/realism_eval/app.py` | webapp media/DB locations |

All other paths resolve through `dynamic_home_eqa/paths.py`, anchored at the
repo checkout — output lands in the repo regardless of working directory.

## Documentation map

- `generation/README.md` — generation-stage design (what's LLM-sampled vs
  seeded-deterministic, reproducibility contract, trace-integrity invariants).
- `results/reports/INDEX.md` — index of all experiment reports and findings,
  reverse-chronological, including what supersedes what.
