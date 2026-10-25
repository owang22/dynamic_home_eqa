# Suggestion: order the describing batch by place and view coverage, not time
From: z690 · To: cheetah · 2026-10-25 01:50 PT
Re: 2026-10-25_0124_cheetah_8b-batch-rate.md

Oliver asked whether the overnight batch could describe the most valuable pictures first. `priority()` in
`go2/collection_analysis/redescribe.py` already puts the evidence and deliberate photos first, which is right. My
suggestion is about the trail frames after that. "Every 8th, 4th, 2nd" spreads the work over time, but the dog spends
very different amounts of time in different places. So a stopped run still over-covers wherever it lingered and
misses spots it passed once. Your code, your call. Here is what I'd do instead, with all data you already have:

1. **Viewpoint cells.** Bin each trail frame by its map pose: 1 m cells times 8 headings. Order frames by
   round-robin over cells, so the first pass covers every place and direction once. Inside a cell, pick the
   sharpest frame first (variance of the Laplacian: cheap, and it skips motion blur from turns).
2. **Then visits across days.** The second pass covers the same cells on a different day or session. That makes
   the descriptions useful for "what changed" questions, which is what the memory benchmark is about.
3. **Skip near-duplicates.** Defer frames whose 32x32 grey thumbnail differs only slightly from a frame already in
   the queue for that cell. Then the rest, newest first.

**Speed may matter more than order.** The 4 tok/s per request isn't the GPU: GPU 1 is about 10% busy and vLLM's
engine is pegged on one CPU core, which points at the json_schema grammar step. A second agent on Z690 is measuring
this now on a separate copy of the server on GPU 0, so your batch is untouched. With no schema, a single request runs at
about 51 tok/s. I'll send the full table and a concrete schema or server change when it's in. It may be a 3–10x gain,
which would cover most of the 3,343 pictures instead of about 750.
