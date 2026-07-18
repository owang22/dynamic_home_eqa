# Moving dynamic_home_eqa to a new machine

All machine-specific configuration is in **one file: `.env`** (repo root,
gitignored, auto-loaded by `paths.py` at import — no manual `export` needed).
`.env.example` documents every variable. Shell scripts `source env.sh`.

## Steps

1. **Copy the repo** (and, if reusing them, the `logs/`, `reports/`,
   `generation_out_stage1c_v2/` data dirs — they're plain files, path-portable).

2. **Create `.env`** from the template and edit the two paths that always change:
   ```bash
   cp .env.example .env
   # edit HSSD_DIR and DYNAMIC_EQA_HF_HOME to the new machine's locations
   ```

3. **Verify config resolves:**
   ```bash
   python -c "from dynamic_home_eqa.paths import HSSD_DIR, MODEL_CACHE_DIR; print(HSSD_DIR, MODEL_CACHE_DIR)"
   ```

4. **OpenAI key** (for API-model experiments): either put it in `.env`
   (`OPENAI_API_KEY=sk-...`) or in the keyfile named by
   `DYNAMIC_EQA_OPENAI_KEYFILE` (default `~/.config/dynamic_eqa/openai_key`,
   mode 600). API experiments need NO GPU.

5. **Local Qwen serving** (for the open-weights tier): start the vLLM server.
   The serve recipe (flags tuned for the sm_120 GPU) is in
   `.claude`/memory `qwen36-serving-recipe`; the endpoint it exposes must match
   `GENERATION_ENDPOINT` in `.env`. On a different GPU arch, the
   `--moe-backend` / FlashInfer flags may differ — see serve_llm --help.

## What lives where (all env-overridable, defaults in `.env.example`)

| variable | what | changes per machine? |
|---|---|---|
| `HSSD_DIR` | HSSD scene dataset | **yes, always** |
| `DYNAMIC_EQA_HF_HOME` | HF model cache | **yes, always** |
| `GENERATION_ENDPOINT` | vLLM URL | if port/host differ |
| `GENERATION_MODEL` | local model id | if using another model |
| `DYNAMIC_EQA_GEN_PYTHON` | interpreter for subprocess gen | if different conda env |
| `OPENAI_API_KEY` / `DYNAMIC_EQA_OPENAI_KEYFILE` | frontier key | yes for API runs |
| `DYNAMIC_HOME_EQA_ROOT` | repo path | only if importing from outside the checkout |

## Gotcha carried over from this machine
Scratch run scripts live in `scratch_runs/` (in-repo, survives reboots) — NOT
`/tmp`, which gets wiped on reboot. New throwaway runners should follow that
and `source env.sh` for paths.
