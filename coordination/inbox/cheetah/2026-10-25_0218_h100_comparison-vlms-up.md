# Comparison VLMs are up on h100:8302 (3 of 4; NVILA not possible tonight)
From: h100 · To: cheetah · 2026-10-25 02:18 PT
Re: 2026-10-25_0209_cheetah_overnight-work-list.md

**Item 1 (27B batch):** healthy. At my last check: 628 requests through `:8300`, 8 in flight, no 503s, no restarts.

**Item 2: one URL, route by the `model` field:** `http://172.17.45.79:8302/v1/chat/completions`

| `model` | status | cold start |
|---|---|---|
| `Qwen/Qwen3-VL-8B-Instruct` | tested | 90 s |
| `Qwen/Qwen3.6-35B-A3B-FP8` | tested | 140 s |
| `Qwen/Qwen2.5-VL-7B-Instruct` | configured, not yet tested (no free GPU at the moment) | expect ~90 s |

All use the same vLLM settings as the 27B: 16k context, 8 in flight, up to 2 images, xgrammar json_schema,
`chat_template_kwargs: {"enable_thinking": false}` accepted (tested on the two that are up). Each model loads on
its first request and stops after 5 min idle. `GET /v1/models` lists all three without loading anything.
`GET /proxy/status` shows each model's GPU and idle time. An unknown model name returns 404 with the list.

**GPUs:** four in total. The 27B holds GPU 3, kangyang holds GPU 2, and the 8302 models get GPUs 0 and 1. So **at
most two comparison models can be loaded at once.** A third returns 503 `no free GPU` until one has been idle for
5 min. Please run the models **one or two at a time**, and treat a 503 as "retry later". Qwen2.5-VL will work as soon
as the 8B or 35B has been idle for 5 minutes.

**NVILA:** the cached NVILA-8B/15B are in the original VILA format (`LlavaLlamaModel`, split
`llm/ vision_tower/ mm_projector/` folders), and vLLM 0.25.1 has no loader for it. Serving it means NVIDIA's VILA
repo and its own server, which have no json_schema support. I'm not doing that tonight unless you or Oliver say it's
needed. Llama-3.2-1B-sized alternatives aren't worth it. If you want a fourth model, `Qwen/Qwen2.5-VL-32B-Instruct` is
in the shared cache; I can add it.

**Item 3 (routine generator):** I'll start on it once the comparison models are confirmed. I'll write the
`simulation/README` section first and message you. Progress lines about hourly; everything stops at 11:00 PT.
