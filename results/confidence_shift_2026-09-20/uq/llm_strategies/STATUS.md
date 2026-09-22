# LLM-strategies status — rewritten 2026-09-21 ~23:50, for a cold read

Superseded the original sick10_all/sick10_partial overnight plan below this line's timestamp: Oliver's decision
was to get ONE suite clean first — the one-person-sick regime (sick10_owner / the workshop session's F1 banks).

## Naming (applies everywhere on the page, in this file, and in story_extra.json's keys)
Every arm comes in three message conditions: **no message** (nothing said about the shift), **start message**
(told on the first sick day), **start + end messages** (also told on the first return day). On-disk run
directory names keep their old spelling (`nottold`/`told`/`told_entry`/`told_entryreturn`, and the workshop's
`run1`/`run2_told`/`run3_toldret`) — only labels, tables, and the keys `llm_<memory>_{nomsg,startmsg,startend}`
in `story_extra.json["llm_live"]` use the new names. Mapped in one place: `msg_tag()` in `llm_live_extra.py`.

## Running right now
- `run_chain_person.sh`, retrieval/longcontext/reflect x {no message, start message, start + end messages},
  hh_s0-9, on `dynamic_home_eqa_fm/results/fm_memory/banks_f1` (no message, start message) and `banks_f1_return`
  (start + end messages) — same banks the workshop session's own run1/run2_told/run3_toldret use, so the truth
  join and the prompt cache both line up. 40 workers, started 23:35. Output: `uq/llm_strategies/chain_person/
  {nottold,told_entry,told_entryreturn}/`.
- `run_knowno_person.sh` — the one new-LLM-call item: MCQ token-probability channel + KnowNo conformal sets,
  buffer(naive) and retrieval, hh_s0-2, day-list 13/14/15/20/24/25/30. Output: `uq/llm_strategies/knowno_person/`.
- `refresh_loop.sh` (in `results/regime_search/tools/`) — every 20 minutes: `llm_live_extra.py` then
  `story_page.py story.html`, so the published page stays current without manual rebuilds.

## On the page now (results/regime_search/story.html, "one person sick" population)
- Accuracy and confidence charts: every landed arm, as a dashed line (solid once an arm reaches its full
  per-household question count) labelled with its message condition and an "(in progress, N of <total>,
  households ...)" progress note.
- Calibration-gap chart: same arms, both "as stated" and "lead-day calibrated" (a real per-arm monotone fit on
  lead days 9-13, not a placeholder) — lead-day-calibrated numbers were cross-checked against the workshop
  session's own headline figures for buffer/no-message and buffer/start-message before shipping (see
  `../problems_found.md`'s 23:20 entry for the one mismatch found and fixed along the way).
- New table, "LLM arms — an answer-or-ask gate on their own stated confidence": an adaptive-conformal
  answer-or-ask gate (decaying-step control on 1-stated-confidence, alpha=0.10) reporting ask rate and realised
  miss rate per window, plus whether the gate's confidence bar tightens right at the shift.

## Not yet done
- KnowNo/conformal channel results aren't wired into the page yet — `run_knowno_person.sh` writes to
  `knowno_person/`, but nothing reads it into `story_extra.json` yet.
- No arm from the relaunched person-regime chain has produced a `run_log.jsonl` (i.e., fully finished) yet as of
  this write-up — everything currently on the page is still in progress.

## How to check progress
```
tail -40 results/confidence_shift_2026-09-20/uq/llm_strategies/chain_progress.log
ps aux | grep -E "run_chain_person|run_knowno_person|refresh_loop"
cat results/regime_search/tools/refresh_loop.log | tail -30
```
