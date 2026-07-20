# dynamic_home_eqa

Dynamic Home EQA. **v2 (current): a profile-driven SYMBOLIC household simulator** —
a provenance-tagged YAML profile (who lives here + weekly routine) deterministically
generates receptacle-level object-movement logs, which feed belief-model and
LLM-routine-knowledge experiments. No Habitat, no scene render, no LLM in the data
loop. See **Profile system** below.

The original **HSSD-scene LLM generation** pipeline (Habitat + HSSD) is **legacy**,
superseded as the data source by the profile simulator. Its scene-generation,
QA, embodied-agent, and webapp code + generated data + tests were moved to
`archive/hssd_generation/` (on disk, out of git — see its README to restore).
Retained in-tree: `src/dynamic_home_eqa/generation/` (shared scene-region +
LLM-HTTP-client utilities that the kept dynbelief replay/topdown code and the E1
Qwen client import), plus `paths.py`/`rooms.py`/`topdown_map.py`. Findings live in
`reports/`.

## Layout

```
.env / .env.example    machine config (paths, endpoints, keys) — SINGLE source; see TRANSFER.md
env.sh                 source in shell scripts to export the same config
src/dynbelief/         belief-model + LLM-agent research package (the active work)
  profiles/            v2 profile system: schema+validator (V1–V5), 4 transforms,
                       symbolic generator, bank builder (profiles -> frozen banks)
  anchors/             anchor-dataset acquisition + profile checks V6a–e (envelope.yaml,
                       validate_profile.py, mapping tables, literature_constants)
  beliefs/             belief zoo b0/b1/b2/b2.5-betabayes/b3-Perpetua*
  replay/, eqa/        ReplayWorld (reads profile OR HSSD episodes), MCQ probe, answerer
  active/              active displacement probe (VoI sense-or-answer, day budget)
  llm_agent/           LLM-as-agent clients (local Qwen + API) + earlier HSSD experiments
  experiments/         e1 (routine-knowledge forecasting) + legacy stage runners
profiles/manual/       VERIFIED profile YAMLs (single_adult, college_roommates, family4)
banks/                 frozen episode banks (typ_v1/atyp_v1/atyp_shift_v1) — gitignored,
                       regenerable from profiles+seed; each dir has a hash manifest
src/dynamic_home_eqa/  LEGACY HSSD generation package + shared infra (paths.py, rooms.py)
  generation/ qa/ embodied/ webapp/   HSSD scene pipeline (legacy; see note above)
  paths.py             single source of truth for every repo/data/output path (+ .env loader)
tests/                 pytest suite (profile validators + belief/replay + legacy HSSD)
data/anchors/          raw anchor data + third_party/ clones — gitignored (hard rule)
reports/               dynbelief + llm_agent experiment reports and raw artifacts
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

## Profile system (v2 — the current data source)

A profile is a provenance-tagged YAML in `profiles/manual/` (schema:
`dynbelief/profiles/schema.py`). Values carry anchor tags `[ATUS] [BEHAV]
[HOMER] [HKEEP] [DESIGN]`; a human verifies them and flips `status: DRAFT ->
VERIFIED` once `validate_profile.py` reports no FAIL. **Atypical profiles are
never hand- or model-authored** — they are produced only by the registered
transforms (`phase_shift`, `block_permutation`, `role_reassignment`,
`compression`) in `dynbelief/profiles/transforms.py`.

### 1. Anchors (once per machine / when mappings change)

```bash
python -m dynbelief.anchors.fetch_all          # clone HOMER+/BDDL/Housekeep/PARSEC
                                               # ATUS -> NEEDS_DATA (bls.gov blocked);
                                               # follow the printed instructions to place zips
