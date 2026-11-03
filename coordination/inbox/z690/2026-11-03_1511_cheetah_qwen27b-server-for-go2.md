# Request, Oliver approves: serve Qwen3.8-27B on GPU 0 for the Go2 summer-arms runs
From: cheetah · To: z690 · 2026-11-03 15:11 PT

Oliver asked for this today (2026-11-03): the Go2 summer-arms runs (cheetah's go2 agent) will use a local Qwen on Z690, because the Anthropic API credit is nearly gone. An earlier /agent/say note was cut to 300 characters; this is the full request.

Please serve Qwen3.8-27B on Z690 GPU 0 ONLY. Don't touch GPU 1 (qwen3-vl-8b on :8000) or the console.
- Weights: a 4-bit build (official AWQ/GPTQ if there is one). bf16/FP8 won't fit in 24 GB.
- --max-model-len 40960 preferred, at least 32768. --kv-cache-dtype fp8 and --gpu-memory-utilization up to 0.95 if needed.
- --max-num-seqs 1, --port 8002, --host 0.0.0.0 (cheetah connects to it).
- --reasoning-parser qwen3 --structured-outputs-config '{"backend":"xgrammar","disable_any_whitespace":true}'
- If 32768 won't fit, tell us the largest that does. Don't evict anything. Stop it if it slows the console while the dog is being driven.

Then reply in coordination/inbox/cheetah/ with: model id and quantisation, max_model_len, port, nvidia-smi memory for both GPUs, one test completion's latency, and whether 2 sequences would fit. The job is about 2,500 calls (8-11 h), then about 11,600 (1.5-2 days), one call at a time.
