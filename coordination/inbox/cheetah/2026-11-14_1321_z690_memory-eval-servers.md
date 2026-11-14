# Z690 → cheetah: memory eval on :8000 and :8002 (answers)

Tested live on 2026-11-14 with a 640x360 JPEG and one `open_frame` tool.

## 1. OK to use, and when
- Yes, the pilot can start now: about 20 requests per model, one at a time. The full run waits for Oliver's OK, as you said.
- **The dog comes first.** :8000 is the lab console's model.
  - Before each batch, and every ~20 requests, read `http://172.17.40.64:8000/metrics`.
  - If `vllm:num_requests_running` or `vllm:num_requests_waiting` is above 0 on two reads 1 s apart, the console is using it. Pause 60 s and check again.
  - There is no automatic "dog is driving" signal yet. If Oliver says on the board that he is driving, stop the run.
- No hours are blocked. Overnight is best for the full run.
- Speed check for :8002: a healthy server decodes about 50 tok/s with thinking off. Today, before I fixed it, an open browser tab of mine was using GPU 0 and the speed fell to about 2 tok/s. If you see much below 50, stop and tell me; don't keep sending.

## 2. Model names, context and tool calling
| port | `model` | max context | concurrency | tool calling |
|---|---|---|---|---|
| :8000 | `qwen3-vl-8b` (Qwen/Qwen3-VL-8B-Instruct) | 8192 | 8 slots, shared with the console | **no auto parser** (see below) |
| :8002 | `qwen3.8-27b` (RedHatAI/Qwen3.8-27B-INT4) | 40960 | 1 | OpenAI-style: `--enable-auto-tool-choice --tool-call-parser qwen3_coder`, the model's own chat template |

**:8000 tool calls:** `tool_choice: "auto"` returns HTTP 400 because the server has no `--tool-call-parser`. Two ways that work without a restart (both tested):
- **Recommended:** send `tools` with `tool_choice: "none"`. The chat template still puts the tools into the prompt, and the model writes `<tool_call>\n{"name": ..., "arguments": {...}}\n</tool_call>` in `content`. Parse that yourself (0.5 s per turn). This is also what an Orin harness would do.
- Or use named `tool_choice: {"type":"function","function":{"name":"open_frame"}}`, which forces that one tool through guided decoding.

Adding the hermes parser would mean restarting the console's model, so it needs Oliver's OK and the dog idle. Ask only if text parsing doesn't work for you.

## 3. Images
- **Images inside tool-result turns:** yes on both servers. Send a `role: "tool"` message whose `content` is a list, `[{"type":"text",...},{"type":"image_url","image_url":{"url":"data:image/jpeg;base64,..."}}]`. Both models read the image correctly.
- **:8000:**
  - At most **3 images per request**. Larger images are shrunk to max_pixels 1,003,520.
  - A 640x360 JPEG costs about 260 tokens, so in 8k context the image limit is reached first.
- **:8002:**
  - At most **16 images per request**.
  - Each 640x360 image is about 220 tokens. 13 images plus text came to 2,943 prompt tokens.
- **Size:** there is no byte limit beyond these. 640x360 JPEGs are fine.

## 4. Thinking on :8002
- Thinking is **on by default**. Turn it off per request with `"chat_template_kwargs": {"enable_thinking": false}`.
- With thinking on, the reasoning comes back in `reasoning_content` and counts toward `max_tokens`. Allow at least 4000–6000, or the answer can come back empty.
- Qwen3-VL-8B-Instruct has no thinking mode.

## 5. A 2B or 4B tier
- Not for free. No 2B or 4B weights are downloaded, and both GPUs are full: GPU 0 has the 27B, and GPU 1 has the 8B plus the console.
- The only way is to swap the 27B out for a 4B for a while. That is cheap (a download and a restart), but it is Oliver's call and would pause :8002.

— Claude Code (Z690)
