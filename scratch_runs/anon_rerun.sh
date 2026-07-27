#!/bin/bash
# Re-run the anonymization confirmatory (h2/confirm.py) on DeepSeek with the
# llm_anon SCORING FIX. Waits for the tau sweep + the queued DeepSeek typical
# runs to release the GPUs, and reuses whatever DeepSeek server they leave up.
set -u
cd "$(dirname "$0")/.."
PY=/home/nesl/anaconda3/envs/fine-eqa/bin/python
until grep -q "TAU_SWEEP_COMPLETE" scratch_runs/tau_sweep.log 2>/dev/null; do sleep 60; done
until grep -q "TYP_DEEPSEEK_COMPLETE" scratch_runs/typ_deepseek.log 2>/dev/null; do sleep 60; done
# the typ script leaves DeepSeek serving; verify, else bring it up
if ! curl -s -m 5 http://127.0.0.1:8400/v1/models 2>/dev/null | grep -q DeepSeek; then
  bash scratch_runs/serve_model.sh "deepseek-ai/DeepSeek-V4-Flash" \
       --kv-cache-dtype fp8 --moe-backend triton_unfused || { echo "SERVE FAILED"; exit 1; }
fi
echo "=== [$(date +%H:%M)] anonymization re-run (DeepSeek, scoring fixed) ==="
$PY -m dynbelief.h2.confirm --label deepseek-anonfix
echo ANON_RERUN_COMPLETE
