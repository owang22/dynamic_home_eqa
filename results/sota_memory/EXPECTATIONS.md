# sota_memory — predictions written BEFORE results (dynamic-home-eqa-34)

Task: frozen one-person regime, banks `dynamic_home_eqa_fm/results/fm_memory/banks_f1`, hh_s0-2, no message, fmt=conf.
Windows: lead 9-13, sick1 14-16, sick 17-23, ret1 24-26, ret 27-31. "cold" = first question about an object that day.
Bar: n=3, so an effect counts only if it is bigger than the spread across households (the stricter rule below n=6).
Tool: `python3 results/sota_memory/stage_table.py '<glob of run_log.jsonl>'`.

Buffer baseline (fm run1 naive, all|cold):
```
hh_s0  lead 85|82  sick1 44|12  sick 49|21  ret1 75|50  ret 79|68
hh_s1  lead 64|64  sick1 65|37  sick 66|36  ret1 67|50  ret 71|62   (379 questions; weak lead-up)
hh_s2  lead 84|85  sick1 50|20  sick 59|33  ret1 90|92  ret 92|91
```
Degenerate check PASSED 2026-09-23 01:50: llm_sota --memory naive --replay-only on hh_s0 against the fm cache reproduces
the fm naive arm 496/496 (answer and confidence identical, all cache hits).

## pinned (launched 01:55, 3 streams, ~30 min expected per household)
The buffer unchanged, plus the most recent sighting of the object within +-1 h of the query's clock time repeated at the top.
- lead: within +-3 of the buffer (the pinned line usually agrees with the latest sighting and the routine).
- sick1: day 14 pinned line is the old routine -> no help that day; days 15-16 it is yesterday's sick-routine sighting.
  Cold +10 to +20 over the buffer.
- sick (17-23): if salience is the failure, cold rises from 21/36/33 to 45-60. This is the main test.
- ret1: day 24's pinned line is a sick-day sighting -> pinned should be WORSE than the buffer on day 24 (cold -10 to -30),
  recovering by day 26. Pinning buys plasticity and pays on the return like a 1-day forgetter.
- If pinned is about equal to the buffer everywhere, salience is not the lever. The alternative mechanism is visible in the first
  smoke prompt: the model's reasoning quotes the resident card ("Yuki is at her desk from 9:00 to 17:30"). A written routine prior
  may override evidence even when that evidence is salient. Check by reading sick-window wrong answers' reasoning for card quotes.

## SOTA arms (to be filled once the shortlist is agreed; each written before its run)
