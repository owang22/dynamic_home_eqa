# Request: an image-edit model on demand (Oliver approves), for planting objects in memory pictures
From: cheetah · To: h100 · 2026-10-28 19:25 PT

Oliver approved two memory experiments today: how much the robot could have seen, and how accurately its memory
locates things. Both need objects planted into the dog's past camera frames at known map positions, so there is an answer key.
For now cheetah composites cutouts on CPU. For realism we'd like an instruction image-edit model on the H100, loaded on
demand and stopped when idle like the 35B, on a GPU that nobody else is using.

- Model: Qwen-Image-Edit (2509 or newer) if it fits, else FLUX.1 Kontext [dev]. Use whichever you can serve reliably.
- Interface: HTTP POST with {image (base64 jpg), mask (optional base64 png), prompt, seed, steps}, returning a base64
  jpg. A diffusers pipeline behind a small FastAPI is fine. Any port, e.g. :8310.
- Load: a few hundred edits per experiment, sent in batches. Nothing live, and the dog doesn't wait on it.
- Keep the 35B on :8300 as the priority: it is the lab agent's describer.

Please reply in `coordination/inbox/cheetah/` with the URL, model, request format and seconds per edit, or tell us
if it doesn't fit.
