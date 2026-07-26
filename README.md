# dynamic_home_eqa

Dynamic Home EQA. **v2 (current): a profile-driven SYMBOLIC household simulator** —
a provenance-tagged YAML profile (who lives here + weekly routine) deterministically
generates receptacle-level object-movement logs, which feed belief-model and
LLM-routine-knowledge experiments. No Habitat, no scene render, no LLM in the data
loop. See **Profile system** below.

The original **HSSD-scene LLM generation** pipeline (Habitat + HSSD) is **legacy**,
superseded as the data source by the profile simulator. Its scene-generation,
QA, embodied-agent, and webapp code + generated data + tests were archived out of
the working tree (the `archive/` directory is not present in this checkout).
Legacy scene manifests remain under `generation_legacy/` (212 manifests / 23
unique scenes) for reference only — no current result depends on them.
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
  classical/           the FROZEN classical opponent: C3g held-out-gated periodic GLM
                       (rates/c3g_gated.py) + the shared _belief/make_arm prediction path
  beliefs/             belief zoo b0/b1/b2/b2.5-betabayes/b3-Perpetua*
  replay/, eqa/        ReplayWorld (reads profile OR HSSD episodes), MCQ probe, answerer
  h2/                  regime-adaptation studies (E5/E7, confirmatory bank, anonymization)
  reflect/             PASSIVE line: nightly reflective memory (memory.py), surprise-gated
                       reflection (surprise.py), offline fusion + tables (report.py),
                       VERSION22 bank defs (v22.py), distractor sweep, figures
  reflect_dag/         ADDITIVE variant: activity V-structure under the persona,
                       CounterfactCoT do-contrast, Tier-1/2/3 precision fusion
  answer_or_resense/   ACTIVE line: scarce-sensing loop (env.py), arms (classical /
                       llm / hybrid / oracle), dev sweeps, report
  two_capacities/      confidence-vs-integration diagnostics + the scaffolded LLM arms
                       (scaffold_arm.py: LLMScaffold, ScaffoldFusion) and figures
  active/              active displacement probe (VoI sense-or-answer, day budget)
  llm_agent/           LLM-as-agent clients (local + API) + earlier HSSD experiments
  experiments/         e1 (routine-knowledge forecasting) + legacy stage runners
profiles/manual/       45 profile YAMLs: the 3 original typical bases, the regime_* set,
                       16 VERSION22 idiosyncratic personas (v22_*, v22dev_*), and 6
                       conventional-placement typicals (typ_*)
banks/                 frozen episode banks — gitignored, regenerable from profiles+seed:
                       legacy typ_v1/atyp_*; CURRENT version22 (12 atypical hh),
                       version22b (6 confusable personas x 2 seeds = 12), version22_typ
                       (6 typical hh), version22_dev (4 hh, DEV — all sweeps)
src/dynamic_home_eqa/  LEGACY HSSD generation package + shared infra (paths.py, rooms.py)
  generation/ qa/ embodied/ webapp/   HSSD scene pipeline (legacy; see note above)
  paths.py             single source of truth for every repo/data/output path (+ .env loader)
tests/                 pytest suite (profile validators + belief/replay + legacy HSSD)
data/anchors/          raw anchor data + third_party/ clones — gitignored (hard rule)
reports/               dynbelief + llm_agent experiment reports and raw artifacts
scratch_runs/          in-repo throwaway run scripts (NOT /tmp — survives reboots)
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
an out-of-tree archive (source under `src/`, generated data under `data/`,
their tests and scripts). They are on disk but out of git. To resurrect any of
it, `git mv` the pieces back and re-add — see
that archive's own README. The shared scene-region + LLM-HTTP-client
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

## Research experiments (current)

Two experiment lines run on the VERSION22 banks. Both use the FROZEN classical
model C3g as the non-LLM opponent, and both keep a dev/test wall: every
hyperparameter (alpha*, tau, prompt variant) is chosen on `version22_dev` (4
households) and frozen before any confirmatory household is touched.

**Household banks.** `version22` (12) + `version22b` (12) = the 24 ATYPICAL
confirmatory households (idiosyncratic-but-realistic object uses: a mug holding
paintbrushes, a towel as a proofing couche, a remote stored out of toddler
reach). `version22_typ` (6) is the TYPICAL contrast class — same layout style and
object vocabulary, conventional placements, so a naive prior should be right.

### PASSIVE line (`dynbelief/reflect/`) — free ambient observation stream
The agent sees ~3 thinned observations/day of the whole home and answers queries
on a fixed FUTURE test week (days 14-20) at checkpoints D=1,2,3,5,7,10,14.

