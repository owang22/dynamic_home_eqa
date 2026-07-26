#!/bin/bash
# serve_model.sh <hf_model_id> [extra vllm args...]
# Swaps the vLLM server on port 8400 to a new model and waits until it answers.
MODEL="$1"; shift
# Kill the parent AND the multiproc WORKERS. Workers do not carry "vllm serve" in
# their command line, so pkill alone leaves them holding ~90GB/GPU and the next
# model fails with "Free memory on device cuda:N (3.9/93.1 GiB)". Kill whatever
# actually holds GPU memory, then wait for the driver to release it.
pkill -9 -f "vllm serve" 2>/dev/null
pkill -9 -f "VLLM::EngineCore" 2>/dev/null
for gp in $(nvidia-smi --query-compute-apps=pid --format=csv,noheader); do kill -9 "$gp" 2>/dev/null; done
for i in $(seq 1 24); do
  USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | sort -rn | head -1)
  [ "$USED" -lt 2000 ] && break
  sleep 5
done
echo "GPUs freed (max used: $(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | sort -rn | head -1) MiB)"
CUDA_VISIBLE_DEVICES=0,1,2,3 HF_HOME=/data/oliver/huggingface_cache setsid \
  /data/oliver/venvs/vllm-v4-cu129/bin/vllm serve "$MODEL" \
  --host 127.0.0.1 --port 8400 --tensor-parallel-size 4 --max-model-len 32768 \
  --gpu-memory-utilization 0.90 "$@" \
  > scratch_runs/vllm_$(echo "$MODEL" | tr '/' '_').log 2>&1 < /dev/null &
disown
LOG=scratch_runs/vllm_$(echo "$MODEL" | tr '/' '_').log
for i in $(seq 1 240); do
  if curl -s -m 3 http://127.0.0.1:8400/v1/models 2>/dev/null | grep -q "$(basename $MODEL)"; then
    echo "SERVER READY: $MODEL"; exit 0; fi
  if grep -qiE "Engine core initialization failed|No supported|ValueError|AssertionError|illegal memory access" "$LOG" 2>/dev/null; then
    echo "SERVER FAILED: $MODEL"; grep -iE "Error|assert|not support" "$LOG" | tail -3; exit 1; fi
  sleep 15
done
echo "SERVER TIMEOUT: $MODEL"; exit 1
