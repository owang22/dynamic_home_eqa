#!/bin/bash
# vLLM server for the LLM arms (Qwen3.6-35B-A3B, the GENERATION_MODEL in .env).
# vllm_q env (vLLM 0.25, torch cu130). The default MoE backend on this GPU
# (sm_120) is FlashInfer's JIT-compiled CUTLASS MoE, which needs nvcc >= 12.9
# and this machine has 11.4; the Triton MoE kernels need no JIT.
source "$(dirname "$0")/../../env.sh"
export HF_HOME="$DYNAMIC_EQA_HF_HOME" HF_HUB_OFFLINE=1 VLLM_USE_FLASHINFER_SAMPLER=0
exec /home/oliver/miniconda3/envs/vllm_q/bin/vllm serve Qwen/Qwen3.6-35B-A3B \
  --host 127.0.0.1 --port 8300 --max-model-len 32768 \
  --gpu-memory-utilization 0.90 --max-num-seqs 32 \
  --reasoning-parser qwen3 \
  --kernel-config '{"moe_backend":"triton"}' \
  --structured-outputs-config '{"backend":"xgrammar","disable_any_whitespace":true}'
