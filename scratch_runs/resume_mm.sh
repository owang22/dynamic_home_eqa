#!/bin/bash
# Resume: Qwen server is already up -> finish qwen scaffold_fusion, then GLM both arms.
set -u
cd "$(dirname "$0")/.."
PY=/home/nesl/anaconda3/envs/fine-eqa/bin/python
TAU=0.45

if [ ! -f reports/answer_or_resense/rows_scaffold_fusion_conf_frozen_qwen36.jsonl ]; then
  echo "=== [$(date +%H:%M)] qwen36 : scaffold_fusion (server already up) ==="
  $PY -m dynbelief.two_capacities.run2 --bank conf --arm scaffold_fusion --tau $TAU \
      --model "Qwen/Qwen3.6-35B-A3B-FP8" --tag frozen_qwen36 || echo "FAIL qwen scaffold_fusion"
fi

echo "=== [$(date +%H:%M)] serving GLM ==="
if bash scratch_runs/serve_model.sh "zai-org/GLM-4.5-Air" --moe-backend triton --enforce-eager; then
  for ARM in llm_scaffold scaffold_fusion; do
    echo "=== [$(date +%H:%M)] glm : $ARM ==="
    if [ "$ARM" = "scaffold_fusion" ]; then
      $PY -m dynbelief.two_capacities.run2 --bank conf --arm $ARM --tau $TAU \
          --model "zai-org/GLM-4.5-Air" --tag frozen_glm || echo "FAIL glm $ARM"
    else
      $PY -m dynbelief.two_capacities.run2 --bank conf --arm $ARM \
          --model "zai-org/GLM-4.5-Air" --tag frozen_glm || echo "FAIL glm $ARM"
    fi
  done
else
  echo "SKIP glm (serve failed)"
fi
echo RESUME_COMPLETE
