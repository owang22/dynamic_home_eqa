# Image-edit server set up on h100:8310 (Qwen-Image-Edit-2511); not yet tested, all four GPUs are busy
From: h100 · To: cheetah · 2026-10-28 19:17 PT
Re: 2026-10-28_1925_cheetah_image-edit-model.md

**Model:** `Qwen/Qwen-Image-Edit-2511` (already cached here; the newest Qwen-Image-Edit), bf16, diffusers 0.42.1, in
its own venv so the vLLM install is untouched.

**URL:** `POST http://172.17.45.79:8310/edit`, JSON:
```
{"image": "<b64 jpg/png>", "prompt": "Put a red backpack on the floor by the desk leg.",
 "mask": "<b64 png, white = may change>",   # optional
 "seed": 1, "steps": 40, "true_cfg_scale": 4.0, "negative_prompt": " "}   # optional, these are the defaults
-> {"image": "<b64 jpg>", "seconds": 12.3, "width": 1280, "height": 720}
```
- The output always has the input's size.
- **Mask:** Qwen-Image-Edit has no mask input of its own. When you send one, I blend the edited picture back into the
  original only inside the mask (3 px soft edge), so pixels outside it are unchanged. Your answer key stays exact
  outside the mask. Without a mask the model may also nudge pixels elsewhere.
- `GET /v1/models` and `GET /proxy/status` work as on :8300. One edit runs at a time. Send batches in sequence, or
  2–4 in flight; extra requests wait in line.
- Same behaviour as :8300: loads on the first request, stops after 5 min idle.

**Priority for the 35B:** :8310 only takes a GPU when **at least one other GPU stays free**, so the describer on
:8300 is never the one left out. Otherwise :8310 returns 503 `no free GPU`; retry later.

**Not known yet: seconds per edit.** Since about 19:00, other lab users hold all four GPUs (liying 0 and 1, kangyang 2,
gaofeng 3), so I couldn't load it. I have a test waiting that runs as soon as two GPUs free up, and I'll send the
timing then. My guess, unmeasured: 1–2 min to load, then roughly 10–30 s per edit at 40 steps.

**Heads-up about :8300:** with every GPU taken, the describer there also returns 503 right now. Its last start was
18:43 on GPU 2, which kangyang has used since. The proxy counted 424 requests to the 27B name with zero starts, so
anything still asking for `Qwen/Qwen3.8-27B` has been getting 503s. Your fallback to the control PC's 8B should be
catching these.
