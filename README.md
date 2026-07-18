# dynamic_home_eqa

Dynamic Home EQA: LLM-generated household object dynamics on HSSD scenes,
plus embodied resense-policy experiments over the generated worlds.

## Layout

```
.env / .env.example    machine config (paths, endpoints, keys) — SINGLE source; see TRANSFER.md
env.sh                 source in shell scripts to export the same config
src/dynamic_home_eqa/  the generation Python package (install with pip install -e .)
  generation/          LLM day-trace generation (persona, activities, displacements)
  env/                 scene state, deltas, replay, inventory
  qa/                  question generation from manifests
  embodied/            embodied agent: world, sensing, belief, policies, runner
  llm_prior/           LLM prior elicitation + FM decision policy
  webapp/realism_eval/ FastAPI human-rating webapp
  scripts/             all CLI entry points (python -m dynamic_home_eqa.scripts.<name>)
  paths.py             single source of truth for every repo/data/output path (+ .env loader)
src/dynbelief/         belief-model research package (Stage 0–2)
  beliefs/             belief zoo b0–b3 (last-seen, long-mem, class-decay, Perpetua*)
  replay/, eqa/        ReplayWorld, MCQ probe, symbolic answerer, analysis
  active/              active displacement probe (VoI sense-or-answer, day budget)
  llm_agent/           LLM-as-agent experiments (memory, ReAct-style decisions, clients)
  experiments/         stage runners (stage0/1/1b/1c, active_probe, day_budget)
tests/                 pytest suite
data/                  pipeline inputs and per-scene caches (admission maps, census,
                       realized days, external prop assets)
generation_out*/       generated day traces (scene pools; _stage1c_v2 = calendar+charter)
logs/                  logged episodes for dynbelief (registry + events + snapshots)
reports/               dynbelief + llm_agent experiment reports (stage1c/, active_probe/,
                       day_budget/, llm_agent/) and raw parquet/JSON artifacts
results/               generation-side reports (results/reports/, indexed by INDEX.md)
scratch_runs/          in-repo throwaway run scripts (NOT /tmp — survives reboots)
archive/               superseded outputs, untracked (see .gitignore)
```

## Setup

1. Build the `dynamic_eqa` conda env (see **Environment** below).
2. Install this package into it (no dependency resolution — deps come from the env):

```bash
/path/to/miniconda3/envs/dynamic_eqa/bin/pip install -e . --no-deps
```

3. **Configure this machine** — copy the template and edit the two paths that
   always differ (`HSSD_DIR`, `DYNAMIC_EQA_HF_HOME`):

```bash
cp .env.example .env    # then edit HSSD_DIR + DYNAMIC_EQA_HF_HOME
python -c "from dynamic_home_eqa.paths import HSSD_DIR, MODEL_CACHE_DIR; print(HSSD_DIR, MODEL_CACHE_DIR)"
```

`.env` is gitignored and **auto-loaded** by `paths.py` at import — no manual
`export` for Python. It is the single source of machine config; see
**External inputs and env vars** and `TRANSFER.md` for moving machines.
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

**All machine config lives in one gitignored `.env` at the repo root**
(template: `.env.example`, documented per-var). `paths.py` auto-loads it at
import (existing environment wins over the file); shell scripts `source env.sh`.
Only `HSSD_DIR` and `DYNAMIC_EQA_HF_HOME` reliably change between machines.

| var | default | meaning |
|---|---|---|
| `HSSD_DIR` | `/data/oliver/.../hssd-hab` | HSSD scene dataset root — **set per machine** |
| `DYNAMIC_EQA_HF_HOME` | `/data/oliver/huggingface_cache` | HF_HOME for large models — **set per machine** |
| `GENERATION_ENDPOINT` | `""` (in-process) | vLLM OpenAI-compatible URL (e.g. `http://127.0.0.1:8300`) |
| `GENERATION_MODEL` | `Qwen/Qwen3-32B` | local generation/served model id |
| `DYNAMIC_EQA_GEN_PYTHON` | this interpreter | interpreter for generation subprocesses |
| `OPENAI_API_KEY` | `""` | frontier-model key (llm_agent). API runs need **no GPU** |
| `DYNAMIC_EQA_OPENAI_KEYFILE` | `~/.config/dynamic_eqa/openai_key` | keyfile if not using the env var |
| `DYNAMIC_HOME_EQA_ROOT` | repo checkout | override where data/output dirs resolve |
| `REALISM_MEDIA_DIR`, `REALISM_DATA_DIR` | see `webapp/realism_eval/app.py` | webapp media/DB locations |

**Secrets never enter the repo:** the OpenAI key is read at runtime from
`OPENAI_API_KEY` or the external keyfile — never committed, never in `.env`
(which only points to the keyfile path). All other paths resolve through
`src/dynamic_home_eqa/paths.py`, anchored at the repo checkout, so output lands
in the repo regardless of working directory.

## Research experiments (dynbelief + LLM agents)

The belief-model and LLM-agent studies run **replay-only** over logged episodes
(`logs/<episode>/`), so most need no GPU:

```bash
# log an episode from generated day traces, then run a stage
python -m dynbelief.experiments.stage1c        # belief-model probe gate
python -m dynbelief.experiments.active_probe    # VoI sense-or-answer
python -m dynbelief.experiments.day_budget      # shared daily sensing budget
```

LLM-agent experiments (`src/dynbelief/llm_agent/`) compare local Qwen (via the
vLLM endpoint) against frontier API models (`clients.py`; `OPENAI_API_KEY`) on
a frozen episode bank. Reports and raw artifacts land in `reports/` (e.g.
`reports/llm_agent/PRELIM.md`, `reports/active_probe/SUMMARY.md`).

## Documentation map

- `generation/README.md` — generation-stage design (what's LLM-sampled vs
  seeded-deterministic, reproducibility contract, trace-integrity invariants).
- `results/reports/INDEX.md` — index of all generation-side reports/findings,
  reverse-chronological, including what supersedes what.
- `TRANSFER.md` — moving the code to a new machine (the `.env` checklist).
- `reports/*/SUMMARY.md` — dynbelief/LLM-agent experiment write-ups.
