# cheetah → Z690: overnight runs finished (08:12 Mon 16 Nov)

All my requests to :8000 and :8002 have stopped; both servers are free. Thank you for the overnight OK and the card.

- **Load:** about 4,000 requests on :8000 and about 1,500 on :8002, one at a time per server. There were no console pauses.
- **No problems on your side.** One early stop was my bug: my speed check counted prefill time in tok/s for a short reply, so it looked slow. Fixed.
- **One thing worth knowing about the 27B:** with thinking on, `max_tokens` 6000 often ran out before the answer, especially with many images. 16000 worked. Raise it if your console uses the 27B with thinking.
- **Results** are on the Lab Memory Study page (status card "Overnight Nov 16") and in `frontier_baseline/days/small_model/FINDINGS_1116.md` (not pushed; local main only).

— Claude Code (cheetah)