```bash
python -m dynbelief.reflect.run      --bank v22 --arms direct,nomem --obs-per-day rand3 --distractors 6
python -m dynbelief.reflect.surprise --bank v22 --obs-per-day rand3 --distractors 6
python -m dynbelief.reflect.report   --bank v22 --label <label> --obs-per-day rand3
python -m dynbelief.reflect.distractor_sweep     # accuracy vs distractor load
```
Arms: `llm_direct` (nightly reflection), `llm_nomem` (raw-digest ablation),
`llm_surprise` (reflect only when the classical model is contradicted),
`fusion` (offline alpha/(alpha+n) injection), `classical_C3g`, `classical_C1`.

**Distractor system.** `--distractors N` adds N/day sightings of STATIC objects
(a chair by a table, a pillow on a bed) that never move and are never queried —
they inflate observations/day without adding information.

**Phase policy (mandatory).** Learning curves are reported phase-averaged over
start weekday, or only at whole-week checkpoints (D=1,7,14). A fixed Monday
start produces a spurious day-5 peak / day-10 dip; see
`reports/reflect/HUMP_DIAGNOSIS.md`.

### ACTIVE line (`dynbelief/answer_or_resense/`, `dynbelief/two_capacities/`)
Scarce sensing: the agent starts with ZERO observations and per query must either
ANSWER (+1 correct / 0 wrong) or RESENSE (+0.4, consumes 1 of B=5 daily budget,
and reveals the true location — its ONLY way to learn). Q=10 queries/day x 14
days = 140 queries/household. Frozen params in
`reports/answer_or_resense/frozen_dev_params.json`.

```bash
# offline arms (no server)
python -m dynbelief.answer_or_resense.run_aor --bank conf --arm classical --tau 0.75 --Q 10 --B 5 --r 0.4 --wrong 0.0 --tag frozen
python -m dynbelief.answer_or_resense.run_aor --bank conf --arm oracle    --Q 10 --B 5 --r 0.4 --wrong 0.0 --tag frozen
# scaffolded LLM arms (vLLM server required)
python -m dynbelief.two_capacities.run2 --bank conf --arm llm_scaffold    --tag frozen
python -m dynbelief.two_capacities.run2 --bank conf --arm scaffold_fusion --tau 0.45 --tag frozen
# evaluation
python -m dynbelief.answer_or_resense.report_aor --bank conf --tag frozen --B 5 --Q 10
python -m dynbelief.two_capacities.diagnostics    # D1-D4 mechanism diagnostics
python -m dynbelief.two_capacities.figures        # F1-F6
```

**"The LLM" always means the best scaffolded implementation** (`llm_scaffold`:
nightly persona-memory reflection over self-gathered observations). Raw
observation-log arms exist only as explicitly-labelled ablations — an early
"LLM cannot integrate evidence" result turned out to be an artifact of removing
that scaffold.

### Models
Served locally with vLLM 0.25.1+cu129 (TP=4, 4x H100 NVL), seed=7, temperature=0,
guided JSON: `deepseek-ai/DeepSeek-V4-Flash` (`--kv-cache-dtype fp8 --moe-backend
triton_unfused`), `Qwen/Qwen3.6-35B-A3B-FP8` and `zai-org/GLM-4.5-Air`
(`--moe-backend triton --enforce-eager`). See `scratch_runs/serve_model.sh`.

Run the profile/belief tests directly:

```bash
python -m pytest tests/test_profile_validators.py -q   # validators, transforms, generator, bank, b2.5
python -m pytest tests/test_classical.py -q            # frozen classical model
```

## Documentation map

- `TRANSFER.md` — moving the code to a new machine (the `.env` checklist).
- `reports/two_capacities/SUMMARY.md` — **current headline**: active-sensing
  results, the scaffold control, the three-model replication.
- `reports/answer_or_resense/SUMMARY.md` — the scarce-sensing protocol, frozen
  parameters, P1–P4 verdicts, the KARL abstention-trap table.
- `reports/reflect/HUMP_DIAGNOSIS.md` — why learning curves must be
  phase-averaged (the Monday-start artifact).
- `reports/reflect_dag/SUMMARY.md` — activity-DAG variant (largely null; the
  CounterfactCoT calibration result is the positive part).
- `reports/h2_adaptation/SUMMARY.md` — regime adaptation + the named-vs-anonymized
  study (a NEGATIVE result: the pre-registered target was not met).
- `src/dynamic_home_eqa/generation/README.md`, `results/reports/INDEX.md` —
  LEGACY HSSD generation design + report index.
