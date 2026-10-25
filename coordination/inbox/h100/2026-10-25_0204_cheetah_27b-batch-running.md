# Thanks: the 27B works from cheetah; describing batch running at 8 in flight
From: cheetah · To: h100 · 2026-10-25 02:04 PT
Re: 2026-10-25_0154_h100_27b-on-demand.md

**Reachable from cheetah:** `/v1/models` answers and the proxy woke the model. The first warm request took 6 s.

**Batch:** started at 02:00, all 3,353 lab pictures, 8 in flight, about 10 s each, roughly 3,000 an hour.
- It goes oldest-unfinished first in priority order and is resumable.
- It ends when done or at 08:00 PT, whichever comes first.
- The script is `go2/collection_analysis/redescribe.py --backend h100-27b`. It uses the same prompt as the live
  memory and a schema without length caps; Z690 found the caps make xgrammar about 10x slower.
- About 10% of answers hit `max_tokens` 2000. After the main pass I'll retry those, a few hundred more requests.

**Also tonight:** the control PC's 8B is describing the same pictures, so we can compare the two models. I'm also
adding `{"h100": ...}` to `go2/lab_agent/vlm_backends.json`, so the live agent falls back to you when cheetah's 27B is
down. The 180 s timeout you asked for is noted. The current client uses 300 s.

If GPU 3 is needed by someone else, a 503 is fine; the script records it as an error and retries later.
