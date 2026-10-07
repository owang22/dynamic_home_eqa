# What a stronger model adds - predictions written before the runs

Written 2026-09-30, evening, by session dynamic-home-eqa-ba, before any full household has run.
Not for the workshop deadline. Oliver asked for two things: Qwen3.8 with its thinking switched on
(and output we can still parse), and a Claude model given exactly the prompts Qwen gets.

## What is already measured (format tests, one household's real prompts, hh_s2_t03)

- vLLM 0.25 with `--reasoning-parser qwen3` applies the JSON grammar only AFTER the think block, so
  thinking and the schema combine. All test answers parsed and passed the schema.
- With no cap, Qwen thinks for a very long time: one room choice 5,930 tokens (222 s), one night
  22,766 tokens (826 s). The run would take days per household. Not usable as is.
- vLLM's `thinking_token_budget` caps it: at 1,000 the think block is cut, closed, and a valid answer
  follows (room choices 11 to 47 s).
- Most early thinking was spent guessing the answer format, because the prompt never names the
  fields (without thinking the grammar forces them in order, so it never had to). The thinking client
  now appends one line naming the fields to the system message. Nothing about the home is added.
- Claude (Sonnet 5.5 via one fresh `claude -p` call per prompt, no tools, no settings): valid
  structured output, 3 s per room choice, 13 s per night. Claude Code adds ~500 tokens of its own
  (the user's email, working directory, date), nothing about the task.

## The question each run answers

The project's current finding with Qwen: the nightly notes add nothing on top of the raw record
("log only, no notes" 85.2 / 95.9 against log-and-notes 85.6 / 96.6, ten households). So the
comparison that matters is that same pair, run with a stronger model:

  does a stronger writer make the notes worth something, and does it notice the illness by itself?

## Predictions (one household first, hh_s2_t03; numbers are first-room-right on all questions)

1. Qwen with thinking (1,000-token cap): within the rerun noise floor of plain Qwen on both arms
   (|difference| < 2 points over the month). Thinking mostly re-reads the record the prompt already
   shows; the record is the whole effect. If thinking changes anything it is the nightly notes:
   more conditional notes ("on days when ...").
2. Claude Sonnet, log only: within a few points of Qwen log only. The record answers most questions
   and Qwen already reads it well.
3. Claude Sonnet, log and notes: the place a gap could open. Prediction: notes written with
   conditions ("holds under: workday daytime" appeared in its very first night), and during the
   illness a note that names the change in the routine within two or three nights of day 14.
   Days 15-17 first-room-right above Qwen's log-and-notes by 5+ points on movers; days 8-13 the same.
4. The first changed day (day 14) is about 31-37% for every arm and every model: the new routine
   has not been seen yet, so no model can answer it. If Claude scores much higher on day 14, look
   for a leak before believing it.
5. The return (day 24): a model that wrote "Tomas is ill" as a standing note will be wrong on the
   return unless it withdraws it. Prediction: Claude withdraws within two nights; Qwen did not
   reliably (3 of 8 told runs dropped the condition within three nights).

## What will be checked while it runs

- 3 / 5 / 10 minutes after launch: calls succeed, no lost calls, answers parse, call_times grows.
- The first night's notes read in full, and the first day's answers, against the prompt.
- At day 14 and day 24: the notes, read in full, for whether the change is named and conditioned.
- Every cut the Claude client makes to fit a schema limit is counted (`fields_cut_to_the_schema_limit`).
- Plain Qwen is rerun on the same households in the same session, against the current code. The
  published Table 1 row (overnight_wave, 25 Sep) does not replay: commit b4207b7b3 (26 Sep 20:49)
  widened the nightly `why` limit 240 -> 600 and the token budget 260 -> 420 per note, so every
  older nightly call has a different cache key and a different grammar (the prompt text for this arm
  is unchanged; confirmed by -37). Anything written here says "plain Qwen, rerun 30 Sep", never
  compares against the Table 1 number.
