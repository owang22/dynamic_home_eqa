#!/bin/bash
# Qwen3.8-27B with vision, smaller share (0.66) so Qwen3-VL-8B fits beside it; overnight 2026-10-23. Copy of serve_vlm.sh.
source /home/oliver/robot/dynamic_home_eqa/env.sh
export HF_HOME="$DYNAMIC_EQA_HF_HOME" HF_HUB_OFFLINE=1 VLLM_USE_FLASHINFER_SAMPLER=0
exec /home/oliver/miniconda3/envs/vllm_q/bin/vllm serve Qwen/Qwen3.8-27B \
  --host 127.0.0.1 --port 8300 --max-model-len 65536 \
  --gpu-memory-utilization 0.66 --max-num-seqs 8 \
  --limit-mm-per-prompt '{"image":16}' \
  --reasoning-parser qwen3 \
  --structured-outputs-config '{"backend":"xgrammar","disable_any_whitespace":true}'
