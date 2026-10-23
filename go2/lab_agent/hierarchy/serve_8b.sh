#!/bin/bash
# Qwen3-VL-8B-Instruct (official FP8) as the hierarchy's small model, beside the 27B on :8300 (2026-10-23).
# Run in tmux:  tmux new -d -s vlm8b bash go2/lab_agent/hierarchy/serve_8b.sh
# Flags follow evidence_memory/serve_vlm.sh (xgrammar structured outputs). No reasoning parser: Instruct, no thinking.
# MODEL=Qwen/Qwen3-VL-8B-Instruct for the bf16 weights (also in the cache; ~17 GB, needs util ~0.28).
export HF_HOME=/mnt/nvme/oliver/robot/models HF_HUB_OFFLINE=1 VLLM_USE_FLASHINFER_SAMPLER=0 VLLM_USE_DEEP_GEMM=0  # DeepGEMM JIT needs NVCC >= 12.3 (not here)
MODEL=${MODEL:-Qwen/Qwen3-VL-8B-Instruct-FP8}
/home/oliver/miniconda3/envs/vllm_q/bin/vllm serve "$MODEL" \
  --host 127.0.0.1 --port ${PORT:-8301} --max-model-len 32768 \
  --gpu-memory-utilization ${UTIL:-0.20} --max-num-seqs 8 \
  --limit-mm-per-prompt '{"image":8}' \
  --structured-outputs-config '{"backend":"xgrammar","disable_any_whitespace":true}' 2>&1 | tee -a /home/oliver/robot/dynamic_home_eqa/go2/lab_agent/hierarchy/logs/serve_8b.log
