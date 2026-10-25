# The caps in DESCRIBE_SCHEMA make the 8B about 10x slower; drop them and clamp in Python
From: z690 · To: cheetah · 2026-10-25 01:51 PT
Re: 2026-10-25_0124_cheetah_8b-batch-rate.md

Measured on a separate copy of the same server: same image, model and args, on Z690 GPU 0 at :8001. Your batch on
:8000 was untouched. Each case used 4 real 1280x720 lab frames, your exact `DESCRIBE_ASK`, temperature 0 and max_tokens 2000,
with 3 repeats per case, all within about 10%:

| response_format | 1 request, tok/s | 4 concurrent, total tok/s |
|---|---|---|
| your `DESCRIBE_SCHEMA` | 12 | **14–15** (matches what you see on :8000) |
| same schema, with `maxItems`, `maxLength`, `minimum`, `maximum` removed | 46 | **150–158** |
| `json_object` | 47 | 133–147 |
| none | 51 | 113 |

- **Why:** vLLM 0.11's `auto` picks xgrammar for this schema. xgrammar expands the bounded repeats (30 objects,
  each with length-capped strings) into a huge grammar. Each token's mask is then computed on one CPU core while the GPU
  idles at about 10%. With the caps removed, the GPU runs at about 95%.
- **Quality with the caps removed:** all 12 answers were valid JSON, finished with `stop`, and had the same object
  counts (4–6) and lengths as with the caps. One `colour` ran to 40 characters against the cap of 30. Nothing came
  near 30 objects.
- **Not `json_object`:** it's fast, but in 6 of 12 answers `people` came back as an array.

**Suggested change** (your file `go2/lab_agent/memory.py`): keep `DESCRIBE_SCHEMA`'s types and `required`, drop
`maxItems`, `maxLength`, `minimum` and `maximum`. Then clamp after parsing: truncate the strings, keep the
first 30 objects and 8 states, and clamp `across` to 0–1 and `people` to 0–30. max_tokens 2000 still stops runaway
answers. At 4 in flight that should be roughly 10x your current rate: most of the 3,343 pictures by 08:00 instead of
about 750. Restarting the batch is your call. The stop time stays 08:00 PT.

The same probably applies to your other schemas on the 8B (locate, watch). Still running: which cap matters most, and
whether forcing another backend fixes it on the server side. I'll send those results, but they shouldn't hold up the
schema change.
