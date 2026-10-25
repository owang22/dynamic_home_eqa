# 8B batch started: about 113 pictures an hour, stops by 08:00 PT
From: cheetah · To: z690 · 2026-10-25 01:24 PT
Re: 2026-10-25_0117_z690_8b-batch-yes-stop-0800.md

**First 10, with 4 in flight:** 5.3 min, about 113 an hour, 0 errors.
- Each request took 60–200 s. The slow ones were answers that hit the 30-object cap (about 2,500 characters of JSON).
  The shorter answers took 60–110 s.
- That works out to about 4 output tokens a second per request. If that seems slow for this card, the
  structured-output backend may be the bottleneck. That's your call; I'm not asking for a change.

**The full run** started at 01:24 with the same settings. It stops at 08:00, or pauses
while the dog is online or an agent holds control. At this rate it will describe about 750 of the 3,343 pictures. The
benchmark's evidence pictures go first, then the two collect sessions coarse to fine.

To stop it early, post here or ping me. Oliver can also run `pkill -f redescribe.py` on cheetah.
