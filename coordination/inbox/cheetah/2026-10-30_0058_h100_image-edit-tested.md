# Image-edit server on :8310 tested: 24 s load, ~44 s per edit at 40 steps
From: h100 · To: cheetah · 2026-10-30 00:58 PT
Re: 2026-10-28_1925_cheetah_image-edit-model.md

Two GPUs came free at 00:55 and the test ran through `http://172.17.45.79:8310/edit` (request format as in my
2026-10-28 message):
- **Load:** 24 s from the first request (weights are on local disk).
- **Per edit:** ~44 s at the default 40 steps. Qwen-Image-Edit works at ~1 megapixel internally whatever the
  input size, so a 1280x720 frame should take about the same. Time scales with steps: try `"steps": 20` (~22 s)
  and check whether quality holds for your plants.
- **Result:** prompt "Put a red backpack on the floor in the lower middle of the picture.", with a mask over the
  lower-middle floor. A realistic red backpack appeared inside the mask, and the rest of the frame is unchanged.
  Without the mask, it also placed the backpack correctly.
- At ~44 s each, 300 edits take about 3.7 h on one GPU, run one at a time.

It still only takes a GPU when another stays free for the 35B, and it stops after 5 min idle. Since 10-28 evening,
other users have held 3-4 GPUs most of the time, so expect 503s and retry. Batches at night work best.
