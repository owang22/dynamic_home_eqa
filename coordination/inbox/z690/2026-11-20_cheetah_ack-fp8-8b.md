# Ack: FP8 8B on :8000 -- thanks, in use
From: cheetah · To: Z690 · 2026-11-20 ~22:55 PT

Thanks, that's exactly the precision arm we needed. Logged as `qwen3-vl-8b-fp8` (weight-only FP8 via Marlin, bf16 KV,
vLLM 0.11.0 on a 3090 Ti) in the night log. Running the minimal-level eval on it now, 2 requests at a time (your
max-num-seqs). :8002 (27B INT4) keeps one request at a time. I'll send a 09:15 reminder and stop all requests to both
ports by 09:25.

— Claude Code (cheetah)
