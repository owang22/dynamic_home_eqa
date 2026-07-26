#!/bin/bash
# Wait for the tau sweep to finish (marker line), then swap to DeepSeek and run
# the two scaffold arms on the TYPICAL bank.
set -u
cd "$(dirname "$0")/.."
PY=/home/nesl/anaconda3/envs/fine-eqa/bin/python
until grep -q "TAU_SWEEP_COMPLETE" scratch_runs/tau_sweep.log 2>/dev/null; do sleep 60; done
echo "=== [$(date +%H:%M)] tau sweep done; serving DeepSeek ==="
if bash scratch_runs/serve_model.sh "deepseek-ai/DeepSeek-V4-Flash" --kv-cache-dtype fp8 --moe-backend triton_unfused; then
  $PY -m dynbelief.two_capacities.run2 --bank typ --arm llm_scaffold --tag frozen_typ
  $PY -m dynbelief.two_capacities.run2 --bank typ --arm scaffold_fusion --tau 0.45 --tag frozen_typ
else
  echo "DEEPSEEK SERVE FAILED"
fi
echo TYP_DEEPSEEK_COMPLETE
