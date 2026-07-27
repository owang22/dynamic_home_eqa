#!/bin/bash
# Passive reflective-memory run on the TYPICAL household bank (version22_typ),
# matched to the atypical v22 d0 protocol: obs rand3, distractors 0, alpha
# FROZEN at 8 (the v22dev value the atypical line used — no re-sweep).
set -u
cd "$(dirname "$0")/.."
PY=/home/nesl/anaconda3/envs/fine-eqa/bin/python
bash scratch_runs/serve_model.sh "deepseek-ai/DeepSeek-V4-Flash" \
    --kv-cache-dtype fp8 --moe-backend triton_unfused || { echo "SERVE FAIL"; exit 1; }
$PY -m dynbelief.reflect.run --endpoint http://127.0.0.1:8400 \
    --model deepseek-ai/DeepSeek-V4-Flash --label typd0 \
    --bank typ --arms direct,nomem --obs-per-day rand3 --distractors 0 \
    || { echo "RUN FAIL"; exit 1; }
$PY -m dynbelief.reflect.report --bank typ --label typd0 --alpha-max 8 \
    --obs-per-day rand3 > reports/reflect/report_typ_typd0.txt 2>&1 || echo "report step nonzero (all_rows may still be written)"
echo TYP_PASSIVE_COMPLETE
