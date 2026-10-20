#!/bin/bash
# Qwen3.8-27B on vLLM for the lab-routine simulation: text only, FP8 weights (an FP8 KV cache fails here: FlashInfer sm75 check).
source /home/oliver/robot/dynamic_home_eqa/env.sh
export HF_HOME="$DYNAMIC_EQA_HF_HOME" HF_HUB_OFFLINE=1 VLLM_USE_FLASHINFER_SAMPLER=0
exec /home/oliver/miniconda3/envs/vllm_q/bin/vllm serve Qwen/Qwen3.8-27B \
  --host 127.0.0.1 --port 8300 --max-model-len 65536 \
  --gpu-memory-utilization 0.90 --max-num-seqs 48 --quantization fp8 \
  --limit-mm-per-prompt '{"image":0}' \
  --reasoning-parser qwen3 \
  --structured-outputs-config '{"backend":"xgrammar","disable_any_whitespace":true}'
