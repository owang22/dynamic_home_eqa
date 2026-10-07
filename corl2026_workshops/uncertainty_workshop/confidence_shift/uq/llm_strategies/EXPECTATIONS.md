# Expectations for the overnight LLM-strategy chain — written 21:05, before the chain runs

Per-arm bar (checked by `llm_strategy_check.py`'s printout against this file, appended to `chain_progress.log`
after every arm — a human/later-session read, not yet an automated pass/fail gate; see STATUS.md for that caveat):

- **status/fallback**: `status` all "ok", fallback rate < 10% in every arm — anything worse means a prompt or
  parsing regression, stop and look rather than trust the numbers.
- **accuracy vs yardsticks** (same household/day, from `uq/regime/<regime>/{none_tt72,none_lastseen}`): every
  strategy should sit AT OR ABOVE last-seen's day-by-day accuracy throughout, and should approach or exceed the
  3-day timetable's by the time each has ~10-13 days of history (matching the classical shape: climbs from
  ~45-50% early to 75-85% by day 13). A strategy that stays at last-seen's level past day 10 is not using its
  memory.
- **cold/warm gap**: warm (later questions about an object, same day) should read higher than cold (the first
  question about it that day) in every arm from day 3 onward — this is the cheapest signal that memory is doing
  anything at all; a near-zero gap deep into the run is suspicious.
- **noticing**: 0 fires on sick10_all/sick10_partial days 1-13 (false alarms) in the great majority of arms; a
  fire on day 14 or 15 (the shift) in at least some arms — no fire at all by day 18 across every strategy would
  be the "these methods do not notice" finding itself, reportable either way but worth a second look before
  calling it that.
- **longcontext token count**: must stay under ~90k prompt tokens through day 31 (Qwen3.8-27B's ~98k window) —
  the chain logs `prompt_tokens` per row; if it approaches the ceiling, the run for that household should be
  capped rather than silently truncated by the server.
- **partial-shift arms** (sick10_partial): accuracy AND confidence should be reported split by owner (the sick
  resident's things vs everyone else's) — these are exactly the "shared-state" panel's missing LLM-memory slot
  from the story page; a strategy with one memory object per household (all four here: none keep a truly
  separate record per resident) belongs in that panel once its numbers land.

Wrong direction, worth a message rather than silent continuation: an arm crashing on every household of a regime
(vs one household — the latter is normal server/simulator noise); accuracy at or below last-seen's on EVERY
household by day 20; a leak-check abort (would show as a Python traceback in the arm's own log file, not just a
low accuracy number).
