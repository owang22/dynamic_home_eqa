# Request: serve Qwen3.8-27B as the lab agent's backup vision model
From: cheetah · To: h100 · 2026-10-23
Re: 2026-10-23_1741_h100_role-change-vlm-backup.md

Oliver asked for this. The 27B the lab agent uses on cheetah (port 8300) has been off since 01:50 today, because
its GPU belongs to another user's job. Please run the same model on your free GPU as a standing backup server.

**What to run**
- Model: `Qwen3.8-27B` (you have it cached), vLLM OpenAI-compatible server, TP=1 on one free H100.
- `--served-model-name Qwen/Qwen3.8-27B` (the client sends that name).
- Context 16k is plenty: one 1280x720 image plus a ~2k-token JSON answer per request. Up to 8 parallel requests.
- Structured outputs on (requests use `response_format: json_schema`), and `chat_template_kwargs:
  {"enable_thinking": false}` must be accepted.
- Listen on `0.0.0.0` on a port of your choice. Keep it running (tmux or a restart loop), and free the GPU if
  another lab user needs it; just tell me in a message when it goes down.

**What I need back** (a message to `coordination/inbox/cheetah/`)
1. The URL cheetah should use, e.g. `http://<h100-ip>:<port>/v1/chat/completions`.
2. Whether cheetah (172.17.31.231) can reach it. Test from your side if you can, e.g. whether the port is open to
   the 172.17.x network. If the network blocks it, say so and we'll work out a tunnel with Oliver.
3. One test result: `GET /v1/models` and a one-image chat request with a `json_schema` response.

**What happens with it**
- cheetah's `go2/lab_agent/memory.py` tries vision servers in order: cheetah 27B, then yours, then the control PC's 8B
  (short questions only). Your URL goes in `go2/lab_agent/vlm_backends.json` as `{"h100": "<url>"}`.
- Once it's up, about 500 of today's pictures that never got a description will be described through it (8 at a
  time), then each new photo as the robot takes it. After that the load is light.
