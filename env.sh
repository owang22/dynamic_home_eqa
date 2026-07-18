#!/bin/bash
# Source this in shell / run scripts: `source env.sh`. Exports every var from
# .env so bash tools (serve_llm, gen_dataset launchers) see the same config
# Python does. Also derives PY (the project interpreter) for scripts.
_here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$_here/.env" ]; then
  set -a; . "$_here/.env"; set +a
fi
export HSSD_DIR DYNAMIC_EQA_HF_HOME GENERATION_ENDPOINT GENERATION_MODEL
PY="${DYNAMIC_EQA_GEN_PYTHON:-python3}"
export PY
