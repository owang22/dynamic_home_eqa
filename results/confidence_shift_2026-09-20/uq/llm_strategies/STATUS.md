# LLM-strategies status — updated 2026-09-22 02:05, for a cold read (Oliver reads the page's "What we found" box; this file is the operator's view)

Superseded the original sick10_all/sick10_partial overnight plan below this line's timestamp: Oliver's decision
was to get ONE suite clean first — the one-person-sick regime (sick10_owner / the workshop session's F1 banks).

## Naming (applies everywhere on the page, in this file, and in story_extra.json's keys)
Every arm comes in three message conditions: **no message** (nothing said about the shift), **start message**
(told on the first sick day), **start + end messages** (also told on the first return day). On-disk run
directory names keep their old spelling (`nottold`/`told`/`told_entry`/`told_entryreturn`, and the workshop's
`run1`/`run2_told`/`run3_toldret`) — only labels, tables, and the keys `llm_<memory>_{nomsg,startmsg,startend}`
in `story_extra.json["llm_live"]` use the new names. Mapped in one place: `msg_tag()` in `llm_live_extra.py`.

## Running right now (all detached with nohup; check with `ps aux | grep -E "run_chain|run_knowno|refresh_loop|chain_watch|queue_after"`)
- `run_person_master.sh` (started 01:53; replaces run_chain_person.sh + the told/2x queues): (1) no message, retrieval +
  reflection, hh_s0-9 (long-context pulled out: it is prefill-bound and starved the server at 39 concurrent — its 10-hh
  progress is kept in the cache); (2) start message: retrieval hh_s0-9 || reflection hh_s0-4; (3) start+end: same
  split; (4) long-context LAST, hh_s0-2 only, all three messages, 3 streams; (5) two spells, buffer + retrieval, no
  message -> start message, hh_s0-2. One llm.py invocation per step (crash-isolated per arm, "ARM FAILED (live)").
  Cut order if the rate does not recover (coordinator): two-spells LLM arms first, long-context stays complete on 3 hh.
  Output `chain_person/{nottold,told_entry,told_entryreturn}/`, `chain_person2x/`. ETAs at ~50 calls/min: no message
  ~03:05, start ~04:30, start+end ~05:10, long-context ~08:05, two spells ~08:50 (re-estimated at 03:00).
- `run_knowno_person.sh` (pid 903472): MCQ token-probability channel + KnowNo sets, naive and retrieval, hh_s0-2,
  day-list 13/14/15/20/24/25/30; sequential, 1 stream. Output `knowno_person/<mem>_<hh>/`.
- two spells (sick2x_owner): classical suite + UQ roster DONE (10 hh), population "one person sick, twice" on both
  dropdowns; counters reuse the first spell through never-overwritten time-of-day bins (../problems_found.md 02:10);
  LLM arms run last from the master script. Expectation E31 in ../regime/EXPECTATIONS.md.
- `chain_watch.sh` (every 5 min): aggregate calls/min + "VERDICT: STALLED ARM" lines into chain_progress.log.
- `results/regime_search/tools/refresh_loop.sh` (every 20 min): llm_live_extra.py -> story_page.py -> story_numbers.py,
  so story.html and STORY_numbers.md always reflect the newest calls.jsonl.

## Write-ups
- `STORY.md` (this dir): the morning story, one section per finding, numbers in every claim; `STORY_numbers.md` is
  regenerated every 20 min with the tables behind it. Oliver reads the page, not these.
- `../problems_found.md`: every bug/misdiagnosis of the night with the check that caught it.

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
- "What we found" box at the top of the page (6 bullets, live numbers, build time stamped) — the thing Oliver reads first.
- "LLM arms — three ways of reading its confidence, and honest sets on its own answer": the KnowNo/channel table.
- "Whose routine changed?" LLM slot: the shared-memory interference table (sick person's vs everyone else's things,
  cold too) from the workshop's partial-shift arms; picks up households s3-s5 as 5a lands them.
- Every LLM line/table blanks a day or window with fewer than 10 pooled answers ("(n=3, too few)" in the hover).

## Not yet done
- No arm from the person-regime chain has produced a `run_log.jsonl` (fully finished) yet — the page shows every arm
  as in progress with its count; days/windows with < 10 pooled answers are blanked.
- Two-spells LLM arms: queued, not started. A "guests for a week" third population was discussed; only if it fits
  before 09:30 after the above — currently it does not.

## How to check progress
```
tail -40 results/confidence_shift_2026-09-20/uq/llm_strategies/chain_progress.log
ps aux | grep -E "run_chain_person|run_knowno_person|refresh_loop"
cat results/regime_search/tools/refresh_loop.log | tail -30
```
