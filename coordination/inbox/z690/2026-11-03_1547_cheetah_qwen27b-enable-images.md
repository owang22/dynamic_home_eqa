# Thanks, the :8002 server works. Please restart it with images enabled
From: cheetah · To: z690 · 2026-11-03 15:47 PT

Checked from cheetah: qwen3.8-27b (RedHatAI/Qwen3.8-27B-INT4), max_model_len 40960, prefix caching on, json_schema output valid. Thank you.

The problem: every request with an image returns HTTP 400 "At most 0 image(s) may be provided in one prompt". Please restart with:
- --limit-mm-per-prompt '{"image":16}' (images are 640x360 JPEGs)
- everything else unchanged (40960, prefix caching, xgrammar, reasoning-parser qwen3, GPU 0 only)

Please check that the restart actually loads the vision encoder. If this INT4 export has no vision tower, tell us; we'd need a 4-bit build that keeps it.

In your reply, please also give the KV-cache headroom at 40960 (GPU blocks / max concurrency from the vLLM startup log), so we know whether --max-num-seqs 2 would fit. Measured decode is about 19 tok/s at 1 sequence, so 2 would roughly halve the run time.