python -m dynbelief.anchors.compile_envelope   # raw anchors -> src/dynbelief/anchors/envelope.yaml
```

`envelope.yaml` and the mapping tables (`*_map.yaml`, `literature_constants.yaml`)
are committed; `data/anchors/` + `third_party/` clones are gitignored.

### 2. Validate a profile (runs V1–V5 + V6a–e; writes anchor_report.md)

```bash
python -m dynbelief.anchors.validate_profile profiles/manual/single_adult_typ_v1.yaml
# exit 0 = no FAIL (may WARN / NEEDS_DATA). Only FAIL blocks a VERIFIED flip.
```

### 3. Freeze the episode banks (A2–A4)

```bash
python -m dynbelief.profiles.bank --bank all              # typ_v1, atyp_v1, atyp_shift_v1
python -m dynbelief.profiles.bank --bank typ_v1 --allow-draft --days 6 --targets 12 \
       --banks-root /tmp/dev_banks                        # dev/throwaway (DRAFT ok, non-reportable)
```

Each bank freezes 3 households × 30 days × 4 queries/day (budget 3), 20 targets
stratified into volatility terciles with 5 class-disjoint held-out objects, plus
ground-truth + `class_hazards` tables and a hash `manifest.json`. The builder
calls `validate_profile` and refuses DRAFT / anchor-FAIL profiles unless
`--allow-draft` (which stamps the manifest `non_reportable`). Banks are
gitignored and regenerable; the manifest pins provenance.

### 4. Experiments (E1 routine-knowledge forecasting; E2–E4 to come)

```bash
python -m dynbelief.experiments.e1 --client mock   # offline plumbing (last-seen baseline)
python -m dynbelief.experiments.e1 --client qwen \
       --endpoint http://127.0.0.1:8300                    # real run (needs the vLLM endpoint / GPU)
```

E1 sweeps {typ_v1, atyp_v1} × history-days {0,1,3,7,14} × {history-only,
history+profile-prose}, plus the `atyp_shift_v1` C4 control, and reports
accuracy-vs-history / ECE / moved-only / held-out slices to `reports/e1/`.

## LEGACY HSSD pipeline (archived)

The four-stage HSSD scene pipeline (anchor admission map -> LLM day-trace
generation -> realized-world artifact -> render eval), the embodied-agent
experiments, and the realism-rating webapp were moved to
`archive/hssd_generation/` (source under `src/`, generated data under `data/`,
their tests and scripts). They are on disk but out of git. To resurrect any of
it, `git mv` the pieces back and re-add — see
`archive/hssd_generation/README.md`. The shared scene-region + LLM-HTTP-client
utilities those stages used still live in `src/dynamic_home_eqa/generation/`.

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

The belief-model and LLM studies run **replay-only** over episode directories, so
most need no GPU. The current substrate is the profile banks (`banks/<name>/`,
built above); `ReplayWorld` reads them exactly as it read the legacy HSSD logs.

```bash
# profile-world experiments (v2)
python -m dynbelief.experiments.e1 --client mock     # routine-knowledge forecasting

# legacy HSSD-logged experiments (replay over logs/<episode>/)
python -m dynbelief.experiments.stage1c        # belief-model probe gate
python -m dynbelief.experiments.active_probe    # VoI sense-or-answer
python -m dynbelief.experiments.day_budget      # shared daily sensing budget
```

The belief zoo (`dynbelief/beliefs/`) now includes **b2.5 (`b25_betabayes`)**, a
Beta-Bayesian per-edge model between b2's class-decay and b3's periodic prior.
LLM clients (`dynbelief/llm_agent/clients.py`) cover local Qwen (vLLM endpoint)
and the frontier API axis (`OPENAI_API_KEY`); per the current experiment plan the
profile runs are **local-Qwen only**. Reports land in `reports/` (e.g.
`reports/e1/`, `reports/llm_agent/PRELIM.md`).

Run the profile/belief tests directly:

```bash
python -m pytest tests/test_profile_validators.py -q   # validators, transforms, generator, bank, b2.5
```

## Documentation map

- `generation/README.md` — generation-stage design (what's LLM-sampled vs
  seeded-deterministic, reproducibility contract, trace-integrity invariants).
- `results/reports/INDEX.md` — index of all generation-side reports/findings,
  reverse-chronological, including what supersedes what.
- `TRANSFER.md` — moving the code to a new machine (the `.env` checklist).
- `reports/*/SUMMARY.md` — dynbelief/LLM-agent experiment write-ups.
